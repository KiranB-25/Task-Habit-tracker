from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='habits'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(
        'tasks.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='habits'
    )
    frequency = models.CharField(
        max_length=10, choices=FREQUENCY_CHOICES, default='daily'
    )
    target_days_per_week = models.PositiveSmallIntegerField(default=7)
    color = models.CharField(max_length=20, default='#10b981')
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def is_completed_on(self, target_date):
        return self.logs.filter(date=target_date, completed=True).exists()

    def is_completed_today(self):
        return self.is_completed_on(timezone.now().date())


class HabitLog(models.Model):
    habit = models.ForeignKey(
        Habit, on_delete=models.CASCADE, related_name='logs'
    )
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('habit', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.habit.name} - {self.date} ({'Done' if self.completed else 'Missed'})"
