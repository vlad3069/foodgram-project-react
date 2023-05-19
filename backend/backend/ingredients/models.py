from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        unique=False,
        max_length=200,
        help_text='Введите название',
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        help_text='Введите единицу измерения',
    )

    class Meta:
        ordering = ('-name', 'measurement_unit')
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                name='unique_ingridients',
                fields=['name', 'measurement_unit'],
            ),
        ]

    def __str__(self):
        return (f'Название: {self.name[:15]}'
                f'Количество: {str(self.measurement_unit)}'
                )
