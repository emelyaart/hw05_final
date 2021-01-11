import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Follow

User = get_user_model()


class PostsViewsTest(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            )
        cls.test_image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(
                username='username'
        )
        cls.user1 = User.objects.create_user(
                username='username1'
        )
        cls.user2 = User.objects.create_user(
                username='username2'
        )

        cls.group_1 = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='a' * 50
        )

        cls.group_2 = Group.objects.create(
            title='test_group_2',
            slug='test-slug_2',
            description='b' * 50
        )

        for i in range(1, 13):
            Post.objects.create(
                text='Текст-' + str(i),
                author=cls.user,
            )

        for i in range(13, 18):
            Post.objects.create(
                text='Текст-' + str(i),
                author=cls.user,
                group=cls.group_1,
            )

        Post.objects.create(
                text='Текст-image',
                author=cls.user,
                group=cls.group_1,
                image=cls.test_image
            )

    def setUp(self):
        self.client = Client()
        self.auth_client = Client()
        self.auth_client_alt = Client()
        self.auth_client.force_login(PostsViewsTest.user)
        self.auth_client_alt.force_login(PostsViewsTest.user2)
        self.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

    def test_pages_uses_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон
        """
        template_pages_names = {
            'index.html': reverse('posts:index'),
            'posts/new_post.html': reverse('posts:new_post'),
            'group.html': (
                reverse('posts:group', kwargs={'slug': 'test-slug'})
            )
        }

        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_first_page_contains_ten_records(self):
        """
        Паджинатор /index соответствует ожиданиям
        возвращает 10 записей на первой странице
        """
        response = self.auth_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_paginator_second_page_contains_three_records(self):
        """
        Паджинатор /index соответствует ожиданиям
        возвращает оставшиеся 8 записи на второй странице
        """
        url = reverse('posts:index')
        url += '?page=2'
        response = self.auth_client.get(url)
        self.assertEqual(len(response.context.get('page').object_list), 8)

    def test_index_page_contains_context(self):
        """
        Контекст /index соответствует ожиданиям
        """
        response = self.auth_client.get(reverse('posts:index'))
        post = response.context.get('page').object_list
        self.assertEqual(post[0].text, 'Текст-image')
        self.assertEqual(post[0].author, PostsViewsTest.user)
        self.assertEqual(post[0].image, 'posts/small.gif')

    def test_group_page_contains_context(self):
        """
        Контекст /group соответствует ожиданиям
        """
        response = self.auth_client.get(
            reverse('posts:group', kwargs={'slug': 'test-slug'})
        )
        post = response.context.get('page').object_list
        self.assertEqual(post[3].text, 'Текст-15')
        self.assertEqual(post[3].author, PostsViewsTest.user)
        self.assertEqual(post[3].group, PostsViewsTest.group_1)
        self.assertEqual(post[0].image, 'posts/small.gif')
        self.assertIsInstance(response.context.get('group'), Group)
        self.assertIsInstance(response.context.get('paginator'), Paginator)

    def test_post_hit_the_wrong_group(self):
        """
        Пост не попал не в ту группу
        """
        response = self.auth_client.get(
            reverse('posts:group', kwargs={'slug': 'test-slug_2'})
        )
        self.assertEqual(len(response.context.get('page').object_list), 0)

    def test_new_post_page_contains_context(self):
        """
        Контекст /new_page соответсвует ожиданиям
        """
        response = self.auth_client.get(reverse('posts:new_post'))

        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_contains_context(self):
        """
        Страница post_edit содержит ожидаемый контекст
        """
        response = self.auth_client.get(
            reverse(
                'posts:post_edit', kwargs={
                    'username': PostsViewsTest.user.username,
                    'post_id': 1
                }
            ))

        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertIsInstance(response.context.get('post'), Post)
        self.assertTrue(response.context.get('is_edit'))

    def test_profile_page_contains_context(self):
        """
        Страница profile содержит ожидаемый контекст
        """
        response = self.auth_client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': PostsViewsTest.user.username
                }
            ))
        self.assertEqual(len(response.context.get('page').object_list), 5)
        self.assertEqual(response.context.get('author'), PostsViewsTest.user)
        self.assertIsInstance(response.context.get('paginator'), Paginator)
        self.assertEqual(response.context.get('page')[0].image,
                         'posts/small.gif')

    def test_post_view_page_contains_context(self):
        """
        Страница post_view содержит ожидаемый контекст
        """
        response = self.auth_client.get(
            reverse(
                'posts:post', kwargs={
                    'username': PostsViewsTest.user.username,
                    'post_id': 18
                }
            ))
        self.assertEqual(response.context.get('post').text, 'Текст-image')
        self.assertEqual(response.context.get('author'), PostsViewsTest.user)
        self.assertEqual(response.context.get('post_count'), 18)
        self.assertEqual(response.context.get('post').image,
                         'posts/small.gif')

    def test_cache_index_page(self):
        """Тестируем cache"""
        response = self.auth_client.get(reverse('posts:index'))
        post = response.context.get('page').object_list
        cache.set('index_page', post[0].text, 10)
        self.assertEqual(cache.get('index_page'), post[0].text)

    def test_authenticated_user_can_profile_follow_and_unfollow(self):
        """
        Авторизованный пользователь может подписываться и отписываться
        на других пользователей
        """
        self.auth_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': PostsViewsTest.user1.username,
                }
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=PostsViewsTest.user,
                author=PostsViewsTest.user1
            ).exists()
        )

        self.auth_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={
                    'username': PostsViewsTest.user1.username,
                }
            )
        )
        self.assertFalse(Follow.objects.filter(
                                user=PostsViewsTest.user,
                                author=PostsViewsTest.user1
                            ).exists())

    def test_record_appears_in_the_subscription_feed(self):
        """Новая запись появляется в ленте тех, кто подписан
        и не появляется в ленте тех кто не подписа"""
        self.auth_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': PostsViewsTest.user1.username,
                }
            )
        )

        Post.objects.create(
                text='Текст-follow',
                author=PostsViewsTest.user1,
                group=PostsViewsTest.group_1,
                image=PostsViewsTest.test_image
            )

        response = self.auth_client.get(reverse('posts:follow_index'))
        post = response.context.get('page').object_list

        self.assertEqual(post[0].text, 'Текст-follow')

        response = self.auth_client_alt.get(reverse('posts:follow_index'))
        post = response.context.get('page').object_list

        self.assertEqual(post, [])

    def test_auth_user_can_comment_on_posts(self):
        """Только авторизованный пользователь может комментирорвать посты"""
        url = reverse(
                'posts:add_comment', kwargs={
                    'username': PostsViewsTest.user1.username,
                    'post_id': 18
                }
            )
        response = self.client.get(url)
        self.assertRedirects(
                    response,
                    f'/auth/login/?next={url}'
                )
