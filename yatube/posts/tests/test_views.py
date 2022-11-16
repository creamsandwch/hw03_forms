from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django import forms

from ..models import User, Post, Group


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
        )
        cls.post_list = []
        for i in range(1, 14):
            cls.post_list.append(
                Post.objects.create(
                    text=f'Текст тестового поста #{i}',
                    author=cls.author,
                    group=cls.group,
                    pub_date=timezone.now() - i * timezone.timedelta(hours=1)
                )
            )

    def test_views_use_correct_templates(self):
        """Проверяем, что view-функции приложения posts
        используют правильные шаблоны."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTest.post_list[0].id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTest.author.username}
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTest.post_list[0].id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_view_show_correct_context(self):
        """Проверяем, что post_create и post_view передает правильный
        context (форма) шаблону при get-запросе."""
        responses = [
            PostViewsTest.authorized_client.get(
                reverse('posts:post_create')
            ),
            PostViewsTest.authorized_client.get(
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': PostViewsTest.post_list[0].id}
                )
            ),
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for response in responses:
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_edit_view_shows_correct_context(self):
        """Проверяем, что post_edit передает правильный
        context шаблону при post-запросе"""

        response = PostViewsTest.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTest.post_list[0].id}
            )
        )
        form_fields_post = {
            'text': 'Текст тестового поста #1',
            'group': PostViewsTest.group,
            'author': PostViewsTest.author,
        }
        form = response.context.get('form').instance
        for value, expected in form_fields_post.items():
            with self.subTest(value=value):
                form_instance_field_value = getattr(form, value)
                self.assertEqual(form_instance_field_value, expected)

    def test_index_shows_correct_context_and_paginator(self):
        """Проверяем, что index view передает правильный
        context шаблону"""
        response = PostViewsTest.guest_client.get(reverse('posts:index'))
        object_list = response.context['page_obj'].object_list
        first_page_objects_count = len(object_list)
        response = PostViewsTest.guest_client.get(
            reverse('posts:index') + '?page=2'
        )
        object_list += response.context['page_obj'].object_list
        second_page_objects_count = len(object_list) - first_page_objects_count
        first_post = object_list[PostViewsTest.post_list[0].id]
        post_fields = {
            'text': f'Текст тестового поста #{first_post.id}',
            'group': PostViewsTest.group,
            'author': PostViewsTest.author,
        }
        self.assertEqual(
            first_page_objects_count,
            10,
            ('Paginator возвращает неверное количество'
             'постов на первой странице index')
        )
        self.assertEqual(
            second_page_objects_count,
            3,
            ('Paginator возвращает неверное количество'
             'постов на второй странице index')
        )
        for value, expected in post_fields.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(first_post, value), expected)

    def test_group_list_view_shows_correct_context_and_paginator(self):
        """Проверяем, что group_list view передает правильный
        context шаблону"""
        response = PostViewsTest.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTest.group.slug}
            )
        )
        object_list = response.context['page_obj'].object_list
        first_page_objects_count = len(object_list)
        response = PostViewsTest.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTest.group.slug}
            ) + '?page=2'
        )
        object_list += response.context['page_obj']
        second_page_objects_count = len(object_list) - first_page_objects_count
        self.assertEqual(
            first_page_objects_count,
            10,
            ('Paginator возвращает неверное количество'
             'постов на первой странице group_list')
        )
        self.assertEqual(
            second_page_objects_count,
            3,
            ('Paginator возвращает неверное количество'
             'постов на второй странице group_list')
        )
        first_post = object_list[PostViewsTest.post_list[0].id]
        post_attr = {
            'text': f'Текст тестового поста #{first_post.id}',
            'group': PostViewsTest.group,
            'author': PostViewsTest.author,
        }
        # Убрать преобразования set() и найти способ упорядочить список из
        # паджинатора object_list
        self.assertEqual(set(object_list), set(PostViewsTest.post_list))
        for value, expected in post_attr.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(first_post, value), expected)

    def test_post_profile_view_shows_correct_context_and_paginator(self):
        """Проверяем, что profile_view передает правильный
        контекст"""
        response = PostViewsTest.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTest.author.username}
            )
        )
        object_list = response.context['page_obj'].object_list
        first_page_objects_count = len(object_list)
        response = PostViewsTest.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTest.author.username}
            ) + '?page=2'
        )
        object_list += response.context['page_obj'].object_list
        second_page_objects_count = len(object_list) - first_page_objects_count
        self.assertEqual(
            first_page_objects_count,
            10,
            ('Paginator возвращает неверное количество'
             'постов на первой странице')
        )
        self.assertEqual(
            second_page_objects_count,
            3,
            ('Paginator возвращает неверное количество'
             'постов на второй странице')
        )
        first_post = object_list[PostViewsTest.post_list[0].id]
        post_attrs = {
            'text': f'Текст тестового поста #{first_post.id}',
            'group': PostViewsTest.group,
            'author': PostViewsTest.author,
        }
        for value, expected in post_attrs.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(first_post, value), expected)

    def test_post_detail_view_shows_correct_context(self):
        response = PostViewsTest.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTest.post_list[0].id}
            )
        )
        post_attrs = {
            'text': f'Текст тестового поста #{PostViewsTest.post_list[0].id}',
            'group': PostViewsTest.group,
            'author': PostViewsTest.author,
        }
        post = response.context['post']
        for value, expected in post_attrs.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(post, value), expected)

    def test_if_group_is_set_post_is_on_pages(self):
        """Проверяем, что если при создании поста указать
        группу, он появится на главной, странице группы
        и профиле пользователя"""
        urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': 'TestUser'}
            ),
        ]
        post = PostViewsTest.post_list[0]
        if post.group.slug == 'test-slug':
            for url in urls:
                response = PostViewsTest.guest_client.get(url)
                object_list = response.context['page_obj'].object_list
                response = PostViewsTest.guest_client.get(url + '?page=2')
                object_list += response.context['page_obj'].object_list
                self.assertTrue(
                    post in object_list,
                    ('Пост с заданной группой не отправлен на'
                     f'страницу по адресу {url}')
                )
