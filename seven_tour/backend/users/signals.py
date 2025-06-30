from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings # To potentially get WELCOME_BONUS_COINS
from .models import CustomUser, GoldenCoin

# Define the welcome bonus amount here or get from settings
# For example, in settings.py: WELCOME_BONUS_COINS = 5
WELCOME_BONUS_COINS_AMOUNT = getattr(settings, 'WELCOME_BONUS_COINS', 5) # Default to 5

@receiver(post_save, sender=CustomUser)
def create_golden_coin_account_and_add_welcome_bonus(sender, instance, created, **kwargs):
    """
    Signal handler to create a GoldenCoin account for a new user
    and award them a welcome bonus.
    """
    if created: # Only run when a new CustomUser instance is created
        GoldenCoin.objects.create(user=instance, balance=WELCOME_BONUS_COINS_AMOUNT)
        # Optionally, log this event or send a notification
        print(f"GoldenCoin account created for {instance.email} with {WELCOME_BONUS_COINS_AMOUNT} bonus coins.")

# If you wanted to also handle referral bonuses here, you could add logic:
# For example, if instance.referred_by is not None:
#   try:
#     referrer_coin_account = GoldenCoin.objects.get(user=instance.referred_by)
#     referrer_coin_account.balance += REFERRAL_BONUS_FOR_REFERRER # Define this amount
#     referrer_coin_account.save()
#     print(f"Awarded referral bonus to {instance.referred_by.email}")
#   except GoldenCoin.DoesNotExist:
#     print(f"Error: GoldenCoin account not found for referrer {instance.referred_by.email}")
#
# And potentially a bonus for the new user if they used a referral code:
# if instance.referred_by is not None: # or check if a valid referral_code was used during signup
#   coin_account = GoldenCoin.objects.get(user=instance) # get the account created above
#   coin_account.balance += BONUS_FOR_BEING_REFERRED # Define this amount
#   coin_account.save()
#   print(f"Awarded bonus for being referred to {instance.email}")

# For now, we'll keep it simple with just the welcome bonus.
# The referral link itself (CustomUser.referred_by) is already in the model.
# The actual awarding of coins for successful referrals (e.g., when a referred user completes a tour)
# would likely be a more complex piece of logic tied to other events.
