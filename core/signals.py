from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, VendorProfile, TouristProfile

# Automatically create profile upon user creation
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    print("🔧 Signal received for user:", instance.username, " | is_vendor:", instance.is_vendor)
    if created:
        if instance.is_vendor:
            print("✅ Creating VendorProfile...")
            VendorProfile.objects.get_or_create(user=instance, defaults={'business_name': instance.username})
        elif instance.is_tourist:
            print("✅ Creating TouristProfile...")
            TouristProfile.objects.get_or_create(user=instance, defaults={'full_name': instance.username})


# Only save if profile already exists (prevents crash)
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_vendor and hasattr(instance, 'vendor_profile'):
        instance.vendor_profile.save()
    elif instance.is_tourist and hasattr(instance, 'tourist_profile'):
        instance.tourist_profile.save()
