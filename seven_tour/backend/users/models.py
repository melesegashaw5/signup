from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

def user_profile_photo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/users/profile_photos/<user_id>/<filename>
    return f'users/profile_photos/{instance.id}/{filename}'

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        USER = 'USER', _('User')
        ADMIN = 'ADMIN', _('Admin')
        SUB_ADMIN = 'SUB_ADMIN', _('Sub-Admin')
        EMBASSY_PARTNER = 'EMBASSY_PARTNER', _('Embassy Partner')

    # Remove username, use email as the unique identifier
    username = None
    email = models.EmailField(_('email address'), unique=True)

    profile_photo = models.ImageField(
        _("profile_photo"),
        upload_to=user_profile_photo_path,
        null=True,
        blank=True
    )
    referral_code = models.CharField(
        _("referral_code"),
        max_length=50,
        unique=True,
        blank=True # Will be generated upon creation
    )
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # No other fields required besides email and password

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4().hex[:10].upper() # Example: 10 char hex
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class GoldenCoin(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='golden_coins_account' # Changed from 'golden_coins' to avoid clash
    )
    balance = models.PositiveIntegerField(default=0)
    # 1 coin = 1000 ETB (this conversion is business logic, not stored here directly)

    def __str__(self):
        return f"{self.user.email} - {self.balance} coins"

    class Meta:
        verbose_name = _("Golden Coin Account")
        verbose_name_plural = _("Golden Coin Accounts")
