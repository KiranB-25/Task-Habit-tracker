from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.tasks.models import Task, Category


class TasksTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='alice', password='Password123!')
        self.user2 = User.objects.create_user(username='bob', password='Password123!')

        self.category = Category.objects.create(name='Work', user=self.user1)
        self.task1 = Task.objects.create(
            user=self.user1,
            title='Alice Task 1',
            priority='high',
            due_date=timezone.now().date(),
            category=self.category
        )
        self.task2 = Task.objects.create(
            user=self.user2,
            title='Bob Secret Task',
            priority='urgent',
            due_date=timezone.now().date() + timedelta(days=2)
        )

    def test_task_list_isolation(self):
        """Alice should only see her own tasks (and legacy unassigned), not Bob's tasks."""
        self.client.login(username='alice', password='Password123!')
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Task 1')
        self.assertNotContains(response, 'Bob Secret Task')

    def test_task_toggle_complete_htmx(self):
        self.client.login(username='alice', password='Password123!')
        self.assertFalse(self.task1.is_completed)

        # Toggle complete via HTMX
        response = self.client.post(
            reverse('tasks:toggle_complete', args=[self.task1.id]),
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.task1.refresh_from_db()
        self.assertTrue(self.task1.is_completed)
        self.assertIsNotNone(self.task1.completed_at)

    def test_user_cannot_delete_other_users_task(self):
        self.client.login(username='alice', password='Password123!')
        response = self.client.post(reverse('tasks:delete', args=[self.task2.id]))
        self.assertRedirects(response, reverse('tasks:list'))
        # Bob's task should still exist!
        self.assertTrue(Task.objects.filter(id=self.task2.id).exists())

    def test_overdue_property(self):
        overdue_task = Task.objects.create(
            user=self.user1,
            title='Overdue Task',
            due_date=timezone.now().date() - timedelta(days=3),
            is_completed=False
        )
        self.assertTrue(overdue_task.is_overdue)
        overdue_task.is_completed = True
        self.assertFalse(overdue_task.is_overdue)
