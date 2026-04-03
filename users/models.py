from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds role-based access control and active status management.
    
    Roles:
    - viewer: Can only view financial records (read-only)
    - analyst: Can view records + access dashboard summaries
    - admin: Full access including user management
    """
    
    # Role choices - defines what each user can do in the system
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),    # Read-only access
        ('analyst', 'Analyst'),  # Read + dashboard access
        ('admin', 'Admin'),      # Full access
    ]
    
    # Role field with default as 'viewer' (least privilege)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='viewer',
        help_text='User role determines access permissions'
    )
    
    # is_active is inherited from AbstractUser
    # We use it to manage user status (active/inactive)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    class Meta:
        # Order users by newest first
        ordering = ['-date_joined']
