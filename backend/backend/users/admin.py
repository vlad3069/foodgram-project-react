from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminAuth

from .models import Subscription, User


@admin.register(User)
class UserAdmin(UserAdminAuth):

    @admin.display(description='Количество рецептов')
    def recipe_amount(self, user):
        '''Количество рецептов для вывода в админке.'''
        return user.recipe.count()

    def subscription_amount(self, user):
        '''Количество подписчиков для вывода в админке.'''
        return user.subscriptions.count()
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
        'subscription_amount',
        'recipe_amount',
    )
    list_filter = (
        'is_superuser',
        'is_staff',
    )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Персональная информация',
            {
                'fields': (
                    'username',
                    'first_name',
                    'last_name',
                )
            },
        ),
        (
            'Права доступа',
            {
                'fields': (
                    'is_active',
                    'is_superuser',
                    'is_staff',
                )
            },
        ),
    )
    search_fields = (
        'username',
        'email',
    )
    ordering = ('email', 'username')
    filter_horizontal = ()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author',
    )
    search_fields = (
        'user',
        'author',
    )
    list_filter = (
        'user',
        'author',
    )
    list_editable = (
        'user',
        'author'
    )
