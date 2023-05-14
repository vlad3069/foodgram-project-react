from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import transaction
from djoser import serializers as djoser_serialize
from drf_base64.fields import Base64ImageField
from rest_framework import serializers as rest_serialize

from ingredients.models import Ingredient
from recipes.models import IngredientInRecipe, Recipe, FavoriteRecipe
from tags.models import Tag
from users.models import Subscription, User


class UserReadSerializer(djoser_serialize.UserSerializer):
    is_subscribed = rest_serialize.SerializerMethodField()

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscription.objects.filter(
                user=self.context['request'].user, author=obj).exists()
        return False

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')


class UserCreateSerializer(djoser_serialize.UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'password')
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
        }

    def validate(self, obj):
        invalid_usernames = ['me', 'set_password',
                             'subscriptions', 'subscribe']
        if self.initial_data.get('username') in invalid_usernames:
            raise rest_serialize.ValidationError(
                {'username': 'Вы не можете использовать этот username.'}
            )
        return obj


class SetPasswordSerializer(rest_serialize.Serializer):
    current_password = rest_serialize.CharField()
    new_password = rest_serialize.CharField()

    def validate(self, obj):
        try:
            validate_password(obj['new_password'])
        except django_exceptions.ValidationError as e:
            raise rest_serialize.ValidationError(
                {'new_password': list(e.messages)}
            )
        return super().validate(obj)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise rest_serialize.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise rest_serialize.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class TagSerializer(rest_serialize.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(rest_serialize.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(rest_serialize.ModelSerializer):
    id = rest_serialize.SlugRelatedField(
        source='ingredient', slug_field='id', queryset=Ingredient.objects.all()
    )
    name = rest_serialize.SlugRelatedField(
        source='ingredient', slug_field='name', read_only=True
    )
    measurement_unit = rest_serialize.SlugRelatedField(
        source='ingredient', slug_field='measurement_unit', read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        exclude = (
            'recipe',
            'ingredient',
        )


class RecipeSerializer(rest_serialize.ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = rest_serialize.ReadOnlyField()
    cooking_time = rest_serialize.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class MySubscriptionSerializer(UserReadSerializer):
    recipes = rest_serialize.SerializerMethodField()
    recipes_count = rest_serialize.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')
        read_only_fields = fields

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                queryset = queryset[:recipes_limit]
            except (TypeError, ValueError):
                pass
        return RecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscripeSerializer(rest_serialize.ModelSerializer):
    user = rest_serialize.HiddenField(
        default=rest_serialize.CurrentUserDefault())
    author = rest_serialize.HiddenField(
        default=rest_serialize.CurrentUserDefault())

    class Meta:
        model = Subscription
        fields = (
            'user',
            'author',
        )

    def validate(self, attrs):
        user = self.context.get('request').user
        author = self.initial_data.get('author')
        if user == author:
            raise rest_serialize.ValidationError(
                'Нельзя подписаться на самого себя!')
        if author.subscriptions.filter(user=user).exists():
            raise rest_serialize.ValidationError(
                'Нельзя подписаться дважды на одного пользователя!'
            )
        return super().validate(attrs)


class RecipeListSerializer(rest_serialize.ModelSerializer):
    author = UserReadSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set', many=True
    )
    tags = TagSerializer(many=True)
    is_favorited = rest_serialize.SerializerMethodField()
    is_in_shopping_cart = rest_serialize.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and FavoriteRecipe.objects.filter(
                user=self.context['request'].user,
                recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and recipe.shoppingcartrecipe_set.filter(
                user=request.user).exists()
        )


class RecipeCreateSerializer(rest_serialize.ModelSerializer):
    tags = rest_serialize.PrimaryKeyRelatedField(many=True,
                                                 queryset=Tag.objects.all())
    author = UserReadSerializer(read_only=True)
    id = rest_serialize.ReadOnlyField()
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set', many=True
    )
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients',
                  'tags', 'image',
                  'name', 'text',
                  'cooking_time', 'author')
        extra_kwargs = {
            'ingredients': {'required': True, 'allow_blank': False},
            'tags': {'required': True, 'allow_blank': False},
            'name': {'required': True, 'allow_blank': False},
            'text': {'required': True, 'allow_blank': False},
            'image': {'required': True, 'allow_blank': False},
            'cooking_time': {'required': True},
        }

    def validate(self, attrs):
        if len(attrs['tags']) == 0:
            raise rest_serialize.ValidationError(
                'Должен быть выбран хотя бы один тег.')
        if len(attrs['tags']) != len(set(attrs['tags'])):
            raise rest_serialize.ValidationError('Теги должны быть уникальны.')
        if len(attrs['ingredientinrecipe_set']) == 0:
            raise rest_serialize.ValidationError(
                'Должен быть выбран хотя бы один ингредиент.'
            )
        ingredients = attrs['ingredientinrecipe_set']
        if len(ingredients) != len(set(
                obj['ingredient'] for obj in ingredients)):
            raise rest_serialize.ValidationError(
                'Ингредиенты должны быть уникальны.')
        if any(obj['amount'] <= 0 for obj in ingredients):
            raise rest_serialize.ValidationError(
                'Количество игредиента должно быть больше нуля.'
            )
        if attrs['cooking_time'] <= 0:
            raise rest_serialize.ValidationError(
                'Время приготовления должно быть больше нуля.'
            )
        return super().validate(attrs)

    @staticmethod
    def create_ingredientsinrecipe(recipe, ingredientinrecipe_set):
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=item['ingredient'],
                    amount=item['amount']
                )
                for item in ingredientinrecipe_set
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request']
        ingredientinrecipe_set = validated_data.pop('ingredientinrecipe_set')
        tags = validated_data.pop('tags')
        instance = Recipe.objects.create(author=request.user, **validated_data)
        self.create_ingredientsinrecipe(
            instance, ingredientinrecipe_set)
        instance.tags.set(tags)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        ingredientinrecipe_set = validated_data.pop('ingredientinrecipe_set')
        IngredientInRecipe.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.create_ingredientsinrecipe(instance, ingredientinrecipe_set)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance,
                                    context=self.context).data
