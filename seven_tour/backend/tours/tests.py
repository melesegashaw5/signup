from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Country, Destination, TourPackage
from users.models import CustomUser # For creating a user if reviews require authenticated user

class TourAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user (if needed for authenticated endpoints later, e.g., reviews)
        cls.user = CustomUser.objects.create_user(email='testuser@example.com', password='testpassword123')

        # Create Country
        cls.country1 = Country.objects.create(name='Ethiopia', country_code='ET')
        cls.country2 = Country.objects.create(name='Kenya', country_code='KE')

        # Create Destinations
        cls.dest1_eth = Destination.objects.create(country=cls.country1, name='Lalibela')
        cls.dest2_eth = Destination.objects.create(country=cls.country1, name='Simien Mountains')
        cls.dest1_ken = Destination.objects.create(country=cls.country2, name='Maasai Mara')

        # Create Tour Packages
        cls.package1 = TourPackage.objects.create(
            title='Historic Ethiopia',
            country=cls.country1,
            description='A journey through ancient history.',
            visa_type=TourPackage.VisaTypeChoices.ON_ARRIVAL,
            price='1200.00',
            duration_days=10,
            highlights='Rock-hewn churches, Axum obelisks',
            inclusions='Guide, Accommodation, Meals',
            is_active=True
        )
        cls.package1.destinations.add(cls.dest1_eth, cls.dest2_eth)

        cls.package2 = TourPackage.objects.create(
            title='Kenyan Safari Adventure',
            country=cls.country2,
            description='Experience the wild.',
            visa_type=TourPackage.VisaTypeChoices.E_VISA,
            price='2500.00',
            duration_days=7,
            highlights='Big Five, Great Migration (seasonal)',
            inclusions='4x4 vehicle, Park fees, Guide',
            is_active=True
        )
        cls.package2.destinations.add(cls.dest1_ken)

        cls.package3 = TourPackage.objects.create(
            title='Inactive Package Test',
            country=cls.country1,
            description='This package should not be listed for users.',
            visa_type=TourPackage.VisaTypeChoices.STICKER_VISA,
            price='500.00',
            duration_days=5,
            is_active=False # Inactive
        )

    def test_list_tour_packages_unauthenticated(self):
        """
        Ensure unauthenticated users can list active tour packages.
        """
        url = reverse('tourpackage-list') # Uses basename from router registration
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2) # Only 2 active packages
        self.assertEqual(len(response.data['results']), 2)
        # Check if titles are present (basic check)
        self.assertTrue(any(p['title'] == 'Historic Ethiopia' for p in response.data['results']))
        self.assertTrue(any(p['title'] == 'Kenyan Safari Adventure' for p in response.data['results']))

    def test_retrieve_tour_package_unauthenticated(self):
        """
        Ensure unauthenticated users can retrieve a specific active tour package.
        """
        url = reverse('tourpackage-detail', kwargs={'pk': self.package1.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.package1.title)
        self.assertEqual(response.data['country']['name'], self.country1.name)
        self.assertTrue(len(response.data['destinations']) > 0)


    def test_retrieve_inactive_tour_package_fails(self):
        """
        Ensure retrieving a specific inactive tour package fails or is not found for regular users.
        (Our ViewSet filters for is_active=True, so it should be 404)
        """
        url = reverse('tourpackage-detail', kwargs={'pk': self.package3.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_packages_by_country_id(self):
        url = reverse('tourpackage-list')
        response = self.client.get(url, {'country__id': self.country1.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1) # Only 'Historic Ethiopia'
        self.assertEqual(response.data['results'][0]['title'], 'Historic Ethiopia')

    def test_filter_packages_by_visa_type(self):
        url = reverse('tourpackage-list')
        response = self.client.get(url, {'visa_type': TourPackage.VisaTypeChoices.E_VISA}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Kenyan Safari Adventure')

    def test_search_packages_by_title(self):
        url = reverse('tourpackage-list')
        response = self.client.get(url, {'search': 'Ethiopia'}, format='json') # Searches title, desc, country, dest
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Historic Ethiopia')

    def test_search_packages_by_destination_name(self):
        url = reverse('tourpackage-list')
        response = self.client.get(url, {'search': 'Lalibela'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Historic Ethiopia')

    def test_ordering_packages_by_price_ascending(self):
        url = reverse('tourpackage-list')
        response = self.client.get(url, {'ordering': 'price'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], 'Historic Ethiopia') # 1200.00
        self.assertEqual(response.data['results'][1]['title'], 'Kenyan Safari Adventure') # 2500.00

    def test_ordering_packages_by_price_descending(self):
        url = reverse('tourpackage-list')
        response = self.client.get(url, {'ordering': '-price'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], 'Kenyan Safari Adventure') # 2500.00
        self.assertEqual(response.data['results'][1]['title'], 'Historic Ethiopia') # 1200.00

    # --- Country API Tests ---
    def test_list_countries(self):
        url = reverse('country-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2) # Ethiopia, Kenya

    def test_retrieve_country(self):
        url = reverse('country-detail', kwargs={'pk': self.country1.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.country1.name)

    # --- Destination API Tests ---
    def test_list_destinations(self):
        url = reverse('destination-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3) # Lalibela, Simien, Maasai Mara

    def test_filter_destinations_by_country_id(self):
        url = reverse('destination-list')
        response = self.client.get(url, {'country__id': self.country1.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2) # Lalibela, Simien
        self.assertTrue(any(d['name'] == 'Lalibela' for d in response.data['results']))
        self.assertTrue(any(d['name'] == 'Simien Mountains' for d in response.data['results']))

    # TODO: Add tests for Review creation once user authentication API is in place.
    # For Review creation, client would need to be authenticated.
    # self.client.login(email='testuser@example.com', password='testpassword123') or set token.
    # Then self.client.post(reverse('review-list'), review_data, format='json')

    # TODO: Test user signal for GoldenCoin creation upon CustomUser creation.
    # This might be better as a unit test for the signal handler itself rather than an API test.
    # from django.test import TestCase
    # class UserSignalTests(TestCase):
    #     def test_golden_coin_creation_on_user_signup(self):
    #         user = CustomUser.objects.create_user(email='signaltest@example.com', password='password')
    #         self.assertTrue(hasattr(user, 'golden_coins_account'))
    #         self.assertEqual(user.golden_coins_account.balance, 5) # Assuming 5 is WELCOME_BONUS_COINS_AMOUNT
    #         self.assertIsNotNone(user.referral_code)
    #         self.assertTrue(len(user.referral_code) > 0)
