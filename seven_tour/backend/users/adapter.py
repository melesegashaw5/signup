from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        This is called when a user signs up and saves their information.
        We can customize this process here.
        """
        user = super().save_user(request, user, form, commit=False)

        # Custom fields from the form (e.g. if RegisterSerializer doesn't handle them directly in its save)
        # For dj_rest_auth, RegisterSerializer's save method is usually the primary place.
        # However, allauth's adapter save_user is also involved in the user creation pipeline.

        # Example: if first_name/last_name were not handled by CustomRegisterSerializer.save
        # user.first_name = form.cleaned_data.get('first_name', '')
        # user.last_name = form.cleaned_data.get('last_name', '')

        # Ensure referral code is generated (model's save method already does this)
        # Ensure GoldenCoin account is created (signal already does this)

        if commit:
            user.save()
        return user

    # You can override other methods as needed, e.g.:
    # def is_open_for_signup(self, request):
    #     """
    #     Checks whether or not the site is open for signups.
    #     Next to simply returning True/False you can also raise
    #     SignupClosedException
    #     """
    #     return True # Default is True, set to False to disable signups

    # def populate_username(self, request, user):
    #     """
    #     Fills in a valid username when the user signs up using a third party
    #     provider account that did not provide a username.
    #     """
    #     # Since we use email as username and don't have a separate username field,
    #     # this might not be strictly necessary unless social accounts don't provide email.
    #     # CustomUser model sets username = None.
    #     pass

    # def clean_email(self, email):
    #     """
    #     Validates an email value. You can hook into this if you want to
    #     (dis)allow certain patterns.
    #     """
    #     return super().clean_email(email)

    # def respond_to_login(self, request, user):
    #     """
    #     Override to customize the response after a successful login.
    #     """
    #     # Default behavior is fine for dj-rest-auth as it handles token/response.
    #     return super().respond_to_login(request, user)

    # def respond_to_logout(self, request):
    #     """
    #     Override to customize the response after a successful logout.
    #     """
    #     # Default behavior is fine for dj-rest-auth.
    #     return super().respond_to_logout(request)

    # def get_email_confirmation_url(self, request, emailconfirmation):
    #     """
    #     Constructs the email confirmation URL.
    #     Override this method to use a custom URL, e.g. one pointing to your frontend app.
    #     """
    #     # Example for frontend handling:
    #     # return f"{settings.FRONTEND_URL}/verify-email/?key={emailconfirmation.key}"
    #     return super().get_email_confirmation_url(request, emailconfirmation)

    # def get_password_reset_url(self, request, password_reset_token_generator, email, **kwargs):
    #     """
    #     Constructs the password reset URL.
    #     Override to point to your frontend.
    #     """
    #     # Example for frontend handling:
    #     # uid = url_str_to_user_pk(password_reset_token_generator.uid) # Helper if needed
    #     # token = password_reset_token_generator.token
    #     # return f"{settings.FRONTEND_URL}/reset-password/?uid={uid}&token={token}"
    #     return super().get_password_reset_url(request, password_reset_token_generator, email, **kwargs)

# If you need to customize social account connections (e.g., auto-connect by email)
# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
#     def pre_social_login(self, request, sociallogin):
#         """
#         Invoked just after a user successfully authenticates via a
#         social provider, but before the login is actually processed
#         (and before any linking to local accounts occurs).
#         """
#         # Example: If user exists with the same email, automatically link.
#         # if sociallogin.is_existing:
#         #     return
#         # try:
#         #     user = CustomUser.objects.get(email=sociallogin.account.extra_data.get('email'))
#         #     sociallogin.connect(request, user)
#         # except CustomUser.DoesNotExist:
#         #     pass
#         pass
