"""
URL configuration for transactions app.
"""
from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction-create'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/<uuid:transaction_id>/cancel/', views.cancel_transaction, name='transaction-cancel'),
    path('transactions/<uuid:transaction_id>/logs/', views.TransactionLogListView.as_view(), name='transaction-logs'),
    
    # Statistics
    path('transactions/statistics/', views.transaction_statistics, name='transaction-statistics'),
    
    # Recurring Transactions
    path('recurring-transactions/', views.RecurringTransactionListView.as_view(), name='recurring-transaction-list'),
    path('recurring-transactions/<uuid:pk>/', views.RecurringTransactionDetailView.as_view(), name='recurring-transaction-detail'),
]