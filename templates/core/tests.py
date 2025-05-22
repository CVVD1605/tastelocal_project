from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from core.models import VendorProfile, Booking
import time

User = get_user_model()

class SearchTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_search_thai_response_time(self):
        start = time.time()
        response = self.client.get('/search/?search=Thai')
        end = time.time()
        duration = end - start
        self.assertEqual(response.status_code, 200)
        self.assertLess(duration, 2.0, f"Search took too long: {duration:.2f}s")


class BookingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='vivi', password='password')
        self.client.login(username='vivi', password='password')
        self.vendor = VendorProfile.objects.create(
            user=self.user,
            business_name="Test Vendor",
            category="Local",
            location_text="City",
            phone="12345678",
            cuisine="Local",
            photo=SimpleUploadedFile("test.jpg", b"img", content_type="image/jpeg")
        )

    def test_booking_page_loads(self):
        response = self.client.get(reverse('vendor-booking', args=[self.vendor.id]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_booking_submission(self):
        response = self.client.post(reverse('vendor-booking', args=[self.vendor.id]), {
            'booking_date': '2025-05-20',
            'booking_time': '18:00',
            'number_of_people': 2,
            'special_request': 'Window seat'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Booking.objects.exists())
