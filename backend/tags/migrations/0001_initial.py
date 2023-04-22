# Generated by Django 4.2 on 2023-04-22 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название', max_length=200, unique=True, verbose_name='Название')),
                ('color', models.CharField(blank=True, help_text='Введите цвет в HEX-формате', max_length=10, null=True, unique=True, verbose_name='Цвет')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('-name',),
            },
        ),
    ]