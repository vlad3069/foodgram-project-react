from django.db import models

from tags.models import Tag
from ingredients.models import Ingredient
from users.models import User

class Reciepe(models.Model):
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        help_text='Автоматически устанавливается текущая дата и время',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Reciepes',
        verbose_name='Автор',
    )
    name = models.CharField(
        "Название",
        unique=True,
        max_length=256,
        help_text="Введите название",
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='Reciepes/images/',
        blank=True,
        null=True,
    )
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag, 
        through='TagRecipe',
        verbose_name='Теги',
        help_text='Выберите теги',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'id: {self.id} Автор: {str(self.author)} Название: {self.name[:15]}'


class FavoriteRecipe(Reciepe, User):
        class Meta:
            constraints = [
                models.UniqueConstraint(
                    name='unique_favorite',
                    fields=['recipe', 'user'],
                ),
            ]
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'

class ShoppingCartRecipe(Reciepe, User):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_shopping_cart',
                fields=['recipe', 'user'],
            ),
        ]
        verbose_name = 'Рецепт в корзине пользователя'
        verbose_name_plural = 'Рецепты в корзинах пользователей'

class IngredientInRecipe(Reciepe):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
        verbose_name='Ингредиент рецепта',
        help_text='Выберите ингредиент рецепта',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингридиента',
        help_text='Введите количество ингридиента',
        verbose_name='Количество ингридиента',
        )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return (
            f'{self.ingredient.name} — {self.amount} {self.ingredient.measure}'
        )

class TagRecipe(Reciepe):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.RESTRICT,
        verbose_name='Тег',
        help_text='Выберите из списка тег',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe_tag',
                fields=['recipe', 'tag'],
            ),
        ]
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'
