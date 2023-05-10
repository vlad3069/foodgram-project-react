from django.core.validators import MinValueValidator
from django.db import models

from ingredients.models import Ingredient
from tags.models import Tag
from users.models import User, UserСonnection


class Recipe(models.Model):
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        help_text='Автоматически устанавливается текущая дата и время',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор',
    )
    name = models.CharField(
        'Название',
        unique=True,
        max_length=200,
        help_text='Введите название',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='Recipes/',
        blank=True,
        null=True,
    )
    text = models.TextField(
        'Текст поста',
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
        return (
            f'Автор: {str(self.author)} Название: {self.name[:15]}'
        )


class RecipeСonnection(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт',
    )

    class Meta:
        abstract = True


class FavoriteRecipe(RecipeСonnection, UserСonnection):

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_favorite',
                fields=['recipe', 'user'],
            ),
        ]
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'


class ShoppingCartRecipe(RecipeСonnection, UserСonnection):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_shopping_cart',
                fields=['recipe', 'user'],
            ),
        ]
        verbose_name = 'Рецепт в корзине пользователя'
        verbose_name_plural = 'Рецепты в корзинах пользователей'


class IngredientInRecipe(RecipeСonnection):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент рецепта',
        help_text='Выберите ингредиент рецепта',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингридиента',
        help_text='Введите количество ингридиента',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return (
            f'{self.ingredient.name} — {self.amount} {self.ingredient.measure}'
        )


class TagRecipe(RecipeСonnection):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.DO_NOTHING,
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
