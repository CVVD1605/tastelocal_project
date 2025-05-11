from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import VendorProfile

class IntegrationTestIT001(TestCase):
    def setUp(self):
        # Create test vendor user (auto VendorProfile via signal)
        self.vendor_user = get_user_model().objects.create_user(
            username='vendoruser',
            email='vendor@example.com',
            password='securepass123',
            is_vendor=True
        )

    def test_login_redirects_to_dashboard_and_loads_profile(self):
        login_url = reverse('login')
        dashboard_url = reverse('vendor-dashboard')

        # Step 1: Log in
        response = self.client.post(login_url, {
            'username': 'vendoruser',
            'password': 'securepass123',
        })

        # Step 2: Follow redirection manually to dashboard
        self.assertRedirects(response, dashboard_url)

        # Step 3: Access the dashboard
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 200)

        # Step 4: Check if profile name or vendor info appears
        self.assertContains(response, 'vendoruser')  # Assumes business_name = username

class UserAcceptanceTestUAT001(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tourist123',
            email='tourist123@example.com',
            password='securepass123',
            is_tourist=True
        )

    def test_tourist_login_redirects_to_dashboard(self):
        login_url = reverse('login')
        dashboard_url = reverse('tourist-dashboard')

        response = self.client.post(login_url, {
            'username': 'tourist123',
            'password': 'securepass123'
        })

        self.assertRedirects(response, dashboard_url)

        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tourist123')
