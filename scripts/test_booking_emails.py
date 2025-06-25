#!/usr/bin/env python
"""
Script to test the booking email notifications system.

Usage:
    python test_booking_emails.py <booking_id> <status>

    status can be: quotation, pending, confirmed, cancelled, completed

Example:
    python test_booking_emails.py 1 quotation
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'envents_project.settings')
django.setup()

from apps.bookings.models import Booking
from apps.bookings.utils import send_booking_status_email


def test_email(booking_id, status):
    """Test sending email for a specific booking and status"""
    try:
        booking = Booking.objects.get(id=booking_id)
        
        # Save original status to restore later
        original_status = booking.status
        
        # Only update if needed (to avoid triggering signals during test)
        if status not in ('quotation', 'pending', 'confirmed', 'cancelled', 'completed'):
            print(f"Error: Invalid status '{status}'. Must be one of: quotation, pending, confirmed, cancelled, completed")
            return False
            
        # Send the email directly using our utility function
        print(f"Sending test {status} email for booking #{booking_id}...")
        result = send_booking_status_email(booking, status)
        
        if result:
            print(f"✅ Successfully sent {status} email test for booking #{booking_id}")
            return True
        else:
            print(f"❌ Failed to send {status} email for booking #{booking_id}")
            return False
            
    except Booking.DoesNotExist:
        print(f"Error: Booking #{booking_id} not found")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
        
    booking_id = sys.argv[1]
    status = sys.argv[2].lower()
    
    success = test_email(booking_id, status)
    sys.exit(0 if success else 1)
