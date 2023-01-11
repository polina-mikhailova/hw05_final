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

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        test_data = {
            self.group.title: str(self.group),
            self.post.text[:MAX_SYMBOLS_STR_POST]:
            str(self.post)
        }
        for field, expected_value in test_data.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_verbose_name(self):
        """verbose_name в полях моделей совпадает с ожидаемым."""
        test_data = (
            ('author', 'Автор', Post),
            ('group', 'Группа', Post),
            ('text', 'Текст поста', Post),
            ('image', 'Картинка', Post),
            ('pub_date', 'Дата публикации', Post),
            ('title', 'Название группы', Group),
            ('description', 'Описание группы', Group),
            ('post', 'Комментарий', Comment),
            ('author', 'Автор', Comment),
            ('author', 'Автор', Follow),
            ('user', 'Подписчик', Follow),
        )
        for data in test_data:
            with self.subTest():
                self.assertEqual(
                    data[2]._meta.get_field(data[0]).verbose_name, data[1])

    def test_help_text_post(self):
        """help_text в полях моделей совпадает с ожидаемым."""
        test_data = (
            ('text', 'Текст нового поста', Post),
            ('group', 'Группа, к которой будет относиться пост', Post),
            ('image', 'Вы можете добавить изображение к вашему посту', Post),
            ('title', 'Введите название группы', Group),
            ('description', 'Добавьте описание новой группы', Group),
            ('text', 'Текст нового комментария', Comment),
        )
        for data in test_data:
            with self.subTest():
                self.assertEqual(
                    data[2]._meta.get_field(data[0]).help_text, data[1])
