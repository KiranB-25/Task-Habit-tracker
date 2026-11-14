from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from .models import Task, Category
from .forms import TaskForm, CategoryForm


@login_required
def task_list_view(request):
    """
    List tasks with search, status filters, priority filters, sorting, and pagination.
    Supports HTMX partial loading.
    """
    # Optimized query with select_related
    tasks = Task.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    ).select_related('category', 'user')

    # Status Filter
    status = request.GET.get('status', 'all')
    today = timezone.now().date()

    if status == 'pending':
        tasks = tasks.filter(is_completed=False)
    elif status == 'completed':
        tasks = tasks.filter(is_completed=True)
    elif status == 'overdue':
        tasks = tasks.filter(is_completed=False, due_date__lt=today)

    # Priority Filter
    priority = request.GET.get('priority', '')
    if priority in ['low', 'medium', 'high', 'urgent']:
        tasks = tasks.filter(priority=priority)

    # Category Filter
    category_id = request.GET.get('category', '')
    if category_id.isdigit():
        tasks = tasks.filter(category_id=int(category_id))

    # Search Query
    q = request.GET.get('q', '').strip()
    if q:
        tasks = tasks.filter(Q(title__icontains=q) | Q(description__icontains=q))

    # Sorting
    sort = request.GET.get('sort', 'default')
    sort_mapping = {
        'due_asc': ['due_date', 'priority'],
        'due_desc': ['-due_date', 'priority'],
        'created_desc': ['-created_at'],
        'created_asc': ['created_at'],
        'title': ['title'],
        'priority': ['priority', 'due_date'],
    }
    if sort in sort_mapping:
        tasks = tasks.order_by(*sort_mapping[sort])
    else:
        # Default: pending first, then due date, then recent
        tasks = tasks.order_by('is_completed', 'due_date', '-created_at')

    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Counts for quick filter tabs
    base_user_tasks = Task.objects.filter(Q(user=request.user) | Q(user__isnull=True))
    total_count = base_user_tasks.count()
    pending_count = base_user_tasks.filter(is_completed=False).count()
    completed_count = base_user_tasks.filter(is_completed=True).count()
    overdue_count = base_user_tasks.filter(is_completed=False, due_date__lt=today).count()

    categories = Category.objects.filter(Q(user=request.user) | Q(user__isnull=True))

    context = {
        'page_obj': page_obj,
        'tasks': page_obj.object_list,
        'status': status,
        'priority': priority,
        'category_id': category_id,
        'q': q,
        'sort': sort,
        'categories': categories,
        'total_count': total_count,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'overdue_count': overdue_count,
        'today': today,
    }

    # HTMX partial response
    if request.headers.get('HX-Request') and not request.headers.get('HX-Boosted'):
        return render(request, 'tasks/partials/_task_list_content.html', context)

    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" was created successfully.')
            return redirect('tasks:list')
    else:
        form = TaskForm(user=request.user)

    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create New Task'})


@login_required
def task_update_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Check permissions
    if task.user and task.user != request.user:
        messages.error(request, 'You do not have permission to edit this task.')
        return redirect('tasks:list')

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Task "{task.title}" was updated.')
            return redirect('tasks:list')
    else:
        form = TaskForm(instance=task, user=request.user)

    return render(request, 'tasks/task_form.html', {'form': form, 'task': task, 'title': 'Edit Task'})


@login_required
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.user and task.user != request.user:
        messages.error(request, 'You do not have permission to delete this task.')
        return redirect('tasks:list')

    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Task "{title}" has been deleted.')
        return redirect('tasks:list')

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_toggle_complete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.user and task.user != request.user:
        return HttpResponse('Unauthorized', status=403)

    task.is_completed = not task.is_completed
    task.completed_at = timezone.now() if task.is_completed else None
    task.save(update_fields=['is_completed', 'completed_at'])

    # If HTMX request, render updated row
    if request.headers.get('HX-Request'):
        return render(request, 'tasks/partials/_task_row.html', {'task': task, 'today': timezone.now().date()})

    messages.info(request, f'Task status updated.')
    return redirect('tasks:list')


@login_required
def category_list_create_view(request):
    categories = Category.objects.filter(Q(user=request.user) | Q(user__isnull=True))
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created.')
            return redirect('tasks:categories')
    else:
        form = CategoryForm()

    return render(request, 'tasks/category_list.html', {'categories': categories, 'form': form})


@login_required
def category_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" removed.')
    return redirect('tasks:categories')
