"""
Transaction models for the fintech application.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import TimeStampedModel
from core.utils import generate_transaction_reference
from accounts.models import Account


class Transaction(TimeStampedModel):
    """
    Main transaction model for all financial operations.
    """
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    TRANSACTION_CATEGORIES = [
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('shopping', 'Shopping'),
        ('bills', 'Bills'),
        ('income', 'Income'),
        ('investment', 'Investment'),
        ('other', 'Other'),
    ]

    # Core transaction fields
    reference = models.CharField(max_length=20, unique=True, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='pending')
    
    # Transaction details
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=TRANSACTION_CATEGORIES)
    
    # Related transaction info
    recipient_account_number = models.CharField(max_length=20, blank=True)
    recipient_name = models.CharField(max_length=100, blank=True)
    
    # Fees and charges
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Processing information
    processed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    
    # External reference (for third-party integrations)
    external_reference = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'transactions_transaction'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account', '-created_at']),
            models.Index(fields=['reference']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_type']),
        ]

    def __str__(self):
        return f"{self.reference} - {self.transaction_type.title()} ${self.amount}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_transaction_reference()
        super().save(*args, **kwargs)

    @property
    def net_amount(self):
        """Calculate net amount including fees."""
        if self.transaction_type == 'debit':
            return self.amount + self.fee_amount
        return self.amount - self.fee_amount

    def can_cancel(self):
        """Check if transaction can be cancelled."""
        return self.status in ['pending', 'processing']

    def cancel(self, reason="Cancelled by user"):
        """Cancel the transaction."""
        if self.can_cancel():
            self.status = 'cancelled'
            self.failure_reason = reason
            self.save()
            return True
        return False


class TransactionLog(TimeStampedModel):
    """
    Log model to track transaction status changes and processing steps.
    """
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='logs')
    previous_status = models.CharField(max_length=10, blank=True)
    new_status = models.CharField(max_length=10)
    message = models.TextField()
    processed_by = models.CharField(max_length=100, blank=True)  # System or user identifier
    
    class Meta:
        db_table = 'transactions_log'
        verbose_name = 'Transaction Log'
        verbose_name_plural = 'Transaction Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction.reference} - {self.new_status}"


class RecurringTransaction(TimeStampedModel):
    """
    Model for recurring transactions like subscriptions or scheduled payments.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='recurring_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Transaction.TRANSACTION_CATEGORIES)
    recipient_account_number = models.CharField(max_length=20, blank=True)
    recipient_name = models.CharField(max_length=100, blank=True)
    
    # Scheduling
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_execution_date = models.DateField()
    
    # Status and tracking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    execution_count = models.PositiveIntegerField(default=0)
    max_executions = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'transactions_recurring'
        verbose_name = 'Recurring Transaction'
        verbose_name_plural = 'Recurring Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Recurring: {self.description} - ${self.amount} {self.frequency}"

    def can_execute(self):
        """Check if recurring transaction can be executed."""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.status != 'active':
            return False
        
        if self.next_execution_date > today:
            return False
            
        if self.max_executions and self.execution_count >= self.max_executions:
            return False
            
        if self.end_date and today > self.end_date:
            return False
            
        return True

    def calculate_next_execution_date(self):
        """Calculate the next execution date based on frequency."""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        current_date = self.next_execution_date
        
        if self.frequency == 'daily':
            return current_date + timedelta(days=1)
        elif self.frequency == 'weekly':
            return current_date + timedelta(weeks=1)
        elif self.frequency == 'monthly':
            return current_date + relativedelta(months=1)
        elif self.frequency == 'quarterly':
            return current_date + relativedelta(months=3)
        elif self.frequency == 'yearly':
            return current_date + relativedelta(years=1)
        
        return current_date