from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.http import JsonResponse
from apps.tasks.models import Task, Category
from apps.habits.models import Habit, HabitLog
from apps.habits.services import get_habit_stats


@login_required
def dashboard_view(request):
    """
    Main dashboard overview with welcome banner, today's actions, metric cards,
    upcoming deadlines, and habit streaks.
    """
    today = timezone.now().date()
    user = request.user

    # Tasks Query
    user_tasks = Task.objects.filter(Q(user=user) | Q(user__isnull=True))

    total_tasks = user_tasks.count()
    pending_tasks = user_tasks.filter(is_completed=False).count()
    completed_tasks = user_tasks.filter(is_completed=True).count()
    overdue_tasks = user_tasks.filter(is_completed=False, due_date__lt=today).count()

    # Tasks due today or pending overdue
    today_tasks = user_tasks.filter(
        Q(due_date=today) | (Q(is_completed=False) & Q(due_date__lt=today))
    ).order_by('is_completed', 'due_date', '-priority')[:8]

    # Upcoming tasks (next 7 days, excluding today)
    next_week = today + timedelta(days=7)
    upcoming_tasks = user_tasks.filter(
        is_completed=False,
        due_date__gt=today,
        due_date__lte=next_week
    ).order_by('due_date')[:5]

    # Today's Task Completion Rate
    today_all_tasks = user_tasks.filter(due_date=today)
    today_all_count = today_all_tasks.count()
    today_completed_count = today_all_tasks.filter(is_completed=True).count()
    today_task_rate = round((today_completed_count / today_all_count) * 100) if today_all_count else 0

    # Habits Query
    habits = Habit.objects.filter(user=user, is_archived=False).prefetch_related('logs')
    total_habits = habits.count()
    completed_habits_today = 0
    max_streak = 0
    habits_summary = []

    for habit in habits:
        stats = get_habit_stats(habit, today)
        if stats['today_completed']:
            completed_habits_today += 1
        if stats['current_streak'] > max_streak:
            max_streak = stats['current_streak']
        habits_summary.append({
            'habit': habit,
            'stats': stats,
        })

    habit_today_rate = round((completed_habits_today / total_habits) * 100) if total_habits else 0

    # Weekly summary (past 7 days tasks completed)
    week_start = today - timedelta(days=6)
    completed_this_week = user_tasks.filter(
        is_completed=True,
        completed_at__date__gte=week_start
    ).count()

    context = {
        'today': today,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'today_tasks': today_tasks,
        'upcoming_tasks': upcoming_tasks,
        'today_task_rate': today_task_rate,
        'today_all_count': today_all_count,
        'today_completed_count': today_completed_count,
        'total_habits': total_habits,
        'completed_habits_today': completed_habits_today,
        'habit_today_rate': habit_today_rate,
        'max_streak': max_streak,
        'habits_summary': habits_summary[:6],
        'completed_this_week': completed_this_week,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def analytics_view(request):
    """
    Dedicated analytics page with productivity charts and breakdown metrics.
    """
    today = timezone.now().date()
    user = request.user
    user_tasks = Task.objects.filter(Q(user=user) | Q(user__isnull=True))

    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(is_completed=True).count()
    overall_completion_rate = round((completed_tasks / total_tasks) * 100) if total_tasks else 0

    habits = Habit.objects.filter(user=user, is_archived=False).prefetch_related('logs')
    habits_data = [
        {'habit': h, 'stats': get_habit_stats(h, today)} for h in habits
    ]

    context = {
        'today': today,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overall_completion_rate': overall_completion_rate,
        'habits_data': habits_data,
    }
    return render(request, 'dashboard/analytics.html', context)


@login_required
def analytics_data_json(request):
    """
    JSON API for Chart.js analytics charts.
    """
    today = timezone.now().date()
    user = request.user
    user_tasks = Task.objects.filter(Q(user=user) | Q(user__isnull=True))

    # 1. 7-Day Task Completion Trend
    past_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    trend_labels = [d.strftime('%a (%b %d)') for d in past_7_days]
    completed_counts = []
    created_counts = []

    for d in past_7_days:
        comp_count = user_tasks.filter(is_completed=True, completed_at__date=d).count()
        creat_count = user_tasks.filter(created_at__date=d).count()
        completed_counts.append(comp_count)
        created_counts.append(creat_count)

    # 2. Priority Breakdown
    priorities = ['low', 'medium', 'high', 'urgent']
    priority_labels = ['Low', 'Medium', 'High', 'Urgent']
    priority_counts = [
        user_tasks.filter(priority=p).count() for p in priorities
    ]

    # 3. Habit Completion Rates (Last 30 Days)
    habits = Habit.objects.filter(user=user, is_archived=False).prefetch_related('logs')
    habit_names = []
    habit_rates = []
    habit_colors = []

    for h in habits:
        stats = get_habit_stats(h, today)
        habit_names.append(h.name)
        habit_rates.append(stats['rate_30'])
        habit_colors.append(h.color or '#4f46e5')

    data = {
        'trend': {
            'labels': trend_labels,
            'completed': completed_counts,
            'created': created_counts,
        },
        'priority': {
            'labels': priority_labels,
            'counts': priority_counts,
        },
        'habits': {
            'names': habit_names,
            'rates': habit_rates,
            'colors': habit_colors,
        }
    }
    return JsonResponse(data)
