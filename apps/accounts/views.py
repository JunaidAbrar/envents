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
    
    # Get all user bookings with related data to reduce N+1 queries
    all_user_bookings = Booking.objects.filter(user=request.user).select_related('venue')
    booking_count = all_user_bookings.count()
    
    # Get upcoming bookings with all related data in a single query
    today = timezone.now().date()
    upcoming_bookings = all_user_bookings.filter(
        event_date__gte=today
    ).select_related(
        'venue', 'venue_catering_package'
    ).prefetch_related(
        'booking_services', 'booking_services__service'
    ).order_by('event_date', 'start_time')[:5]
    
    # Get recent bookings with all related data in a single query
    recent_bookings = all_user_bookings.select_related(
        'venue', 'venue_catering_package'
    ).prefetch_related(
        'booking_services', 'booking_services__service'
    ).order_by('-created_at')[:5]
    
    # Get favorite venues and services with fully loaded related objects
    favorite_venues = request.user.favorite_venues.select_related('venue').prefetch_related(
        'venue__category', 'venue__photos'
    ).all()[:4]
    
    favorite_services = request.user.favorite_services.select_related('service').prefetch_related(
        'service__photos'
    ).all()[:4]
    
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
    # Use select_related and prefetch_related to optimize database queries
    favorite_venues = request.user.favorite_venues.select_related('venue').prefetch_related(
        'venue__category', 'venue__photos', 'venue__amenities'
    ).all()
    
    favorite_services = request.user.favorite_services.select_related('service').prefetch_related(
        'service__category', 'service__photos'
    ).all()
    
    context = {
        'favorite_venues': favorite_venues,
        'favorite_services': favorite_services,
    }
    return render(request, 'accounts/favorites.html', context)

@login_required
def user_bookings(request):
    # Redirect to the main bookings page which has better UI
    return redirect('bookings:booking_list')
