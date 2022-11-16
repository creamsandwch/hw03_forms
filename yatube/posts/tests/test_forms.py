from django.test import TestCase, Client
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post, Group, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
        )
        cls.author = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.author,
            group=cls.group
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.form = PostForm()

    def test_post_form_create(self):
        """Валидная форма PostForm создаёт запись в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст тестового поста из формы',
            'group': PostFormTests.group,
        }
        response = PostFormTests.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostFormTests.author.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст тестового поста из формы',
                group=PostFormTests.group,
            ).exists()
        )
