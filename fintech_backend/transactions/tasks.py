"""
Celery tasks for the transactions app.
"""
from celery import shared_task
from django.utils import timezone
from .services import RecurringTransactionService
from .models import Transaction


@shared_task
def process_recurring_transactions():
    """
    Celery task to process due recurring transactions.
    This task should be scheduled to run daily.
    """
    results = RecurringTransactionService.process_due_recurring_transactions()
    
    return {
        'task': 'process_recurring_transactions',
        'timestamp': timezone.now().isoformat(),
        'results': results
    }


@shared_task
def cleanup_old_transaction_logs():
    """
    Celery task to cleanup old transaction logs.
    Keeps logs for the last 90 days.
    """
    from datetime import timedelta
    from .models import TransactionLog
    
    cutoff_date = timezone.now() - timedelta(days=90)
    deleted_count = TransactionLog.objects.filter(
        created_at__lt=cutoff_date
    ).delete()[0]
    
    return {
        'task': 'cleanup_old_transaction_logs',
        'timestamp': timezone.now().isoformat(),
        'deleted_logs': deleted_count
    }


@shared_task
def update_failed_transactions():
    """
    Celery task to retry failed transactions or mark them as permanently failed.
    """
    from datetime import timedelta
    
    # Get failed transactions from the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    failed_transactions = Transaction.objects.filter(
        status='failed',
        created_at__gte=one_hour_ago,
        failure_reason__icontains='temporary'  # Only retry temporary failures
    )
    
    retry_count = 0
    for transaction in failed_transactions:
        # Attempt to reprocess
        from .services import TransactionService
        if TransactionService.process_transaction(transaction):
            retry_count += 1
    
    return {
        'task': 'update_failed_transactions',
        'timestamp': timezone.now().isoformat(),
        'retried_transactions': retry_count,
        'total_failed': failed_transactions.count()
    }