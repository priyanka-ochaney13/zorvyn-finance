from rest_framework.permissions import BasePermission


class CanViewRecords(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.role in ['viewer', 'analyst', 'admin']
        
        return False


class CanModifyRecords(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.role == 'viewer':
            return False
        
        return request.user.role in ['analyst', 'admin']
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanAccessDashboard(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.role in ['viewer', 'analyst', 'admin']
        
        return False


class CanManageUsers(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role == 'admin'
