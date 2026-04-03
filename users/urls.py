from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    UserListView,
    UserStatusUpdateView
)

# URL patterns for the users app
urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # User management endpoints
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/status/', UserStatusUpdateView.as_view(), name='user-status-update'),
]
