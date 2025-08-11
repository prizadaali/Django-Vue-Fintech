"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Account, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['is_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'date_of_birth', 'is_verified', 'verification_token')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'date_of_birth')
        }),
    )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Admin interface for Account model."""
    list_display = ['account_number', 'user', 'account_type', 'balance', 'status', 'is_primary', 'created_at']
    list_filter = ['account_type', 'status', 'is_primary', 'created_at']
    search_fields = ['account_number', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['account_number', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'account_number', 'account_type', 'is_primary')
        }),
        ('Balance Information', {
            'fields': ('balance', 'available_balance')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for Profile model."""
    list_display = ['user', 'city', 'country', 'identity_verified', 'created_at']
    list_filter = ['identity_verified', 'country', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'city', 'country']
    readonly_fields = ['created_at', 'updated_at', 'identity_verified_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'avatar')
        }),
        ('Address Information', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Verification', {
            'fields': ('identity_document', 'identity_verified', 'identity_verified_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )