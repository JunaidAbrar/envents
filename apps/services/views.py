from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Service, ServiceCategory, ServiceReview, FavoriteService
from .forms import ServiceReviewForm

def service_list(request):
    """Display list of services with filtering options"""
    # Use prefetch_related to avoid N+1 queries
    services = Service.objects.filter(status='approved').select_related('category', 'provider').prefetch_related('photos')
    categories = ServiceCategory.objects.all()
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(ServiceCategory, slug=category_slug)
        services = services.filter(category=category)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        services = services.filter(base_price__gte=min_price)
    if max_price:
        services = services.filter(base_price__lte=max_price)
    
    # Sorting
    sort = request.GET.get('sort', 'name')
    if sort == 'price_asc':
        services = services.order_by('base_price')
    elif sort == 'price_desc':
        services = services.order_by('-base_price')
    elif sort == 'rating':
        services = services.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        services = services.order_by('name')
    
    # Pagination
    paginator = Paginator(services, 9)  # 9 services per page
    page = request.GET.get('page')
    try:
        services = paginator.page(page)
    except PageNotAnInteger:
        services = paginator.page(1)
    except EmptyPage:
        services = paginator.page(paginator.num_pages)
    
    return render(request, 'services/service_list.html', {
        'services': services,
        'categories': categories,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
        'current_category': category_slug,
    })

def service_detail(request, slug):
    """Display details of a specific service"""
    # Use select_related and prefetch_related to optimize queries
    service = get_object_or_404(
        Service.objects.select_related('category', 'provider').prefetch_related(
            'photos', 'packages'
        ),
        slug=slug, 
        status='approved'
    )
    
    # Get service packages with efficient querying
    packages = service.packages.filter(is_active=True).order_by('order', 'name')
    
    # Get related services with optimization
    related_services = Service.objects.filter(
        category=service.category, status='approved'
    ).select_related('category', 'provider').prefetch_related(
        'photos'
    ).exclude(id=service.id)[:3]
    
    # Check if favorited
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteService.objects.filter(
            user=request.user, service=service
        ).exists()
    
    # Get reviews with user information in a single query
    reviews = service.reviews.select_related('user').all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Review form
    if request.method == 'POST':
        review_form = ServiceReviewForm(request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.service = service
            new_review.user = request.user
            
            # Check if user already reviewed this service
            try:
                existing_review = ServiceReview.objects.get(service=service, user=request.user)
                existing_review.rating = new_review.rating
                existing_review.comment = new_review.comment
                existing_review.save()
                messages.success(request, 'Your review has been updated!')
            except ServiceReview.DoesNotExist:
                new_review.save()
                messages.success(request, 'Your review has been submitted!')
                
            return redirect('services:service_detail', slug=slug)
    else:
        review_form = ServiceReviewForm()
    
    return render(request, 'services/service_detail.html', {
        'service': service,
        'packages': packages,
        'related_services': related_services,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
    })

def service_list_by_category(request, category_slug):
    """Display services filtered by category"""
    category = get_object_or_404(ServiceCategory, slug=category_slug)
    
    # Add select_related and prefetch_related for optimization
    services = Service.objects.filter(
        category=category, status='approved'
    ).select_related('category', 'provider').prefetch_related('photos')
    
    return render(request, 'services/service_list.html', {
        'services': services,
        'categories': ServiceCategory.objects.all(),
        'current_category': category_slug,
    })

def service_search(request):
    """Search for services by name or description"""
    query = request.GET.get('q', '')
    services = []
    
    if query:
        # Add select_related and prefetch_related for optimization
        services = Service.objects.filter(
            (Q(name__icontains=query) | Q(description__icontains=query)),
            status='approved'
        ).select_related('category', 'provider').prefetch_related('photos')
    
    return render(request, 'services/search_results.html', {
        'services': services,
        'query': query
    })

@login_required
def toggle_favorite(request, slug):
    """Toggle a service as favorite/unfavorite"""
    service = get_object_or_404(Service, slug=slug)
    favorite, created = FavoriteService.objects.get_or_create(
        user=request.user,
        service=service
    )
    
    if not created:
        favorite.delete()
        messages.success(request, f'{service.name} removed from favorites')
    else:
        messages.success(request, f'{service.name} added to favorites')
    
    return redirect('services:service_detail', slug=slug)

@login_required
def submit_review(request, slug):
    """Submit a review for a service"""
    service = get_object_or_404(Service, slug=slug)
    
    if request.method == 'POST':
        form = ServiceReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.service = service
            review.user = request.user
            
            # Update or create review
            ServiceReview.objects.update_or_create(
                service=service,
                user=request.user,
                defaults={
                    'rating': review.rating,
                    'comment': review.comment
                }
            )
            
            messages.success(request, 'Your review has been saved!')
            return redirect('services:service_detail', slug=slug)
    
    return redirect('services:service_detail', slug=slug)
