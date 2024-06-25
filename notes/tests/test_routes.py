from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    TITLE = 'Заголовок новости'
    TEXT = 'Тестовый текст'
    SLUG = 'test-note'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.user = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author
        )

    def test_pages_availability_home_signup_login_logout(self):
        urls = (
            ('notes:home', None),
            ('users:signup', None),
            ('users:login', None),
            ('users:logout', None),
        )
        for name, args in urls:
            self.client.force_login(self.user)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_list_done_add(self):
        users_statuses = (
            (self.user, HTTPStatus.OK),
            (self.author, HTTPStatus.OK),
        )
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_notes_detail_edit_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.user, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ('notes:detail', None),
            ('notes:edit', None),
            ('notes:delete', None),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client_for_note_detail_edit_delete(self):
        login_url = reverse('users:login')
        urls = ('notes:detail', 'notes:edit', 'notes:delete')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_client_for_note_list_success_add(self):
        login_url = reverse('users:login')
        urls = ('notes:list', 'notes:success', 'notes:add')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
