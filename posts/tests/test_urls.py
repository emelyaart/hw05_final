from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(
            username='author')
        cls.user_non_author = User.objects.create_user(
            username='non_author')
        Post.objects.create(
            text='а' * 100,
            author=cls.user_author
        )
        Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='c' * 50
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(
            PostsURLTests.user_author
        )
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(
            PostsURLTests.user_non_author
        )
        self.urls = {
            'availabel_all_users': [
                    '/',
                    '/group/test-slug/',
                    '/author/',
                    '/author/1/'
            ],
            'availabel_authorized_users': [
                    '/new/',
                    '/author/1/edit/'
            ],
            'used_correct_templated': {
                    '/': 'index.html',
                    '/new/': 'posts/new_post.html',
                    '/group/test-slug/': 'group.html',
                    '/author/': 'posts/profile.html',
                    '/author/1/': 'posts/post_view.html',
                    '/author/1/edit/': 'posts/new_post.html'
            }
        }

    def test_pages_availibility_unauthorized_user(self):
        """
        Страницы доступные всем пользователям
        """
        for url in self.urls['availabel_all_users']:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200,
                                 f'Страница {url} недоступна')

    def test_pages_redirects_unauthorized_user(self):
        """
        Страницы которые переадресовывают неавторизованных пользователей
        """
        for url in self.urls['availabel_authorized_users']:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response,
                    f'/auth/login/?next={url}'
                )

    def test_pages_availibility_authorized_user(self):
        """
        Страницы доступные авторизованным пользователям
        """
        for url in self.urls['availabel_authorized_users']:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200,
                                 f'Страница {url} недоступна')

    def test_edit_page_availability_non_author_post(self):
        """
        Страница перенаправляет авторизованного НЕ автора поста
        """
        response = self.authorized_client_1.get('/author/1/edit/')
        self.assertRedirects(
            response,
            '/author/1/'
            )

    def test_urls_uses_correct_template(self):
        """
        URL-адрес соответствет ожидаемому шаблону
        """
        for url, template in self.urls['used_correct_templated'].items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_404_page_not_found(self):
        """
        Возвращаем код 404 если страница не найдена
        """
        response = self.authorized_client.get('/abracadabra/')
        self.assertEqual(response.status_code, 404)
