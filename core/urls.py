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
    BookingCreateView
)

urlpatterns = [
    # Home page
    path('', HomeView.as_view(), name='home'),
    # Vendor Food Management
    path('vendor/food-items/', VendorFoodItemListView.as_view(), name='vendor-fooditem-list'),
    path('vendor/food-items/add/', VendorFoodItemCreateView.as_view(), name='vendor-fooditem-add'),
    path('vendor/food-items/<int:pk>/edit/', VendorFoodItemUpdateView.as_view(), name='vendor-fooditem-edit'),
    path('vendor/food-items/<int:pk>/delete/', VendorFoodItemDeleteView.as_view(), name='vendor-fooditem-delete'),
    # Tourist Vendor Listing
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
    path('vendors/<int:pk>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('vendor/setup/', VendorProfileCreateView.as_view(), name='vendor-setup'),
    path('vendors/<int:pk>/book/', BookingCreateView.as_view(), name='booking-create')
]
