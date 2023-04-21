from django.contrib import admin

from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measure',
    )
    list_editable = (
        'name',
        'measure',
    )
    search_fields = (
        'name',
        'measure',
    )
    list_filter = ('name',)
