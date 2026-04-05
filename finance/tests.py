from decimal import Decimal
from datetime import date
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from finance.models import FinancialRecord


class ViewerPermissionTests(APITestCase):
    """Tests for viewer role permission enforcement."""

    def setUp(self):
        self.viewer = User.objects.create_user(
            username='viewer_user',
            password='testpass123',
            role='viewer'
        )
        self.client.force_authenticate(user=self.viewer)

    def test_viewer_cannot_create_record(self):
        """Viewer attempting to create a financial record should receive 403."""
        url = reverse('record-list')
        data = {
            'type': 'expense',
            'category': 'food',
            'amount': '100.00',
            'date': str(date.today()),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_update_record(self):
        """Viewer attempting to update a record should receive 403."""
        analyst = User.objects.create_user(
            username='analyst_user',
            password='testpass123',
            role='analyst'
        )
        record = FinancialRecord.objects.create(
            user=analyst,
            type='expense',
            category='food',
            amount=Decimal('100.00'),
            date=date.today(),
        )
        url = reverse('record-detail', kwargs={'pk': record.pk})
        data = {'amount': '200.00'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_delete_record(self):
        """Viewer attempting to delete a record should receive 403."""
        analyst = User.objects.create_user(
            username='analyst_user2',
            password='testpass123',
            role='analyst'
        )
        record = FinancialRecord.objects.create(
            user=analyst,
            type='expense',
            category='food',
            amount=Decimal('100.00'),
            date=date.today(),
        )
        url = reverse('record-detail', kwargs={'pk': record.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ValidationTests(APITestCase):
    """Tests for field validation on record creation."""

    def setUp(self):
        self.analyst = User.objects.create_user(
            username='analyst_user',
            password='testpass123',
            role='analyst'
        )
        self.client.force_authenticate(user=self.analyst)

    def test_missing_amount_returns_400(self):
        """Submitting a record with missing amount should return 400 with error."""
        url = reverse('record-list')
        data = {
            'type': 'expense',
            'category': 'food',
            'date': str(date.today()),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('details', response.data)

    def test_missing_category_returns_400(self):
        """Submitting a record with missing category should return 400 with error."""
        url = reverse('record-list')
        data = {
            'type': 'expense',
            'amount': '100.00',
            'date': str(date.today()),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('details', response.data)

    def test_negative_amount_returns_400(self):
        """Submitting a record with negative amount should return 400 with error."""
        url = reverse('record-list')
        data = {
            'type': 'expense',
            'category': 'food',
            'amount': '-50.00',
            'date': str(date.today()),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('details', response.data)


class DashboardSummaryTests(APITestCase):
    """Tests for dashboard summary endpoint aggregation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='testpass123',
            role='analyst'
        )
        self.client.force_authenticate(user=self.user)

    def test_dashboard_summary_returns_correct_totals(self):
        """Dashboard summary should return correct aggregated totals for known seeded data."""
        FinancialRecord.objects.create(
            user=self.user,
            type='income',
            category='salary',
            amount=Decimal('5000.00'),
            date=date.today(),
        )
        FinancialRecord.objects.create(
            user=self.user,
            type='income',
            category='investment',
            amount=Decimal('1500.00'),
            date=date.today(),
        )
        FinancialRecord.objects.create(
            user=self.user,
            type='expense',
            category='food',
            amount=Decimal('800.00'),
            date=date.today(),
        )
        FinancialRecord.objects.create(
            user=self.user,
            type='expense',
            category='transport',
            amount=Decimal('200.00'),
            date=date.today(),
        )

        url = reverse('dashboard-summary')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        summary = response.data['summary']
        self.assertEqual(Decimal(summary['total_income']), Decimal('6500.00'))
        self.assertEqual(Decimal(summary['total_expenses']), Decimal('1000.00'))
        self.assertEqual(Decimal(summary['net_balance']), Decimal('5500.00'))
