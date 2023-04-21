from django.contrib import admin

from .models import (
    Reciepe,
    IngredientInRecipe,
    FavoriteRecipe,
    TagRecipe,
    ShoppingCartRecipe,
)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1


class FavoriteRecipeInline(admin.TabularInline):
    model = FavoriteRecipe


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    min_num = 1


class ShoppingCartRecipeInline(admin.TabularInline):
    model = ShoppingCartRecipe


@admin.register(Reciepe)
class RecipeAdmin(admin.ModelAdmin):
    @admin.display(description='Количество добавлений в избранное')
    def favorite_amount(self):
        return FavoriteRecipe.objects.filter(recipe=self.id).count()

    @admin.display(description='Игредиенты')
    def ingredients_in_recipe(self):
        pass
    list_display = (
        'pk',
        'name',
        'author',
    )
    search_fields = (
        'author',
        'name',
    )
    list_filter = (
        'name',
        'author',
        'tags',
    )
    inlines = (
        IngredientInRecipeInline,
        FavoriteRecipeInline,
        TagRecipeInline,
        ShoppingCartRecipeInline,
    )
    readonly_fields = (favorite_amount,)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount',
    )
    list_editable = ('amount',)
    list_filter = (
        'recipe',
        'ingredient',
    )


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'user',
    )
    list_filter = (
        'recipe',
        'user',
    )


@admin.register(ShoppingCartRecipe)
class ShoppingCartRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'user',
    )
    list_filter = (
        'recipe',
        'user',
    )


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'tag',
    )
    list_filter = (
        'recipe',
        'tag',
    )
