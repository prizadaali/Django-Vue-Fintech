# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
import uuid

class User(AbstractUser):
    """Custom user model with financial account information"""
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)
    
    def generate_account_number(self):
        """Generate unique account number"""
        return f"ACC{uuid.uuid4().hex[:8].upper()}"

class Transaction(models.Model):
    """Transaction model for financial operations"""
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    CATEGORIES = [
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
        ('shopping', 'Shopping'),
        ('bills', 'Bills'),
        ('income', 'Income'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    recipient_account = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_type.title()} - {self.amount} - {self.user.username}"

# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Transaction

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile data"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'balance', 'account_number']
        read_only_fields = ['id', 'account_number']

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transaction data"""
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)
    type = serializers.CharField(source='transaction_type', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'type', 'transaction_type', 'description', 
            'category', 'recipient_account', 'status', 'timestamp'
        ]
        read_only_fields = ['id', 'status', 'timestamp']

class CreateTransactionSerializer(serializers.ModelSerializer):
    """Serializer for creating new transactions"""
    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'category', 'recipient_account']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['transaction_type'] = 'debit'  # Outgoing payment
        
        # Create transaction
        transaction = Transaction.objects.create(**validated_data)
        
        # Update user balance (simplified - would use database transactions in production)
        user.balance -= validated_data['amount']
        user.save()
        
        # Process transaction (would integrate with payment processor)
        transaction.status = 'completed'
        transaction.save()
        
        return transaction

# views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from .models import Transaction
from .serializers import UserSerializer, TransactionSerializer, CreateTransactionSerializer

User = get_user_model()

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Profile retrieved successfully'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_balance(request, user_id):
    """Get updated user balance"""
    if request.user.id != user_id:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Refresh balance from database
    request.user.refresh_from_db()
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Balance updated'
    })

class TransactionListView(generics.ListAPIView):
    """List user transactions with pagination and filtering"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        filter_param = self.request.query_params.get('filter')
        
        if filter_param:
            queryset = queryset.filter(category__icontains=filter_param)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': {
                'transactions': response.data['results'],
                'total': response.data['count']
            },
            'message': 'Transactions retrieved successfully'
        })

class CreateTransactionView(generics.CreateAPIView):
    """Create new transaction/payment"""
    serializer_class = CreateTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Validate sufficient balance
        user = request.user
        amount = request.data.get('amount', 0)
        
        if user.balance < Decimal(str(amount)):
            return Response({
                'success': False,
                'message': 'Insufficient balance'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        response = super().create(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': response.data,
            'message': 'Transaction created successfully'
        }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_detail(request, transaction_id):
    """Get specific transaction details"""
    try:
        transaction = Transaction.objects.get(id=transaction_id, user=request.user)
        serializer = TransactionSerializer(transaction)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Transaction retrieved successfully'
        })
    except Transaction.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Transaction not found'
        }, status=status.HTTP_404_NOT_FOUND)

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('users/profile/', views.user_profile, name='user-profile'),
    path('users/<int:user_id>/balance/', views.user_balance, name='user-balance'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/', views.CreateTransactionView.as_view(), name='create-transaction'),
    path('transactions/<uuid:transaction_id>/', views.transaction_detail, name='transaction-detail'),
]

# settings.py additions
"""
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'accounts',
    'transactions',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewTokenMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]

AUTH_USER_MODEL = 'accounts.User'
"""