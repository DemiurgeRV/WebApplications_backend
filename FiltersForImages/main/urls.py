from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.getFilters, name='Home'),
    path('filter/<int:id>/', views.getFilter, name='filter_url'),
    path('filter/<int:id>/delete', views.delete_filter, name='delete_filter')
]
