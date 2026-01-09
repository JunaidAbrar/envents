from django.shortcuts import render
from django.db.models import Q
from apps.venues.models import Venue, VenueCategory
import random

def home(request):
    """
    Home page view that passes context data for the venue search form
    Optimized for performance with caching and efficient queries
    """
    from django.core.cache import cache
    
    # Cache cities list for 1 hour (recalculated only when cache expires)
    cities = cache.get('venue_cities_list')
    if cities is None:
        # Efficient aggregation - only get distinct cities
        cities_raw = Venue.objects.filter(status='approved').values_list('city', flat=True).distinct()
        # Create a case-insensitive set of unique cities
        cities_set = set(city.lower() for city in cities_raw if city)
        # Map each lowercase city to its standard display form
        cities_map = {}
        for city in cities_raw:
            if city and city.lower() not in cities_map:
                cities_map[city.lower()] = city
        # Final list of unique cities with proper casing
        cities = sorted([cities_map[city_lower] for city_lower in cities_set])
        cache.set('venue_cities_list', cities, 3600)  # Cache for 1 hour
    
    # Cache categories for 1 hour
    categories = cache.get('venue_categories_list')
    if categories is None:
        categories = list(VenueCategory.objects.all())
        cache.set('venue_categories_list', categories, 3600)
    
    # Get featured venues efficiently with prefetch_related to avoid N+1 queries
    featured_venues = list(
        Venue.objects.filter(status='approved', is_featured=True)
        .prefetch_related('photos', 'category')
        .select_related()[:4]
    )
    
    # If we have fewer than 4 featured venues, add random venues
    if len(featured_venues) < 4:
        featured_ids = [venue.id for venue in featured_venues]
        needed_venues = 4 - len(featured_venues)
        
        # CRITICAL FIX: Use database-level random selection instead of loading all venues
        # order_by('?') is handled by PostgreSQL RANDOM() - much faster than Python random.sample
        additional_venues = list(
            Venue.objects.filter(status='approved')
            .exclude(id__in=featured_ids)
            .prefetch_related('photos', 'category')
            .select_related()
            .order_by('?')[:needed_venues]
        )
        featured_venues.extend(additional_venues)
    
    return render(request, 'home.html', {
        'cities': cities,
        'categories': categories,
        'top_venues': featured_venues,
    })

def about(request):
    """
    About Us page view
    """
    return render(request, 'about.html')