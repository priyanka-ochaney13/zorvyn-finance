from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('analyst', 'Analyst'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='viewer',
        help_text='User role determines access permissions'
    )
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    class Meta:
        ordering = ['-date_joined']
