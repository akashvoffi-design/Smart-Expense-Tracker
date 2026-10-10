"""
accounts/views.py

Handles landing page, signup, login, and logout.
Uses Django's built-in auth system throughout.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, LoginForm


def landing(request):
    """
    Landing / Welcome page.
    Redirects authenticated users straight to the dashboard
    so they never see the marketing page when logged in.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/landing.html')


def signup_view(request):
    """
    Signup view.
    On success: creates the user, logs them in, and redirects to the dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log the user in after signup
            login(request, user)
            messages.success(request, f'Welcome to Maison Rouge, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """
    Login view.
    Uses Django's AuthenticationForm for secure credential handling.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Respect ?next= redirect param if present
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Logout view.
    Only accepts POST to prevent CSRF logout attacks.
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been signed out successfully.')
    return redirect('landing')
