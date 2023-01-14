from http import HTTPStatus

from django.shortcuts import get_object_or_404
from django.test import Client, TestCase

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
            f'profile/{cls.user.username}/follow/'
        )
        cls.PROFILE_UNFOLLOW_PAGE_ADDRESS = (
            f'profile/{cls.user.username}/unfollow/'
        )
        cls.UNEXISTING_PAGE = '/unexisting_page/'

        cls.CREATE_PAGE_UNAUTH_REDIRECT_ADDRESS = '/auth/login/?next=/create/'
        cls.POST_EDIT_PAGE_UNAUTH_REDIRECT_ADDRESS = (
            f'/auth/login/?next=/posts/{cls.post.id}/edit/'
        )
        cls.FOLLOW_INDEX_PAGE_UNAUTH_REDIRECT_ADDRESS = (
            '/auth/login/?next=/follow/'
        )
        cls.CREATE_PAGE_AUTH_REDIRECT_ADDRESS = cls.PROFILE_PAGE_ADDRESS
        cls.POST_EDIT_PAGE_REDIRECT_ADDRESS = cls.POST_DETAIL_PAGE_ADDRESS

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.INDEX_PAGE_ADDRESS: 'posts/index.html',
            self.GROUP_PAGE_ADDRESS: 'posts/group_list.html',
            self.PROFILE_PAGE_ADDRESS: 'posts/profile.html',
            self.POST_DETAIL_PAGE_ADDRESS: 'posts/post_detail.html',
            self.CREATE_PAGE_ADDRESS: 'posts/create_post.html',
            self.POST_EDIT_PAGE_ADDRESS: 'posts/create_post.html',
            self.FOLLOW_INDEX_PAGE_ADDRESS: 'posts/follow.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_exists_at_desired_location(self):
        """Проверка доступа к страницам."""
        test_data = (
            (self.INDEX_PAGE_ADDRESS, self.guest_client, HTTPStatus.OK),
            (self.GROUP_PAGE_ADDRESS, self.guest_client, HTTPStatus.OK),
            (self.PROFILE_PAGE_ADDRESS, self.guest_client, HTTPStatus.OK),
            (self.POST_DETAIL_PAGE_ADDRESS, self.guest_client, HTTPStatus.OK),
            (self.CREATE_PAGE_ADDRESS, self.authorized_client, HTTPStatus.OK),
            (self.UNEXISTING_PAGE, self.guest_client, HTTPStatus.NOT_FOUND),
            (self.POST_COMMENT_PAGE_ADDRESS, self.authorized_client,
             HTTPStatus.FOUND),
            (self.FOLLOW_INDEX_PAGE_ADDRESS, self.authorized_client,
             HTTPStatus.OK),
        )
        for address, client, status in test_data:
            with self.subTest(address=address):
                response = client.get(address)
                self.assertEqual(response.status_code, status)

    def test_posts_edit_url_access_only_for_author(self):
        """Страница /posts/<post_id>/edit/ доступна только автору поста."""
        self.post = get_object_or_404(Post, id=self.post.id)
        self.assertEqual(self.user.username, self.user.username)

    def test_urls_redirect_anonymous_on_auth_login(self):
        """Страницы /create/, /posts/<post_id>/edit/ и /follow/ перенаправят"""
        """ анонимного пользователя на страницу логина."""
        address_redirects = {
            self.CREATE_PAGE_ADDRESS: self.CREATE_PAGE_UNAUTH_REDIRECT_ADDRESS,
            self.POST_EDIT_PAGE_ADDRESS:
            self.POST_EDIT_PAGE_UNAUTH_REDIRECT_ADDRESS,
            self.FOLLOW_INDEX_PAGE_ADDRESS:
            self.FOLLOW_INDEX_PAGE_UNAUTH_REDIRECT_ADDRESS
        }
        for address, redirect in address_redirects.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redirect)
