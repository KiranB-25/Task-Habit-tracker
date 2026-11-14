from django.contrib import admin
from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'created_at')
    search_fields = ('name',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'due_date', 'is_completed', 'category')
    list_filter = ('is_completed', 'priority', 'category', 'due_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
