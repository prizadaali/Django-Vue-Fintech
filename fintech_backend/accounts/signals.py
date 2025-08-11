"""
Signals for the accounts app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile, Account


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile when a new user is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile when the user is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=User)
def create_primary_account(sender, instance, created, **kwargs):
    """Create a primary account when a new user is created."""
    if created and not Account.objects.filter(user=instance).exists():
        Account.objects.create(
            user=instance,
            account_type='checking',
            is_primary=True
        )