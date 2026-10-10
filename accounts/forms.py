"""
accounts/forms.py

Custom signup form extending Django's built-in UserCreationForm.
Adds email field and friendly labels.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    """Extended signup form with email and custom styling attributes."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': ' ',
            'id': 'id_email',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply luxury input styling classes to all fields
        field_attrs = {
            'username': {'placeholder': ' ', 'id': 'id_username', 'class': 'form-input'},
            'password1': {'placeholder': ' ', 'id': 'id_password1', 'class': 'form-input'},
            'password2': {'placeholder': ' ', 'id': 'id_password2', 'class': 'form-input'},
        }
        for field_name, attrs in field_attrs.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update(attrs)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Custom login form with luxury input styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': ' ',
            'id': 'id_login_username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': ' ',
            'id': 'id_login_password',
        })
