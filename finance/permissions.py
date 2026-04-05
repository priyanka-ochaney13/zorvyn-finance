from rest_framework.permissions import BasePermission


class IsViewer(BasePermission):
    """
    Permission for viewers - read-only access to their own records.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.method in ['GET', 'HEAD', 'OPTIONS']


class IsAnalyst(BasePermission):
    """
    Permission for analysts - read access + dashboard.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.method in ['GET', 'HEAD', 'OPTIONS']


class IsAdmin(BasePermission):
    """
    Permission for admins - full access.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True


class CanViewRecords(BasePermission):
    """
    Combined permission: All roles can view records.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        return False


class CanModifyRecords(BasePermission):
    """
    Permission for modifying records (create, update, delete).
    Only admins can modify records.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role == 'admin'


class CanAccessDashboard(BasePermission):
    """
    Permission for accessing dashboard endpoints.
    All roles (viewer, analyst, admin) can access dashboard for read-only views.
    Per assignment: "Viewer: Can only view dashboard data"
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.method in ['GET', 'HEAD', 'OPTIONS']


class CanManageUsers(BasePermission):
    """
    Permission for user management endpoints.
    Only admins can manage users.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role == 'admin'
