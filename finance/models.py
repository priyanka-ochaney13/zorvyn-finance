from django.db import models
from django.conf import settings


class FinancialRecord(models.Model):
    """
    Financial record representing an income or expense transaction.
    Linked to a user who created the record.
    All amounts are in Indian Rupees (Rs).
    """
    
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
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='financial_records',
        help_text='User who owns this financial record'
    )
    
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        help_text='Type of transaction'
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text='Category of the transaction'
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Transaction amount in Indian Rupees (Rs)'
    )
    
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='INR',
        help_text='Currency type (currently only INR supported)'
    )
    
    date = models.DateField(
        help_text='Date of the transaction'
    )
    
    description = models.TextField(
        blank=True,
        default='',
        help_text='Optional description of the transaction'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Financial Record'
        verbose_name_plural = 'Financial Records'
    
    def __str__(self):
        return f"{self.type}: {self.category} - {self.amount} ({self.date})"
