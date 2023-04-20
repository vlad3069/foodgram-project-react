from django.db import models

class Tag(models.Model):
    name = models.CharField(
        'Название',
        unique=True,
        max_length=256,
        help_text='Введите название',
        verbose_name='Название',
    )
    color = models.CharField(
        'Цвет',
        unique=True,
        max_length=256,
        help_text='Введите цвет в HEX-формате',
        verbose_name='Цвет',
        blank=True,
        null=True,
    )
    slug = models.SlugField(
        'Slug',
        null=False,
        unique=True,
        verbose_name='Адрес',
    )


    class Meta:
        ordering = ('-name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'Название: {self.name[:15]} Адрес: {str(self.slug)}'
