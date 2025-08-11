"""
Utility functions for the fintech application.
"""
import random
import string
from decimal import Decimal
from typing import Dict, Any


def generate_account_number() -> str:
    """Generate a unique account number."""
    prefix = "ACC"
    suffix = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}{suffix}"


def generate_transaction_reference() -> str:
    """Generate a unique transaction reference."""
    prefix = "TXN"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"{prefix}{suffix}"


def format_currency(amount: Decimal, currency: str = "USD") -> str:
    """Format amount as currency string."""
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def validate_account_number(account_number: str) -> bool:
    """Validate account number format."""
    if not account_number:
        return False
    
    # Check if it starts with ACC and has 8 digits after
    if account_number.startswith("ACC") and len(account_number) == 11:
        suffix = account_number[3:]
        return suffix.isdigit()
    
    return False


def create_api_response(data: Any = None, message: str = "", success: bool = True) -> Dict[str, Any]:
    """Create standardized API response format."""
    return {
        "success": success,
        "message": message,
        "data": data
    }


def calculate_transaction_fee(amount: Decimal, transaction_type: str = "transfer") -> Decimal:
    """Calculate transaction fee based on amount and type."""
    fee_rates = {
        "transfer": Decimal("0.01"),  # 1%
        "payment": Decimal("0.005"),  # 0.5%
        "withdrawal": Decimal("0.02"),  # 2%
    }
    
    base_fee = Decimal("1.00")  # Minimum fee
    calculated_fee = amount * fee_rates.get(transaction_type, Decimal("0.01"))
    
    return max(base_fee, calculated_fee)