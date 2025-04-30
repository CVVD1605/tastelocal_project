from django.urls import path, include
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
    SearchResultsView,
    BookingCancelView,
    EditProfileView,
    TouristDashboardView,
    BookingUpdateView,
    TouristPasswordChangeView,
    ReviewCreateView  # Added missing import
)
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView

urlpatterns = [
    # Home page
    path('', HomeView.as_view(), name='home'),
    # Authentication
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('thank-you/', ThankYouView.as_view(), name='thank-you'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/password_change/',TouristPasswordChangeView.as_view(),name='password_change'),
    path('accounts/password_change/done/',PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),name='password_change_done'),
    # Vendor Food Management
    path('vendor/food/create/', VendorFoodItemCreateView.as_view(), name='vendor-fooditem-create'),
    path('vendor/food-items/', VendorFoodItemListView.as_view(), name='vendor-fooditem-list'),
    path('vendor/food-items/add/', VendorFoodItemCreateView.as_view(), name='vendor-fooditem-add'),
    path('vendor/food-items/<int:pk>/edit/', VendorFoodItemUpdateView.as_view(), name='vendor-fooditem-edit'),
    path('vendor/food-items/<int:pk>/delete/', VendorFoodItemDeleteView.as_view(), name='vendor-fooditem-delete'),
    # Tourist Vendor Listing
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
    path('vendors/<int:pk>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('vendor/setup/', VendorProfileCreateView.as_view(), name='vendor-setup'),
    path('vendors/<int:pk>/book/', BookingCreateView.as_view(), name='vendor-booking'),
    # Tourist Booking Management
    path('my-bookings/', TouristBookingListView.as_view(), name='my-bookings'),
    path('booking/<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
    path('bookings/<int:pk>/edit/', BookingUpdateView.as_view(), name='booking-update'),
    path('profile/edit/', EditProfileView.as_view(), name='edit-profile'),
    path('tourist/dashboard/', TouristDashboardView.as_view(), name='tourist-dashboard'),
    # Search functionalit
    path('search/', SearchResultsView.as_view(), name='search-results'),
    # Vendor Review
    path('vendors/<int:vendor_id>/review/', ReviewCreateView.as_view(), name='vendor-review'),

]
