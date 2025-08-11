"""
Signals for the transactions app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Transaction, TransactionLog


@receiver(pre_save, sender=Transaction)
def log_transaction_status_change(sender, instance, **kwargs):
    """Log transaction status changes."""
    if instance.pk:  # Only for existing transactions
        try:
            old_instance = Transaction.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Status changed, create log entry
                TransactionLog.objects.create(
                    transaction=instance,
                    previous_status=old_instance.status,
                    new_status=instance.status,
                    message=f"Status changed from {old_instance.status} to {instance.status}",
                    processed_by="system"
                )
        except Transaction.DoesNotExist:
            pass


@receiver(post_save, sender=Transaction)
def create_initial_transaction_log(sender, instance, created, **kwargs):
    """Create initial log entry for new transactions."""
    if created:
        TransactionLog.objects.create(
            transaction=instance,
            previous_status="",
            new_status=instance.status,
            message="Transaction created",
            processed_by="system"
        )