from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
    path('tasks/', include(('apps.tasks.urls', 'tasks'), namespace='tasks')),
    path('habits/', include(('apps.habits.urls', 'habits'), namespace='habits')),
    path('', include(('apps.dashboard.urls', 'dashboard'), namespace='dashboard')),
]
