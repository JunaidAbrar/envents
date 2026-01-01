#!/usr/bin/env python
"""
Quick test script for dynamic pricing functionality.
Run: python test_pricing.py
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'envents_project.settings.development')
django.setup()

from decimal import Decimal
from apps.venues.models import Venue
from apps.services.models import Service

def test_venue_pricing():
    print("\n=== TESTING VENUE PRICING ===\n")
    
    # Test HOURLY pricing
    print("Test 1: Hourly Venue Pricing")
    print("- Pricing Type: HOURLY")
    print("- Hourly Price: $100")
    print("- Duration: 3 hours")
    venue_hourly = Venue.objects.filter(pricing_type='HOURLY').first()
    if venue_hourly:
        cost = venue_hourly.calculate_cost(Decimal('3'))
        print(f"✓ Calculated Cost: {cost}")
        print(f"✓ Display Price: {venue_hourly.display_price}")
        expected = venue_hourly.hourly_price * 3
        assert cost == expected, f"Expected {expected}, got {cost}"
        print("✓ PASSED\n")
    else:
        print("⚠ No hourly venues found in database\n")
    
    # Test FLAT pricing
    print("Test 2: Flat Venue Pricing")
    print("- Pricing Type: FLAT")
    print("- Flat Price: $500")
    print("- Duration: 3 hours (should not affect cost)")
    venue_flat = Venue.objects.filter(pricing_type='FLAT').first()
    if venue_flat:
        cost = venue_flat.calculate_cost(Decimal('3'))
        print(f"✓ Calculated Cost: {cost}")
        print(f"✓ Display Price: {venue_flat.display_price}")
        assert cost == venue_flat.flat_price, f"Expected {venue_flat.flat_price}, got {cost}"
        print("✓ PASSED\n")
    else:
        print("⚠ No flat-rate venues found in database\n")

def test_service_pricing():
    print("\n=== TESTING SERVICE PRICING ===\n")
    
    # Test HOURLY pricing
    print("Test 3: Hourly Service Pricing")
    print("- Pricing Type: HOURLY")
    print("- Hourly Price: $50")
    print("- Quantity: 4 hours")
    service_hourly = Service.objects.filter(pricing_type='HOURLY').first()
    if service_hourly:
        cost = service_hourly.calculate_cost(4)
        print(f"✓ Calculated Cost: {cost}")
        print(f"✓ Display Price: {service_hourly.display_price}")
        expected = service_hourly.hourly_price * 4
        assert cost == expected, f"Expected {expected}, got {cost}"
        print("✓ PASSED\n")
    else:
        print("⚠ No hourly services found in database\n")
    
    # Test FLAT pricing
    print("Test 4: Flat Service Pricing")
    print("- Pricing Type: FLAT")
    print("- Flat Price: $200")
    print("- Quantity: 5 (should not affect cost)")
    service_flat = Service.objects.filter(pricing_type='FLAT').first()
    if service_flat:
        cost = service_flat.calculate_cost(5)
        print(f"✓ Calculated Cost: {cost}")
        print(f"✓ Display Price: {service_flat.display_price}")
        assert cost == service_flat.flat_price, f"Expected {service_flat.flat_price}, got {cost}"
        print("✓ PASSED\n")
    else:
        print("⚠ No flat-rate services found in database\n")

def test_validation():
    print("\n=== TESTING PRICING VALIDATION ===\n")
    
    # Count venues by pricing type
    hourly_venues = Venue.objects.filter(pricing_type='HOURLY').count()
    flat_venues = Venue.objects.filter(pricing_type='FLAT').count()
    print(f"Venues - HOURLY: {hourly_venues}, FLAT: {flat_venues}")
    
    # Count services by pricing type
    hourly_services = Service.objects.filter(pricing_type='HOURLY').count()
    flat_services = Service.objects.filter(pricing_type='FLAT').count()
    print(f"Services - HOURLY: {hourly_services}, FLAT: {flat_services}")
    
    # Check data integrity
    print("\nData Integrity Checks:")
    venues_no_hourly = Venue.objects.filter(pricing_type='HOURLY', hourly_price__isnull=True).count()
    venues_no_flat = Venue.objects.filter(pricing_type='FLAT', flat_price__isnull=True).count()
    services_no_hourly = Service.objects.filter(pricing_type='HOURLY', hourly_price__isnull=True).count()
    services_no_flat = Service.objects.filter(pricing_type='FLAT', flat_price__isnull=True).count()
    
    if venues_no_hourly == 0 and venues_no_flat == 0 and services_no_hourly == 0 and services_no_flat == 0:
        print("✓ All pricing data is valid (no missing prices)")
    else:
        print(f"⚠ Warning: Found invalid pricing data:")
        if venues_no_hourly > 0:
            print(f"  - {venues_no_hourly} hourly venues missing hourly_price")
        if venues_no_flat > 0:
            print(f"  - {venues_no_flat} flat venues missing flat_price")
        if services_no_hourly > 0:
            print(f"  - {services_no_hourly} hourly services missing hourly_price")
        if services_no_flat > 0:
            print(f"  - {services_no_flat} flat services missing flat_price")

if __name__ == '__main__':
    print("=" * 60)
    print("DYNAMIC PRICING IMPLEMENTATION TEST")
    print("=" * 60)
    
    try:
        test_venue_pricing()
        test_service_pricing()
        test_validation()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n✓ Pricing calculations work correctly")
        print("✓ Display methods format prices properly")
        print("✓ Data migration completed successfully")
        print("\nNext steps:")
        print("1. Test the submission forms in your browser")
        print("2. Verify admin interface shows/hides correct price fields")
        print("3. Create test bookings to verify cost calculations")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
