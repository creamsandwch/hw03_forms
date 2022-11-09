from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Post, Group
from .forms import PostForm


def index(request):
    post_list = Post.objects.select_related(
        'group',
        'author'
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    posts = Post.objects.select_related(
        'group',
    ).filter(author__username=username)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    author = get_object_or_404(get_user_model(), username=username)
    context = {
        'page_obj': page_obj,
        'posts_count': author.posts.count(),
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    author_posts_count = post.author.posts.count()
    context = {
        'post': post,
        'posts_count': author_posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    group_list = Group.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('posts:profile', request.user.username)
        context = {
            'form': form,
            'group_list': group_list,
            'is_edit': False,
        }
        return render(request, 'posts/create_post.html', context)
    form = PostForm()
    context = {
        'form': form,
        'group_list': group_list,
        'is_edit': False,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    edited_post = Post.objects.get(id=post_id)
    group_list = Group.objects.all()
    if request.user == edited_post.author:
        if request.method == 'POST':
            form = PostForm(request.POST or None, instance=edited_post)
            context = {
                'form': form,
                'group_list': group_list,
                'is_edit': True,
            }
            if form.is_valid():
                form.save()
                return redirect('posts:post_detail', post_id)
            return render(request, 'posts/create_post.html', context)
        else:
            form = PostForm(request.POST or None, instance=edited_post)
            context = {
                'form': form,
                'group_list': group_list,
                'is_edit': True,
            }
            return render(request, 'posts/create_post.html', context)
    else:
        return redirect('posts:post_detail', post_id)
