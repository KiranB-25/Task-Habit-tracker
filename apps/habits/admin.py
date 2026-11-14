from django.contrib import admin
from .models import Habit, HabitLog


class HabitLogInline(admin.TabularInline):
    model = HabitLog
    extra = 0
    fields = ('date', 'completed', 'notes')


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'frequency', 'target_days_per_week', 'color', 'is_archived', 'created_at')
    list_filter = ('frequency', 'is_archived', 'created_at')
    search_fields = ('name', 'description')
    inlines = [HabitLogInline]


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ('habit', 'date', 'completed', 'created_at')
    list_filter = ('completed', 'date')
    search_fields = ('habit__name', 'notes')
