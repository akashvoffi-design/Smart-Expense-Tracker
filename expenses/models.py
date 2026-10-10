"""
expenses/models.py

Two models:
  Category — seed data for expense categories with chart colors
  Expense   — the core record, always tied to a User
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """
    Expense category (e.g. Food, Travel, Bills).
    color is a hex string used for Chart.js slices and category chips.
    """
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(
        max_length=7,
        default='#B3001B',
        help_text='Hex color code, e.g. #B3001B',
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    """
    A single spending record.
    Always scoped to a User — views must filter by request.user.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expenses',
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Must be greater than 0',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
    )
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Show the most recent expenses first
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.description} — ₹{self.amount} ({self.date})'
