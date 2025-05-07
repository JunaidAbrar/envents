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
    user_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')[:5]
    context = {
        'user': request.user,
        'recent_bookings': user_bookings
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
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/user_bookings.html', {'bookings': bookings})
