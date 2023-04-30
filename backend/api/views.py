from djoser.views import TokenCreateView
from rest_framework import status, permissions, viewsets
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import Http404, HttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAuthorOrReadOnly
from api.mixins import CreateListDestroyViewSet
from rest_framework.generics import get_object_or_404
from api.serializers import (
    TagSerializer,
    SubscripeSerializer,
    IngredientSerializer,
    RecipeListSerializer,
    RecipeCreateSerializer,
    RecipeSerializer
)
from ingredients.models import Ingredient
from recipes.models import (
    Reciepe,
    FavoriteRecipe,
    ShoppingCartRecipe,
    IngredientInRecipe
)
from tags.models import Tag
from users.models import (
    User,
    Subscription,
)


class TokenCreateView(TokenCreateView):

    permission_classes = (permissions.AllowAny,)

    def _action(self, serializer):
        response = super()._action(serializer)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_201_CREATED
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    pagination_class = None

    def get_queryset(self):
        return Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        return Ingredient.objects.all()


class RecipesSubscriptionViewSet(CreateListDestroyViewSet):
    serializer_class = SubscripeSerializer
    permission_classes = (IsAuthenticated,)

    def get_author(self):
        return get_object_or_404(User, id=self.kwargs.get('author_id'))

    def get_object(self):
        return get_object_or_404(
            Subscription, user=self.request.user, author=self.get_author()
        )

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

    def destroy(self, request, *args, **kwargs):
        self.get_author()
        try:
            self.get_object()
        except Http404:
            data = {'errors': 'Невозможно отпистаться.'}
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


class ReciepeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeListSerializer
    edit_permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Reciepe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, data=request.data,
                                          context={"request": request})
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
        recipe = get_object_or_404(Reciepe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, data=request.data,
                                          context={"request": request})
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
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        filename = 'shopping_cart.pdf'
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = (f'attachment; filename={filename}')
        return file
