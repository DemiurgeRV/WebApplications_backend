from rest_framework.routers import DefaultRouter
from . import views
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/',  views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('api/edit_image/<int:id>/', views.edit_image),

    path('api/filters/', views.filters_list),
    path('api/filters/<int:id>/', views.one_filter),
    path('api/filters/create/', views.create_filter),
    path('api/filters/<int:id>/update/', views.update_filter),
    path('api/filters/<int:id>/delete/', views.delete_filter),
    path('api/filters/<int:id>/add_to_order/', views.add_to_order),

    path('api/orders/', views.orders_list),
    path('api/orders/<int:id>/', views.one_order),
    path('api/orders/<int:id>/update_status_owner/', views.update_status_owner),
    path('api/orders/<int:id>/update_status_moderator/', views.update_status_moderator),
    path('api/orders/<int:id>/delete/', views.delete_order),
    path('api/orders/<int:order_id>/delete_filter/<int:filter_id>/', views.delete_filter_from_order),
    path('api/orders/<int:order_id>/update_filter/<int:filter_id>/', views.update_order_filter),

    path('api/filters/<int:id>/image/', views.get_image),
    path('api/filters/<int:id>/image/update/', views.update_image)
]




# urlpatterns = [
#     path('home/', views.getFilters, name='Home'),
#     path('filter/<int:id>/', views.getFilter, name='filter_url'),
#     path('filter/<int:id>/delete', views.delete_filter, name='delete_filter')
# ]
