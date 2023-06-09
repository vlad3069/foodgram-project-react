# Generated by Django 4.2 on 2023-04-22 13:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tags', '0001_initial'),
        ('ingredients', '0001_initial'),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcartrecipe',
            name='user',
            field=models.ForeignKey(help_text='Выберите из списка пользователя', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='reciepe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Reciepes', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='reciepe',
            name='ingredients',
            field=models.ManyToManyField(help_text='Выберите ингредиенты', through='recipes.IngredientInRecipe', to='ingredients.ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AddField(
            model_name='reciepe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите теги', through='recipes.TagRecipe', to='tags.tag', verbose_name='Теги'),
        ),
        migrations.AddField(
            model_name='ingredientinrecipe',
            name='ingredient',
            field=models.ForeignKey(help_text='Выберите ингредиент рецепта', on_delete=django.db.models.deletion.CASCADE, to='ingredients.ingredient', verbose_name='Ингредиент рецепта'),
        ),
        migrations.AddField(
            model_name='ingredientinrecipe',
            name='recipe',
            field=models.ForeignKey(help_text='Выберите рецепт', on_delete=django.db.models.deletion.CASCADE, to='recipes.reciepe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='favoriterecipe',
            name='recipe',
            field=models.ForeignKey(help_text='Выберите рецепт', on_delete=django.db.models.deletion.CASCADE, to='recipes.reciepe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='favoriterecipe',
            name='user',
            field=models.ForeignKey(help_text='Выберите из списка пользователя', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='tagrecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'tag'), name='unique_recipe_tag'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcartrecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='unique_shopping_cart'),
        ),
        migrations.AddConstraint(
            model_name='favoriterecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='unique_favorite'),
        ),
    ]
