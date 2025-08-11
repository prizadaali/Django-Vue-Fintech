"""
Admin configuration for transactions app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction, TransactionLog, RecurringTransaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction model."""
    list_display = [
        'reference', 'account_user', 'amount', 'transaction_type', 
        'status', 'category', 'created_at', 'status_badge'
    ]
    list_filter = [
        'transaction_type', 'status', 'category', 'created_at',
        'account__account_type'
    ]
    search_fields = [
        'reference', 'description', 'recipient_name', 
        'account__user__email', 'account__account_number'
    ]
    readonly_fields = [
        'reference', 'created_at', 'updated_at', 'processed_at'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'reference', 'account', 'amount', 'transaction_type', 
                'status', 'description', 'category'
            )
        }),
        ('Recipient Information', {
            'fields': ('recipient_account_number', 'recipient_name'),
            'classes': ('collapse',)
        }),
        ('Financial Details', {
            'fields': ('fee_amount', 'external_reference')
        }),
        ('Processing Information', {
            'fields': ('processed_at', 'failure_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def account_user(self, obj):
        """Display account user email."""
        return obj.account.user.email
    account_user.short_description = 'User'
    account_user.admin_order_field = 'account__user__email'
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    """Admin interface for TransactionLog model."""
    list_display = [
        'transaction_reference', 'previous_status', 'new_status', 
        'processed_by', 'created_at'
    ]
    list_filter = ['new_status', 'previous_status', 'created_at']
    search_fields = [
        'transaction__reference', 'message', 'processed_by'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def transaction_reference(self, obj):
        """Display transaction reference."""
        return obj.transaction.reference
    transaction_reference.short_description = 'Transaction'
    transaction_reference.admin_order_field = 'transaction__reference'


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    """Admin interface for RecurringTransaction model."""
    list_display = [
        'description', 'account_user', 'amount', 'frequency', 
        'status', 'next_execution_date', 'execution_count'
    ]
    list_filter = [
        'frequency', 'status', 'category', 'created_at'
    ]
    search_fields = [
        'description', 'account__user__email', 'recipient_name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'execution_count']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'account', 'amount', 'description', 'category'
            )
        }),
        ('Recipient Information', {
            'fields': ('recipient_account_number', 'recipient_name')
        }),
        ('Scheduling', {
            'fields': (
                'frequency', 'start_date', 'end_date', 
                'next_execution_date', 'max_executions'
            )
        }),
        ('Status & Tracking', {
            'fields': ('status', 'execution_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def account_user(self, obj):
        """Display account user email."""
        return obj.account.user.email
    account_user.short_description = 'User'
    account_user.admin_order_field = 'account__user__email'