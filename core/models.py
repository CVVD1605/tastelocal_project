from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django import forms

class CustomUser(AbstractUser):
    is_tourist = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)

    def __str__(self):
        return str(self.username)

# NEW TouristProfile
class TouristProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='tourist_profile')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='tourist_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.full_name)

# NEW VendorProfile
class VendorProfile(models.Model):
    CUISINE_CHOICES = [
        ('Thai', 'Thai'),
        ('Japanese', 'Japanese'),
        ('Indian', 'Indian'),
        ('Italian', 'Italian'),
        ('Local', 'Local'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, default="General", blank=True)
    location_text = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    photo_url = models.URLField(blank=True, null=True)
    average_rating = models.FloatField(default=0.0)
    cuisine = models.CharField(max_length=50, choices=CUISINE_CHOICES, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.business_name)

class FoodItem(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='food_items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='food_items/', blank=True, null=True)
    objects = models.Manager()  # Ensure a default manager is defined
    created_at = models.DateTimeField(auto_now_add=True)

      # Ensure a default manager is defined
    objects = models.Manager()
    def __str__(self):
        return str(self.name)
    
class Booking(models.Model):
    tourist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    booking_time = models.TimeField()
    number_of_people = models.PositiveIntegerField()
    special_request = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Booking by {self.tourist.username} at {self.vendor.business_name}"
    
class Cuisine(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
# NEW Review Model
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review for {self.vendor.business_name}"


