from rest_framework import permissions
import redis
from django.conf import settings
from .models import Users

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        ssid = request.COOKIES.get("session_id", None)
        if ssid != None:
            user_name = session_storage.get(ssid).decode('utf-8')
            if user_name != None:
                user_object = Users.objects.get(login=user_name)
                return user_object.role
        return False

# class IsAdmin(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_superuser)

class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if not(request.user.role or request.user.is_superuser):
                return True
        return False

# class IsAnon(permissions.BasePermission):
#     def has_permission(self, request, view):
#         if request.user.is_authenticated:
#             return False
#         return True
