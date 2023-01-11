from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class CreationFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_user_create(self):
        """Валидная форма создает новго пользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Test first name',
            'last_name': 'Test last name',
            'username': 'TestUser',
            'email': 'test@email.com',
            'password1': 'testpassword1',
            'password2': 'testpassword1',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(username='TestUser').exists()
        )
