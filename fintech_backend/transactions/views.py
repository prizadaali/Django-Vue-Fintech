"""
Views for the transactions app.
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction
from core.utils import create_api_response
from core.permissions import IsAccountOwner
from accounts.models import Account
from .models import Transaction, TransactionLog, RecurringTransaction
from .serializers import (
    TransactionSerializer, CreateTransactionSerializer,
    TransactionLogSerializer, RecurringTransactionSerializer,
    CreateRecurringTransactionSerializer
)
from .filters import TransactionFilter
from .services import TransactionService


class TransactionListView(generics.ListAPIView):
    """List user transactions with filtering and pagination."""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ['description', 'recipient_name', 'reference']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get transactions for user's accounts."""
        user_accounts = Account.objects.filter(user=self.request.user)
        return Transaction.objects.filter(account__in=user_accounts)

    def list(self, request, *args, **kwargs):
        """Return paginated transaction list."""
        response = super().list(request, *args, **kwargs)
        return Response(
            create_api_response(
                data={
                    'transactions': response.data['results'],
                    'total': response.data['count'],
                    'page': request.GET.get('page', 1),
                    'page_size': self.paginator.page_size
                },
                message="Transactions retrieved successfully"
            )
        )


class TransactionCreateView(generics.CreateAPIView):
    """Create new transaction/payment."""
    serializer_class = CreateTransactionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create and process a new transaction."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Use transaction service to process the payment
        with transaction.atomic():
            transaction_obj = serializer.save()
            
            # Process the transaction
            success = TransactionService.process_transaction(transaction_obj)
            
            if success:
                return Response(
                    create_api_response(
                        data=TransactionSerializer(transaction_obj).data,
                        message="Transaction created and processed successfully"
                    ),
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    create_api_response(
                        data=TransactionSerializer(transaction_obj).data,
                        message="Transaction created but processing failed",
                        success=False
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )


class TransactionDetailView(generics.RetrieveAPIView):
    """Get transaction details."""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]

    def get_queryset(self):
        """Get transactions for user's accounts."""
        user_accounts = Account.objects.filter(user=self.request.user)
        return Transaction.objects.filter(account__in=user_accounts)

    def retrieve(self, request, *args, **kwargs):
        """Return transaction details."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            create_api_response(
                data=serializer.data,
                message="Transaction retrieved successfully"
            )
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_transaction(request, transaction_id):
    """Cancel a pending transaction."""
    user_accounts = Account.objects.filter(user=request.user)
    transaction_obj = get_object_or_404(
        Transaction, 
        id=transaction_id, 
        account__in=user_accounts
    )
    
    if transaction_obj.can_cancel():
        reason = request.data.get('reason', 'Cancelled by user')
        success = transaction_obj.cancel(reason)
        
        if success:
            return Response(
                create_api_response(
                    data=TransactionSerializer(transaction_obj).data,
                    message="Transaction cancelled successfully"
                )
            )
    
    return Response(
        create_api_response(
            message="Transaction cannot be cancelled",
            success=False
        ),
        status=status.HTTP_400_BAD_REQUEST
    )


class TransactionLogListView(generics.ListAPIView):
    """List transaction logs for a specific transaction."""
    serializer_class = TransactionLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get logs for user's transaction."""
        transaction_id = self.kwargs['transaction_id']
        user_accounts = Account.objects.filter(user=self.request.user)
        
        # Verify transaction belongs to user
        transaction_obj = get_object_or_404(
            Transaction,
            id=transaction_id,
            account__in=user_accounts
        )
        
        return TransactionLog.objects.filter(transaction=transaction_obj)

    def list(self, request, *args, **kwargs):
        """Return transaction logs."""
        response = super().list(request, *args, **kwargs)
        return Response(
            create_api_response(
                data=response.data,
                message="Transaction logs retrieved successfully"
            )
        )


class RecurringTransactionListView(generics.ListCreateAPIView):
    """List and create recurring transactions."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'frequency', 'category']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get recurring transactions for user's accounts."""
        user_accounts = Account.objects.filter(user=self.request.user)
        return RecurringTransaction.objects.filter(account__in=user_accounts)

    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'POST':
            return CreateRecurringTransactionSerializer
        return RecurringTransactionSerializer

    def list(self, request, *args, **kwargs):
        """Return recurring transactions list."""
        response = super().list(request, *args, **kwargs)
        return Response(
            create_api_response(
                data=response.data,
                message="Recurring transactions retrieved successfully"
            )
        )

    def create(self, request, *args, **kwargs):
        """Create new recurring transaction."""
        response = super().create(request, *args, **kwargs)
        return Response(
            create_api_response(
                data=response.data,
                message="Recurring transaction created successfully"
            ),
            status=status.HTTP_201_CREATED
        )


class RecurringTransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage individual recurring transactions."""
    serializer_class = RecurringTransactionSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]

    def get_queryset(self):
        """Get recurring transactions for user's accounts."""
        user_accounts = Account.objects.filter(user=self.request.user)
        return RecurringTransaction.objects.filter(account__in=user_accounts)

    def retrieve(self, request, *args, **kwargs):
        """Return recurring transaction details."""
        response = super().retrieve(request, *args, **kwargs)
        return Response(
            create_api_response(
                data=response.data,
                message="Recurring transaction retrieved successfully"
            )
        )

    def update(self, request, *args, **kwargs):
        """Update recurring transaction."""
        response = super().update(request, *args, **kwargs)
        return Response(
            create_api_response(
                data=response.data,
                message="Recurring transaction updated successfully"
            )
        )

    def destroy(self, request, *args, **kwargs):
        """Delete recurring transaction."""
        super().destroy(request, *args, **kwargs)
        return Response(
            create_api_response(
                message="Recurring transaction deleted successfully"
            ),
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_statistics(request):
    """Get transaction statistics for the user."""
    user_accounts = Account.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(account__in=user_accounts, status='completed')
    
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta
    
    # Calculate statistics
    total_transactions = transactions.count()
    total_credits = transactions.filter(transaction_type='credit').aggregate(
        total=Sum('amount'))['total'] or 0
    total_debits = transactions.filter(transaction_type='debit').aggregate(
        total=Sum('amount'))['total'] or 0
    
    # This month statistics
    this_month = datetime.now().replace(day=1)
    monthly_transactions = transactions.filter(created_at__gte=this_month)
    monthly_credits = monthly_transactions.filter(transaction_type='credit').aggregate(
        total=Sum('amount'))['total'] or 0
    monthly_debits = monthly_transactions.filter(transaction_type='debit').aggregate(
        total=Sum('amount'))['total'] or 0
    
    # Category breakdown
    category_stats = transactions.values('category').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    ).order_by('-total_amount')
    
    stats_data = {
        'total_transactions': total_transactions,
        'total_credits': float(total_credits),
        'total_debits': float(total_debits),
        'net_flow': float(total_credits - total_debits),
        'monthly_credits': float(monthly_credits),
        'monthly_debits': float(monthly_debits),
        'monthly_net_flow': float(monthly_credits - monthly_debits),
        'category_breakdown': list(category_stats)
    }
    
    return Response(
        create_api_response(
            data=stats_data,
            message="Transaction statistics retrieved successfully"
        )
    )