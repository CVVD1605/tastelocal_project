from django import forms
from .models import VendorProfile, Booking, Review, TouristProfile
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()
CustomUser = get_user_model()

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

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'number_of_people', 'special_request']
        widgets = {
            'booking_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'booking_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'number_of_people': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'special_request': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any dietary needs or requests?'
            }),
        }

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class TouristProfileForm(forms.ModelForm):
    class Meta:
        model = TouristProfile
        fields = ['full_name', 'phone_number', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class TouristAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }