"""
expenses/tests.py

Unit tests covering:
  1. Category prediction (predict_category utility)
  2. Data isolation — User A cannot see User B's expenses
  3. Period filters (today / week / month)
  4. Basic CRUD access control
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from .models import Category, Expense
from .utils import predict_category
from .views import get_period_dates


# ─── 1. Category Prediction Tests ─────────────────────────────────────────────

class CategoryPredictionTests(TestCase):
    """Tests for the keyword-based predict_category() function."""

    def test_food_keywords(self):
        self.assertEqual(predict_category('pizza slice from zomato'), 'Food')
        self.assertEqual(predict_category('lunch at a restaurant'), 'Food')
        self.assertEqual(predict_category('morning coffee'), 'Food')
        self.assertEqual(predict_category('biryani for dinner'), 'Food')

    def test_travel_keywords(self):
        self.assertEqual(predict_category('uber ride to office'), 'Travel')
        self.assertEqual(predict_category('metro card recharge'), 'Travel')
        self.assertEqual(predict_category('petrol for car'), 'Travel')
        self.assertEqual(predict_category('flight ticket Mumbai'), 'Travel')

    def test_shopping_keywords(self):
        self.assertEqual(predict_category('amazon order headphones'), 'Shopping')
        self.assertEqual(predict_category('new shoes from mall'), 'Shopping')
        self.assertEqual(predict_category('flipkart delivery'), 'Shopping')

    def test_bills_keywords(self):
        self.assertEqual(predict_category('electricity bill payment'), 'Bills')
        self.assertEqual(predict_category('wifi recharge'), 'Bills')
        self.assertEqual(predict_category('monthly rent'), 'Bills')

    def test_entertainment_keywords(self):
        self.assertEqual(predict_category('netflix subscription'), 'Entertainment')
        self.assertEqual(predict_category('movie tickets'), 'Entertainment')
        self.assertEqual(predict_category('spotify premium'), 'Entertainment')

    def test_health_keywords(self):
        self.assertEqual(predict_category('doctor visit'), 'Health')
        self.assertEqual(predict_category('pharmacy medicine'), 'Health')
        self.assertEqual(predict_category('gym membership'), 'Health')

    def test_education_keywords(self):
        self.assertEqual(predict_category('udemy course python'), 'Education')
        self.assertEqual(predict_category('exam fees'), 'Education')
        self.assertEqual(predict_category('tuition payment'), 'Education')

    def test_groceries_keywords(self):
        self.assertEqual(predict_category('vegetables from dmart'), 'Groceries')
        self.assertEqual(predict_category('milk and fruits'), 'Groceries')
        self.assertEqual(predict_category('bigbasket delivery'), 'Groceries')

    def test_fallback_to_others(self):
        self.assertEqual(predict_category('random purchase xyz'), 'Others')
        self.assertEqual(predict_category(''), 'Others')
        self.assertEqual(predict_category('   '), 'Others')

    def test_case_insensitive(self):
        self.assertEqual(predict_category('PIZZA order'), 'Food')
        self.assertEqual(predict_category('UBER Ride'), 'Travel')


# ─── 2. Data Isolation Tests ───────────────────────────────────────────────────

class DataIsolationTests(TestCase):
    """Ensure User A cannot view or modify User B's expenses."""

    def setUp(self):
        # Create two users and seed a category
        self.user_a = User.objects.create_user('alice', password='alice_pass')
        self.user_b = User.objects.create_user('bob',   password='bob_pass')
        # Use get_or_create since the seed migration already runs in the test DB
        self.category, _ = Category.objects.get_or_create(name='Food', defaults={'color': '#E63946'})

        # User A expense
        self.expense_a = Expense.objects.create(
            user=self.user_a,
            description='Alice lunch',
            amount=Decimal('120.00'),
            category=self.category,
            date=date.today(),
        )
        # User B expense
        self.expense_b = Expense.objects.create(
            user=self.user_b,
            description='Bob coffee',
            amount=Decimal('80.00'),
            category=self.category,
            date=date.today(),
        )

        self.client_a = Client()
        self.client_b = Client()
        self.client_a.login(username='alice', password='alice_pass')
        self.client_b.login(username='bob',   password='bob_pass')

    def test_dashboard_shows_only_own_expenses(self):
        """Dashboard should only show Alice's expenses to Alice."""
        response = self.client_a.get(reverse('dashboard') + '?period=today')
        self.assertEqual(response.status_code, 200)
        # Alice's expense appears
        self.assertContains(response, 'Alice lunch')
        # Bob's expense does NOT appear
        self.assertNotContains(response, 'Bob coffee')

    def test_user_a_cannot_edit_user_b_expense(self):
        """Alice trying to edit Bob's expense should get 404."""
        response = self.client_a.get(
            reverse('expense_edit', args=[self.expense_b.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_user_a_cannot_delete_user_b_expense(self):
        """Alice trying to delete Bob's expense should get 404."""
        response = self.client_a.post(
            reverse('expense_delete', args=[self.expense_b.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_expense_list_only_shows_own_expenses(self):
        """Expense list must be scoped to the logged-in user."""
        response = self.client_a.get(reverse('expense_list') + '?period=today')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice lunch')
        self.assertNotContains(response, 'Bob coffee')


# ─── 3. Period Filter Tests ────────────────────────────────────────────────────

class PeriodFilterTests(TestCase):
    """Test the get_period_dates() helper for correctness."""

    def test_today_period(self):
        start, end = get_period_dates('today')
        today = date.today()
        self.assertEqual(start, today)
        self.assertEqual(end, today)

    def test_week_period_starts_on_monday(self):
        start, end = get_period_dates('week')
        today = date.today()
        # Start must be the Monday of the current week
        self.assertEqual(start.weekday(), 0)
        # End must be Sunday (start + 6 days)
        self.assertEqual((end - start).days, 6)
        # Today must be between start and end
        self.assertGreaterEqual(today, start)
        self.assertLessEqual(today, end)

    def test_month_period_starts_on_first(self):
        start, end = get_period_dates('month')
        today = date.today()
        self.assertEqual(start.day, 1)
        self.assertEqual(start.month, today.month)
        self.assertEqual(start.year, today.year)
        # End must be >= start
        self.assertGreaterEqual(end, start)

    def test_unknown_period_defaults_to_month(self):
        start, end = get_period_dates('invalid_value')
        today = date.today()
        self.assertEqual(start.day, 1)
        self.assertEqual(start.month, today.month)


# ─── 4. CRUD View Tests ───────────────────────────────────────────────────────

class ExpenseCRUDTests(TestCase):
    """Basic view access and redirect tests."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='testpass')
        # Use get_or_create since seed migration already ran
        self.category, _ = Category.objects.get_or_create(name='Food', defaults={'color': '#E63946'})
        self.client = Client()

    def test_unauthenticated_redirect_dashboard(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/dashboard/')

    def test_unauthenticated_redirect_add(self):
        response = self.client.get(reverse('expense_add'))
        self.assertRedirects(response, '/login/?next=/expenses/add/')

    def test_add_expense_creates_record(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('expense_add'), {
            'description': 'Test pizza lunch',
            'amount': '250.00',
            'category': self.category.pk,
            'date': date.today().strftime('%Y-%m-%d'),
            'notes': '',
        })
        # Should redirect to dashboard on success
        self.assertRedirects(response, reverse('dashboard'))
        # Expense should exist in the DB
        self.assertTrue(
            Expense.objects.filter(user=self.user, description='Test pizza lunch').exists()
        )

    def test_add_expense_negative_amount_rejected(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('expense_add'), {
            'description': 'Bad amount',
            'amount': '-50.00',
            'category': self.category.pk,
            'date': date.today().strftime('%Y-%m-%d'),
            'notes': '',
        })
        # Should re-render the form (200) not redirect
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Expense.objects.filter(description='Bad amount').exists()
        )

    def test_predict_category_api(self):
        """The prediction endpoint should return JSON without login."""
        response = self.client.get(reverse('api_predict_category') + '?q=pizza')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['category'], 'Food')
