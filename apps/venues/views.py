from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Venue, VenueCategory, VenueReview, FavoriteVenue, Amenity
from .forms import VenueReviewForm

def venue_list(request):
    # Use select_related and prefetch_related to avoid N+1 queries
    venues_queryset = Venue.objects.filter(status='approved').prefetch_related(
        'category', 'amenities', 'photos'
    ).annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    all_categories = VenueCategory.objects.all()
    all_amenities = Amenity.objects.all()
    
    # Get all distinct cities from venues - case insensitive
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

    # Filter by category (single selection)
    category_id = request.GET.get('category')
    if category_id:
        venues_queryset = venues_queryset.filter(category__id=category_id)
    
    # Filter by capacity
    capacity = request.GET.get('capacity')
    if capacity and capacity != '1000+':  # Handle the 1000+ special case
        venues_queryset = venues_queryset.filter(capacity__gte=capacity)
    elif capacity == '1000+':
        venues_queryset = venues_queryset.filter(capacity__gte=1000)
    
    # Filter by price range (handles both hourly and flat pricing)
    min_price = request.GET.get('min_price')
    if min_price:
        from django.db.models import Q
        # Filter venues where either hourly_price OR flat_price meets the minimum
        venues_queryset = venues_queryset.filter(
            Q(pricing_type='HOURLY', hourly_price__gte=min_price) |
            Q(pricing_type='FLAT', flat_price__gte=min_price)
        )
    
    max_price = request.GET.get('max_price')
    if max_price:
        from django.db.models import Q
        # Filter venues where either hourly_price OR flat_price meets the maximum
        venues_queryset = venues_queryset.filter(
            Q(pricing_type='HOURLY', hourly_price__lte=max_price) |
            Q(pricing_type='FLAT', flat_price__lte=max_price)
        )
    
    # Filter by city
    city = request.GET.get('city')
    if city:
        venues_queryset = venues_queryset.filter(city__iexact=city)
    
    # Filter by amenities
    amenities = request.GET.getlist('amenities')
    # Filter out empty strings
    amenities = [a for a in amenities if a]
    if amenities:
        # Convert string IDs to integers before filtering
        amenities_int = [int(a) for a in amenities]
        venues_queryset = venues_queryset.filter(amenities__id__in=amenities_int).distinct()
    
    # Sorting (handles both hourly and flat pricing)
    sort = request.GET.get('sort', 'name')
    if sort == 'price_low' or sort == 'price_asc':
        # Sort by effective price (hourly_price for HOURLY, flat_price for FLAT)
        from django.db.models import Case, When, F
        venues_queryset = venues_queryset.annotate(
            effective_price=Case(
                When(pricing_type='HOURLY', then=F('hourly_price')),
                When(pricing_type='FLAT', then=F('flat_price')),
                default=F('hourly_price')
            )
        ).order_by('effective_price')
    elif sort == 'price_high' or sort == 'price_desc':
        from django.db.models import Case, When, F
        venues_queryset = venues_queryset.annotate(
            effective_price=Case(
                When(pricing_type='HOURLY', then=F('hourly_price')),
                When(pricing_type='FLAT', then=F('flat_price')),
                default=F('hourly_price')
            )
        ).order_by('-effective_price')
    elif sort == 'capacity':
        venues_queryset = venues_queryset.order_by('-capacity')
    elif sort == 'rating':
        venues_queryset = venues_queryset.order_by('-average_rating')
    else:
        venues_queryset = venues_queryset.order_by('name')
    
    # Get user favorites efficiently in one query
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = FavoriteVenue.objects.filter(user=request.user).values_list('venue', flat=True)
    
    # Count total venues before pagination
    total_venues = venues_queryset.count()
    
    # Pagination
    paginator = Paginator(venues_queryset, 9)  # 9 venues per page
    page = request.GET.get('page')
    try:
        venues = paginator.page(page)
    except PageNotAnInteger:
        venues = paginator.page(1)
    except EmptyPage:
        venues = paginator.page(paginator.num_pages)
    
    return render(request, 'venues/venue_list.html', {
        'page_obj': venues,  # Only need one variable for the paginated venues
        'all_categories': all_categories,
        'min_capacity': capacity,  # Use the same variable name we use above
        'city': city,
        'sort': sort,
        'cities': cities,
        'amenities': all_amenities,
        'selected_amenities': amenities,  # Pass the original string IDs to maintain form state
        'user_favorites': user_favorites,
        'is_paginated': True if paginator.num_pages > 1 else False,
        'venues_count': total_venues,
    })

def venue_detail(request, slug):
    # Use select_related and prefetch_related to avoid N+1 queries
    venue = get_object_or_404(
        Venue.objects.prefetch_related(
            'category', 
            'amenities', 
            'photos', 
            'catering_packages'
        ), 
        slug=slug, 
        status='approved'
    )
    
    # Get related venues with prefetch_related to optimize performance
    venue_categories = venue.category.all()
    related_venues = Venue.objects.filter(
        category__in=venue_categories, status='approved'
    ).prefetch_related('photos').exclude(id=venue.id).distinct()[:3]
    
    # Check if favorited
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteVenue.objects.filter(
            user=request.user, venue=venue
        ).exists()
    
    # Get reviews with select_related to include user information in a single query
    reviews = venue.reviews.select_related('user').all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Review form
    if request.method == 'POST':
        review_form = VenueReviewForm(request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.venue = venue
            new_review.user = request.user
            
            # Check if user already reviewed this venue
            try:
                existing_review = VenueReview.objects.get(venue=venue, user=request.user)
                existing_review.rating = new_review.rating
                existing_review.comment = new_review.comment
                existing_review.save()
                messages.success(request, 'Your review has been updated!')
            except VenueReview.DoesNotExist:
                new_review.save()
                messages.success(request, 'Your review has been submitted!')
                
            return redirect('venues:venue_detail', slug=slug)
    else:
        review_form = VenueReviewForm()
    
    return render(request, 'venues/venue_detail.html', {
        'venue': venue,
        'related_venues': related_venues,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
    })

def venue_list_by_category(request, category_slug):
    category = get_object_or_404(VenueCategory, slug=category_slug)
    # Add prefetch_related to optimize queries
    venues = Venue.objects.filter(category=category, status='approved').prefetch_related(
        'category', 'amenities', 'photos'
    ).annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    
    return render(request, 'venues/venue_list.html', {
        'page_obj': venues,  # Use page_obj for consistency with venue_list view
        'category': category,
    })

def venue_search(request):
    query = request.GET.get('q', '')
    venues = []
    
    if query:
        # Add prefetch_related to optimize venue search results
        venues = Venue.objects.filter(
            (Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(city__icontains=query)),
            status='approved'
        ).prefetch_related('category', 'amenities', 'photos').annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )
    
    return render(request, 'venues/search_results.html', {
        'page_obj': venues,  # Use page_obj for consistency with other venue views
        'query': query
    })

@login_required
def toggle_favorite(request, slug):
    venue = get_object_or_404(Venue, slug=slug)
    favorite, created = FavoriteVenue.objects.get_or_create(
        user=request.user,
        venue=venue
    )
    
    if not created:
        favorite.delete()
        messages.success(request, f'{venue.name} removed from favorites')
    else:
        messages.success(request, f'{venue.name} added to favorites')
    
    return redirect('venues:venue_detail', slug=slug)

@login_required
def submit_review(request, slug):
    venue = get_object_or_404(Venue, slug=slug)
    
    if request.method == 'POST':
        form = VenueReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.venue = venue
            review.user = request.user
            
            # Update or create review
            VenueReview.objects.update_or_create(
                venue=venue,
                user=request.user,
                defaults={
                    'rating': review.rating,
                    'comment': review.comment
                }
            )
            
            messages.success(request, 'Your review has been saved!')
            return redirect('venues:venue_detail', slug=slug)
    
    return redirect('venues:venue_detail', slug=slug)
