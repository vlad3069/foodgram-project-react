from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        help_text=(
            'Введите уникальное имя пользователя. Максимум 150 символов. '
            'Используйте только английские буквы, цифры и символы @/./+/-/_'
        ),
    #   validators= 

    )
    email = models.EmailField(
        max_length=254,
        verbose_name='email',
        unique=True,
            #   validators= 
        help_text='Введите адрес электронной почты',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='фамилия',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return self.username[:15]