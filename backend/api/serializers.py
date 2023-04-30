
from django.db import transaction
from rest_framework import serializers as rest_serialize
from djoser import serializers as djoser_serialize
from drf_base64.fields import Base64ImageField

from recipes.models import Reciepe, IngredientInRecipe
from ingredients.models import Ingredient
from tags.models import Tag
from users.models import User, Subscription


class UserSerializer(djoser_serialize.UserSerializer):
    is_subscribed = rest_serialize.SerializerMethodField()

    def get_is_subscribed(self, author):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and author.subscriptions.filter(user=request.user).exists()
        )

    class Meta(djoser_serialize.UserSerializer.Meta):
        model = User
        fields = djoser_serialize.UserSerializer.Meta.fields + (
            'is_subscribed',)


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


class MySubscriptionSerializer(UserSerializer):
    recipes = rest_serialize.SerializerMethodField()
    recipes_count = rest_serialize.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_recipes(self, user_object):
        queryset = user_object.recipes.all()
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                queryset = queryset[:recipes_limit]
            except (TypeError, ValueError):
                pass
        return RecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, user_object):
        return user_object.recipes.count()


class SubscripeSerializer(rest_serialize.ModelSerializer):
    user = rest_serialize.HiddenField()
    author = rest_serialize.HiddenField()

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
    author = UserSerializer()
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set', many=True
    )
    tags = TagSerializer(many=True)
    is_favorited = rest_serialize.SerializerMethodField()
    is_in_shopping_cart = rest_serialize.SerializerMethodField()

    class Meta:
        model = Reciepe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')

    def get_is_favorited(self, recipe):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and recipe.favoriterecipe_set.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and recipe.shoppingcartrecipe_set.filter(
                user=request.user).exists()
        )


class RecipeSerializer(rest_serialize.ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = rest_serialize.ReadOnlyField()
    cooking_time = rest_serialize.ReadOnlyField()

    class Meta:
        model = Reciepe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class RecipeCreateSerializer(rest_serialize.ModelSerializer):
    tags = rest_serialize.PrimaryKeyRelatedField(many=True,
                                                 queryset=Tag.objects.all())
    author = UserSerializer(read_only=True)
    id = rest_serialize.ReadOnlyField()
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Reciepe
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

    def validate(self, obj):
        for field in ['name', 'text', 'cooking_time']:
            if not obj.get(field):
                raise rest_serialize.ValidationError(
                    f'{field} - Обязательное поле.'
                )
        if not obj.get('tags'):
            raise rest_serialize.ValidationError(
                'Нужно указать минимум 1 тег.'
            )
        if not obj.get('ingredients'):
            raise rest_serialize.ValidationError(
                'Нужно указать минимум 1 ингредиент.'
            )
        inrgedient_id_list = [item['id'] for item in obj.get('ingredients')]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise rest_serialize.ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        return obj

    @transaction.atomic
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Reciepe.objects.create(author=self.context['request'].user,
                                        **validated_data)
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        IngredientInRecipe.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.tags_and_ingredients_set(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance,
                                    context=self.context).data
