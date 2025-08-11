"""
Serializers for the transactions app.
"""
from rest_framework import serializers
from decimal import Decimal
from .models import Transaction, TransactionLog, RecurringTransaction
from accounts.models import Account
from core.utils import validate_account_number, calculate_transaction_fee


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transaction data."""
    account_number = serializers.CharField(source='account.masked_account_number', read_only=True)
    net_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)
    type = serializers.CharField(source='transaction_type', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'account_number', 'amount', 'net_amount',
            'transaction_type', 'type', 'status', 'description', 'category',
            'recipient_account_number', 'recipient_name', 'fee_amount',
            'timestamp', 'processed_at', 'failure_reason'
        ]
        read_only_fields = [
            'id', 'reference', 'account_number', 'net_amount', 'type',
            'status', 'fee_amount', 'timestamp', 'processed_at', 'failure_reason'
        ]


class CreateTransactionSerializer(serializers.ModelSerializer):
    """Serializer for creating new transactions."""
    account_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Transaction
        fields = [
            'account_id', 'amount', 'description', 'category',
            'recipient_account_number', 'recipient_name'
        ]

    def validate_amount(self, value):
        """Validate transaction amount."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        if value > Decimal('100000.00'):  # Max transaction limit
            raise serializers.ValidationError("Amount exceeds maximum transaction limit.")
        return value

    def validate_recipient_account_number(self, value):
        """Validate recipient account number format."""
        if value and not validate_account_number(value):
            raise serializers.ValidationError("Invalid account number format.")
        return value

    def validate(self, attrs):
        """Validate transaction data."""
        user = self.context['request'].user
        account_id = attrs.get('account_id')
        amount = attrs.get('amount')

        # Validate account ownership
        try:
            account = Account.objects.get(id=account_id, user=user)
        except Account.DoesNotExist:
            raise serializers.ValidationError("Invalid account.")

        # Check if account can be debited
        fee = calculate_transaction_fee(amount, 'transfer')
        total_amount = amount + fee

        if not account.can_debit(total_amount):
            raise serializers.ValidationError("Insufficient balance for this transaction.")

        attrs['account'] = account
        attrs['fee_amount'] = fee
        return attrs

    def create(self, validated_data):
        """Create a new transaction."""
        account = validated_data.pop('account')
        validated_data.pop('account_id')
        
        # Set transaction type as debit (outgoing payment)
        validated_data['transaction_type'] = 'debit'
        validated_data['account'] = account
        
        transaction = Transaction.objects.create(**validated_data)
        return transaction


class TransactionLogSerializer(serializers.ModelSerializer):
    """Serializer for transaction logs."""
    class Meta:
        model = TransactionLog
        fields = [
            'id', 'previous_status', 'new_status', 'message',
            'processed_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RecurringTransactionSerializer(serializers.ModelSerializer):
    """Serializer for recurring transactions."""
    account_number = serializers.CharField(source='account.masked_account_number', read_only=True)
    can_execute = serializers.BooleanField(read_only=True)

    class Meta:
        model = RecurringTransaction
        fields = [
            'id', 'account_number', 'amount', 'description', 'category',
            'recipient_account_number', 'recipient_name', 'frequency',
            'start_date', 'end_date', 'next_execution_date', 'status',
            'execution_count', 'max_executions', 'can_execute', 'created_at'
        ]
        read_only_fields = [
            'id', 'account_number', 'execution_count', 'can_execute', 'created_at'
        ]


class CreateRecurringTransactionSerializer(serializers.ModelSerializer):
    """Serializer for creating recurring transactions."""
    account_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = RecurringTransaction
        fields = [
            'account_id', 'amount', 'description', 'category',
            'recipient_account_number', 'recipient_name', 'frequency',
            'start_date', 'end_date', 'max_executions'
        ]

    def validate(self, attrs):
        """Validate recurring transaction data."""
        user = self.context['request'].user
        account_id = attrs.get('account_id')

        # Validate account ownership
        try:
            account = Account.objects.get(id=account_id, user=user)
        except Account.DoesNotExist:
            raise serializers.ValidationError("Invalid account.")

        attrs['account'] = account
        
        # Set next execution date to start date initially
        attrs['next_execution_date'] = attrs['start_date']
        
        return attrs

    def create(self, validated_data):
        """Create a new recurring transaction."""
        account = validated_data.pop('account')
        validated_data.pop('account_id')
        validated_data['account'] = account
        
        return RecurringTransaction.objects.create(**validated_data)