from django.contrib import admin
from .models import FinancialRecord


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    """Admin configuration for FinancialRecord model."""
    
    list_display = ['id', 'user', 'type', 'category', 'amount', 'date', 'created_at']
    list_filter = ['type', 'category', 'date']
    search_fields = ['user__username', 'description']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
