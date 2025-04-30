from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from .models import FoodItem, VendorProfile, Booking
from .forms import VendorProfileForm, UserRegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model

User = get_user_model()

# Home page view
class HomeView(TemplateView):
    template_name = 'home.html'

# Register view for new users
class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    authentication_form = AuthenticationForm

    def get_success_url(self):
        user = self.request.user
        if user.is_vendor:
            return reverse_lazy('vendor-fooditem-list')
        elif user.is_tourist:
            return reverse_lazy('my-bookings')
        return reverse_lazy('home')

class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'auth/register.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        role = self.request.GET.get('role')
        if role in ['tourist', 'vendor']:
            kwargs['initial_role'] = role
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        role = form.cleaned_data.get('role', 'tourist')
        return redirect(f"{reverse_lazy('thank-you')}?role={role}")
    

# Thank you page after registration
class ThankYouView(TemplateView):
    template_name = 'auth/thank_you.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = self.request.GET.get('role', 'tourist')
        return context


# Create a new food item
class VendorFoodItemCreateView(LoginRequiredMixin, CreateView):
    model = FoodItem
    fields = ['name', 'description', 'price', 'image']
    template_name = 'vendors/fooditem_form.html'
    success_url = reverse_lazy('vendor-fooditem-list')

    def form_valid(self, form):
        form.instance.vendor = self.request.user.vendor_profile
        return super().form_valid(form)
    
# List all food items for a Vendor
class VendorFoodItemListView(LoginRequiredMixin, ListView):
    model = FoodItem
    template_name = 'vendors/fooditem_list.html'
    context_object_name = 'fooditems'

    def get_queryset(self):
        return FoodItem.objects.filter(vendor=self.request.user.vendor_profile)

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

# This view will list all vendors
class VendorListView(ListView):
    model = VendorProfile
    template_name = 'vendors/vendor_list.html'
    context_object_name = 'vendors'

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
    template_name = 'vendors/vendor_profile_form.html'
    success_url = reverse_lazy('vendor-fooditem-list')  # after setup

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
# Booking Creation
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
    
# List all bookings for a Tourist
class TouristBookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/my_bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(tourist=self.request.user).select_related('vendor').order_by('-booking_date')
