from django.db.models.query_utils import Q
from django_filters.rest_framework import FilterSet, filters

from ingredients.models import Ingredient
from recipes.models import (FavoriteRecipe, Recipe,
                            ShoppingCartRecipe)
from tags.models import Tag


class FilterRecipe(FilterSet):
    queryset = Recipe.objects.all()
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def is_favorited_filter(self, queryset, name, value):
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
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
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
        return queryset


class FilterIngridientInRecipe(FilterSet):
    queryset = Ingredient.objects.all()
    is_name_similar = filters.BooleanFilter(
        method='is_name_similar_filter')

    class Meta:
        model = Ingredient
        fields = ('name', )

    def is_name_similar_filter(self, queryset, name, value):
        name = self.request.query_params.get('name')
        if name:
            filter1 = queryset.filter(name__istartswith=name)
            filter1and2 = queryset.filter(
                ~Q(name__istartswith=name) & Q(name__icontains=name)
            )
            queryset = list(filter1) + list(filter1and2)
        return queryset
