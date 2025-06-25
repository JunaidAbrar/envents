from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.contrib.sites.models import Site


def send_booking_status_email(booking, status_type=None, additional_context=None):
    """
    Generic function to send booking status update emails
    
    Args:
        booking: The Booking object
        status_type: Status type (for template selection, if None uses booking.status)
        additional_context: Any additional context to pass to the template
    """
    status = status_type or booking.status
    
    # Configure email based on status
    templates = {
        'confirmed': 'emails/booking_confirmation.html',
        'quotation': 'emails/booking_quotation.html',
        'cancelled': 'emails/booking_cancelled.html',
        'completed': 'emails/booking_completed.html',
        'pending': 'emails/booking_status_update.html',
    }
    
    subjects = {
        'confirmed': f"Your Booking #{booking.id} is Confirmed",
        'quotation': f"Price Quote for Your Booking #{booking.id}",
        'cancelled': f"Your Booking #{booking.id} has been Cancelled",
        'completed': f"Your Booking #{booking.id} is Completed",
        'pending': f"Your Booking #{booking.id} Status Update",
    }
    
    # Get the correct template and subject
    template = templates.get(status, 'emails/booking_status_update.html')
    subject = subjects.get(status, f"Update on Your Booking #{booking.id}")
    
    try:
        # Get the absolute URL to the booking detail
        current_site = Site.objects.get_current()
        booking_url = f"https://{current_site.domain}{reverse('bookings:booking_detail', args=[booking.id])}"
        
        # Prepare context
        context = {
            'booking': booking,
            'booking_url': booking_url,
            'status': status,
        }
        
        # Add any additional context
        if additional_context:
            context.update(additional_context)
        
        # Render HTML email
        html_message = render_to_string(template, context)
        
        # Plain text version for email clients that don't support HTML
        plain_message = strip_tags(html_message)
        
        # Send the email
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        # Log the error but don't crash the application
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending booking status email for booking #{booking.id}: {str(e)}")
        return False
