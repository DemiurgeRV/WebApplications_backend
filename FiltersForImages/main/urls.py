from django.urls import path
from . import views

urlpatterns = [
    path('api/filters/', views.filters_list),
    path('api/filter/<int:id>/', views.one_filter),
    path('api/filter/create/', views.create_filter),
    path('api/filter/<int:id>/update/', views.update_filter),
    path('api/filter/<int:id>/delete/', views.delete_filter),
    path('api/filter/<int:id>/add_to_order/', views.add_to_order)
]




# urlpatterns = [
#     path('home/', views.getFilters, name='Home'),
#     path('filter/<int:id>/', views.getFilter, name='filter_url'),
#     path('filter/<int:id>/delete', views.delete_filter, name='delete_filter')
# ]
