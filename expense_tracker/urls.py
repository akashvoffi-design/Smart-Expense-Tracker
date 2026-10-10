"""
URL configuration for expense_tracker project.

Routes are grouped:
  / and /login/, /signup/, /logout/ - auth and landing
  /dashboard/, /expenses/ - core expense views
  /reports/ - export and analytics
  /api/ - JSON endpoints for live category prediction and chart data
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Accounts app handles landing, signup, login, logout
    path('', include('accounts.urls')),
    # Expenses app handles CRUD, dashboard, reports, and API
    path('', include('expenses.urls')),
]
