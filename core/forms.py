from django import forms
from .models import VendorProfile
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'description', 'category', 'location_text', 'latitude', 'longitude', 'phone', 'photo_url']


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    ROLE_CHOICES = (
        ('tourist', 'Tourist'),
        ('vendor', 'Vendor'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def __init__(self, *args, **kwargs):
        initial_role = kwargs.pop('initial_role', None)
        super().__init__(*args, **kwargs)
        if initial_role:
            self.fields['role'].initial = initial_role