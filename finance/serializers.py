from rest_framework import serializers
from .models import FinancialRecord


class FinancialRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for FinancialRecord model.
    Handles validation and serialization of financial records in Indian Rupees.
    """
    
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
        """Format amount as Indian Rupees."""
        return f"Rs {obj.amount:,.2f}"
    
    def validate_amount(self, value):
        """Ensure amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class FinancialRecordCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating financial records in Indian Rupees.
    User and currency are automatically set from the request.
    """
    
    class Meta:
        model = FinancialRecord
        fields = ['type', 'category', 'amount', 'date', 'description']
    
    def validate_amount(self, value):
        """Ensure amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    
    def create(self, validated_data):
        """Create record with user from request context and currency as INR."""
        validated_data['user'] = self.context['request'].user
        validated_data['currency'] = 'INR'
        return super().create(validated_data)


class FinancialRecordUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating financial records.
    All fields except user can be updated.
    """
    
    class Meta:
        model = FinancialRecord
        fields = ['type', 'category', 'amount', 'date', 'description']
    
    def validate_amount(self, value):
        """Ensure amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


# ============== DASHBOARD SERIALIZERS ==============

class SummarySerializer(serializers.Serializer):
    """
    Serializer for financial summary data.
    Returns total income, expenses, and net balance in Indian Rupees.
    """
    total_income = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_income_formatted = serializers.SerializerMethodField()
    total_expenses_formatted = serializers.SerializerMethodField()
    net_balance_formatted = serializers.SerializerMethodField()
    
    def get_total_income_formatted(self, obj):
        """Format total income as Indian Rupees."""
        return f"Rs {obj['total_income']:,.2f}"
    
    def get_total_expenses_formatted(self, obj):
        """Format total expenses as Indian Rupees."""
        return f"Rs {obj['total_expenses']:,.2f}"
    
    def get_net_balance_formatted(self, obj):
        """Format net balance as Indian Rupees."""
        return f"Rs {obj['net_balance']:,.2f}"


class CategoryTotalSerializer(serializers.Serializer):
    """
    Serializer for category-wise totals in Indian Rupees.
    """
    category = serializers.CharField()
    total = serializers.DecimalField(max_digits=14, decimal_places=2)
    count = serializers.IntegerField()
    total_formatted = serializers.SerializerMethodField()
    
    def get_total_formatted(self, obj):
        """Format total as Indian Rupees."""
        return f"Rs {obj['total']:,.2f}"


class MonthlyTrendSerializer(serializers.Serializer):
    """
    Serializer for monthly trend data in Indian Rupees.
    """
    month = serializers.CharField()
    income = serializers.DecimalField(max_digits=14, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=14, decimal_places=2)
    net = serializers.DecimalField(max_digits=14, decimal_places=2)
    income_formatted = serializers.SerializerMethodField()
    expenses_formatted = serializers.SerializerMethodField()
    net_formatted = serializers.SerializerMethodField()
    
    def get_income_formatted(self, obj):
        """Format income as Indian Rupees."""
        return f"Rs {obj['income']:,.2f}"
    
    def get_expenses_formatted(self, obj):
        """Format expenses as Indian Rupees."""
        return f"Rs {obj['expenses']:,.2f}"
    
    def get_net_formatted(self, obj):
        """Format net as Indian Rupees."""
        return f"Rs {obj['net']:,.2f}"
