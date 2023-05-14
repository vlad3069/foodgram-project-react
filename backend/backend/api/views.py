from django.db.models import Sum
from django.db.models.query_utils import Q
from django.http import Http404, HttpResponse, JsonResponse
from djoser.views import TokenCreateView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.mixins import CreateListDestroyViewSet
from api.pagination import CustomPaginator
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer, MySubscriptionSerializer,
                             RecipeCreateSerializer, RecipeListSerializer,
                             RecipeSerializer, SetPasswordSerializer,
                             SubscripeSerializer, TagSerializer,
                             UserCreateSerializer, UserReadSerializer)
from ingredients.models import Ingredient
from recipes.models import (FavoriteRecipe, IngredientInRecipe, Recipe,
                            ShoppingCartRecipe, TagRecipe)
from tags.models import Tag
from users.models import Subscription, User


class TokenCreateView(TokenCreateView):

    permission_classes = (AllowAny,)

    def _action(self, serializer):
        response = super()._action(serializer)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_201_CREATED
        return response


class UserViewSet(CreateListDestroyViewSet):
    pagination_class = CustomPaginator
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return UserCreateSerializer

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if self.request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPaginator)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscriptions__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscripeSerializer(page, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = SubscripeSerializer(
                author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscription, user=request.user,
                              author=author).delete()
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    pagination_class = None

    def get_queryset(self):
        return Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            filter1 = queryset.filter(name__istartswith=name)
            filter1and2 = queryset.filter(
                ~Q(name__istartswith=name) & Q(name__icontains=name)
            )
            queryset = list(filter1) + list(filter1and2)
        return queryset


class RecipesSubscriptionViewSet(CreateListDestroyViewSet):
    serializer_class = MySubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_author(self):
        return get_object_or_404(User, id=self.kwargs.get('author_id'))

    def get_object(self):
        return get_object_or_404(
            Subscription, user=self.request.user, author=self.get_author()
        )

    def destroy(self, request, *args, **kwargs):
        self.get_author()
        try:
            self.get_object()
        except Http404:
            data = {'errors': 'Невозможно отписаться.'}
            return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in (
            'create',
            'destroy',
        ):
            return SubscripeSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.filter(subscriptions__user=self.request.user)
        return None

    def create(self, request, *args, **kwargs):
        request.data.update(author=self.get_author())
        super().create(request, *args, **kwargs)
        serializer = self.serializer_class(
            instance=self.get_author(), context=self.get_serializer_context()
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(author=self.get_author())


class ReciepeViewSet(viewsets.ModelViewSet):
    edit_permission_classes = (IsAuthorOrReadOnly,)

    def get_permissions(self):
        if self.action in (
            'destroy',
            'partial_update',
        ):
            return [
                permission() for permission in self.edit_permission_classes
                ]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeListSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited:
            recipes_id = (
                FavoriteRecipe.objects.filter(user=user).values('recipe__id')
                if user.is_authenticated
                else []
            )
            condition = Q(id__in=recipes_id)
            queryset = queryset.filter(
                condition if is_favorited == '1' else ~condition
            ).all()
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart:
            recipes_id = (
                ShoppingCartRecipe.objects.filter(user=user).values(
                    'recipe__id')
                if user.is_authenticated
                else []
            )
            condition = Q(id__in=recipes_id)
            queryset = queryset.filter(
                condition if is_in_shopping_cart == '1' else ~condition
            ).all()
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author__id=author_id).all()
        tags = self.request.query_params.getlist('tags')
        if tags:
            tags = Tag.objects.filter(slug__in=tags).all()
            recipes_id = (
                TagRecipe.objects.filter(tag__in=tags).values(
                    'recipe__id').distinct()
            )
            queryset = queryset.filter(id__in=recipes_id)
        return queryset

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, data=request.data,
                                          context={'request': request})
            serializer.is_valid(raise_exception=True)
            if not FavoriteRecipe.objects.filter(user=request.user,
                                                 recipe=recipe).exists():
                FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(FavoriteRecipe, user=request.user,
                              recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, data=request.data,
                                          context={'request': request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingCartRecipe.objects.filter(user=request.user,
                                                     recipe=recipe).exists():
                ShoppingCartRecipe.objects.create(
                    user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(ShoppingCartRecipe, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__shoppingcartrecipe__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        filename = 'shopping_cart.pdf'
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='application/pdf')
        file['Content-Disposition'] = (
            f'attachment; filename={filename}')
        return file
