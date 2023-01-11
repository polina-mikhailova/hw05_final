from django.test import Client, TestCase
from django.urls import reverse

from . import constants as c
from ..models import Follow, Post, User


class ViewsFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_name')
        cls.user2 = User.objects.create_user(username='test_name2')
        cls.author = User.objects.create_user(username='test_author')

        cls.PROFILE_FOLLOW_PAGE_REVERSE = reverse(c.PROFILE_FOLLOW_URL_NAME,
                                                  args=[cls.author.username])
        cls.PROFILE_UNFOLLOW_PAGE_REVERSE = reverse(
            c.PROFILE_UNFOLLOW_URL_NAME,
            args=[cls.author.username])
        cls.FOLLOW_INDEX_PAGE_REVERSE = reverse(c.FOLLOW_INDEX_URL_NAME)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_user_subscribes_to_author(self):
        """Авторизованный пользователь может"""
        """ подписываться на других пользователей"""
        count_sub = Follow.objects.filter(user=self.user).count()
        data_sub = {
            'user': self.user,
            'author': self.author
        }
        self.authorized_client.post(
            self.PROFILE_FOLLOW_PAGE_REVERSE,
            data=data_sub,
            follow=True
        )
        new_count_sub = Follow.objects.filter(user=self.user).count()

        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )
        self.assertEqual(count_sub + 1, new_count_sub)

    def test_user_unfollower_authors(self):
        """Пользователь может"""
        """ отписываться от других пользователей"""
        count_sub = Follow.objects.filter(user=self.user).count()
        data_sub = {
            'user': self.user,
            'author': self.author
        }
        self.guest_client.post(
            self.PROFILE_UNFOLLOW_PAGE_REVERSE,
            data=data_sub,
            follow=True
        )
        new_count_sub = Follow.objects.filter(user=self.user).count()

        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )
        self.assertEqual(count_sub, new_count_sub)

    def test_subscriber_sees_new_post(self):
        """Новый пост пользователя виден только"""
        """ его подписчику"""
        new_post = Post.objects.create(
            author=self.author,
            text='Text subscription text'
        )
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        response_subscriber = self.authorized_client.get(
            self.FOLLOW_INDEX_PAGE_REVERSE
        )
        response_nonsubscriber = self.authorized_client2.get(
            self.FOLLOW_INDEX_PAGE_REVERSE
        )
        new_post_sub = response_subscriber.context['page_obj']
        new_post_nonsub = response_nonsubscriber.context['page_obj']

        self.assertIn(new_post, new_post_sub)
        self.assertNotIn(new_post, new_post_nonsub)
