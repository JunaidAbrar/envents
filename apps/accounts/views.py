from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileForm
from django.contrib.auth import login
from apps.bookings.models import Booking

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Envents.')
            return redirect('accounts:profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    from django.utils import timezone
    import datetime
    
    # Get all user bookings and count
    all_user_bookings = Booking.objects.filter(user=request.user)
    booking_count = all_user_bookings.count()
    
    # Get upcoming bookings (bookings with event_date in the future)
    today = timezone.now().date()
    upcoming_bookings = all_user_bookings.filter(
        event_date__gte=today
    ).order_by('event_date', 'start_time')[:5]
    
    # Get recent bookings for backward compatibility
    recent_bookings = all_user_bookings.order_by('-created_at')[:5]
    
    # Get favorite venues and services (not just counts)
    favorite_venues = request.user.favorite_venues.select_related('venue').all()[:4]
    favorite_services = request.user.favorite_services.select_related('service').all()[:4]
    
    # Get counts
    favorite_venues_count = request.user.favorite_venues.count()
    favorite_services_count = request.user.favorite_services.count()
    
    context = {
        'user': request.user,
        'recent_bookings': recent_bookings,
        'upcoming_bookings': upcoming_bookings,
        'booking_count': booking_count,
        'favorite_venues': favorite_venues,
        'favorite_services': favorite_services,
        'favorite_venues_count': favorite_venues_count,
        'favorite_services_count': favorite_services_count
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def favorites(request):
    favorite_venues = request.user.favorite_venues.all()
    favorite_services = request.user.favorite_services.all()
    context = {
        'favorite_venues': favorite_venues,
        'favorite_services': favorite_services,
    }
    return render(request, 'accounts/favorites.html', context)

@login_required
def user_bookings(request):
    # Redirect to the main bookings page which has better UI
    return redirect('bookings:booking_list')
