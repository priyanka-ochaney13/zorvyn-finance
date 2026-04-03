"""
URL configuration for core project.

Main URL router that connects all app endpoints:
- /api/users/  -> User management (register, login, etc.)
- /api/finance/ -> Financial records CRUD
- /api/dashboard/ -> Summary and analytics APIs
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),
    
    # Users app - registration, login, user management
    path('api/users/', include('users.urls')),
    
    # Finance app - financial records CRUD + dashboard
    path('api/finance/', include('finance.urls')),
    
    # JWT token refresh endpoint
    # Use this to get a new access token using your refresh token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
