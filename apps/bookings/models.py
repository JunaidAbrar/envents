from django.db import models
from django.conf import settings
from apps.venues.models import Venue
from apps.services.models import Service

class Booking(models.Model):
    STATUS_CHOICES = (
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
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    guest_count = models.PositiveIntegerField()
    event_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Made nullable for existing records
    
    # Pricing fields
    venue_cost = models.DecimalField(max_digits=10, decimal_places=2)
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
        return f"Booking #{self.id} - {self.venue.name} on {self.event_date}"
    
    def save(self, *args, **kwargs):
        # Calculate total cost before saving
        if not self.total_cost:
            self.total_cost = self.venue_cost + self.services_cost
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
