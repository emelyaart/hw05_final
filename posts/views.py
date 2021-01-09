from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow

User = get_user_model()


def index(request):
    """
    Главная страница сайта.
    Выводит по 10 постов на страницу.
    в request.GET параметр 'page', передает номер страницы которую
    нужно вывести паджинатору
    """
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
                request,
                'index.html',
                {
                    'page': page,
                    'paginator': paginator
                }
            )


def group_posts(request, slug):
    """
    Выводит по 10 постов на страницу относящиеся к выброной группе.
    """
    group = get_object_or_404(Group, slug=slug)
    group_post_list = group.posts.all()
    paginator = Paginator(group_post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
                request,
                'group.html',
                {
                    'group': group,
                    'page': page,
                    'paginator': paginator
                }
            )


@login_required
def new_post(request, post=None):
    """
    Функция создания новой записи в блог.
    Проверяет форму на валидность и делает запись в БД.
    """
    form = PostForm(request.POST or None)
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'posts/new_post.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect('posts:index')


def profile(request, username):
    """
    Профайл пользователя.
    Выводит все посты созданные пользователем на портале
    с погинацией по 5 постов.
    """
    author = get_object_or_404(User, username=username)
    author_posts_list = author.posts.all()
    paginator = Paginator(author_posts_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    user = request.user
    follow = {
        'follower': author.follower.count(),
        'following': author.following.count(),
        'is_following': False,
    }

    if Follow.objects.filter(user=user, author=author).exists():
        follow['is_following'] = True

    return render(
                request,
                'posts/profile.html',
                {
                    'page': page,
                    'profile': author,
                    'paginator': paginator,
                    'follow': follow
                }
            )


@login_required
def follow_index(request):
    """
    Выводит ленту постов подписок
    """
    users = Follow.objects.filter(user=request.user)
    post_list = []
    for user in users:
        post_list += user.author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
                request,
                'follow.html',
                {
                    'page': page,
                    'paginator': paginator
                }
            )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if user == author or Follow.objects.filter(
                                user=user, author=author).exists():
        return redirect('posts:profile', username=username)

    Follow.objects.create(
        user=request.user,
        author=author
    )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)


def post_view(request, username, post_id):
    """
    Страница просмотра отдельной записи
    """
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    count = post.author.posts.count()
    follow = {
        'follower': post.author.follower.count(),
        'following': post.author.following.count(),
        'is_following': False,
    }

    if Follow.objects.filter(user=request.user, author=post.author).exists():
        follow['is_following'] = True

    return render(
                request,
                'posts/post_view.html',
                {
                    'post': post,
                    'profile': post.author,
                    'post_count': count,
                    'comments': comments,
                    'form': form,
                    'follow': follow
                }
            )


@login_required
def post_edit(request, username, post_id):
    """
    Страница с формой редактирования существующей записи
    Доступна только авторизованным пользователям
    и позволяет редаактировать только свои посты.
    При успешно изменении записи возвращает на страницу просмотра поста
    """
    post = get_object_or_404(Post, pk=post_id, author__username=username)

    if post.author != request.user:
        return redirect('posts:post', username=username, post_id=post_id)

    form = PostForm(
                request.POST or None,
                instance=post,
                files=request.FILES or None
            )

    if form.is_valid():
        form.save()
        return redirect('posts:post', username=username, post_id=post_id)
    return render(
                request,
                'posts/new_post.html',
                {
                    'form': form,
                    'post': post,
                    'is_edit': True
                }
            )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if request.method == 'GET' or not form.is_valid():
        return redirect('posts:post', username=username, post_id=post_id)

    comment = form.save(commit=False)
    comment.post = post
    comment.author = post.author
    comment.save()

    return redirect('posts:post', username=username, post_id=post_id)


def page_not_found(request, exception):
    return render(
                request,
                'misc/404.html',
                {'path': request.path},
                status=404
            )


def server_error(request):
    return render(request, 'misc/500html', status=500)
