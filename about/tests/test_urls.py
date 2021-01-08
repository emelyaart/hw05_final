from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

    def test_static_pages_url_exists_at_desired_location(self):
        """Проверка доступности адресов статических страниц."""
        for url in self.urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_static_pages_urls_uses_correct_templates(self):
        """Проверка шаблонов для статических страниц."""
        for url, template in self.urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
