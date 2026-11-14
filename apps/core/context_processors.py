from django.utils import timezone


def global_context(request):
    """
    Context processor providing current theme, user profile, and active date.
    """
    theme = 'light'
    profile = None

    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            theme = profile.theme
    else:
        theme = request.COOKIES.get('theme', 'light')

    return {
        'current_theme': theme,
        'user_profile': profile,
        'today': timezone.now().date(),
    }
