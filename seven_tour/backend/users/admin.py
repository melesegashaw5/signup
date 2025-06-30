from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, GoldenCoin

class GoldenCoinInline(admin.StackedInline): # Or TabularInline for a more compact view
    model = GoldenCoin
    can_delete = False
    verbose_name_plural = 'Golden Coin Account'
    fk_name = 'user'
    fields = ('balance',) # Only show balance, user is implicit

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    # Add or override fields as needed
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'referral_code', 'get_golden_coin_balance')
    list_filter = BaseUserAdmin.list_filter + ('role',) # Add role to filters
    search_fields = ('email', 'first_name', 'last_name', 'referral_code') # Essential for autocomplete_fields

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('profile_photo', 'role', 'referral_code', 'referred_by')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('profile_photo', 'email', 'first_name', 'last_name', 'role', 'referral_code', 'referred_by')}),
    )
    # Make 'username' not required if it's not used or handled by AbstractUser's None setting
    # For email as USERNAME_FIELD, 'email' should be in the first fieldset for creation

    # If you removed username field from model, you might need to adjust ordering or fieldsets
    # Ensure 'email' is the first field in forms if it's the USERNAME_FIELD and username is None
    ordering = ('email',)
    inlines = (GoldenCoinInline,)

    @admin.display(description='Golden Coins')
    def get_golden_coin_balance(self, obj):
        # GoldenCoin account is created by a signal, so it might not exist immediately
        # or if signals fail/are disabled.
        try:
            return obj.golden_coins_account.balance
        except GoldenCoin.DoesNotExist:
            return "N/A (No account)"
        except Exception: # Catch any other unexpected errors
            return "Error"


@admin.register(GoldenCoin)
class GoldenCoinAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'balance')
    search_fields = ('user__email',)
    readonly_fields = ('user',) # Typically user shouldn't be changed here

    @admin.display(description='User Email', ordering='user__email')
    def user_email(self, obj):
        return obj.user.email

    def has_add_permission(self, request):
        # Usually GoldenCoin accounts are created automatically via signal
        return False # Disallow manual creation from admin for consistency

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion if it's tied to user lifecycle
        return False # Or True if manual deletion is desired under some circumstances

# Note: If you were using the default User model and just extending it via a profile,
# you would unregister User and re-register it with your inline.
# Since CustomUser is a full replacement, we register it directly.
