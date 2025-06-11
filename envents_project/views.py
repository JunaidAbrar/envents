from django.shortcuts import render
from django.db.models import Q
from apps.venues.models import Venue, VenueCategory
import random

def home(request):
    """
    Home page view that passes context data for the venue search form
    """
    # Get all distinct cities from approved venues - case insensitive
    cities_raw = Venue.objects.filter(status='approved').values_list('city', flat=True)
    # Create a case-insensitive set of unique cities
    cities_set = set(city.lower() for city in cities_raw if city)
    # Map each lowercase city to its standard display form (first occurrence)
    cities_map = {}
    for city in cities_raw:
        if city and city.lower() not in cities_map:
            cities_map[city.lower()] = city
    # Final list of unique cities with proper casing
    cities = [cities_map[city_lower] for city_lower in cities_set]
    cities.sort()  # Sort alphabetically for better UX
    
    # Get all venue categories for "Program Type" dropdown
    categories = VenueCategory.objects.all()
    
    # Get featured venues (maximum 4)
    featured_venues = list(Venue.objects.filter(status='approved', is_featured=True)[:4])
    
    # If we have fewer than 4 featured venues, add some random venues to reach 4
    if len(featured_venues) < 4:
        # Exclude IDs of already selected featured venues to avoid duplicates
        featured_ids = [venue.id for venue in featured_venues]
        # Get random venues that aren't already in the featured list
        remaining_venues = list(Venue.objects.filter(status='approved').exclude(id__in=featured_ids))
        # Randomly select enough venues to get to 4 total
        needed_venues = min(4 - len(featured_venues), len(remaining_venues))
        if needed_venues > 0 and remaining_venues:
            random_venues = random.sample(remaining_venues, needed_venues)
            featured_venues.extend(random_venues)
    
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