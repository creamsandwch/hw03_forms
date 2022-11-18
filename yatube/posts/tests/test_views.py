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
        cls.group_1 = Group.objects.create(
            title='Первая тестовая группа',
            slug='test-slug-1',
        )
        cls.group_2 = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test-slug-2'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group_1,
            author=cls.author
        )

    def test_views_use_correct_templates(self):
        """Проверяем, что view-функции приложения posts
        используют правильные шаблоны."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTest.group_1.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTest.test_post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTest.test_post.author.username}
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTest.test_post.id}
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
                    kwargs={'post_id': PostViewsTest.test_post.id}
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
                kwargs={'post_id': PostViewsTest.test_post.id}
            )
        )
        form_fields_post = {
            'text': 'Тестовый пост',
            'group': PostViewsTest.group_1,
            'author': PostViewsTest.author,
        }
        form = response.context.get('form').instance
        for value, expected in form_fields_post.items():
            with self.subTest(value=value):
                self.assertEqual(getattr(form, value), expected)

    def test_index_shows_correct_context_and_paginator(self):
        """Проверяем, что index view передает правильный
        context шаблону"""
        response = PostViewsTest.guest_client.get(reverse('posts:index'))
        object_list = response.context['page_obj'].object_list
        post_fields = {
            'text': 'Тестовый пост',
            'group': PostViewsTest.group_1,
            'author': PostViewsTest.author,
        }
        self.assertIn(
            PostViewsTest.test_post,
            object_list,
            'Пост не передан в контексте'
        )
        for value, expected in post_fields.items():
            with self.subTest(value=value):
                self.assertEqual(
                    getattr(PostViewsTest.test_post, value),
                    expected,
                    'Данные поста неверно переданы в шаблон'
                )

    def test_group_list_view_shows_correct_context_and_paginator(self):
        """Проверяем, что group_list view передает правильный
        context шаблону"""
        response = PostViewsTest.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug-2'}
            )
        )
        object_list = response.context['page_obj'].object_list
        self.assertNotIn(
            PostViewsTest.test_post,
            object_list,
            'Ошибка: пост передан в контекст страницы чужой группы'
        )
        response = PostViewsTest.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug-1'}
            )
        )
        object_list = response.context['page_obj'].object_list
        self.assertIn(
            PostViewsTest.test_post,
            object_list,
            'Ошибка: пост не передан в контекст своей группы'
        )
        post_attr = {
            'text': 'Тестовый пост',
            'group': PostViewsTest.group_1,
            'author': PostViewsTest.author,
        }
        for value, expected in post_attr.items():
            with self.subTest(value=value):
                self.assertEqual(
                    getattr(PostViewsTest.test_post, value),
                    expected,
                    'Данные поста неверно переданы в шаблон'
                )

    def test_post_profile_view_shows_correct_context_and_paginator(self):
        """Проверяем, что profile_view передает правильный
        контекст"""
        response = PostViewsTest.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'TestUser'}
            )
        )
        object_list = response.context['page_obj'].object_list
        self.assertIn(
            PostViewsTest.test_post,
            object_list,
            ('Ошибка: пост не был передан'
             ' в контексте страницы профиля автора поста')
        )
        post_attrs = {
            'text': 'Тестовый пост',
            'group': PostViewsTest.group_1,
            'author': PostViewsTest.author,
        }
        for value, expected in post_attrs.items():
            with self.subTest(value=value):
                self.assertEqual(
                    getattr(PostViewsTest.test_post, value),
                    expected
                )

    def test_post_detail_view_shows_correct_context(self):
        response = PostViewsTest.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTest.test_post.id}
            )
        )
        post_attrs = {
            'text': 'Тестовый пост',
            'group': PostViewsTest.group_1,
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
        responses = [
            PostViewsTest.guest_client.get(
                reverse('posts:index')
            ),
            PostViewsTest.guest_client.get(
                reverse(
                    'posts:group_list',
                    kwargs={'slug': 'test-slug-1'}
                )
            ),
            PostViewsTest.guest_client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': 'TestUser'}
                )
            )
        ]
        for response in responses:
            object_list = response.context['page_obj'].object_list
            self.assertIn(
                PostViewsTest.test_post,
                object_list,
                ('Пост с заданной группой не отправлен на'
                 f'страницу по адресу {response}')
            )


class TestPaginator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Первая тестовая группа',
            slug='test-slug-1',
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

    def test_pagination(self):
        reversed_urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug-1'}),
            reverse('posts:profile', kwargs={'username': 'TestUser'})
        ]
        responses_urls = []
        for url in reversed_urls:
            responses_urls.append(
                (PostViewsTest.authorized_client.get(url), url)
            )
        for response_url in responses_urls:
            self.assertEqual(
                10,
                len(response_url[0].context['page_obj'].object_list),
                f'Количество постов не равно 10 на первой странице {url}'
            )
        responses_urls = []
        for url in reversed_urls:
            responses_urls.append(
                (PostViewsTest.authorized_client.get(url + '?page=2'), url)
            )
        for response_url in responses_urls:
            self.assertEqual(
                3,
                len(response_url[0].context['page_obj'].object_list),
                f'Количество постов не равно 3 на второй странице {url}'
            )
