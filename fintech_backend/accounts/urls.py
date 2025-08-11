"""
URL configuration for accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Accounts
    path('accounts/', views.AccountListView.as_view(), name='account-list'),
    path('accounts/<uuid:pk>/', views.AccountDetailView.as_view(), name='account-detail'),
    path('accounts/<uuid:account_id>/balance/', views.account_balance_view, name='account-balance'),
]