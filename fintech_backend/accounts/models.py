"""
User and account models for the fintech application.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from decimal import Decimal
from core.models import TimeStampedModel
from core.utils import generate_account_number


class User(AbstractUser, TimeStampedModel):
    """
    Custom user model extending Django's AbstractUser with fintech-specific fields.
    """
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )],
        blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    
    # Override username to use email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.email} - {self.get_full_name()}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Account(TimeStampedModel):
    """
    Financial account model for users.
    """
    ACCOUNT_TYPES = [
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('business', 'Business'),
    ]

    ACCOUNT_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(max_length=20, unique=True, editable=False)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='checking')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=10, choices=ACCOUNT_STATUS, default='active')
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'accounts_account'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.account_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = generate_account_number()
        
        # Ensure available balance doesn't exceed actual balance
        if self.available_balance > self.balance:
            self.available_balance = self.balance
            
        super().save(*args, **kwargs)

    @property
    def masked_account_number(self):
        """Return masked account number for display purposes."""
        if len(self.account_number) > 4:
            return f"****{self.account_number[-4:]}"
        return self.account_number

    def can_debit(self, amount: Decimal) -> bool:
        """Check if account has sufficient available balance for debit."""
        return self.available_balance >= amount and self.status == 'active'

    def credit(self, amount: Decimal):
        """Credit amount to account."""
        self.balance += amount
        self.available_balance += amount
        self.save()

    def debit(self, amount: Decimal):
        """Debit amount from account if sufficient balance exists."""
        if self.can_debit(amount):
            self.balance -= amount
            self.available_balance -= amount
            self.save()
            return True
        return False


class Profile(TimeStampedModel):
    """
    Extended user profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # KYC fields
    identity_document = models.ImageField(upload_to='documents/', null=True, blank=True)
    identity_verified = models.BooleanField(default=False)
    identity_verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'accounts_profile'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f"Profile for {self.user.email}"