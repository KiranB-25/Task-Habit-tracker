from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.habits.models import Habit, HabitLog
from apps.habits.services import get_habit_stats


class HabitsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='carol', password='Password123!')
        self.other_user = User.objects.create_user(username='dave', password='Password123!')
        self.today = timezone.now().date()

        self.habit = Habit.objects.create(
            user=self.user,
            name='Daily Meditation',
            frequency='daily',
            target_days_per_week=7
        )

    def test_current_streak_completed_today(self):
        # Completed today, yesterday, and 2 days ago = 3-day streak
        HabitLog.objects.create(habit=self.habit, date=self.today, completed=True)
        HabitLog.objects.create(habit=self.habit, date=self.today - timedelta(days=1), completed=True)
        HabitLog.objects.create(habit=self.habit, date=self.today - timedelta(days=2), completed=True)

        stats = get_habit_stats(self.habit, self.today)
        self.assertEqual(stats['current_streak'], 3)
        self.assertEqual(stats['longest_streak'], 3)
        self.assertTrue(stats['today_completed'])

    def test_current_streak_completed_yesterday_not_today(self):
        # Completed yesterday and 2 days ago, but not yet today -> streak should still be 2!
        HabitLog.objects.create(habit=self.habit, date=self.today - timedelta(days=1), completed=True)
        HabitLog.objects.create(habit=self.habit, date=self.today - timedelta(days=2), completed=True)

        stats = get_habit_stats(self.habit, self.today)
        self.assertEqual(stats['current_streak'], 2)
        self.assertFalse(stats['today_completed'])

    def test_broken_streak(self):
        # Completed 3 days ago, but missed yesterday and today -> streak is 0
        HabitLog.objects.create(habit=self.habit, date=self.today - timedelta(days=3), completed=True)

        stats = get_habit_stats(self.habit, self.today)
        self.assertEqual(stats['current_streak'], 0)
        self.assertEqual(stats['longest_streak'], 1)

    def test_longest_streak_over_multiple_periods(self):
        # Period 1: 5-day streak 20 days ago
        for i in range(20, 15, -1):
            HabitLog.objects.create(habit=self.habit, date=self.today - timedelta(days=i), completed=True)

        # Gap of 5 days

        # Period 2: 2-day current streak
        HabitLog.objects.create(habit=self.habit, date=self.today, completed=True)
        HabitLog.objects.create(habit=self.habit, date=self.today - timedelta(days=1), completed=True)

        stats = get_habit_stats(self.habit, self.today)
        self.assertEqual(stats['current_streak'], 2)
        self.assertEqual(stats['longest_streak'], 5)

    def test_habit_log_toggle_htmx(self):
        self.client.login(username='carol', password='Password123!')
        date_str = self.today.strftime('%Y-%m-%d')

        # First toggle: marks completed
        response = self.client.post(
            f"{reverse('habits:toggle_log', args=[self.habit.id])}?date={date_str}",
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.habit.is_completed_today())

        # Second toggle: marks uncompleted
        response = self.client.post(
            f"{reverse('habits:toggle_log', args=[self.habit.id])}?date={date_str}",
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.habit.is_completed_today())

    def test_user_cannot_toggle_other_users_habit(self):
        self.client.login(username='dave', password='Password123!')
        response = self.client.post(reverse('habits:toggle_log', args=[self.habit.id]))
        self.assertEqual(response.status_code, 404)
