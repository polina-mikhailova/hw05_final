from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User, MAX_SYMBOLS_STR_POST


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='username')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        test_data = {
            self.group.title: str(self.group),
            self.post.text[:MAX_SYMBOLS_STR_POST]:
            str(self.post),
            self.comment.text: str(self.comment)
        }
        for field, expected_value in test_data.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_verbose_name(self):
        """verbose_name в полях моделей совпадает с ожидаемым."""
        test_data = {
            Post: {
                'author': 'Автор',
                'text': 'Текст поста',
                'image': 'Картинка',
                'group': 'Группа',
                'pub_date': 'Дата публикации'
            },
            Group: {
                'title': 'Название группы',
                'description': 'Описание группы'
            },
            Comment: {
                'post': 'Комментарий',
                'author': 'Автор'
            },
            Follow: {
                'author': 'Автор',
                'user': 'Подписчик'
            },
        }
        for model, fields in test_data.items():
            for field, expected_value in fields.items():
                with self.subTest():
                    self.assertEqual(
                        model._meta.get_field(field).verbose_name,
                        expected_value)

    def test_help_text_post(self):
        """help_text в полях моделей совпадает с ожидаемым."""
        test_data = {
            Post: {
                'text': 'Текст нового поста',
                'image': 'Вы можете добавить изображение к вашему посту',
                'group': 'Группа, к которой будет относиться пост'
            },
            Group: {
                'title': 'Введите название группы',
                'description': 'Добавьте описание новой группы'
            },
            Comment: {'text': 'Текст нового комментария'},
        }
        for model, fields in test_data.items():
            for field, expected_value in fields.items():
                with self.subTest():
                    self.assertEqual(
                        model._meta.get_field(field).help_text, expected_value)
