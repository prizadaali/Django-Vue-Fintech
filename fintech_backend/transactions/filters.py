"""
Filters for the transactions app.
"""
import django_filters
from django.db import models
from .models import Transaction


class TransactionFilter(django_filters.FilterSet):
    """Filter for transaction queries."""
    
    # Date range filters
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Amount range filters
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    # Status filter (multiple selection)
    status = django_filters.MultipleChoiceFilter(
        choices=Transaction.TRANSACTION_STATUS,
        widget=django_filters.widgets.CSVWidget
    )
    
    # Transaction type filter
    transaction_type = django_filters.ChoiceFilter(choices=Transaction.TRANSACTION_TYPES)
    
    # Category filter (multiple selection)
    category = django_filters.MultipleChoiceFilter(
        choices=Transaction.TRANSACTION_CATEGORIES,
        widget=django_filters.widgets.CSVWidget
    )
    
    # Text search in description and recipient name
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Transaction
        fields = {
            'created_at': ['exact', 'gte', 'lte'],
            'amount': ['exact', 'gte', 'lte'],
            'status': ['exact'],
            'transaction_type': ['exact'],
            'category': ['exact'],
        }

    def filter_search(self, queryset, name, value):
        """Custom search filter for description and recipient name."""
        return queryset.filter(
            models.Q(description__icontains=value) |
            models.Q(recipient_name__icontains=value) |
            models.Q(reference__icontains=value)
        )