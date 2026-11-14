from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'created_at', 'updated_at')
    list_filter = ('theme', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')
