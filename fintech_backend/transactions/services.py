"""
Business logic services for transactions.
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Transaction, TransactionLog
from accounts.models import Account
from core.utils import calculate_transaction_fee


class TransactionService:
    """Service class for transaction processing logic."""
    
    @staticmethod
    def process_transaction(transaction_obj: Transaction) -> bool:
        """
        Process a transaction by updating account balances and status.
        
        Args:
            transaction_obj: Transaction instance to process
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with transaction.atomic():
                account = transaction_obj.account
                
                # Log transaction processing start
                TransactionLog.objects.create(
                    transaction=transaction_obj,
                    previous_status=transaction_obj.status,
                    new_status='processing',
                    message="Transaction processing started",
                    processed_by="system"
                )
                
                transaction_obj.status = 'processing'
                transaction_obj.save()
                
                if transaction_obj.transaction_type == 'debit':
                    # Outgoing transaction - debit from account
                    total_amount = transaction_obj.amount + transaction_obj.fee_amount
                    
                    if not account.can_debit(total_amount):
                        # Insufficient funds
                        transaction_obj.status = 'failed'
                        transaction_obj.failure_reason = 'Insufficient funds'
                        transaction_obj.save()
                        
                        TransactionLog.objects.create(
                            transaction=transaction_obj,
                            previous_status='processing',
                            new_status='failed',
                            message="Transaction failed: Insufficient funds",
                            processed_by="system"
                        )
                        return False
                    
                    # Debit the account
                    account.debit(total_amount)
                    
                elif transaction_obj.transaction_type == 'credit':
                    # Incoming transaction - credit to account
                    net_amount = transaction_obj.amount - transaction_obj.fee_amount
                    account.credit(net_amount)
                
                # Mark transaction as completed
                transaction_obj.status = 'completed'
                transaction_obj.processed_at = timezone.now()
                transaction_obj.save()
                
                TransactionLog.objects.create(
                    transaction=transaction_obj,
                    previous_status='processing',
                    new_status='completed',
                    message="Transaction completed successfully",
                    processed_by="system"
                )
                
                return True
                
        except Exception as e:
            # Handle any processing errors
            transaction_obj.status = 'failed'
            transaction_obj.failure_reason = str(e)
            transaction_obj.save()
            
            TransactionLog.objects.create(
                transaction=transaction_obj,
                previous_status='processing',
                new_status='failed',
                message=f"Transaction failed: {str(e)}",
                processed_by="system"
            )
            
            return False
    
    @staticmethod
    def create_transfer(from_account: Account, to_account_number: str, 
                       amount: Decimal, description: str, category: str = 'transfer') -> Transaction:
        """
        Create a transfer transaction between accounts.
        
        Args:
            from_account: Source account
            to_account_number: Destination account number
            amount: Transfer amount
            description: Transaction description
            category: Transaction category
            
        Returns:
            Transaction: Created transaction instance
        """
        fee = calculate_transaction_fee(amount, 'transfer')
        
        transaction_obj = Transaction.objects.create(
            account=from_account,
            amount=amount,
            transaction_type='debit',
            description=description,
            category=category,
            recipient_account_number=to_account_number,
            fee_amount=fee
        )
        
        return transaction_obj
    
    @staticmethod
    def create_deposit(account: Account, amount: Decimal, 
                      description: str, external_ref: str = None) -> Transaction:
        """
        Create a deposit transaction.
        
        Args:
            account: Target account
            amount: Deposit amount
            description: Transaction description
            external_ref: External reference (e.g., from payment processor)
            
        Returns:
            Transaction: Created transaction instance
        """
        transaction_obj = Transaction.objects.create(
            account=account,
            amount=amount,
            transaction_type='credit',
            description=description,
            category='deposit',
            external_reference=external_ref or '',
            fee_amount=Decimal('0.00')  # No fee for deposits
        )
        
        return transaction_obj
    
    @staticmethod
    def create_withdrawal(account: Account, amount: Decimal, 
                         description: str) -> Transaction:
        """
        Create a withdrawal transaction.
        
        Args:
            account: Source account
            amount: Withdrawal amount
            description: Transaction description
            
        Returns:
            Transaction: Created transaction instance
        """
        fee = calculate_transaction_fee(amount, 'withdrawal')
        
        transaction_obj = Transaction.objects.create(
            account=account,
            amount=amount,
            transaction_type='debit',
            description=description,
            category='withdrawal',
            fee_amount=fee
        )
        
        return transaction_obj
    
    @staticmethod
    def get_account_balance(account: Account) -> dict:
        """
        Get current account balance information.
        
        Args:
            account: Account instance
            
        Returns:
            dict: Balance information
        """
        # Refresh account from database
        account.refresh_from_db()
        
        return {
            'balance': account.balance,
            'available_balance': account.available_balance,
            'account_number': account.masked_account_number,
            'account_type': account.account_type,
            'status': account.status
        }


class RecurringTransactionService:
    """Service class for recurring transaction processing."""
    
    @staticmethod
    def execute_recurring_transaction(recurring_transaction) -> bool:
        """
        Execute a recurring transaction.
        
        Args:
            recurring_transaction: RecurringTransaction instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not recurring_transaction.can_execute():
            return False
        
        try:
            # Create the transaction
            transaction_obj = TransactionService.create_transfer(
                from_account=recurring_transaction.account,
                to_account_number=recurring_transaction.recipient_account_number,
                amount=recurring_transaction.amount,
                description=f"Recurring: {recurring_transaction.description}",
                category=recurring_transaction.category
            )
            
            # Process the transaction
            success = TransactionService.process_transaction(transaction_obj)
            
            if success:
                # Update recurring transaction
                recurring_transaction.execution_count += 1
                recurring_transaction.next_execution_date = recurring_transaction.calculate_next_execution_date()
                
                # Check if we've reached max executions
                if (recurring_transaction.max_executions and 
                    recurring_transaction.execution_count >= recurring_transaction.max_executions):
                    recurring_transaction.status = 'completed'
                
                recurring_transaction.save()
                
            return success
            
        except Exception as e:
            # Log error and continue
            print(f"Error executing recurring transaction {recurring_transaction.id}: {str(e)}")
            return False
    
    @staticmethod
    def process_due_recurring_transactions():
        """
        Process all due recurring transactions.
        This method would typically be called by a scheduled task (Celery).
        """
        from django.utils import timezone
        from .models import RecurringTransaction
        
        today = timezone.now().date()
        due_transactions = RecurringTransaction.objects.filter(
            status='active',
            next_execution_date__lte=today
        )
        
        results = {
            'processed': 0,
            'failed': 0,
            'total': due_transactions.count()
        }
        
        for recurring_tx in due_transactions:
            if RecurringTransactionService.execute_recurring_transaction(recurring_tx):
                results['processed'] += 1
            else:
                results['failed'] += 1
        
        return results