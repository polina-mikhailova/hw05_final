from django.test import TestCase
from django.urls import reverse

from . import constants as c
from ..models import Group, Post, User


class PostURLTest(TestCase):
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
            text='Тестовый пост',
        )
        cls.INDEX_PAGE_ADDRESS = '/'
        cls.GROUP_PAGE_ADDRESS = f'/group/{cls.group.slug}/'
        cls.PROFILE_PAGE_ADDRESS = f'/profile/{cls.user.username}/'
        cls.POST_DETAIL_PAGE_ADDRESS = f'/posts/{cls.post.id}/'
        cls.CREATE_PAGE_ADDRESS = '/create/'
        cls.POST_EDIT_PAGE_ADDRESS = f'/posts/{cls.post.id}/edit/'
        cls.POST_COMMENT_PAGE_ADDRESS = f'/posts/{cls.post.id}/comment/'
        cls.FOLLOW_INDEX_PAGE_ADDRESS = '/follow/'
        cls.PROFILE_FOLLOW_PAGE_ADDRESS = (
            f'/profile/{cls.user.username}/follow/'
        )
        cls.PROFILE_UNFOLLOW_PAGE_ADDRESS = (
            f'/profile/{cls.user.username}/unfollow/'
        )

    def test_routes_give_correct_urls(self):
        """Расчеты дают ожидаемые явные URLы."""
        test_data = (
            (c.INDEX_URL_NAME, None, self.INDEX_PAGE_ADDRESS),
            (c.GROUP_LIST_URL_NAME, [self.group.slug],
             self.GROUP_PAGE_ADDRESS),
            (c.PROFILE_URL_NAME, [self.user.username],
             self.PROFILE_PAGE_ADDRESS),
            (c.POST_DETAIL_URL_NAME, [self.post.id],
             self.POST_DETAIL_PAGE_ADDRESS),
            (c.POST_CREATE_URL_NAME, None, self.CREATE_PAGE_ADDRESS),
            (c.POST_EDIT_URL_NAME, [self.post.id],
             self.POST_EDIT_PAGE_ADDRESS),
            (c.POST_COMMENT_URL_NAME, [self.post.id],
             self.POST_COMMENT_PAGE_ADDRESS),
            (c.FOLLOW_INDEX_URL_NAME, None, self.FOLLOW_INDEX_PAGE_ADDRESS),
            (c.PROFILE_FOLLOW_URL_NAME, [self.user.username],
             self.PROFILE_FOLLOW_PAGE_ADDRESS),
            (c.PROFILE_UNFOLLOW_URL_NAME, [self.user.username],
             self.PROFILE_UNFOLLOW_PAGE_ADDRESS)
        )
        for url, args, address in test_data:
            with self.subTest():
                reversed = reverse(url, args=args,)
                self.assertEqual(reversed, address)
