from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.accounts.models import Profile


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePassword123!'
        )

    def test_profile_auto_created_on_user_creation(self):
        """Verify post_save signal created Profile with default light theme."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.theme, 'light')

    def test_user_login_success(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'SecurePassword123!',
        })
        self.assertRedirects(response, reverse('dashboard:index'))

    def test_user_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPassword456!',
            'confirm_password': 'StrongPassword456!',
        })
        self.assertRedirects(response, reverse('dashboard:index'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(new_user, 'profile'))

    def test_toggle_theme_authenticated(self):
        self.client.login(username='testuser', password='SecurePassword123!')
        response = self.client.post(reverse('accounts:toggle_theme'), {'theme': 'dark'})
        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.theme, 'dark')
