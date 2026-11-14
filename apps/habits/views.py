from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
from .models import Habit, HabitLog
from .forms import HabitForm
from .services import get_habit_stats


@login_required
def habit_list_view(request):
    """
    List habits with streak analytics, 7-day interactive checkoff, and completion rates.
    """
    today = timezone.now().date()
    habits = Habit.objects.filter(
        user=request.user, is_archived=False
    ).select_related('category').prefetch_related('logs')

    habits_data = []
    completed_today_count = 0
    total_rate = 0
    max_streak = 0

    for habit in habits:
        stats = get_habit_stats(habit, today)
        if stats['today_completed']:
            completed_today_count += 1
        total_rate += stats['rate_7']
        if stats['current_streak'] > max_streak:
            max_streak = stats['current_streak']

        habits_data.append({
            'habit': habit,
            'stats': stats,
        })

    avg_rate_7 = round(total_rate / len(habits)) if habits else 0

    context = {
        'habits_data': habits_data,
        'today': today,
        'total_habits': len(habits),
        'completed_today_count': completed_today_count,
        'avg_rate_7': avg_rate_7,
        'max_streak': max_streak,
    }
    return render(request, 'habits/habit_list.html', context)


@login_required
def habit_create_view(request):
    if request.method == 'POST':
        form = HabitForm(request.POST, user=request.user)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, f'Habit "{habit.name}" created successfully!')
            return redirect('habits:list')
    else:
        form = HabitForm(user=request.user)

    return render(request, 'habits/habit_form.html', {'form': form, 'title': 'Create New Habit'})


@login_required
def habit_update_view(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit, user=request.user)
        if form.is_valid():
            habit = form.save()
            messages.success(request, f'Habit "{habit.name}" updated successfully.')
            return redirect('habits:list')
    else:
        form = HabitForm(instance=habit, user=request.user)

    return render(request, 'habits/habit_form.html', {'form': form, 'habit': habit, 'title': 'Edit Habit'})


@login_required
def habit_delete_view(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        name = habit.name
        habit.delete()
        messages.success(request, f'Habit "{name}" has been removed.')
        return redirect('habits:list')

    return render(request, 'habits/habit_confirm_delete.html', {'habit': habit})


@login_required
def habit_log_toggle_view(request, pk):
    """
    Toggle completion for a specific date via HTMX or standard POST.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    date_str = request.POST.get('date') or request.GET.get('date')

    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = timezone.now().date()
    else:
        target_date = timezone.now().date()

    # Toggle log
    log, created = HabitLog.objects.get_or_create(
        habit=habit,
        date=target_date,
        defaults={'completed': True}
    )
    if not created:
        log.completed = not log.completed
        log.save(update_fields=['completed'])

    # If HTMX, render updated habit card
    if request.headers.get('HX-Request'):
        stats = get_habit_stats(habit, timezone.now().date())
        return render(request, 'habits/partials/_habit_card.html', {
            'item': {'habit': habit, 'stats': stats},
            'today': timezone.now().date(),
        })

    return redirect('habits:list')
