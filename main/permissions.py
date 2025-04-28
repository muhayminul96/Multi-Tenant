from rest_framework import permissions

class IsAdminOrVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.role == 'vendor'

class IsVendorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'vendor' or request.method in permissions.SAFE_METHODS

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'customer'
