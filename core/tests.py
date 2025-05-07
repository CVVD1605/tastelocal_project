from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class IntegrationTestIT001(TestCase):
    def setUp(self):
        self.vendor_user = get_user_model().objects.create_user(
            username='vendoruser', email='vendor@example.com', password='securepass123', is_vendor=True
        )

    def test_login_redirects_to_dashboard_and_loads_profile(self):
        login_url = reverse('login')
        dashboard_url = reverse('vendor-dashboard')

        response = self.client.post(login_url, {
            'username': 'vendoruser',
            'password': 'securepass123',
        })

        self.assertEqual(response.status_code, 302)  # Redirects after login
        self.assertRedirects(response, dashboard_url)

        # Follow redirect and check for vendor business name
        response = self.client.get(dashboard_url)
        self.assertContains(response, 'vendoruser')  # or vendor business name if set
