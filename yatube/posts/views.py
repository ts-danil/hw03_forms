from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import PostForm

from .models import Group, Post, User


def index(request):
    title = 'Последние обновления на сайте'
    posts = Post.objects.select_related('group', 'author').all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {group}'
    posts = group.posts.all()[:10]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj}
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    title = f'Профайл пользователя  {author.get_full_name()}'
    posts = author.posts.select_related('author').all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'author': author,
        'posts_count': posts.count(),
        'page_obj': page_obj}
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.select_related('group', 'author').get(id=post_id)
    title = f'Пост {post.text[:30]}'
    posts_count = post.author.posts.count()
    context = {
        'title': title,
        'post': post,
        'posts_count': posts_count
    }
    return render(request, 'posts/post_detail.html', context)


class PostView(CreateView):
    form_class = PostForm
    template_name = 'posts/create_post.html'
    success_url = reverse_lazy('about:author')


def post_create(request):
    if request.method == 'GET':
        title = 'Новый пост'
        is_edit = False
        form = PostForm()
        context = {
            'title': title,
            'is_edit': is_edit,
            'form': form
        }
        return render(request, 'posts/create_post.html', context)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
        else:
            return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if request.method == 'GET':
        title = 'Редактировать запись'
        is_edit = True
        form = PostForm(instance=post)
        context = {
            'title': title,
            'is_edit': is_edit,
            'form': form
        }
        return render(request, 'posts/create_post.html', context)
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post_id)
