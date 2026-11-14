from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list_view, name='list'),
    path('create/', views.task_create_view, name='create'),
    path('<int:pk>/edit/', views.task_update_view, name='update'),
    path('<int:pk>/delete/', views.task_delete_view, name='delete'),
    path('<int:pk>/toggle/', views.task_toggle_complete_view, name='toggle_complete'),
    path('categories/', views.category_list_create_view, name='categories'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
]
