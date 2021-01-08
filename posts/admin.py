from django.contrib import admin

from .models import Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('text', 'pub_date', 'author', 'group')
    search_fields = ['text']
    list_filter = ['pub_date']
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    search_fields = ['title']
    list_filter = ['slug']
