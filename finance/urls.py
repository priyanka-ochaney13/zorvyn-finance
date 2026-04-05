from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FinancialRecordViewSet,
    DashboardSummaryView,
    CategoryTotalsView,
    MonthlyTrendsView,
    RecentActivityView,
)

router = DefaultRouter()
router.register(r'records', FinancialRecordViewSet, basename='record')

urlpatterns = [
    # ============== RESTful CRUD Endpoints via Router ==============
    path('', include(router.urls)),
    
    # ============== Dashboard Endpoints ==============
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/categories/', CategoryTotalsView.as_view(), name='dashboard-categories'),
    path('dashboard/trends/', MonthlyTrendsView.as_view(), name='dashboard-trends'),
    path('dashboard/recent/', RecentActivityView.as_view(), name='dashboard-recent'),
]
