from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст записи',
                            help_text=('Здесь находится текст'
                                       ' Вашей записи'))
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='posts',
                              verbose_name='Группа',
                              help_text=('Выберите группу в которой'
                                         ' нужно опубликовать запись'))
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name='Картинка')

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(verbose_name='Текст комментария',
                            help_text=('Здесь Вы можете написать'
                                       ' свой комментарий'))
    created = models.DateTimeField('date published', auto_now_add=True)

    def __str__(self):
        return self.text[:10]
