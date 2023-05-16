from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models


class User(AbstractUser):

    username = models.CharField(
        max_length=150,
        verbose_name='юзернейм пользователя',
        unique=True,
        help_text=(
            'Введите юзернейм пользователя. Максимум 150 символов. '
            'Используйте только английские буквы, цифры и символы @/./+/-/_'
        ),
        validators=[ASCIIUsernameValidator()],
        error_messages={
            'unique': 'Пользователь с таким юзернеймом уже существует',
        },
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='email',
        unique=True,
        validators=[ASCIIUsernameValidator()],
        help_text='Введите адрес электронной почты',
        error_messages={
            'unique': 'Пользователь с такой почтой уже существует',
        },
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='имя',
        help_text='Введите ваше имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='фамилия',
        help_text='Введите вашу фамилию',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return self.username[:15]


class UserConnection(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите из списка пользователя',
    )

    class Meta:
        abstract = True


class Subscription(UserConnection):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Автор',
        help_text='Выберите автора из списка',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name='unique_subscription',
                fields=['user', 'author'],
            ),
        ]
