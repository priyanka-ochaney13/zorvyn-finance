from django.db import models
from django.conf import settings


class FinancialRecord(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    CATEGORY_CHOICES = [
        ('salary', 'Salary'),
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('utilities', 'Utilities'),
        ('entertainment', 'Entertainment'),
        ('healthcare', 'Healthcare'),
        ('shopping', 'Shopping'),
        ('investment', 'Investment'),
        ('other', 'Other'),
    ]
    
    CURRENCY_CHOICES = [
        ('INR', 'Indian Rupees (₹)'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='financial_records')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Financial Record'
        verbose_name_plural = 'Financial Records'
    
    def __str__(self):
        return f"{self.type}: {self.category} - {self.amount} ({self.date})"
