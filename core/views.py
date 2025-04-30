from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from .models import FoodItem, VendorProfile, Booking
from .forms import VendorProfileForm  # Import the missing form
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Home page view
class HomeView(TemplateView):
    template_name = 'home.html'

# List all food items for a Vendor
class VendorFoodItemListView(LoginRequiredMixin, ListView):
    model = FoodItem
    template_name = 'vendors/fooditem_list.html'
    context_object_name = 'fooditems'

    def get_queryset(self):
        return FoodItem.objects.filter(vendor=self.request.user.vendor_profile)

# Create a new food item
class VendorFoodItemCreateView(LoginRequiredMixin, CreateView):
    model = FoodItem
    fields = ['name', 'description', 'price', 'image']
    template_name = 'vendors/fooditem_form.html'
    success_url = reverse_lazy('vendor-fooditem-list')

    def form_valid(self, form):
        form.instance.vendor = self.request.user.vendor_profile
        return super().form_valid(form)

# Update an existing food item
class VendorFoodItemUpdateView(LoginRequiredMixin, UpdateView):
    model = FoodItem
    fields = ['name', 'description', 'price', 'image']
    template_name = 'vendors/fooditem_form.html'
    success_url = reverse_lazy('vendor-fooditem-list')

# Delete a food item
class VendorFoodItemDeleteView(LoginRequiredMixin, DeleteView):
    model = FoodItem
    template_name = 'vendors/fooditem_confirm_delete.html'
    success_url = reverse_lazy('vendor-fooditem-list')

class VendorListView(ListView):
    model = VendorProfile
    template_name = 'vendors/vendor_list.html'
    context_object_name = 'vendors'

# This view will list all vendors
class VendorDetailView(DetailView):
    model = VendorProfile
    template_name = 'vendors/vendor_detail.html'
    context_object_name = 'vendor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['food_items'] = FoodItem.objects.filter(vendor=self.object)
        return context
    
# Vendor Profile Creation
@method_decorator(login_required, name='dispatch')
class VendorProfileCreateView(CreateView):
    model = VendorProfile
    form_class = VendorProfileForm
    template_name = 'vendor/vendor_profile_form.html'
    success_url = reverse_lazy('vendor-fooditem-list')  # after setup

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

#
class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['booking_date', 'booking_time', 'number_of_people', 'special_request']
    template_name = 'bookings/booking_form.html'

    def form_valid(self, form):
        form.instance.tourist = self.request.user
        form.instance.vendor = VendorProfile.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('my-bookings')  # we'll build this next