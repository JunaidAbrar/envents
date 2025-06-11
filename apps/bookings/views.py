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
    # Get all bookings for the current user with related objects in a single query
    bookings = Booking.objects.filter(user=request.user).select_related(
        'venue', 'venue_catering_package'
    ).prefetch_related('booking_services', 'booking_services__service')
    
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
    # Use select_related and prefetch_related to fetch related data in single queries
    booking = get_object_or_404(
        Booking.objects.select_related(
            'venue', 'user', 'venue_catering_package'
        ).prefetch_related(
            'booking_services', 
            'booking_services__service',
            'booking_services__package'
        ), 
        id=booking_id, 
        user=request.user
    )
    
    # Calculate time remaining until event
    now = timezone.now().date()
    days_remaining = (booking.event_date - now).days if booking.event_date > now else 0
    
    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
        'booking_services': booking.booking_services.all(),
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
                booking.status = 'quotation'  # Set initial status to quotation
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
                
                messages.success(request, f"Your booking request has been submitted and we'll prepare a quote for you. You can add services while we review your request.")
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
    booking = get_object_or_404(
        Booking.objects.select_related('venue', 'venue_catering_package'), 
        id=booking_id, 
        user=request.user
    )
    
    # Only allow adding services to pending or quotation bookings
    if booking.status not in ['pending', 'quotation']:
        messages.error(request, "You can only add services to bookings that are in quotation or pending state.")
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    # Check if venue catering is being used
    exclude_catering = booking.uses_venue_catering
    
    # Get all available services with prefetch_related for packages to avoid N+1 queries
    services = Service.objects.filter(status='approved').prefetch_related('packages').select_related('category')
    
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        package_id = request.POST.get('package_id')
        
        # Safely handle quantity as a text input
        try:
            quantity = int(request.POST.get('quantity', 1))
            # Ensure quantity is at least 1
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1
            
        special_requirements = request.POST.get('special_requirements', '')
        
        if service_id:
            service = get_object_or_404(Service.objects.prefetch_related('packages'), id=service_id)
            
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
            
    # Get current booking services with related data
    booking_services = booking.booking_services.select_related('service', 'package').all()
    
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
    booking = get_object_or_404(
        Booking.objects.select_related(
            'venue', 'venue_catering_package', 'user'
        ).prefetch_related(
            'booking_services',
            'booking_services__service'
        ),
        id=booking_id, 
        user=request.user
    )
    
    # Allow confirmation for pending or quotation statuses
    if booking.status not in ['pending', 'quotation']:
        messages.error(request, "This booking has already been processed or cannot be confirmed.")
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        # If it's a quotation, move it to pending status
        if booking.status == 'quotation':
            booking.status = 'pending'
            
        # The booking stays in 'pending' status for admin approval
        booking.save()
        
        messages.success(request, "Your booking request has been submitted successfully! Our team will review your request shortly.")
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    return render(request, 'bookings/confirm_booking.html', {
        'booking': booking,
        'booking_services': booking.booking_services.all()
    })

@login_required
def accept_quotation(request, booking_id):
    """Handle user acceptance of a quotation"""
    booking = get_object_or_404(
        Booking.objects.select_related('user'), 
        id=booking_id, 
        user=request.user,
        status='quotation'
    )
    
    if request.method == 'POST':
        # Update the booking status to pending (waiting for admin confirmation)
        booking.status = 'pending'
        booking.save()
        
        messages.success(request, "You have accepted the quotation. Your booking is now pending confirmation.")
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    return redirect('bookings:booking_detail', booking_id=booking.id)

@login_required
def create_service_booking(request):
    """Create a new service-only booking (without requiring a venue)"""
    # Get service_id and package_id from query parameters
    service_id = request.GET.get('service_id')
    package_id = request.GET.get('package_id')
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            with transaction.atomic():  # Use transaction to ensure data integrity
                booking = form.save(commit=False)
                booking.user = request.user
                booking.booking_type = 'service_only'
                booking.venue = None  # No venue for service-only bookings
                booking.status = 'quotation'  # Set initial status to quotation
                booking.venue_cost = 0  # No venue cost
                booking.services_cost = 0  # Initialize services cost
                booking.total_cost = 0  # Will be updated when services are added
                booking.save()
                
                # If a service was selected before booking creation, automatically add it
                if service_id:
                    try:
                        service = Service.objects.prefetch_related('packages').get(id=service_id, status='approved')
                        
                        # Determine price based on package or base price
                        package = None
                        price = service.base_price
                        
                        if package_id:
                            try:
                                package = service.packages.get(id=package_id, is_active=True)
                                price = package.price
                            except:
                                # If package doesn't exist, use default price
                                pass
                        
                        # Create booking service with default quantity=1
                        booking_service = BookingService.objects.create(
                            booking=booking,
                            service=service,
                            package=package,
                            quantity=1,
                            price=price,
                            special_requirements=''
                        )
                        
                        # Update booking costs
                        booking.services_cost = booking_service.price * booking_service.quantity
                        booking.total_cost = booking.services_cost
                        booking.save()
                        # Indicate that a service was automatically added in the redirect
                        return redirect(f'/bookings/{booking.id}/add-services/?auto_added=1')
                    except Service.DoesNotExist:
                        # If service doesn't exist or isn't approved, just continue without adding it
                        pass
                
                messages.success(request, "Your service booking request has been submitted and we'll prepare a quote for you. You can now select the services you need.")
                return redirect('bookings:add_services', booking_id=booking.id)
    else:
        form = BookingForm(initial={'booking_type': 'service_only'})
    
    # Store service information in context for the template
    context = {
        'form': form,
        'service_id': service_id,
        'package_id': package_id
    }
    
    # If service_id exists, add service details to context
    if service_id:
        try:
            service = Service.objects.get(id=service_id)
            context['selected_service'] = service
        except Service.DoesNotExist:
            pass
    
    return render(request, 'bookings/create_service_booking.html', context)
