from django.urls import path
from .views import (
    HomeView,
    VendorFoodItemListView, 
    VendorFoodItemCreateView, 
    VendorFoodItemUpdateView, 
    VendorFoodItemDeleteView,
    VendorListView,
    VendorDetailView,
    VendorProfileCreateView,
    BookingCreateView,
    TouristBookingListView,
    RegisterView,
    CustomLoginView,
    ThankYouView,
    SearchResultsView
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Home page
    path('', HomeView.as_view(), name='home'),
    # Authentication
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('thank-you/', ThankYouView.as_view(), name='thank-you'),
    # Vendor Food Management
    path('vendor/food-items/', VendorFoodItemListView.as_view(), name='vendor-fooditem-list'),
    path('vendor/food-items/add/', VendorFoodItemCreateView.as_view(), name='vendor-fooditem-add'),
    path('vendor/food-items/<int:pk>/edit/', VendorFoodItemUpdateView.as_view(), name='vendor-fooditem-edit'),
    path('vendor/food-items/<int:pk>/delete/', VendorFoodItemDeleteView.as_view(), name='vendor-fooditem-delete'),
    # Tourist Vendor Listing
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
    path('vendors/<int:pk>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('vendor/setup/', VendorProfileCreateView.as_view(), name='vendor-setup'),
    path('vendors/<int:pk>/book/', BookingCreateView.as_view(), name='booking-create'),
    # Tourist Booking Management
    path('my-bookings/', TouristBookingListView.as_view(), name='my-bookings'),
    # Search functionalit
    path('search/', SearchResultsView.as_view(), name='search-results')
]
