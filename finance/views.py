from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from decimal import Decimal

from .models import FinancialRecord
from .serializers import (
    FinancialRecordSerializer,
    FinancialRecordCreateSerializer,
    FinancialRecordUpdateSerializer,
    SummarySerializer,
    CategoryTotalSerializer,
    MonthlyTrendSerializer,
)
from .filters import FinancialRecordFilter
from .permissions import CanViewRecords, CanModifyRecords, CanAccessDashboard


# ============== CRUD VIEWS ==============

class FinancialRecordListView(generics.ListAPIView):
    """
    API endpoint to list financial records for the authenticated user.
    Supports filtering by date range, category, type, and search.
    
    GET /api/finance/records/
    
    Query Parameters:
    - type: Filter by 'income' or 'expense'
    - category: Filter by category (salary, food, transport, etc.)
    - date_from: Filter records from this date (YYYY-MM-DD)
    - date_to: Filter records up to this date (YYYY-MM-DD)
    - ordering: Order by field (e.g., '-date', 'amount', '-amount')
    - search: Search in description field
    
    Returns: Paginated list of financial records
    """
    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAuthenticated, CanViewRecords]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FinancialRecordFilter
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    search_fields = ['description']
    
    def get_queryset(self):
        """Return only records belonging to the authenticated user."""
        return FinancialRecord.objects.filter(user=self.request.user)


class FinancialRecordCreateView(generics.CreateAPIView):
    """
    API endpoint to create a new financial record.
    
    POST /api/finance/records/create/
    """
    serializer_class = FinancialRecordCreateSerializer
    permission_classes = [IsAuthenticated, CanModifyRecords]
    
    def create(self, request, *args, **kwargs):
        """Create financial record with custom response format."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = serializer.save()
        
        response_data = FinancialRecordSerializer(record).data
        
        return Response({
            'message': 'Financial record created successfully',
            'record': response_data
        }, status=status.HTTP_201_CREATED)


class FinancialRecordDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a single financial record.
    
    GET /api/finance/records/<id>/
    """
    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAuthenticated, CanViewRecords]
    
    def get_queryset(self):
        """Return only records belonging to the authenticated user."""
        return FinancialRecord.objects.filter(user=self.request.user)


class FinancialRecordUpdateView(generics.UpdateAPIView):
    """
    API endpoint to update a financial record.
    
    PUT/PATCH /api/finance/records/<id>/update/
    """
    serializer_class = FinancialRecordUpdateSerializer
    permission_classes = [IsAuthenticated, CanModifyRecords]
    
    def get_queryset(self):
        """Return only records belonging to the authenticated user."""
        return FinancialRecord.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Update financial record with custom response format."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        response_data = FinancialRecordSerializer(instance).data
        
        return Response({
            'message': 'Financial record updated successfully',
            'record': response_data
        }, status=status.HTTP_200_OK)


class FinancialRecordDeleteView(generics.DestroyAPIView):
    """
    API endpoint to delete a financial record.
    
    DELETE /api/finance/records/<id>/delete/
    """
    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAuthenticated, CanModifyRecords]
    
    def get_queryset(self):
        """Return only records belonging to the authenticated user."""
        return FinancialRecord.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Delete financial record with custom response format."""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return Response({
            'message': 'Financial record deleted successfully'
        }, status=status.HTTP_200_OK)


# ============== DASHBOARD VIEWS ==============

class DashboardSummaryView(generics.GenericAPIView):
    """
    API endpoint for financial summary.
    
    GET /api/finance/dashboard/summary/
    
    Returns: Total income, total expenses, and net balance
    """
    permission_classes = [IsAuthenticated, CanAccessDashboard]
    
    def get(self, request, *args, **kwargs):
        """Calculate and return financial summary."""
        user = request.user
        records = FinancialRecord.objects.filter(user=user)
        
        total_income = records.filter(type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        total_expenses = records.filter(type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        net_balance = total_income - total_expenses
        
        data = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
        }
        
        serializer = SummarySerializer(data)
        
        return Response({
            'message': 'Financial summary retrieved successfully',
            'summary': serializer.data
        }, status=status.HTTP_200_OK)


class CategoryTotalsView(generics.GenericAPIView):
    """
    API endpoint for category-wise totals.
    
    GET /api/finance/dashboard/categories/
    Query Parameters:
    - type: Filter by 'income' or 'expense' (optional)
    
    Returns: List of categories with their totals and transaction counts
    """
    permission_classes = [IsAuthenticated, CanAccessDashboard]
    
    def get(self, request, *args, **kwargs):
        """Calculate and return category-wise totals."""
        user = request.user
        records = FinancialRecord.objects.filter(user=user)
        
        record_type = request.query_params.get('type')
        if record_type in ['income', 'expense']:
            records = records.filter(type=record_type)
        
        category_data = records.values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        serializer = CategoryTotalSerializer(category_data, many=True)
        
        return Response({
            'message': 'Category totals retrieved successfully',
            'categories': serializer.data
        }, status=status.HTTP_200_OK)


class MonthlyTrendsView(generics.GenericAPIView):
    """
    API endpoint for monthly trends over the past 12 months.
    
    GET /api/finance/dashboard/trends/
    
    Returns: Monthly breakdown of income, expenses, and net for past 12 months
    """
    permission_classes = [IsAuthenticated, CanAccessDashboard]
    
    def get(self, request, *args, **kwargs):
        """Calculate and return monthly trends."""
        user = request.user
        
        today = datetime.now().date()
        twelve_months_ago = today - timedelta(days=365)
        
        records = FinancialRecord.objects.filter(
            user=user,
            date__gte=twelve_months_ago
        )
        
        monthly_data = records.annotate(
            month=TruncMonth('date')
        ).values('month', 'type').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        months_dict = {}
        for item in monthly_data:
            month_str = item['month'].strftime('%Y-%m')
            if month_str not in months_dict:
                months_dict[month_str] = {'income': Decimal('0.00'), 'expenses': Decimal('0.00')}
            
            if item['type'] == 'income':
                months_dict[month_str]['income'] = item['total']
            else:
                months_dict[month_str]['expenses'] = item['total']
        
        trends = []
        for month, data in sorted(months_dict.items()):
            trends.append({
                'month': month,
                'income': data['income'],
                'expenses': data['expenses'],
                'net': data['income'] - data['expenses']
            })
        
        serializer = MonthlyTrendSerializer(trends, many=True)
        
        return Response({
            'message': 'Monthly trends retrieved successfully',
            'trends': serializer.data
        }, status=status.HTTP_200_OK)


class RecentActivityView(generics.ListAPIView):
    """
    API endpoint for recent transactions.
    
    GET /api/finance/dashboard/recent/
    
    Returns: Last 10 transactions (most recent first)
    """
    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAuthenticated, CanAccessDashboard]
    pagination_class = None
    
    def get_queryset(self):
        """Return last 10 records for the authenticated user."""
        return FinancialRecord.objects.filter(
            user=self.request.user
        ).order_by('-date', '-created_at')[:10]
    
    def list(self, request, *args, **kwargs):
        """Return recent activity with custom response format."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'message': 'Recent activity retrieved successfully',
            'recent_transactions': serializer.data
        }, status=status.HTTP_200_OK)
