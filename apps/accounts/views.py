from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Ensure Profile exists
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to your productivity tracker, {user.username}!')
            return redirect('dashboard:index')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next') or 'dashboard:index'
            return redirect(next_url)
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    })


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})


@require_POST
def toggle_theme_view(request):
    new_theme = request.POST.get('theme')
    if new_theme not in ['light', 'dark']:
        # Toggle current
        current_theme = 'light'
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            current_theme = request.user.profile.theme
        else:
            current_theme = request.COOKIES.get('theme', 'light')
        new_theme = 'dark' if current_theme == 'light' else 'light'

    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.theme = new_theme
        profile.save(update_fields=['theme'])

    response = JsonResponse({'status': 'ok', 'theme': new_theme})
    response.set_cookie('theme', new_theme, max_age=365 * 24 * 60 * 60, samesite='Lax')
    return response
