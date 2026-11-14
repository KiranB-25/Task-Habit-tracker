from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('api/analytics-data/', views.analytics_data_json, name='analytics_data_json'),
]
