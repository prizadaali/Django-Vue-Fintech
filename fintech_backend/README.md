# Fintech Backend - Django REST API

A comprehensive Django REST API backend for a fintech application with user management, account handling, and transaction processing.

## Features

- **User Management**: Custom user model with authentication and profiles
- **Account Management**: Multiple account types with balance tracking
- **Transaction Processing**: Real-time transaction processing with status tracking
- **Recurring Transactions**: Automated recurring payments and transfers
- **Security**: Token-based authentication with proper permissions
- **Admin Interface**: Comprehensive Django admin for management
- **API Documentation**: RESTful API with standardized responses
- **Background Tasks**: Celery integration for async processing

## Project Structure

```
fintech_backend/
├── fintech_backend/          # Main project settings
├── core/                     # Shared utilities and base classes
├── accounts/                 # User and account management
├── transactions/             # Transaction processing
├── requirements.txt          # Python dependencies
├── manage.py                # Django management script
└── README.md                # This file
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fintech_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/auth/profile/` - Get user profile
- `PUT /api/v1/auth/profile/` - Update user profile
- `POST /api/v1/auth/change-password/` - Change password

### Accounts
- `GET /api/v1/auth/accounts/` - List user accounts
- `GET /api/v1/auth/accounts/{id}/` - Get account details
- `GET /api/v1/auth/accounts/{id}/balance/` - Get account balance

### Transactions
- `GET /api/v1/transactions/` - List transactions (with filtering)
- `POST /api/v1/transactions/create/` - Create new transaction
- `GET /api/v1/transactions/{id}/` - Get transaction details
- `POST /api/v1/transactions/{id}/cancel/` - Cancel transaction
- `GET /api/v1/transactions/{id}/logs/` - Get transaction logs
- `GET /api/v1/transactions/statistics/` - Get transaction statistics

### Recurring Transactions
- `GET /api/v1/recurring-transactions/` - List recurring transactions
- `POST /api/v1/recurring-transactions/` - Create recurring transaction
- `GET /api/v1/recurring-transactions/{id}/` - Get recurring transaction details
- `PUT /api/v1/recurring-transactions/{id}/` - Update recurring transaction
- `DELETE /api/v1/recurring-transactions/{id}/` - Delete recurring transaction

### Health Check
- `GET /api/v1/health/` - Application health status

## API Response Format

All API responses follow a standardized format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  }
}
```

## Authentication

The API uses Token-based authentication. Include the token in the Authorization header:

```
Authorization: Token your-token-here
```

## Database Models

### User Model
- Custom user model extending AbstractUser
- Email as username field
- Additional fields: phone_number, date_of_birth, is_verified

### Account Model
- Multiple accounts per user
- Account types: checking, savings, business
- Balance tracking with available balance
- Account status management

### Transaction Model
- Comprehensive transaction tracking
- Support for credits and debits
- Status tracking (pending, processing, completed, failed, cancelled)
- Fee calculation and tracking
- Transaction categories and descriptions

### Recurring Transaction Model
- Automated recurring payments
- Flexible scheduling (daily, weekly, monthly, quarterly, yearly)
- Execution tracking and limits

## Background Tasks

The application uses Celery for background task processing:

1. **Recurring Transaction Processing**: Daily execution of due recurring transactions
2. **Log Cleanup**: Weekly cleanup of old transaction logs
3. **Failed Transaction Retry**: Hourly retry of failed transactions

To run Celery workers:
```bash
celery -A fintech_backend worker -l info
celery -A fintech_backend beat -l info
```

## Security Features

- Token-based authentication
- Custom permissions for resource access
- Input validation and sanitization
- SQL injection protection
- CORS configuration for frontend integration
- Secure password validation

## Testing

Run the test suite:
```bash
python manage.py test
```

## Production Deployment

1. Set `DEBUG=False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up Redis for Celery
4. Configure static file serving
5. Set up proper logging
6. Use environment variables for sensitive settings
7. Set up SSL/TLS certificates
8. Configure firewall and security groups

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.