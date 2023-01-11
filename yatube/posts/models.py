from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel, PubDateModel


User = get_user_model()
MAX_SYMBOLS_STR_POST = 15


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        max_length=200,
        help_text='Введите название группы'
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(
        'Описание группы',
        help_text='Добавьте описание новой группы'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(PubDateModel):
    text = models.TextField(
        'Текст поста',
        help_text='Текст нового поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Вы можете добавить изображение к вашему посту'
    )

    class Meta:
        default_related_name = 'posts'
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:MAX_SYMBOLS_STR_POST]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
    )
    text = models.TextField(
        'Текст',
        help_text='Текст нового комментария'
    )

    def __str__(self) -> str:
        return self.text

    class Meta:
        ordering = ['-created']


class Follow(CreatedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following'
    )

    class Meta:
        ordering = ['-author']
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                                               name='unique_following')]
