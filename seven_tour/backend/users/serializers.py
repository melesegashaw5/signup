from rest_framework import serializers
from dj_rest_auth.serializers import UserDetailsSerializer as BaseUserDetailsSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer as BaseRegisterSerializer
from .models import CustomUser

class UserDetailsSerializer(BaseUserDetailsSerializer):
    """
    Custom UserDetailsSerializer to include 'role' and 'profile_photo', 'referral_code'.
    """
    # If profile_photo is an ImageField, its URL will be serialized.
    profile_photo_url = serializers.ImageField(source='profile_photo', read_only=True)
    referral_code = serializers.CharField(read_only=True)
    # Golden coin balance can be added if needed
    # golden_coin_balance = serializers.IntegerField(source='golden_coins_account.balance', read_only=True)


    class Meta(BaseUserDetailsSerializer.Meta):
        model = CustomUser
        fields = BaseUserDetailsSerializer.Meta.fields + ('role', 'profile_photo_url', 'referral_code',
                                                          # 'golden_coin_balance'
                                                          )
        # Ensure 'profile_photo' (the actual field for upload) is handled if you allow profile updates here.
        # For uploads, you'd typically use a different endpoint or handle it carefully.
        # If 'profile_photo' (ImageFieldFile) is included in fields for writing,
        # it will expect a file upload. 'profile_photo_url' is for reading the URL.
        # For now, UserDetailsSerializer is primarily for reading user details.
        # Updates to profile_photo might be handled by a dedicated profile update serializer/view.


class CustomRegisterSerializer(BaseRegisterSerializer):
    """
    Custom RegisterSerializer to include first_name, last_name.
    It already handles email, password, password2.
    """
    first_name = serializers.CharField(required=False, max_length=30)
    last_name = serializers.CharField(required=False, max_length=150)
    # Role is not set at registration by user, defaults in model or admin sets it.
    # Referral code is auto-generated.
    # referred_by_code = serializers.CharField(required=False, write_only=True, max_length=50) # If user can enter a code

    def get_cleaned_data(self):
        data_dict = super().get_cleaned_data()
        data_dict['first_name'] = self.validated_data.get('first_name', '')
        data_dict['last_name'] = self.validated_data.get('last_name', '')
        # data_dict['referred_by_code'] = self.validated_data.get('referred_by_code', '')
        return data_dict

    def save(self, request):
        user = super().save(request) # This calls adapter.new_user(request) and then user.save()

        # Custom logic after user is created by dj_rest_auth's default mechanism
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')

        # Example: Handle 'referred_by_code' if it was part of the form
        # referred_by_code_str = self.cleaned_data.get('referred_by_code')
        # if referred_by_code_str:
        #     try:
        #         referrer = CustomUser.objects.get(referral_code__iexact=referred_by_code_str)
        #         if referrer != user: # Cannot refer self
        #             user.referred_by = referrer
        #             # Potentially award bonus to referrer here or via signal based on referred_by being set
        #     except CustomUser.DoesNotExist:
        #         # Handle invalid referral code, e.g. log it, or raise validation error earlier
        #         pass

        user.save() # Save again to store first_name, last_name, and potentially referred_by
        return user


# If you need a serializer for profile updates (e.g. changing first_name, last_name, profile_photo)
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'profile_photo')
        # Email changes are typically handled by allauth's email management views/forms
        # Password changes are handled by dj-rest-auth's password change endpoint

    # You might want to add extra validation, e.g., for profile_photo size/type if not handled by model/field directly.
    # If profile_photo is updated, ensure old photo is handled (e.g. deleted if desired).
    # This can be done in the view or model's save method.

    # Example: Make profile_photo optional on update
    # profile_photo = serializers.ImageField(required=False, allow_null=True)

    def update(self, instance, validated_data):
        # Handle profile_photo deletion if an empty value is sent for it
        # and you want to clear the photo. Check DRF docs for clearable ImageField.
        return super().update(instance, validated_data)
