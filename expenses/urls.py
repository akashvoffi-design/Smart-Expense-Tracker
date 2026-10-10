"""
expenses/urls.py

URL routes for the expenses app, including API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    # ── Dashboard ──────────────────────────────────────────────────────────
    path('dashboard/', views.dashboard, name='dashboard'),

    # ── Expense CRUD ───────────────────────────────────────────────────────
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    # ── Reports & Exports ──────────────────────────────────────────────────
    path('reports/', views.reports, name='reports'),
    path('reports/export/csv/', views.export_csv, name='export_csv'),
    path('reports/export/pdf/', views.export_pdf, name='export_pdf'),

    # ── JSON API ───────────────────────────────────────────────────────────
    path('api/predict-category/', views.api_predict_category, name='api_predict_category'),
    path('api/chart-data/', views.api_chart_data, name='api_chart_data'),
]
