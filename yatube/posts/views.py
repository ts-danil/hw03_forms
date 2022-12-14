from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    posts = Post.objects.select_related('group', 'author').all()
    paginator = Paginator(posts, settings.POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related(
        'group', 'author').all()[:settings.POST_PER_PAGE]
    paginator = Paginator(posts, settings.POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj}
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author').all()
    paginator = Paginator(posts, settings.POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'posts_count': posts.count(),
        'page_obj': page_obj}
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.select_related('group', 'author').get(id=post_id)
    posts_count = post.author.posts.count()
    context = {
        'post': post,
        'posts_count': posts_count
    }
    return render(request, 'posts/post_detail.html', context)


class PostView(CreateView):
    form_class = PostForm
    template_name = 'posts/create_post.html'
    success_url = reverse_lazy('about:author')


def post_create(request):
    form = PostForm(request.POST or None)
    is_edit = False
    context = {
        'is_edit': is_edit,
        'form': form
    }
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    is_edit = True
    context = {
        'is_edit': is_edit,
        'form': form
    }
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context)
