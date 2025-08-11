"""
Celery configuration for the fintech backend.
"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fintech_backend.settings')

app = Celery('fintech_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'process-recurring-transactions': {
        'task': 'transactions.tasks.process_recurring_transactions',
        'schedule': 60.0 * 60.0 * 24.0,  # Daily at midnight
    },
    'cleanup-old-logs': {
        'task': 'transactions.tasks.cleanup_old_transaction_logs',
        'schedule': 60.0 * 60.0 * 24.0 * 7.0,  # Weekly
    },
    'retry-failed-transactions': {
        'task': 'transactions.tasks.update_failed_transactions',
        'schedule': 60.0 * 60.0,  # Hourly
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')