from django.shortcuts import render
from apps.venues.models import Venue, VenueCategory

def home(request):
    """
    Home page view that passes context data for the venue search form
    """
    # Get all distinct cities from approved venues
    cities = Venue.objects.filter(status='approved').values_list('city', flat=True).distinct()
    
    # Get all venue categories for "Program Type" dropdown
    categories = VenueCategory.objects.all()
    
    return render(request, 'home.html', {
        'cities': cities,
        'categories': categories,
    })

def about(request):
    """
    About Us page view
    """
    return render(request, 'about.html')