from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse, reverse_lazy
from .models import FoodItem, VendorProfile, Booking, Cuisine, Review, TouristProfile
from .forms import VendorProfileForm, UserRegisterForm, EditProfileForm, ReviewForm, TouristAccountForm, TouristProfileForm, UserUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Min
from django.utils import timezone
from datetime import timedelta
from django.views import View

User = get_user_model()

# Home page view
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_vendors'] = VendorProfile.objects.prefetch_related('food_items').order_by('-created_at')[:3]
        return context


class SearchResultsView(TemplateView):
    template_name = 'search/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        request = self.request
        query = request.GET.get('search', '')
        selected_cuisine = request.GET.get('cuisine')
        selected_price = request.GET.get('price')
        selected_rating = request.GET.get('rating')
        sort = request.GET.get('sort')  # 👈 New line to catch `sort=top`

        # Handle sort=top as a shortcut for selected_rating = 4
        if sort == 'top' and not selected_rating:
            selected_rating = '4'

        # Annotate vendors with average rating and minimum price
        vendors = VendorProfile.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            min_price=Min('food_items__price')
        )

        # Text search
        if query:
            vendors = vendors.filter(
                Q(business_name__icontains=query) |
                Q(description__icontains=query)
            )

        if selected_cuisine:
            vendors = vendors.filter(cuisine__iexact=selected_cuisine)

        if selected_price:
            try:
                vendors = vendors.filter(min_price__lte=int(selected_price))
            except ValueError:
                pass  # Fail silently if price input is not numeric

        if selected_rating:
            try:
                vendors = vendors.filter(avg_rating__gte=int(selected_rating))
            except ValueError:
                pass  # Same for rating

        context.update({
            'query': query,
            'vendor_results': vendors.distinct(),
            'selected_cuisine': selected_cuisine,
            'selected_price': selected_price,
            'selected_rating': selected_rating,
            'sort': sort,
            'today': timezone.now() - timedelta(days=7),
        })

        return context

# Register view for new users
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_vendor:
            return reverse_lazy('vendor-fooditem-list')
        elif user.is_tourist:
            return reverse_lazy('tourist-dashboard')
        return reverse_lazy('home')

# Custom logout view
def custom_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')  # or use reverse_lazy('home')
# Custom registration view
class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('thank-you')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = self.request.GET.get('role', 'tourist')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        role = self.request.GET.get('role')
        if role in ['tourist', 'vendor']:
            kwargs['initial_role'] = role  # Optional use if your form shows the role
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object

        # Fix here: get role from GET, not from form.cleaned_data
        role = self.request.GET.get('role', 'tourist')
        if role == 'vendor':
            user.is_vendor = True
        elif role == 'tourist':
            user.is_tourist = True
        user.save()

        login(self.request, user)
        return redirect(f"{reverse_lazy('thank-you')}?role={role}")

# Thank you page after registration
class ThankYouView(TemplateView):
    template_name = 'auth/thank_you.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = self.request.GET.get('role', 'tourist')
        return context

# Edit Profile for Tourist
class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'tourists/edit_profile.html'
    success_url = reverse_lazy('tourist-dashboard')  # or any confirmation page

    def get_object(self, queryset=None):
        return self.request.user

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
        context['reviews'] = self.object.reviews.select_related('user').order_by('-created_at')
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

# Vendor Profile Update
class VendorProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = VendorProfile
    form_class = VendorProfileForm
    template_name = 'vendors/vendor_profile_form.html'

    def get_object(self):
        return self.request.user.vendor_profile

    def get_success_url(self):
        messages.success(self.request, "Profile updated successfully.")
        return reverse('vendor-dashboard')  # or wherever the vendor lands
    
## Vendor Dashboard
class VendorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'vendors/vendor_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendor'] = self.request.user.vendor_profile
        return context
    
# Dashboard for Tourist
class TouristDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tourists/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Bookings already present
        context['bookings'] = Booking.objects.filter(tourist=user).select_related('vendor').order_by('-booking_date')

        # Add submitted reviews
        context['my_reviews'] = Review.objects.filter(user=self.request.user).select_related('vendor').order_by('-created_at')


        return context

# Edit Tourist Profile
@login_required
def edit_tourist_profile(request):
    user = request.user
    profile, created = TouristProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = EditProfileForm(request.POST, instance=user)
        profile_form = TouristProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('tourist-dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        user_form = EditProfileForm(instance=user)
        profile_form = TouristProfileForm(instance=profile)

    return render(request, 'tourists/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

class TouristProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = TouristProfile
    form_class = TouristProfileForm
    template_name = 'tourists/edit_profile.html'

    def get_object(self):
        return self.request.user.tourist_profile

    def get_success_url(self):
        messages.success(self.request, "Profile updated successfully.")
        return reverse('tourist-dashboard')

# For Tourists – to see their own bookings (already exists):
class TouristBookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/my_bookings.html'
    context_object_name = 'bookings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now().date()

        context['upcoming_bookings'] = Booking.objects.filter(
            tourist=self.request.user, booking_date__gte=now
        ).order_by('booking_date')

        context['past_bookings'] = Booking.objects.filter(
            tourist=self.request.user, booking_date__lt=now
        ).order_by('-booking_date')

        return context

# Password Change for Tourist
class TouristPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('tourist-dashboard')  
# # Update an existing booking  a new booking
class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = ['booking_date', 'booking_time', 'number_of_people', 'special_request']
    template_name = 'bookings/booking_form.html'  # reuse existing form
    success_url = reverse_lazy('tourist-dashboard')

    def get_queryset(self):
        return Booking.objects.filter(tourist=self.request.user)

# Booking Creation
class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['booking_date', 'booking_time', 'number_of_people', 'special_request']
    template_name = 'bookings/booking_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'is_tourist') or not request.user.is_tourist:
            messages.warning(request, "You need to be logged in as a tourist to make a booking.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tourist = self.request.user
        form.instance.vendor = get_object_or_404(VendorProfile, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Booking successful!")
        return reverse('my-bookings')  # ✅ Return URL string instead of redirect

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendor'] = get_object_or_404(VendorProfile, pk=self.kwargs['pk'])
        return context

# Cancel a booking
class BookingCancelView(LoginRequiredMixin, TemplateView):
    template_name = 'bookings/booking_cancel_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'], tourist=self.request.user)
        context['booking'] = booking
        return context

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=kwargs['pk'], tourist=request.user)
        if booking.status == 'pending':
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, f"Booking for {booking.vendor.business_name} has been cancelled.")
        else:
            messages.warning(request, "This booking cannot be cancelled.")
        return redirect('my-bookings')

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.vendor = get_object_or_404(VendorProfile, pk=kwargs['vendor_id'])

        # Prevent multiple reviews
        if Review.objects.filter(user=request.user, vendor=self.vendor).exists():
            messages.warning(request, "You've already reviewed this vendor.")
            return redirect('vendor-detail', pk=self.vendor.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.vendor = self.vendor
        response = super().form_valid(form)
    
        # Update vendor's average rating
        avg_rating = Review.objects.filter(vendor=self.vendor).aggregate(avg=Avg('rating'))['avg']
        self.vendor.average_rating = avg_rating or 0.0
        self.vendor.save()

        return response

    def get_success_url(self):
        return reverse('vendor-detail', kwargs={'pk': self.vendor.pk})

# For Vendors – to see incoming bookings for their business:
class VendorBookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'vendors/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(
            vendor=self.request.user.vendor_profile
        ).select_related('tourist').order_by('-booking_date')

# For Vendors – to accept/decline individual bookings:
class VendorBookingUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, vendor=request.user.vendor_profile)
        new_status = request.GET.get('status')

        if new_status in ['confirmed', 'declined'] and booking.status == 'pending':
            booking.status = new_status
            booking.save()
            messages.success(request, f"Booking has been {new_status}.")
        else:
            messages.warning(request, "Invalid or duplicate action.")

        return redirect('vendor-booking-list')
