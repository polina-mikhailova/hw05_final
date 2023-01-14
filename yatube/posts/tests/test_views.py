from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from . import constants as c
from ..models import Group, Post, User
from yatube.settings import LATEST_POSTS_COUNT


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='authorized')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )
        cls.TOTAL_POSTS = 13
        cls.PAGINATOR_AMOUNT = LATEST_POSTS_COUNT
        cls.SECOND_PAGE = cls.TOTAL_POSTS - cls.PAGINATOR_AMOUNT

        cls.INDEX_REVERSE = reverse(c.INDEX_URL_NAME)
        cls.GROUP_LIST_REVERSE = reverse(c.GROUP_LIST_URL_NAME,
                                         kwargs={'slug': cls.group.slug})
        cls.PROFILE_REVERSE = reverse(c.PROFILE_URL_NAME,
                                      kwargs={'username': cls.user.username})
        cls.PROFILE_FOLLOW_REVERSE = reverse(c.PROFILE_FOLLOW_URL_NAME,
                                             kwargs={'username':
                                                     cls.user.username})
        cls.POST_DETAIL_REVERSE = reverse('posts:post_detail',
                                          kwargs={'post_id': f'{cls.post.pk}'})

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_correct_page_context_client(self):
        """Проверка количества постов на основных страницах."""
        post_paginator = Post(text='Тестовый текст',
                              group=self.group,
                              author=self.user)
        posts: list = [post_paginator for x in range(1, self.TOTAL_POSTS)]
        Post.objects.bulk_create(posts)
        pages = (
            (1, self.PAGINATOR_AMOUNT),
            (2, self.SECOND_PAGE)
        )
        paginated_urls: tuple = (
            self.INDEX_REVERSE,
            self.PROFILE_REVERSE,
            self.GROUP_LIST_REVERSE
        )
        for url in paginated_urls:
            for page, count in pages:
                with self.subTest(url=url, page=page):
                    response = self.authorized_client.get(url, {'page': page})
            self.assertEqual(len(response.context['page_obj']), count)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_DETAIL_REVERSE)
        post_context = response.context['post']
        self.assertEqual(post_context.author, self.post.author)
        self.assertEqual(post_context.text, self.post.text)
        self.assertEqual(post_context.group, self.post.group)
        self.assertEqual(post_context.image, self.post.image)

    def test_unauth_pages_show_correct_context(self):
        """Шаблоны index, group_list, profile """
        """сформированы с правильным контекстом."""
        urls_list = {c.INDEX_URL_NAME: None,
                     c.PROFILE_URL_NAME: {'username': f'{self.user.username}'},
                     c.GROUP_LIST_URL_NAME: {'slug': f'{self.group.slug}'}}

        for url, data in urls_list.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(
                    reverse(url, kwargs=data))
                post_context = response.context['page_obj'][0]
                self.assertEqual(post_context.text, self.post.text)
                self.assertEqual(post_context.group, self.post.group)
                self.assertEqual(post_context.author, self.post.author)
                self.assertEqual(post_context.image, self.post.image)

    def test_cache_works_correctly(self):
        """Кеш работает правильно"""
        response = self.authorized_client.get(self.INDEX_REVERSE)
        before = response.content.decode("utf-8")
        Post.objects.get(id=self.post.id).delete()
        response = self.authorized_client.get(self.INDEX_REVERSE)
        after = response.content.decode("utf-8")
        self.assertEqual(before, after)
        cache.clear()
        response = self.authorized_client.get(self.INDEX_REVERSE)
        after = response.content.decode("utf-8")
        self.assertNotEqual(before, after)
