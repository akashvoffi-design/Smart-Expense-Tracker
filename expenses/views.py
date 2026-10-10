"""
expenses/views.py

All expense-related views. Every queryset is filtered by request.user
so users can never access each other's data.

Key helpers:
  get_period_dates(period)   → (start_date, end_date) for the filter
  build_chart_data(qs)       → dict ready for Chart.js JSON
"""
import csv
import json
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ExpenseForm
from .models import Category, Expense
from .utils import predict_category


# ─── Date helpers ─────────────────────────────────────────────────────────────

def get_period_dates(period: str):
    """
    Return (start_date, end_date) for the requested period.

    period values:
      'today'  → just today
      'week'   → Monday to Sunday of the current week
      'month'  → first to last day of the current month (default)
    """
    today = date.today()

    if period == 'today':
        return today, today

    elif period == 'week':
        # Monday of the current week
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end

    else:  # 'month' (default)
        start = today.replace(day=1)
        # Last day of the month: first day of next month minus one day
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return start, end


def get_greeting(username: str) -> str:
    """Return a time-appropriate greeting."""
    hour = timezone.localtime().hour
    if hour < 12:
        time_of_day = 'morning'
    elif hour < 17:
        time_of_day = 'afternoon'
    else:
        time_of_day = 'evening'
    return f'Good {time_of_day}, {username}'


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    """
    Main dashboard view.
    Shows aggregated stats, charts, and the recent expense list
    filtered by the selected period (today / week / month).
    """
    period = request.GET.get('period', 'month')
    start_date, end_date = get_period_dates(period)

    # Base queryset — ALWAYS scoped to the logged-in user
    qs = Expense.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date,
    ).select_related('category')

    # Aggregated stats
    total_amount = qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    transaction_count = qs.count()

    # Top category by total spend
    top_category_data = (
        qs.values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
        .first()
    )
    top_category = top_category_data['category__name'] if top_category_data else 'N/A'

    # Recent 10 expenses for the list section
    recent_expenses = qs[:10]

    # All categories for the filter dropdown (expense list page)
    categories = Category.objects.all()

    context = {
        'greeting': get_greeting(request.user.username),
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_amount': total_amount,
        'transaction_count': transaction_count,
        'top_category': top_category,
        'recent_expenses': recent_expenses,
        'categories': categories,
    }
    return render(request, 'expenses/dashboard.html', context)


# ─── Expense List ─────────────────────────────────────────────────────────────

@login_required
def expense_list(request):
    """
    Full paginated list of expenses with period and category filters.
    """
    period = request.GET.get('period', 'month')
    category_id = request.GET.get('category', '')
    start_date, end_date = get_period_dates(period)

    qs = Expense.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date,
    ).select_related('category')

    if category_id:
        qs = qs.filter(category_id=category_id)

    # Pagination — 20 per page
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_amount = qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'period': period,
        'category_id': category_id,
        'categories': categories,
        'total_amount': total_amount,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'expenses/expense_list.html', context)


# ─── Add Expense ──────────────────────────────────────────────────────────────

@login_required
def expense_add(request):
    """
    Add a new expense.
    On GET: empty form.
    On POST: validate, save, redirect to dashboard.
    """
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # enforce ownership
            expense.save()
            messages.success(
                request,
                f'Expense "{expense.description}" added successfully!'
            )
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ExpenseForm()

    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'form_title': 'Add Expense',
        'form_action': 'add',
    })


# ─── Edit Expense ─────────────────────────────────────────────────────────────

@login_required
def expense_edit(request, pk):
    """
    Edit an existing expense.
    get_object_or_404 with user filter prevents accessing other users' records.
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Expense "{expense.description}" updated successfully!'
            )
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'form_title': 'Edit Expense',
        'form_action': 'edit',
        'expense': expense,
    })


# ─── Delete Expense ───────────────────────────────────────────────────────────

@login_required
def expense_delete(request, pk):
    """
    Delete an expense — POST only for CSRF safety.
    Shows a confirmation page on GET.
    Ownership enforced by filtering on request.user.
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        desc = expense.description
        expense.delete()
        messages.success(request, f'"{desc}" has been deleted.')
        return redirect('expense_list')

    return render(request, 'expenses/expense_confirm_delete.html', {
        'expense': expense,
    })


# ─── Reports ──────────────────────────────────────────────────────────────────

@login_required
def reports(request):
    """
    Reports page with larger charts and export buttons.
    """
    period = request.GET.get('period', 'month')
    start_date, end_date = get_period_dates(period)

    qs = Expense.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date,
    ).select_related('category').order_by('date')

    total_amount = qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    transaction_count = qs.count()

    # Per-category breakdown
    category_breakdown = (
        qs.values('category__name', 'category__color')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )

    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_amount': total_amount,
        'transaction_count': transaction_count,
        'category_breakdown': category_breakdown,
        'expenses': qs,
    }
    return render(request, 'expenses/reports.html', context)


# ─── CSV Export ───────────────────────────────────────────────────────────────

@login_required
def export_csv(request):
    """
    Download expenses as a CSV file.
    Columns: Date, Description, Category, Amount, Notes
    """
    period = request.GET.get('period', 'month')
    start_date, end_date = get_period_dates(period)

    qs = Expense.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date,
    ).select_related('category').order_by('date')

    # Set up the HTTP response as a CSV attachment
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="expenses_{period}_{date.today()}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(['Date', 'Description', 'Category', 'Amount (INR)', 'Notes'])

    for expense in qs:
        writer.writerow([
            expense.date.strftime('%d %b %Y'),
            expense.description,
            expense.category.name if expense.category else 'Uncategorized',
            expense.amount,
            expense.notes,
        ])

    # Summary row at the bottom
    total = qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    writer.writerow([])
    writer.writerow(['', '', 'TOTAL', total, ''])

    return response


# ─── PDF Export ───────────────────────────────────────────────────────────────

@login_required
def export_pdf(request):
    """
    Generate and download a branded PDF expense report using ReportLab.
    Header in red/white, table with alternating rows, total at the bottom.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    )
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT

    period = request.GET.get('period', 'month')
    start_date, end_date = get_period_dates(period)

    qs = Expense.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date,
    ).select_related('category').order_by('date')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="expense_report_{period}_{date.today()}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    # Branded red colour
    MAISON_RED = colors.HexColor('#B3001B')
    DEEP_RED = colors.HexColor('#7A0012')
    SOFT_GRAY = colors.HexColor('#FAF8F7')

    styles = getSampleStyleSheet()
    story = []

    # ── Header ──
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        textColor=MAISON_RED,
        fontSize=22,
        spaceAfter=4,
        fontName='Helvetica-Bold',
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        textColor=colors.HexColor('#6B6B6B'),
        fontSize=10,
        spaceAfter=16,
    )

    story.append(Paragraph('Smart Expense Tracker', title_style))
    story.append(Paragraph('Spend smart. Live well.', subtitle_style))
    story.append(Paragraph(
        f'Report for: <b>{request.user.username}</b> &nbsp;|&nbsp; '
        f'Period: <b>{start_date.strftime("%d %b %Y")}</b> to <b>{end_date.strftime("%d %b %Y")}</b>',
        subtitle_style,
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ── Table ──
    headers = ['Date', 'Description', 'Category', 'Amount (INR)', 'Notes']
    data = [headers]

    for expense in qs:
        data.append([
            expense.date.strftime('%d %b %Y'),
            expense.description[:40],
            expense.category.name if expense.category else '—',
            f'Rs. {expense.amount:,.2f}',
            expense.notes[:30] if expense.notes else '',
        ])

    # Total row
    total = qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    data.append(['', '', 'TOTAL', f'Rs. {total:,.2f}', ''])

    col_widths = [2.8 * cm, 5.5 * cm, 3 * cm, 3.2 * cm, 3.3 * cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    table_style = TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), MAISON_RED),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        # Body rows
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, SOFT_GRAY]),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ('TOPPADDING', (0, 1), (-1, -2), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 5),
        # Total row
        ('BACKGROUND', (0, -1), (-1, -1), DEEP_RED),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 9),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, MAISON_RED),
    ])
    table.setStyle(table_style)
    story.append(table)

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        f'Generated on {date.today().strftime("%d %B %Y")} | Smart Expense Tracker',
        ParagraphStyle('footer', parent=styles['Normal'],
                       textColor=colors.HexColor('#6B6B6B'), fontSize=7, alignment=TA_CENTER),
    ))

    doc.build(story)
    return response


# ─── API: Category Prediction ─────────────────────────────────────────────────

def api_predict_category(request):
    """
    GET /api/predict-category/?q=<text>
    Returns JSON: {"category": "Food"}
    Used by the Add Expense form to suggest a category as the user types.
    No login required — it's read-only and stateless.
    """
    q = request.GET.get('q', '')
    predicted = predict_category(q)
    return JsonResponse({'category': predicted})


# ─── API: Chart Data ─────────────────────────────────────────────────────────

@login_required
def api_chart_data(request):
    """
    GET /api/chart-data/?period=today|week|month
    Returns JSON with two chart datasets and live aggregated statistics.
    """
    from django.urls import reverse

    period = request.GET.get('period', 'month')
    start_date, end_date = get_period_dates(period)

    qs = Expense.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date,
    ).select_related('category')

    # Aggregated stats
    total_amount = qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    transaction_count = qs.count()

    top_category_data = (
        qs.values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
        .first()
    )
    top_category = top_category_data['category__name'] if top_category_data else 'N/A'

    # ── Doughnut chart: per-category totals ──
    category_totals = (
        qs.values('category__name', 'category__color')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )

    doughnut_labels = []
    doughnut_data = []
    doughnut_colors = []
    category_breakdown = []

    FALLBACK_COLORS = [
        '#B3001B', '#E63946', '#7A0012', '#FF6B6B', '#FF8E8E',
        '#C62828', '#D32F2F', '#EF5350', '#F44336', '#FFCDD2',
    ]

    for i, row in enumerate(category_totals):
        cname = row['category__name'] or 'Uncategorized'
        amt = float(row['total'])
        color = row.get('category__color') or FALLBACK_COLORS[i % len(FALLBACK_COLORS)]
        doughnut_labels.append(cname)
        doughnut_data.append(amt)
        doughnut_colors.append(color)

        pct = round((amt / float(total_amount) * 100), 1) if total_amount > 0 else 0
        category_breakdown.append({
            'name': cname,
            'color': color,
            'total': amt,
            'count': row['count'],
            'percentage': pct,
        })

    # ── Time-series chart: daily totals ──
    # Expense.date is already a DateField, so we group directly on 'date'
    daily_totals = (
        qs.values('date')
        .annotate(total=Sum('amount'))
        .order_by('date')
    )

    timeseries_labels = []
    timeseries_data = []
    for row in daily_totals:
        timeseries_labels.append(row['date'].strftime('%d %b'))
        timeseries_data.append(float(row['total']))

    # Recent expenses for live dashboard updates
    recent_list = []
    for e in qs.order_by('-date', '-created_at')[:10]:
        recent_list.append({
            'id': e.id,
            'description': e.description,
            'amount': float(e.amount),
            'date': e.date.strftime('%d %b %Y'),
            'category_name': e.category.name if e.category else None,
            'category_color': e.category.color if e.category else '#B3001B',
            'edit_url': reverse('expense_edit', args=[e.id]),
            'delete_url': reverse('expense_delete', args=[e.id]),
        })

    # All expenses for reports table updates
    all_expenses_list = []
    for e in qs.order_by('date'):
        all_expenses_list.append({
            'id': e.id,
            'description': e.description,
            'amount': float(e.amount),
            'date': e.date.strftime('%d %b %Y'),
            'category_name': e.category.name if e.category else None,
            'category_color': e.category.color if e.category else '#B3001B',
        })

    period_display = 'Today' if period == 'today' else ('This Week' if period == 'week' else 'This Month')
    if period == 'today':
        period_sub = f"Today · {start_date.strftime('%d %b %Y')}"
    elif period == 'week':
        period_sub = f"This Week · {start_date.strftime('%d %b')} – {end_date.strftime('%d %b %Y')}"
    else:
        period_sub = f"This Month · {start_date.strftime('%B %Y')}"

    return JsonResponse({
        'period': period,
        'period_display': period_display,
        'period_sub': period_sub,
        'start_date_str': start_date.strftime('%d %b %Y'),
        'end_date_str': end_date.strftime('%d %b %Y'),
        'total_amount': float(total_amount),
        'transaction_count': transaction_count,
        'top_category': top_category,
        'doughnut': {
            'labels': doughnut_labels,
            'data': doughnut_data,
            'colors': doughnut_colors,
        },
        'timeseries': {
            'labels': timeseries_labels,
            'data': timeseries_data,
        },
        'category_breakdown': category_breakdown,
        'recent_expenses': recent_list,
        'all_expenses': all_expenses_list,
        'total': float(total_amount),
    })
