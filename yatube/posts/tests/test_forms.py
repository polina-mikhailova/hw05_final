import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from . import constants as c
from ..forms import CommentForm, PostForm
from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test_slug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост для редактирования',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

        cls.POST_CREATE_REVERSE = reverse(c.POST_CREATE_URL_NAME)
        cls.POST_EDIT_REVERSE = reverse(c.POST_EDIT_URL_NAME,
                                        args=[cls.post.id])
        cls.POST_DETAIL_REVERSE = reverse(c.POST_DETAIL_URL_NAME,
                                          args=[cls.post.id])
        cls.PROFILE_REVERSE = reverse(c.PROFILE_URL_NAME,
                                      args=[cls.user])

        cls.REDIRECT_CREATE_URL_NAME = '/auth/login/?next=/create/'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка создания поста"""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='posts/small.gif',
            content=c.SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый пост',
            'author': self.user,
            'image': uploaded
        }
        response = self.authorized_client.post(
            self.POST_CREATE_REVERSE,
            data=form_data,
            follow=True)
        image_name = 'posts/' + str(form_data['image'].name)
        self.assertRedirects(response, self.PROFILE_REVERSE)
        self.assertEqual(Post.objects.count(), post_count + 1,
                         'Поcт не добавлен в БД')
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'], 'Данные не совпадают')
        self.assertEqual(post.group.id, form_data['group'],
                         'Данные не совпадают')
        self.assertEqual(post.author, form_data['author'],
                         'Данные не совпадают')
        self.assertEqual(post.image.name, image_name,
                         'Данные не совпадают')

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        posts_count = Post.objects.count()
        uploaded_new = SimpleUploadedFile(
            name='big.gif',
            content=c.SMALL_GIF,
            content_type='image/gif'
        )
        form_data_new = {
            'text': 'Тестовый пост2',
            'group': self.group2.id,
            'author': self.user,
            'image': uploaded_new
        }
        response = self.authorized_client.post(
            self.POST_EDIT_REVERSE,
            data=form_data_new,
            follow=True
        )
        image_name = 'posts/' + str(form_data_new['image'].name)
        post = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, self.POST_DETAIL_REVERSE)
        self.assertEqual(post.author, form_data_new['author'])
        self.assertEqual(post.text, form_data_new['text'])
        self.assertEqual(post.group.id, form_data_new['group'])
        self.assertEqual(post.image.name, image_name,
                         'Данные не совпадают')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauth_user_cant_publish_post(self):
        """Проверка запрета создания не авторизованным пользователем поста"""
        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст',
                     'group': self.group.id
                     }
        response = self.guest_client.post(
            self.POST_CREATE_REVERSE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.REDIRECT_CREATE_URL_NAME)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_create_page_show_correct_context(self):
        """Шаблоны post_edit и post_create"""
        """ сформированы с правильным контекстом."""
        responses_create_edit = (self.authorized_client.get(
            self.POST_EDIT_REVERSE),
            self.authorized_client.get(
                self.POST_CREATE_REVERSE))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for response in responses_create_edit:
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post_for_comment = Post.objects.create(text='Тестовый пост',
                                                   author=cls.user,
                                                   group=cls.group,
                                                   image=None)
        cls.form = CommentForm()

        cls.ADD_COMMENT_URL_NAME = 'posts:add_comment'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment(self):
        """Проверка создания комментария"""
        form_data = {
            'post': self.post_for_comment,
            'text': 'Тестовый комментарий',
            'author': self.user
        }
        response = self.authorized_client.post(
            reverse(self.ADD_COMMENT_URL_NAME,
                    kwargs={'post_id': self.post_for_comment.id}),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.first()
        self.assertEqual(comment.author, form_data['author'])
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
