from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        labels = {
            'text': 'Текст записи',
            'group': 'Группа',
            'image': 'Картинка'
        }

        help_text = {
            'text': 'Здесь находится текст Вашей записи',
            'group': 'Выберите группу в которой нужно опубликовать запись',
            'image': 'Здесь можно прикрепить изображение для Вашего поста'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_text = {
            'text': 'Здесь Вы можете написать свой комментарий'
        }
