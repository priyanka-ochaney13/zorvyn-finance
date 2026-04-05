from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.http import Http404
from datetime import datetime, timedelta, date
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


class FinancialRecordViewSet(viewsets.ModelViewSet):
    """
    RESTful ViewSet for financial records.
    GET    /records/        - List all records
    POST   /records/        - Create a record
    GET    /records/{id}/   - Retrieve a record
    PUT    /records/{id}/   - Update a record
    DELETE /records/{id}/   - Delete a record
    """
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = FinancialRecordFilter
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    search_fields = ['description']

    def get_queryset(self):
        return FinancialRecord.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return FinancialRecordCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FinancialRecordUpdateSerializer
        return FinancialRecordSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), CanViewRecords()]
        return [IsAuthenticated(), CanModifyRecords()]

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve records',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)

            if not serializer.is_valid():
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            record = serializer.save()
            response_data = FinancialRecordSerializer(record).data

            return Response({
                'message': 'Financial record created successfully',
                'record': response_data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': 'Failed to create financial record',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return Response({
                'error': 'Record not found',
                'details': 'The financial record you requested does not exist or you do not have permission to access it.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve record',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)

            if not serializer.is_valid():
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            self.perform_update(serializer)
            response_data = FinancialRecordSerializer(instance).data

            return Response({
                'message': 'Financial record updated successfully',
                'record': response_data
            }, status=status.HTTP_200_OK)

        except Http404:
            return Response({
                'error': 'Record not found',
                'details': 'The financial record you requested does not exist or you do not have permission to update it.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': 'Failed to update record',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            record_id = instance.id
            self.perform_destroy(instance)

            return Response({
                'message': 'Financial record deleted successfully',
                'record_id': record_id
            }, status=status.HTTP_200_OK)

        except Http404:
            return Response({
                'error': 'Record not found',
                'details': 'The financial record you requested does not exist or you do not have permission to delete it.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': 'Failed to delete record',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardSummaryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, CanAccessDashboard]
    
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            records = FinancialRecord.objects.filter(user=user)
            
            if not records.exists():
                return Response({
                    'message': 'No financial records found',
                    'summary': {
                        'total_income': Decimal('0.00'),
                        'total_income_formatted': 'Rs 0.00',
                        'total_expenses': Decimal('0.00'),
                        'total_expenses_formatted': 'Rs 0.00',
                        'net_balance': Decimal('0.00'),
                        'net_balance_formatted': 'Rs 0.00',
                    }
                }, status=status.HTTP_200_OK)
            
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
        
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve financial summary',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryTotalsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, CanAccessDashboard]
    
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            records = FinancialRecord.objects.filter(user=user)
            
            record_type = request.query_params.get('type')
            if record_type:
                if record_type not in ['income', 'expense']:
                    return Response({
                        'error': 'Invalid type parameter',
                        'details': f"Type must be 'income' or 'expense', got '{record_type}'."
                    }, status=status.HTTP_400_BAD_REQUEST)
                records = records.filter(type=record_type)
            
            if not records.exists():
                return Response({
                    'message': 'No records found for the specified criteria',
                    'categories': []
                }, status=status.HTTP_200_OK)
            
            category_data = records.values('category').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')
            
            serializer = CategoryTotalSerializer(category_data, many=True)
            
            return Response({
                'message': 'Category totals retrieved successfully',
                'categories': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve category totals',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MonthlyTrendsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, CanAccessDashboard]
    
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            
            today = datetime.now().date()
            twelve_months_ago = today - timedelta(days=365)
            
            records = FinancialRecord.objects.filter(
                user=user,
                date__gte=twelve_months_ago
            )
            
            if not records.exists():
                return Response({
                    'message': 'No records found for the past 12 months',
                    'trends': []
                }, status=status.HTTP_200_OK)
            
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
        
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve monthly trends',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecentActivityView(generics.ListAPIView):
    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAuthenticated, CanAccessDashboard]
    pagination_class = None
    
    def get_queryset(self):
        return FinancialRecord.objects.filter(
            user=self.request.user
        ).order_by('-date', '-created_at')[:10]
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            
            if not queryset.exists():
                return Response({
                    'message': 'No recent activity found',
                    'recent_transactions': []
                }, status=status.HTTP_200_OK)
            
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'message': 'Recent activity retrieved successfully',
                'recent_transactions': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve recent activity',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
