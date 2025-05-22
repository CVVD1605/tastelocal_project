from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse, reverse_lazy
from .models import FoodItem, VendorProfile, Booking, Cuisine, Review, TouristProfile
from .forms import VendorProfileForm, UserRegisterForm, EditProfileForm, ReviewForm, TouristAccountForm, TouristProfileForm, UserUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django import forms
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth import get_user_model
import json
from django.db.models import Q, Avg, Min, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from django.views import View
from decimal import Decimal

User = get_user_model()

# Admin site
class AdminDashboardView(TemplateView):
    template_name = 'admin/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_users = User.objects.count()
        total_tourists = User.objects.filter(is_tourist=True).count()
        total_vendors = User.objects.filter(is_vendor=True).count()
        total_reviews = Review.objects.count()
        reviews_with_comment = Review.objects.exclude(comment__isnull=True).exclude(comment__exact="").count()
        reviews_without_comment = total_reviews - reviews_with_comment

        total_bookings = Booking.objects.count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()

        # 📊 Signups Over Last 6 Months
        six_months_ago = timezone.now() - timedelta(days=180)
        signup_data = (
            User.objects.filter(date_joined__gte=six_months_ago)
            .annotate(month=TruncMonth('date_joined'))
            .values('month', 'is_tourist', 'is_vendor')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        monthly_data = {}
        for entry in signup_data:
            month_str = entry['month'].strftime('%b %Y')
            if month_str not in monthly_data:
                monthly_data[month_str] = {'tourists': 0, 'vendors': 0}
            if entry['is_tourist']:
                monthly_data[month_str]['tourists'] += entry['count']
            elif entry['is_vendor']:
                monthly_data[month_str]['vendors'] += entry['count']

        signup_months = list(monthly_data.keys())
        signup_tourists = [monthly_data[m]['tourists'] for m in signup_months]
        signup_vendors = [monthly_data[m]['vendors'] for m in signup_months]

        context.update({
            'total_users': total_users,
            'total_tourists': total_tourists,
            'total_vendors': total_vendors,
            'total_reviews': total_reviews,
            'reviews_with_comment': reviews_with_comment,
            'reviews_without_comment': reviews_without_comment,
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
            'signup_months': json.dumps(signup_months),
            'signup_tourists': json.dumps(signup_tourists),
            'signup_vendors': json.dumps(signup_vendors),
        })

        return context

# Admin user list view
class AdminUserListView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/admin_user_list.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = self.request.GET.get('role')

        users = User.objects.all().order_by('-date_joined')
        if role == 'tourist':
            users = users.filter(is_tourist=True)
        elif role == 'vendor':
            users = users.filter(is_vendor=True)

        context['users'] = users
        context['selected_role'] = role
        return context
    
# User form for admin editing
class AdminUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'is_staff', 'is_superuser']

# User list view
# Removed duplicate definition of AdminUserListView
# User update view
class AdminUserUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = AdminUserEditForm
    template_name = 'admin/user_edit.html'
    success_url = reverse_lazy('admin-user-list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "User updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error updating the user.")
        return super().form_invalid(form)

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
            'vendor_results': vendors.order_by('business_name').distinct(),
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
            return reverse_lazy('vendor-dashboard')
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
        return FoodItem.objects.filter(vendor=self.request.user.vendor_profile).order_by('name')

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

# Filter vendors by cuisine
class VendorDetailView(DetailView):
    model = VendorProfile
    template_name = 'vendors/vendor_detail.html'
    context_object_name = 'vendor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.object

        # 🔹 Food items and reviews
        context['food_items'] = FoodItem.objects.filter(vendor=vendor).order_by('name')
        context['reviews'] = vendor.reviews.select_related('user').order_by('-created_at')

        # 🔹 Recommended vendors based on cuisine (excluding the current one)
        context['similar_vendors'] = VendorProfile.objects.filter(
            cuisine=vendor.cuisine
        ).exclude(id=vendor.id).order_by('-average_rating')[:3]

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
        profile, _ = VendorProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        profile = form.save(commit=False)

        # DEBUG POSTED VALUES
        print("Posted lat/lng:", self.request.POST.get('latitude'), self.request.POST.get('longitude'))
        print("Posted address:", self.request.POST.get('location_text'))

        try:
            profile.latitude = Decimal(self.request.POST.get('latitude') or '0')
            profile.longitude = Decimal(self.request.POST.get('longitude') or '0')
        except Exception as e:
            print("Decimal conversion failed:", e)

        profile.location_text = self.request.POST.get('location_text', '')

        profile.save()
        messages.success(self.request, "Profile updated successfully.")
        return redirect('vendor-dashboard')

    
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

class TouristProfileUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'tourists/edit_profile.html'

    def get(self, request, *args, **kwargs):
        user_form = forms.modelform_factory(User, fields=['username', 'email', 'first_name', 'last_name'])(instance=request.user)
        profile_form = TouristProfileForm(instance=request.user.tourist_profile)
        return self.render_to_response({
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request, *args, **kwargs):
        user_form_class = forms.modelform_factory(User, fields=['username', 'email', 'first_name', 'last_name'])
        user_form = user_form_class(request.POST, instance=request.user)
        profile_form = TouristProfileForm(request.POST, request.FILES, instance=request.user.tourist_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('tourist-dashboard')

        return self.render_to_response({
            'user_form': user_form,
            'profile_form': profile_form
        })

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
    

@method_decorator(csrf_exempt, name='dispatch')
class TestBookingAPI(View):
    def post(self, request, vendor_id):
        # simulate booking logic
        return JsonResponse({"status": "success"}, status=200)
