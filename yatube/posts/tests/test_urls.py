# posts/tests/test_urls.py
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import User, Post, Group


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.author,
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
        )

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_non_existent_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_exist_at_desired_location(self):
        urls = [
            '/',
            '/group/test-slug/',
            '/profile/TestUser/',
            '/posts/1/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_templates_used(self):
        urls_templates = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/TestUser/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, expected_template in urls_templates.items():
            with self.subTest(url=url):
                response = StaticURLTests.authorized_client.get(url)
                self.assertTemplateUsed(response, expected_template)
