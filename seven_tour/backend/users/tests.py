from django.test import TestCase
from django.conf import settings
from .models import CustomUser, GoldenCoin

class UserSignalTests(TestCase):
    def test_golden_coin_creation_and_referral_code_on_user_signup(self):
        """
        Test that a GoldenCoin account is created with a welcome bonus
        and a referral code is generated when a new CustomUser is created.
        """
        email = 'signaltest@example.com'
        password = 'testpassword123'

        # Ensure no user or coin account exists initially (though test DB isolation handles this)
        self.assertFalse(CustomUser.objects.filter(email=email).exists())

        user = CustomUser.objects.create_user(email=email, password=password)

        # Check if user was created
        self.assertTrue(CustomUser.objects.filter(email=email).exists())

        # Check for referral code
        self.assertIsNotNone(user.referral_code)
        self.assertTrue(len(user.referral_code) > 0) # Basic check for non-empty string

        # Check for GoldenCoin account and welcome bonus
        # The related name for GoldenCoin is 'golden_coins_account'
        self.assertTrue(hasattr(user, 'golden_coins_account'), "User should have a 'golden_coins_account' attribute.")

        # Verify the GoldenCoin object exists in the database too
        golden_coin_entry = GoldenCoin.objects.filter(user=user).first()
        self.assertIsNotNone(golden_coin_entry, "GoldenCoin entry not found in database for user.")

        # Make sure WELCOME_BONUS_COINS_AMOUNT is accessible or defined for test
        # We can use the default from signals.py for this test if not overriding settings
        # from users.signals import WELCOME_BONUS_COINS_AMOUNT # Not ideal to import from signals directly in test
        # Instead, rely on the value used by the signal, or override settings if it's from django.conf.settings

        # Assuming WELCOME_BONUS_COINS_AMOUNT in signals.py defaults to 5 if settings.WELCOME_BONUS_COINS is not set
        # This depends on how WELCOME_BONUS_COINS_AMOUNT is defined in signals.py
        # WELCOME_BONUS_COINS_AMOUNT = getattr(settings, 'WELCOME_BONUS_COINS', 5)
        expected_bonus = getattr(settings, 'WELCOME_BONUS_COINS', 5)

        self.assertEqual(user.golden_coins_account.balance, expected_bonus)
        if golden_coin_entry: # Check if not None before accessing attribute
            self.assertEqual(golden_coin_entry.balance, expected_bonus)

    def test_referral_code_uniqueness(self):
        """
        Test that referral codes are unique (probabilistically, by creating a few users).
        """
        user1 = CustomUser.objects.create_user(email='user1@example.com', password='password1')
        user2 = CustomUser.objects.create_user(email='user2@example.com', password='password2')
        user3 = CustomUser.objects.create_user(email='user3@example.com', password='password3')

        self.assertIsNotNone(user1.referral_code)
        self.assertIsNotNone(user2.referral_code)
        self.assertIsNotNone(user3.referral_code)

        referral_codes = {user1.referral_code, user2.referral_code, user3.referral_code}
        self.assertEqual(len(referral_codes), 3, "Referral codes should be unique among these users.")

    def test_custom_user_creation_fields(self):
        """
        Test creation of CustomUser with all fields and default role.
        """
        user = CustomUser.objects.create_user(
            email='fulluser@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.email, 'fulluser@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.role, CustomUser.Role.USER) # Check default role
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNotNone(user.referral_code)


class CustomUserModelTests(TestCase):
    def test_email_is_username_field(self):
        self.assertEqual(CustomUser.USERNAME_FIELD, 'email')

    def test_create_superuser(self):
        # For create_superuser, the role might be set by logic within create_superuser or by default
        # In our CustomUser model, there isn't specific logic to default role to ADMIN for superuser
        # It will take the default Role.USER unless explicitly set or if BaseUserManager handles it.
        # Django's BaseUserManager sets is_staff=True, is_superuser=True. Role is custom.
        # Let's assume for a superuser, we'd expect an ADMIN role, which might need to be
        # set in a custom manager's create_superuser method or handled by default if appropriate.
        # For now, test what BaseUserManager provides and what our model defaults.

        admin_user = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword',
            # role=CustomUser.Role.ADMIN # Explicitly set role if create_superuser doesn't default it to ADMIN
        )
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

        # Check the role. If CustomUser.role defaults to USER, this will be USER.
        # If we want superusers to be ADMIN by default, this needs adjustment in CustomUserManager.
        # For now, testing the current behavior:
        self.assertEqual(admin_user.role, CustomUser.Role.USER, "Default role for superuser should be USER, unless manager overrides.")
        # To make it ADMIN, the CustomUserManager would need to set it.

        # Check if golden coin account is also created for superuser
        self.assertTrue(hasattr(admin_user, 'golden_coins_account'))
        expected_bonus = getattr(settings, 'WELCOME_BONUS_COINS', 5)
        self.assertEqual(admin_user.golden_coins_account.balance, expected_bonus)
        self.assertIsNotNone(admin_user.referral_code)

    def test_create_superuser_with_admin_role(self):
        # Test explicitly setting role for superuser if manager doesn't handle it
        admin_user = CustomUser.objects.create_superuser(
            email='admin_explicit_role@example.com',
            password='adminpassword',
            role=CustomUser.Role.ADMIN
        )
        self.assertEqual(admin_user.role, CustomUser.Role.ADMIN)

# If WELCOME_BONUS_COINS is critical and comes from settings.py, and not base.py,
# tests might need @override_settings decorator if that setting isn't globally available during tests.
# from django.test import override_settings
# @override_settings(WELCOME_BONUS_COINS=10)
# class UserSignalTestsWithSettingsOverride(TestCase):
#    ... tests ...

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

class AuthAPITests(APITestCase):
    def test_user_registration_success(self):
        """
        Test new user registration is successful.
        """
        url = reverse('rest_register') # dj_rest_auth.registration default name
        data = {
            'email': 'newuser@example.com',
            'password': 'strongpassword123',
            'password2': 'strongpassword123', # dj_rest_auth's default RegisterSerializer requires password confirmation
            'first_name': 'New',
            'last_name': 'User',
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertTrue(CustomUser.objects.filter(email='newuser@example.com').exists())
        created_user = CustomUser.objects.get(email='newuser@example.com')
        self.assertEqual(created_user.first_name, 'New')
        self.assertEqual(created_user.last_name, 'User')

        # Check if JWT tokens are returned (if REST_AUTH.USE_JWT = True)
        # dj-rest-auth by default returns 'key' for basic token auth, or access/refresh for JWT
        if getattr(settings, 'REST_AUTH', {}).get('USE_JWT'):
            self.assertIn('access_token', response.data) # or 'access' depending on simplejwt version/config
            self.assertIn('refresh_token', response.data) # or 'refresh'
        else: # Basic token auth
            self.assertIn('key', response.data)


    def test_user_registration_password_mismatch(self):
        url = reverse('rest_register')
        data = {
            'email': 'anotheruser@example.com',
            'password': 'password123',
            'password2': 'passwordmismatch',
            'first_name': 'Another',
            'last_name': 'User',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data) # Check if error is related to password confirmation


    def test_user_login_success_and_token_generation(self):
        # First, create a user to log in with
        email = 'loginuser@example.com'
        password = 'loginpassword123'
        CustomUser.objects.create_user(email=email, password=password, first_name='Login', last_name='User')

        url = reverse('rest_login') # dj_rest_auth default name
        data = {
            'email': email,
            'password': password,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        if getattr(settings, 'REST_AUTH', {}).get('USE_JWT'):
            self.assertIn('access_token', response.data)
            self.assertIn('refresh_token', response.data)
            self.assertIn('user', response.data) # UserDetailsSerializer output
            self.assertEqual(response.data['user']['email'], email)
        else: # Basic token auth
            self.assertIn('key', response.data)
            self.assertIn('user', response.data)
            self.assertEqual(response.data['user']['email'], email)


    def test_user_login_invalid_credentials(self):
        url = reverse('rest_login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # Or 401 depending on setup
        self.assertIn('non_field_errors', response.data) # Or specific error message key

    def test_user_logout_success(self):
        # Create and log in a user
        email = 'logoutuser@example.com'
        password = 'logoutpassword123'
        user = CustomUser.objects.create_user(email=email, password=password)

        login_url = reverse('rest_login')
        login_data = {'email': email, 'password': password}
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        if getattr(settings, 'REST_AUTH', {}).get('USE_JWT'):
            token = login_response.data['access_token']
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        else:
            token = login_response.data['key']
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        logout_url = reverse('rest_logout')
        logout_response = self.client.post(logout_url, {}, format='json') # Logout is typically a POST

        self.assertEqual(logout_response.status_code, status.HTTP_200_OK, logout_response.content)
        # For JWT, logout might mean blacklisting token if configured, or just client-side deletion.
        # dj-rest-auth's default JWT logout does not blacklist but can be configured to.
        # For Token auth, it deletes the token.

        # Try to access a protected endpoint (e.g., user details) after logout
        user_details_url = reverse('rest_user_details')
        details_response_after_logout = self.client.get(user_details_url, format='json')
        self.assertEqual(details_response_after_logout.status_code, status.HTTP_401_UNAUTHORIZED, "User should be unauthorized after logout")

    def test_user_details_endpoint_authenticated(self):
        email = 'detailsuser@example.com'
        password = 'detailspassword123'
        user = CustomUser.objects.create_user(email=email, password=password, first_name="Details", last_name="User", role=CustomUser.Role.USER)

        login_url = reverse('rest_login')
        login_data = {'email': email, 'password': password}
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        if getattr(settings, 'REST_AUTH', {}).get('USE_JWT'):
            token = login_response.data['access_token']
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        else:
            token = login_response.data['key']
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        url = reverse('rest_user_details')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], email)
        self.assertEqual(response.data['first_name'], "Details")
        self.assertEqual(response.data['role'], CustomUser.Role.USER)
        self.assertIn('profile_photo_url', response.data) # From UserDetailsSerializer
        self.assertIn('referral_code', response.data)


    def test_user_details_endpoint_unauthenticated(self):
        url = reverse('rest_user_details')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# Note: For JWT tests, ensure SIMPLE_JWT settings like 'ACCESS_TOKEN_LIFETIME' are reasonable for tests.
# If using refresh tokens, those flows would need separate tests.
# Password reset and email verification flows also need their own tests, often involving email mocking.
