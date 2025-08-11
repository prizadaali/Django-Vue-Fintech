"""
Views for the accounts app.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from core.utils import create_api_response
from core.permissions import IsAccountOwner
from .models import User, Account, Profile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    AccountSerializer, ProfileSerializer, ChangePasswordSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create user token
        token, created = Token.objects.get_or_create(user=user)
        
        # Create user profile
        Profile.objects.create(user=user)
        
        # Create primary account
        Account.objects.create(
            user=user,
            account_type='checking',
            is_primary=True
        )
        
        return Response(
            create_api_response(
                data={
                    'user': UserSerializer(user).data,
                    'token': token.key
                },
                message="User registered successfully"
            ),
            status=status.HTTP_201_CREATED
        )


class UserLoginView(generics.GenericAPIView):
    """User login endpoint."""
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Login user
        login(request, user)
        
        return Response(
            create_api_response(
                data={
                    'user': UserSerializer(user).data,
                    'token': token.key
                },
                message="Login successful"
            ),
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """User logout endpoint."""
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response(
            create_api_response(message="Logout successful"),
            status=status.HTTP_200_OK
        )
    except Token.DoesNotExist:
        return Response(
            create_api_response(message="User was not logged in"),
            status=status.HTTP_200_OK
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            create_api_response(
                data=serializer.data,
                message="Profile retrieved successfully"
            )
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(
            create_api_response(
                data=serializer.data,
                message="Profile updated successfully"
            )
        )


class AccountListView(generics.ListAPIView):
    """List user accounts."""
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            create_api_response(
                data=serializer.data,
                message="Accounts retrieved successfully"
            )
        )


class AccountDetailView(generics.RetrieveAPIView):
    """Account detail endpoint."""
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            create_api_response(
                data=serializer.data,
                message="Account retrieved successfully"
            )
        )


class ChangePasswordView(generics.GenericAPIView):
    """Change password endpoint."""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Delete old token and create new one
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        
        return Response(
            create_api_response(
                data={'token': token.key},
                message="Password changed successfully"
            )
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_balance_view(request, account_id):
    """Get updated account balance."""
    account = get_object_or_404(Account, id=account_id, user=request.user)
    
    # Refresh from database
    account.refresh_from_db()
    
    return Response(
        create_api_response(
            data={
                'balance': account.balance,
                'available_balance': account.available_balance,
                'account_number': account.masked_account_number
            },
            message="Balance retrieved successfully"
        )
    )