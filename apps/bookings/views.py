from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from decimal import Decimal

from .models import Booking, BookingService
from apps.venues.models import Venue
from apps.services.models import Service
from .forms import BookingForm, BookingServiceForm

@login_required
def booking_list(request):
    """Display all bookings for the current user"""
    # Get all bookings for the current user
    bookings = Booking.objects.filter(user=request.user)
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    # Sorting
    sort = request.GET.get('sort', '-event_date')
    bookings = bookings.order_by(sort)
    
    # Pagination
    paginator = Paginator(bookings, 5)  # 5 bookings per page
    page = request.GET.get('page')
    try:
        bookings = paginator.page(page)
    except PageNotAnInteger:
        bookings = paginator.page(1)
    except EmptyPage:
        bookings = paginator.page(paginator.num_pages)
    
    return render(request, 'bookings/booking_list.html', {
        'bookings': bookings,
        'current_status': status,
        'sort': sort
    })

@login_required
def booking_detail(request, booking_id):
    """Display details for a specific booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking_services = booking.booking_services.all()
    
    # Calculate time remaining until event
    now = timezone.now().date()
    days_remaining = (booking.event_date - now).days if booking.event_date > now else 0
    
    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
        'booking_services': booking_services,
        'days_remaining': days_remaining
    })

@login_required
def create_booking(request, venue_slug):
    """Create a new booking for a venue"""
    venue = get_object_or_404(Venue, slug=venue_slug, status='approved')
    
    if request.method == 'POST':
        form = BookingForm(request.POST, venue=venue)
        if form.is_valid():
            with transaction.atomic():
                booking = form.save(commit=False)
                booking.user = request.user
                booking.venue = venue
                booking.booking_type = 'venue'  # Explicitly set booking type for venue bookings
                hours_diff = booking.end_time.hour - booking.start_time.hour
                minutes_diff = booking.end_time.minute - booking.start_time.minute
                time_fraction = Decimal(hours_diff + (minutes_diff / 60))
                booking.venue_cost = venue.price_per_hour * time_fraction
                booking.services_cost = 0  # Initialize services cost
                
                # Handle venue catering package selection
                if booking.uses_venue_catering and booking.venue_catering_package:
                    booking.venue_catering_cost = booking.venue_catering_package.price * booking.venue_catering_count
                else:
                    booking.uses_venue_catering = False
                    booking.venue_catering_package = None
                    booking.venue_catering_count = 0
                    booking.venue_catering_cost = 0
                
                # Calculate total cost (venue + services + catering)
                booking.total_cost = booking.venue_cost + booking.services_cost + booking.venue_catering_cost
                booking.save()
                
                messages.success(request, f"Booking created successfully! You can now add services to your booking.")
                return redirect('bookings:add_services', booking_id=booking.id)
    else:
        form = BookingForm(initial={'booking_type': 'venue'}, venue=venue)
    
    return render(request, 'bookings/create_booking.html', {
        'form': form,
        'venue': venue
    })

@login_required
def add_services(request, booking_id):
    """Add services to an existing booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Only allow adding services to pending bookings
    if booking.status != 'pending':
        messages.error(request, "You can only add services to pending bookings.")
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    # Check if venue catering is being used
    exclude_catering = booking.uses_venue_catering
    
    # Get all available services
    services = Service.objects.filter(status='approved')
    
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        package_id = request.POST.get('package_id')
        quantity = int(request.POST.get('quantity', 1))
        special_requirements = request.POST.get('special_requirements', '')
        
        if service_id:
            service = get_object_or_404(Service, id=service_id)
            
            # Prevent adding catering services if venue catering is selected
            if exclude_catering:
                try:
                    from apps.services.models import ServiceCategory
                    catering_category = ServiceCategory.objects.get(name='Catering')
                    if service.category == catering_category:
                        messages.error(request, "You cannot add external catering services when using venue catering.")
                        return redirect('bookings:add_services', booking_id=booking.id)
                except ServiceCategory.DoesNotExist:
                    pass  # If no catering category exists, allow all services
            
            package = None
            price = service.base_price
            
            # Check if a package was selected
            if package_id:
                package = get_object_or_404(service.packages.filter(is_active=True), id=package_id)
                price = package.price
            
            # Create or update the booking service
            with transaction.atomic():
                booking_service, created = BookingService.objects.update_or_create(
                    booking=booking,
                    service=service,
                    defaults={
                        'package': package,
                        'quantity': quantity,
                        'price': price,
                        'special_requirements': special_requirements
                    }
                )
                
                # Update the booking's services_cost
                booking.services_cost = sum(bs.price * bs.quantity for bs in booking.booking_services.all())
                # Calculate total cost including venue, services, and venue catering
                booking.total_cost = (booking.venue_cost or 0) + booking.services_cost + (booking.venue_catering_cost or 0)
                booking.save()
            
            if created:
                messages.success(request, f"{service.name} added to your booking.")
            else:
                messages.success(request, f"{service.name} updated in your booking.")
                
            return redirect('bookings:add_services', booking_id=booking.id)
            
    # Get current booking services
    booking_services = booking.booking_services.all()
    
    # If venue catering is selected, create a form that excludes catering services
    form = BookingServiceForm(exclude_catering=exclude_catering)
    
    return render(request, 'bookings/add_services.html', {
        'booking': booking,
        'services': services,
        'booking_services': booking_services,
        'form': form,
        'exclude_catering': exclude_catering
    })

@login_required
def confirm_booking(request, booking_id):
    """Confirm a booking request"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status != 'pending':
        messages.error(request, "This booking has already been processed.")
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        # The booking stays in 'pending' status for admin approval
        # We just record that the user has confirmed their request
        booking.save()
        
        messages.success(request, "Your booking request has been submitted successfully! The venue owner will review your request shortly.")
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    return render(request, 'bookings/confirm_booking.html', {
        'booking': booking,
        'booking_services': booking.booking_services.all()
    })

@login_required
def create_service_booking(request):
    """Create a new service-only booking (without requiring a venue)"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            with transaction.atomic():  # Use transaction to ensure data integrity
                booking = form.save(commit=False)
                booking.user = request.user
                booking.booking_type = 'service_only'
                booking.venue = None  # No venue for service-only bookings
                booking.venue_cost = 0  # No venue cost
                booking.services_cost = 0  # Initialize services cost
                booking.total_cost = 0  # Will be updated when services are added
                booking.save()
                
                messages.success(request, "Service booking created successfully! Please add services to your booking.")
                return redirect('bookings:add_services', booking_id=booking.id)
    else:
        form = BookingForm(initial={'booking_type': 'service_only'})
    
    return render(request, 'bookings/create_service_booking.html', {
        'form': form
    })
