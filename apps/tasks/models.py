from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='#4f46e5')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='categories', null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks'
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='medium'
    )
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['is_completed', 'due_date', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.due_date and not self.is_completed:
            return self.due_date < timezone.now().date()
        return False

    @property
    def is_due_today(self):
        if self.due_date and not self.is_completed:
            return self.due_date == timezone.now().date()
        return False

    @property
    def priority_badge_class(self):
        return {
            'low': 'bg-secondary-subtle text-secondary border border-secondary-subtle',
            'medium': 'bg-info-subtle text-info-emphasis border border-info-subtle',
            'high': 'bg-warning-subtle text-warning-emphasis border border-warning-subtle',
            'urgent': 'bg-danger-subtle text-danger-emphasis border border-danger-subtle',
        }.get(self.priority, 'bg-secondary-subtle text-secondary')
