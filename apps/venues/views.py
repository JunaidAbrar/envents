from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Venue, VenueCategory, VenueReview, FavoriteVenue, Amenity

def venue_list(request):
    venues_queryset = Venue.objects.filter(status='approved')
    all_categories = VenueCategory.objects.all()
    all_amenities = Amenity.objects.all()
    
    # Get all distinct cities from venues
    cities = Venue.objects.filter(status='approved').values_list('city', flat=True).distinct()
    
    # Filter by categories
    categories = request.GET.getlist('categories')
    if categories:
        venues_queryset = venues_queryset.filter(category__id__in=categories).distinct()
    
    # Filter by capacity
    min_capacity = request.GET.get('capacity')
    if min_capacity and min_capacity != '1000+':  # Handle the 1000+ special case
        venues_queryset = venues_queryset.filter(capacity__gte=min_capacity)
    elif min_capacity == '1000+':
        venues_queryset = venues_queryset.filter(capacity__gte=1000)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    if min_price:
        venues_queryset = venues_queryset.filter(price_per_hour__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        venues_queryset = venues_queryset.filter(price_per_hour__lte=max_price)
    
    # Filter by city
    city = request.GET.get('city')
    if city:
        venues_queryset = venues_queryset.filter(city__iexact=city)
    
    # Filter by amenities
    amenities = request.GET.getlist('amenities')
    if amenities:
        venues_queryset = venues_queryset.filter(amenities__id__in=amenities).distinct()
    
    # For home page search compatibility
    # Redirect from the home search with location, guests and type parameters
    location = request.GET.get('location')
    if location:
        venues_queryset = venues_queryset.filter(city__iexact=location)
        city = location  # Set city for template rendering
    
    guests = request.GET.get('guests')
    if guests:
        venues_queryset = venues_queryset.filter(capacity__gte=guests)
        min_capacity = guests  # Set min_capacity for template rendering
    
    event_type = request.GET.get('type')
    # Note: If you want to filter by event type, you would need to implement
    # that logic here. This might require adding an event_type field to the 
    # Venue model or relating it to categories.
    
    # Sorting
    sort = request.GET.get('sort', 'name')
    if sort == 'price_low' or sort == 'price_asc':
        venues_queryset = venues_queryset.order_by('price_per_hour')
    elif sort == 'price_high' or sort == 'price_desc':
        venues_queryset = venues_queryset.order_by('-price_per_hour')
    elif sort == 'capacity':
        venues_queryset = venues_queryset.order_by('-capacity')
    elif sort == 'rating':
        venues_queryset = venues_queryset.order_by('-average_rating')
    else:
        venues_queryset = venues_queryset.order_by('name')
    
    # Get user favorites if user is authenticated
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
        'venues': venues,
        'all_categories': all_categories,
        'min_capacity': min_capacity,
        'city': city,
        'sort': sort,
        'cities': cities,
        'amenities': all_amenities,  # Provide actual amenities list
        'user_favorites': user_favorites,
        'is_paginated': True if paginator.num_pages > 1 else False,
        'page_obj': venues,
        'venues_count': total_venues,
    })

def venue_detail(request, slug):
    venue = get_object_or_404(Venue, slug=slug, status='approved')
    
    # Get related venues (same category)
    related_venues = Venue.objects.filter(
        category=venue.category, status='approved'
    ).exclude(id=venue.id)[:3]
    
    # Check if favorited
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteVenue.objects.filter(
            user=request.user, venue=venue
        ).exists()
    
    # Get reviews
    reviews = venue.reviews.all()
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
    venues = Venue.objects.filter(category=category, status='approved')
    
    return render(request, 'venues/venue_list.html', {
        'venues': venues,
        'category': category,
    })

def venue_search(request):
    query = request.GET.get('q', '')
    venues = []
    
    if query:
        venues = Venue.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(city__icontains=query),
            status='approved'
        )
    
    return render(request, 'venues/search_results.html', {
        'venues': venues,
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
