from django import forms
from .models import VendorProfile
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'description', 'category', 'location_text', 'latitude', 'longitude', 'phone', 'photo_url', 'cuisine']

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
    
    def save(self, commit=True):
        user = super().save(commit=False)
         # Set the user’s password (hash it)
        user.set_password(self.cleaned_data['password'])

         # Set role flags
        role = self.cleaned_data.get('role')
        if role == 'vendor':
            user.is_vendor = True
        elif role == 'tourist':
            user.is_tourist = True

        if commit:
            user.save()

        return user
