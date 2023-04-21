from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        unique=True,
        max_length=200,
        help_text='Введите название',
        verbose_name='Название',
    )
    measure = models.CharField(
        'Единица измерения',
        max_length=200,
        help_text='Введите единицу измерения',
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ('-name', 'measure')
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                name='unique_ingridient',
                fields=['name', 'measure'],
            ),
        ]

    def __str__(self):
        return f'Название: {self.name[:15]} Адрес: {str(self.measure)}'
