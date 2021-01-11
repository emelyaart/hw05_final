import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class PostFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username='username')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_form_create_new_record(self):
        """
        Форма PostForm добавляет запись в БД
        """
        posts_count = Post.objects.count()
        small_gif = (
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'a' * 50,
            'author': PostFormTests.user,
            'image': uploaded
        }

        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, 200)

    def test_form_post_edit(self):
        """
        Форма PostForm изменяет запись в БД
        """
        form_data = {
            'text': 'Изменённый текст',
            'author': PostFormTests.user
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'username': PostFormTests.user,
                'post_id': PostFormTests.post.id
            }),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk=PostFormTests.post.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(response.status_code, 200)
