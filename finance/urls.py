from django.urls import path
from .views import (
    # CRUD Views
    FinancialRecordListView,
    FinancialRecordCreateView,
    FinancialRecordDetailView,
    FinancialRecordUpdateView,
    FinancialRecordDeleteView,
    # Dashboard Views
    DashboardSummaryView,
    CategoryTotalsView,
    MonthlyTrendsView,
    RecentActivityView,
)

urlpatterns = [
    # ============== CRUD Endpoints ==============
    path('records/', FinancialRecordListView.as_view(), name='record-list'),
    path('records/create/', FinancialRecordCreateView.as_view(), name='record-create'),
    path('records/<int:pk>/', FinancialRecordDetailView.as_view(), name='record-detail'),
    path('records/<int:pk>/update/', FinancialRecordUpdateView.as_view(), name='record-update'),
    path('records/<int:pk>/delete/', FinancialRecordDeleteView.as_view(), name='record-delete'),
    
    # ============== Dashboard Endpoints ==============
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/categories/', CategoryTotalsView.as_view(), name='dashboard-categories'),
    path('dashboard/trends/', MonthlyTrendsView.as_view(), name='dashboard-trends'),
    path('dashboard/recent/', RecentActivityView.as_view(), name='dashboard-recent'),
]
