from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Booking
from .utils import send_booking_status_email


@receiver(pre_save, sender=Booking)
def handle_booking_status_change(sender, instance, **kwargs):
    """
    Signal handler to detect booking status changes and send appropriate emails
    """
    # Skip for new bookings (no previous state)
    if not instance.pk:
        return
    
    # Get the current state from the database
    try:
        old_instance = Booking.objects.get(pk=instance.pk)
        old_status = old_instance.status
        
        # Status has changed
        if old_status != instance.status:
            # Send email based on the new status
            if instance.status == 'quotation' and instance.quoted_price:
                send_booking_status_email(instance)
            elif instance.status == 'confirmed':
                send_booking_status_email(instance)
            elif instance.status == 'cancelled':
                send_booking_status_email(instance)
            elif instance.status == 'completed':
                send_booking_status_email(instance)
                
    except Booking.DoesNotExist:
        # New booking, no need to send status change email
        pass
