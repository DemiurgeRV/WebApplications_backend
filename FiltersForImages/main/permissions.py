from rest_framework import permissions
import redis
from django.conf import settings

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role
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
