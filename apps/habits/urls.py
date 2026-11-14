from django.urls import path
from . import views

urlpatterns = [
    path('', views.habit_list_view, name='list'),
    path('create/', views.habit_create_view, name='create'),
    path('<int:pk>/edit/', views.habit_update_view, name='update'),
    path('<int:pk>/delete/', views.habit_delete_view, name='delete'),
    path('<int:pk>/toggle/', views.habit_log_toggle_view, name='toggle_log'),
]
