from django.db import models
from django.conf import settings
from apps.venues.models import Venue, VenueCateringPackage
from apps.services.models import Service, ServicePackage

class Booking(models.Model):
    STATUS_CHOICES = (
        ('quotation', 'Quotation'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('refunded', 'Refunded'),
    )
    
    BOOKING_TYPE_CHOICES = (
        ('venue', 'Venue Booking'),
        ('service_only', 'Service Only'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='bookings',
        null=True,  # Allow null for service-only bookings
        blank=True  # Optional in forms
    )
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES, default='venue')
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    guest_count = models.PositiveIntegerField()
    event_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='quotation')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Made nullable for existing records
    
    # Quotation fields
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quoted_message = models.TextField(blank=True, null=True, help_text="Admin message for the quotation")
    
    # Venue catering package fields
    venue_catering_package = models.ForeignKey(
        VenueCateringPackage,
        on_delete=models.SET_NULL,
        related_name='bookings',
        null=True,
        blank=True
    )
    venue_catering_count = models.PositiveIntegerField(default=0)
    uses_venue_catering = models.BooleanField(default=False)
    venue_catering_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Pricing fields
    venue_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    services_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional details
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-event_date', '-created_at']
        indexes = [
            models.Index(fields=['event_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        if self.venue:
            return f"Booking #{self.id} - {self.venue.name} on {self.event_date}"
        else:
            return f"Service Booking #{self.id} - {self.event_type} on {self.event_date}"
    
    def save(self, *args, **kwargs):
        # Ensure consistency between booking_type and venue
        if self.booking_type == 'service_only':
            self.venue = None
            self.venue_cost = 0
            self.venue_catering_package = None
            self.uses_venue_catering = False
            self.venue_catering_cost = 0
        
        # Calculate venue catering cost if applicable
        if self.uses_venue_catering and self.venue_catering_package:
            self.venue_catering_cost = self.venue_catering_package.price * self.venue_catering_count
        else:
            self.venue_catering_cost = 0
        
        # Calculate total cost before saving
        self.total_cost = (self.venue_cost or 0) + (self.services_cost or 0) + (self.venue_catering_cost or 0)
        super().save(*args, **kwargs)

class BookingService(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='booking_services'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='booking_services'
    )
    package = models.ForeignKey(
        ServicePackage,
        on_delete=models.SET_NULL,
        related_name='booking_services',
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    special_requirements = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('booking', 'service')
    
    def __str__(self):
        return f"{self.service.name} for Booking #{self.booking.id}"
    
    @property
    def total_price(self):
        return self.quantity * self.price
