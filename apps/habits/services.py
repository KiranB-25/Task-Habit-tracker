from datetime import timedelta
from django.utils import timezone


def get_habit_stats(habit, ref_date=None):
    """
    Computes accurate streak metrics, completion rates, and recent 7-day grid.
    Optimized to query completion dates once.
    """
    if ref_date is None:
        ref_date = timezone.now().date()

    # Get all dates completed as a set for O(1) lookups
    completed_dates = set(
        habit.logs.filter(completed=True).values_list('date', flat=True)
    )

    # 1. Current Streak Calculation
    current_streak = 0
    today_completed = ref_date in completed_dates
    yesterday = ref_date - timedelta(days=1)
    yesterday_completed = yesterday in completed_dates

    if today_completed:
        check_date = ref_date
        while check_date in completed_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
    elif yesterday_completed:
        check_date = yesterday
        while check_date in completed_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
    else:
        current_streak = 0

    # 2. Longest Streak Calculation
    longest_streak = 0
    if completed_dates:
        sorted_dates = sorted(list(completed_dates))
        temp_streak = 1
        longest_streak = 1
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] == sorted_dates[i - 1] + timedelta(days=1):
                temp_streak += 1
            elif sorted_dates[i] != sorted_dates[i - 1]:
                temp_streak = 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak

    # 3. 7-Day & 30-Day Completion Rate
    last_7_days = [ref_date - timedelta(days=i) for i in range(7)]
    last_30_days = [ref_date - timedelta(days=i) for i in range(30)]

    completed_7 = sum(1 for d in last_7_days if d in completed_dates)
    completed_30 = sum(1 for d in last_30_days if d in completed_dates)

    rate_7 = round((completed_7 / 7) * 100)
    rate_30 = round((completed_30 / 30) * 100)

    # 4. 7-Day Interactive Grid (chronological Monday to Sunday or past 7 days)
    # Ordered from 6 days ago up to today
    grid_days = []
    for i in range(6, -1, -1):
        d = ref_date - timedelta(days=i)
        grid_days.append({
            'date': d,
            'date_str': d.strftime('%Y-%m-%d'),
            'day_name': d.strftime('%a'),
            'day_num': d.day,
            'is_today': d == ref_date,
            'completed': d in completed_dates,
        })

    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'rate_7': rate_7,
        'rate_30': rate_30,
        'completed_7': completed_7,
        'completed_30': completed_30,
        'total_completed': len(completed_dates),
        'today_completed': today_completed,
        'grid_days': grid_days,
    }
