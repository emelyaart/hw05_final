from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(
                username='username'
            )
        cls.post = Post.objects.create(
            text='а' * 100,
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='c' * 50
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='d' * 50
        )

    def setUp(self):
        self.post = Post.objects.get()
        self.group = Group.objects.get()
        self.comment = Comment.objects.get()

    def test_verbose_name_post(self):
        """verbose name в модели Post совпадает с ожидаемым."""
        post = self.post
        field_verbose = {
            'text': 'Текст записи',
            'group': 'Группа'
        }

        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text_post(self):
        """help_text в модели Post совпадает с ожидаемым."""
        post = self.post
        field_help_texts = {
            'text': 'Здесь находится текст Вашей записи',
            'group': 'Выберите группу в которой нужно опубликовать запись'
        }

        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_verbose_name_comment(self):
        """verbose_name в модели Comment совпадает с ожидаемым"""
        comment = self.comment
        expected = 'Текст комментария'
        self.assertEqual(
                    comment._meta.get_field('text').verbose_name, expected
                )

    def test_help_text_comment(self):
        """help_text в модели Comment совпадает с ожидаемым"""
        comment = self.comment
        expected = 'Здесь Вы можете написать свой комментарий'
        self.assertEqual(
                    comment._meta.get_field('text').help_text, expected
                )

    def test_str_post(self):
        """__str__ в Post возвращает первые 15 символов"""
        post = self.post
        self.assertEqual(post.__str__(), 'а' * 15)

    def test_str_group(self):
        """__str__ в Group возвращает title"""
        group = self.group
        self.assertEqual(group.__str__(), 'test_group')

    def test_str_comment(self):
        """__str__ в Comment возвращает первые 10 символов"""
        comment = self.comment
        self.assertEqual(comment.__str__(), 'd' * 10)
