from django.test import TestCase, Client
from django.urls import reverse


class StaticPagesURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.urls = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html'
        }

    def test_static_pages_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:***, доступен."""
        for rev in self.urls:
            with self.subTest(rev=rev):
                response = self.guest_client.get(reverse(rev))
                self.assertEqual(response.status_code, 200)

    def test_static_pages_urls_uses_correct_templates(self):
        """Проверка шаблонов для статических страниц."""
        for rev, template in self.urls.items():
            with self.subTest(rev=rev):
                response = self.guest_client.get(reverse(rev))
                self.assertTemplateUsed(response, template)
