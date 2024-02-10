from rest_framework import permissions

class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role)

# class IsAdmin(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_superuser)

class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user:
            if not(request.user.role or request.user.is_superuser):
                return True
        return False

class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user)

class IsAnon(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(not(request.user))
