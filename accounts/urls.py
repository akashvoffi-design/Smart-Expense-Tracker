"""
accounts/urls.py

URL routes for authentication and the landing page.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Landing page – redirects to dashboard if logged in
    path('', views.landing, name='landing'),
    # Signup
    path('signup/', views.signup_view, name='signup'),
    # Login
    path('login/', views.login_view, name='login'),
    # Logout (POST only for CSRF safety)
    path('logout/', views.logout_view, name='logout'),
]
