from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, VendorProfile, TouristProfile

# Automatically create VendorProfile or TouristProfile when a new user is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_vendor:
            VendorProfile.objects.create(user=instance, business_name=instance.username)
        elif instance.is_tourist:
            TouristProfile.objects.create(user=instance, full_name=instance.username)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_vendor:
        instance.vendor_profile.save()
    elif instance.is_tourist:
        instance.tourist_profile.save()
