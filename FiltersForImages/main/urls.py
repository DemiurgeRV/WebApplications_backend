from django.urls import path
from . import views

urlpatterns = [
    path('api/filters/', views.filters_list),
    path('api/filter/<int:id>/', views.one_filter),
    path('api/filter/create/', views.create_filter),
    path('api/filter/<int:id>/update/', views.update_filter),
    path('api/filter/<int:id>/delete/', views.delete_filter),
    path('api/filter/<int:id>/add_to_order/', views.add_to_order),

    path('api/orders/', views.orders_list),
    path('api/order/<int:id>/', views.one_order),
    path('api/order/<int:id>/update/', views.update_order),
    path('api/order/<int:id>/update_status_owner/', views.update_status_owner),
    path('api/order/<int:id>/update_status_moderator/', views.update_status_moderator),
    path('api/order/<int:id>/delete/', views.delete_order),
    path('api/order/<int:order_id>/delete_filter/<int:filter_id>/', views.delete_filter_from_order),
    path('api/order/<int:order_id>/update_filter/<int:filter_id>/', views.update_order_filter)
]




# urlpatterns = [
#     path('home/', views.getFilters, name='Home'),
#     path('filter/<int:id>/', views.getFilter, name='filter_url'),
#     path('filter/<int:id>/delete', views.delete_filter, name='delete_filter')
# ]
