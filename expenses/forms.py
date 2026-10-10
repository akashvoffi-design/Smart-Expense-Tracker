"""
expenses/forms.py

ExpenseForm — used for both Add and Edit views.
Validates that amount > 0 and applies luxury CSS styling.
"""
from django import forms
from django.utils import timezone
from .models import Expense, Category


class ExpenseForm(forms.ModelForm):
    """
    Form for creating and editing expenses.
    - Applies luxury glass-input styling.
    - Validates that amount is positive.
    - Date defaults to today.
    """

    class Meta:
        model = Expense
        fields = ['description', 'amount', 'category', 'date', 'notes']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': ' ',
                'id': 'id_description',
                'autocomplete': 'off',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': ' ',
                'id': 'id_amount',
                'min': '0.01',
                'step': '0.01',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'id': 'id_date',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': ' ',
                'id': 'id_notes',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default the date field to today
        if not self.instance.pk:
            self.initial['date'] = timezone.now().date()
        # Make category optional from the form side too
        self.fields['category'].required = False
        self.fields['category'].empty_label = 'Select a category'

    def clean_amount(self):
        """Ensure the expense amount is strictly positive."""
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount
