# Generated by Django 2.2.16 on 2023-01-05 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
    ]
