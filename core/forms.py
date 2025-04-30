from django import forms
from .models import VendorProfile

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'description', 'category', 'location_text', 'latitude', 'longitude', 'phone', 'photo_url']
