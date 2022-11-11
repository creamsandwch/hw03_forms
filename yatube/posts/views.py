from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_VIEWED

from .forms import PostForm
from .models import Group, Post, User
from .utils import paginate


def index(request):
    post_list = Post.objects.select_related(
        'group',
        'author'
    )
    page_obj = paginate(request, post_list, POSTS_VIEWED)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    page_obj = paginate(request, post_list, POSTS_VIEWED)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginate(request, posts, POSTS_VIEWED)
    context = {
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    context = {
        'form': form,
    }
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    edited_post = Post.objects.get(id=post_id)
    if not request.user == edited_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=edited_post)
    context = {
        'form': form,
        'is_edit': True,
    }
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    form.save()
    return redirect('posts:post_detail', post_id)
