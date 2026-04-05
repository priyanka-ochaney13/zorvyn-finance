import django_filters
from .models import FinancialRecord


class FinancialRecordFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        help_text='Filter records from this date (inclusive)'
    )
    date_to = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        help_text='Filter records up to this date (inclusive)'
    )
    
    type = django_filters.ChoiceFilter(choices=FinancialRecord.TYPE_CHOICES)
    category = django_filters.ChoiceFilter(choices=FinancialRecord.CATEGORY_CHOICES)
    
    class Meta:
        model = FinancialRecord
        fields = ['type', 'category', 'date_from', 'date_to']
