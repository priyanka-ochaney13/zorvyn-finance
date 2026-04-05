from rest_framework import serializers
from datetime import datetime, date
from decimal import Decimal
from .models import FinancialRecord


class FinancialRecordSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    amount_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialRecord
        fields = [
            'id',
            'user',
            'user_username',
            'type',
            'category',
            'amount',
            'amount_formatted',
            'currency',
            'date',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'user_username', 'currency', 'created_at', 'updated_at']
    
    def get_amount_formatted(self, obj):
        return f"Rs {obj.amount:,.2f}"
    
    def validate_amount(self, value):
        if value is None:
            raise serializers.ValidationError("Amount cannot be empty.")
        
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError("Amount is too large. Maximum allowed is Rs 999,999,999.99.")
        
        return value
    
    def validate_date(self, value):
        if value is None:
            raise serializers.ValidationError("Date cannot be empty.")
        
        today = date.today()
        
        if value > today:
            raise serializers.ValidationError("Transaction date cannot be in the future.")
        
        from datetime import timedelta
        ten_years_ago = today - timedelta(days=365*10)
        if value < ten_years_ago:
            raise serializers.ValidationError("Transaction date is too old. Records cannot be older than 10 years.")
        
        return value
    
    def validate(self, data):
        if 'type' in data and 'category' in data:
            record_type = data['type']
            category = data['category']
            
            if record_type not in ['income', 'expense']:
                raise serializers.ValidationError({
                    'type': f"Invalid type '{record_type}'. Must be 'income' or 'expense'."
                })
            
            valid_categories = dict(FinancialRecord.CATEGORY_CHOICES)
            if category not in valid_categories:
                raise serializers.ValidationError({
                    'category': f"Invalid category '{category}'. Allowed categories: {', '.join(valid_categories.keys())}"
                })
        
        return data


class FinancialRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialRecord
        fields = ['type', 'category', 'amount', 'date', 'description']
    
    def validate_amount(self, value):
        if value is None:
            raise serializers.ValidationError("Amount cannot be empty.")
        
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError("Amount is too large. Maximum allowed is Rs 999,999,999.99.")
        
        return value
    
    def validate_date(self, value):
        if value is None:
            raise serializers.ValidationError("Date cannot be empty.")
        
        today = date.today()
        
        if value > today:
            raise serializers.ValidationError("Transaction date cannot be in the future.")
        
        from datetime import timedelta
        ten_years_ago = today - timedelta(days=365*10)
        if value < ten_years_ago:
            raise serializers.ValidationError("Transaction date is too old. Records cannot be older than 10 years.")
        
        return value
    
    def validate_type(self, value):
        if value not in ['income', 'expense']:
            raise serializers.ValidationError(f"Invalid type '{value}'. Must be 'income' or 'expense'.")
        return value
    
    def validate_category(self, value):
        valid_categories = dict(FinancialRecord.CATEGORY_CHOICES)
        if value not in valid_categories:
            raise serializers.ValidationError(f"Invalid category '{value}'. Allowed: {', '.join(valid_categories.keys())}")
        return value
    
    def validate_description(self, value):
        if value and len(value) > 500:
            raise serializers.ValidationError("Description is too long. Maximum 500 characters allowed.")
        return value
    
    def validate(self, data):
        if 'type' not in data:
            raise serializers.ValidationError({'type': 'Type is required.'})
        if 'category' not in data:
            raise serializers.ValidationError({'category': 'Category is required.'})
        if 'amount' not in data:
            raise serializers.ValidationError({'amount': 'Amount is required.'})
        if 'date' not in data:
            raise serializers.ValidationError({'date': 'Date is required.'})
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['currency'] = 'INR'
        return super().create(validated_data)


class FinancialRecordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialRecord
        fields = ['type', 'category', 'amount', 'date', 'description']
    
    def validate_amount(self, value):
        if value is None:
            raise serializers.ValidationError("Amount cannot be empty.")
        
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        
        if value > Decimal('999999999.99'):
            raise serializers.ValidationError("Amount is too large. Maximum allowed is Rs 999,999,999.99.")
        
        return value
    
    def validate_date(self, value):
        if value is None:
            raise serializers.ValidationError("Date cannot be empty.")
        
        today = date.today()
        
        if value > today:
            raise serializers.ValidationError("Transaction date cannot be in the future.")
        
        from datetime import timedelta
        ten_years_ago = today - timedelta(days=365*10)
        if value < ten_years_ago:
            raise serializers.ValidationError("Transaction date is too old. Records cannot be older than 10 years.")
        
        return value
    
    def validate_type(self, value):
        if value and value not in ['income', 'expense']:
            raise serializers.ValidationError(f"Invalid type '{value}'. Must be 'income' or 'expense'.")
        return value
    
    def validate_category(self, value):
        if value:
            valid_categories = dict(FinancialRecord.CATEGORY_CHOICES)
            if value not in valid_categories:
                raise serializers.ValidationError(f"Invalid category '{value}'. Allowed: {', '.join(valid_categories.keys())}")
        return value
    
    def validate_description(self, value):
        if value and len(value) > 500:
            raise serializers.ValidationError("Description is too long. Maximum 500 characters allowed.")
        return value


class SummarySerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_income_formatted = serializers.SerializerMethodField()
    total_expenses_formatted = serializers.SerializerMethodField()
    net_balance_formatted = serializers.SerializerMethodField()
    
    def get_total_income_formatted(self, obj):
        return f"Rs {obj['total_income']:,.2f}"
    
    def get_total_expenses_formatted(self, obj):
        return f"Rs {obj['total_expenses']:,.2f}"
    
    def get_net_balance_formatted(self, obj):
        return f"Rs {obj['net_balance']:,.2f}"


class CategoryTotalSerializer(serializers.Serializer):
    category = serializers.CharField()
    total = serializers.DecimalField(max_digits=14, decimal_places=2)
    count = serializers.IntegerField()
    total_formatted = serializers.SerializerMethodField()
    
    def get_total_formatted(self, obj):
        return f"Rs {obj['total']:,.2f}"


class MonthlyTrendSerializer(serializers.Serializer):
    month = serializers.CharField()
    income = serializers.DecimalField(max_digits=14, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=14, decimal_places=2)
    net = serializers.DecimalField(max_digits=14, decimal_places=2)
    income_formatted = serializers.SerializerMethodField()
    expenses_formatted = serializers.SerializerMethodField()
    net_formatted = serializers.SerializerMethodField()
    
    def get_income_formatted(self, obj):
        return f"Rs {obj['income']:,.2f}"
    
    def get_expenses_formatted(self, obj):
        return f"Rs {obj['expenses']:,.2f}"
    
    def get_net_formatted(self, obj):
        return f"Rs {obj['net']:,.2f}"
