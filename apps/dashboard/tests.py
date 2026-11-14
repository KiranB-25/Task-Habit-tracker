from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from apps.tasks.models import Task
from apps.habits.models import Habit


class DashboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='eva', password='Password123!')
        self.today = timezone.now().date()
        Task.objects.create(
            user=self.user,
            title='Eva Task 1',
            priority='high',
            due_date=self.today
        )
        Habit.objects.create(user=self.user, name='Eva Habit 1')

    def test_dashboard_redirects_unauthenticated(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_dashboard_authenticated(self):
        self.client.login(username='eva', password='Password123!')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Eva Task 1')
        self.assertContains(response, 'Eva Habit 1')

    def test_analytics_json_api(self):
        self.client.login(username='eva', password='Password123!')
        response = self.client.get(reverse('dashboard:analytics_data_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('trend', data)
        self.assertIn('priority', data)
        self.assertIn('habits', data)
        self.assertEqual(len(data['trend']['labels']), 7)
