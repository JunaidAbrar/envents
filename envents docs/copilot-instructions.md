Copilot Instructions for Envents
An event management platform for venue discovery, comparison, and booking with admin features.
Technologies used...
Django 5
Django REST Framework
PostgreSQL
TailwindCSS
📘 Django / DRF / PostgreSQL / TailwindCSS Best Practices
This guide outlines best practices for building the Envents application. The goal is readability and maintainability, minimizing abstractions to keep the codebase clear.

📁 Project Structure
/envents
    /envents (core project)
        settings/
            __init__.py
            base.py
            development.py
            production.py
        urls.py
        asgi.py
        wsgi.py
    /apps
        /accounts
        /venues
        /bookings
        /services
    /templates
    /static
        /css
        /js
        /images
    /media
    manage.py

For each Django app:
/app_name
    /api
        __init__.py
        serializers.py
        views.py
    /migrations
    /templates
        /app_name
    /static
        /app_name
    __init__.py
    admin.py
    apps.py
    forms.py
    models.py
    urls.py
    views.py

🚨 Rules
Code Organization
Flat is better than nested - Keep directory structures shallow when possible
# Good
/venues
    models.py  # All venue-related models in one file
    forms.py   # All venue-related forms in one file

# Avoid
/venues
    /models
        venue.py
        amenity.py
    /forms
        venue_creation.py
        venue_update.py

No generic 'helpers' folder - Keep components close to where they are used
# Good
/venues
    models.py
    services.py  # Venue-specific services

# Avoid
/helpers
    venue_services.py
    booking_services.py

Explicit is better than implicit - Prefer clarity over cleverness
# Good
def get_available_venues(date, guest_count):
    return Venue.objects.filter(capacity__gte=guest_count).exclude(bookings__date=date)

# Avoid
def get_venues(d, g):
    return Venue.objects.filter(capacity__gte=g).exclude(bookings__date=d)

Function-based views for simplicity - Use class-based views only when needed
# Good for simple views
def venue_detail(request, pk):
    venue = get_object_or_404(Venue, pk=pk)
    context = {'venue': venue}
    return render(request, 'venues/detail.html', context)

# Good for complex views
class VenueListView(ListView):
    model = Venue
    paginate_by = 12
    context_object_name = 'venues'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if 'location' in self.request.GET:
            queryset = queryset.filter(city=self.request.GET['location'])
        return queryset

Django Practices
Always use related_name for relationships
# Good
class Booking(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')

Name URLs and use reverse() or get_absolute_url()
# urls.py
path('venues/<int:pk>/', views.venue_detail, name='venue_detail')

# models.py
def get_absolute_url(self):
    return reverse('venue_detail', kwargs={'pk': self.pk})

Keep views thin, push logic to models or services
# models.py
class VenueManager(models.Manager):
    def search_by_criteria(self, location, guest_count, event_type):
        queryset = self.filter(is_published=True)
        if location:
            queryset = queryset.filter(city__iexact=location)
        if guest_count:
            queryset = queryset.filter(capacity__gte=guest_count)
        if event_type:
            queryset = queryset.filter(event_types__name__iexact=event_type)
        return queryset

# views.py
def search_venues(request):
    form = VenueSearchForm(request.GET)
    venues = []
    if form.is_valid():
        venues = Venue.objects.search_by_criteria(
            form.cleaned_data['location'],
            form.cleaned_data['guest_count'],
            form.cleaned_data['event_type']
        )
    return render(request, 'venues/search.html', {'form': form, 'venues': venues})

Database
Create indexes for fields used in filtering
class Venue(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100, db_index=True)
    capacity = models.PositiveIntegerField(db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['city', 'capacity']),
        ]

Use select_related and prefetch_related to avoid N+1 queries
# Good
venues = Venue.objects.select_related('owner').prefetch_related('amenities')

# Avoid
venues = Venue.objects.all()  # Each venue.owner access will trigger a query

Use PostgreSQL-specific fields where appropriate
from django.contrib.postgres.fields import ArrayField

class Venue(models.Model):
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    
    # Query example
    Venue.objects.filter(tags__contains=['wedding', 'outdoor'])

Frontend
Use Django templates with TailwindCSS utilities
<!-- Good -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {% for venue in venues %}
        <div class="bg-white rounded shadow p-4">
            <h2 class="text-xl font-bold">{{ venue.name }}</h2>
            <p class="text-gray-600">{{ venue.city }}</p>
        </div>
    {% endfor %}
</div>

Avoid custom CSS when possible - use TailwindCSS
<!-- Good -->
<button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Submit
</button>

<!-- Avoid -->
<button class="submit-button">
    Submit
</button>
<!-- And then creating custom CSS -->

Organize templates with includes and inheritance
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Envents{% endblock %}</title>
</head>
<body>
    {% include 'components/header.html' %}
    <main>
        {% block content %}{% endblock %}
    </main>
    {% include 'components/footer.html' %}
</body>
</html>

<!-- venue_detail.html -->
{% extends 'base.html' %}

{% block title %}{{ venue.name }} | Envents{% endblock %}

{% block content %}
    {% include 'venues/partials/venue_header.html' %}
    {% include 'venues/partials/venue_details.html' %}
    {% include 'venues/partials/venue_booking_form.html' %}
{% endblock %}

API Design
RESTful endpoints with consistent naming
# urls.py
router = DefaultRouter()
router.register(r'venues', VenueViewSet)
router.register(r'bookings', BookingViewSet)

# views.py
class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    filterset_class = VenueFilter

Clear serializers with appropriate depth
class VenueSerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.get_full_name')
    amenities = AmenitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Venue
        fields = ['id', 'name', 'description', 'address', 'city', 
                  'capacity', 'owner_name', 'amenities', 'created_at']

Proper filtering and searching
class VenueFilter(filters.FilterSet):
    min_capacity = filters.NumberFilter(field_name='capacity', lookup_expr='gte')
    max_capacity = filters.NumberFilter(field_name='capacity', lookup_expr='lte')
    city = filters.CharFilter(lookup_expr='iexact')
    
    class Meta:
        model = Venue
        fields = ['city', 'min_capacity', 'max_capacity']

Testing
Test models, views, and complex queries
class VenueModelTest(TestCase):
    def setUp(self):
        self.venue = Venue.objects.create(
            name='Test Venue',
            city='Test City',
            capacity=100
        )
    
    def test_str_representation(self):
        self.assertEqual(str(self.venue), 'Test Venue')
        
    def test_absolute_url(self):
        self.assertEqual(
            self.venue.get_absolute_url(),
            reverse('venue_detail', kwargs={'pk': self.venue.pk})
        )

Use factories for test data
# Install factory-boy first
import factory
from apps.venues.models import Venue

class VenueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Venue
    
    name = factory.Faker('company')
    description = factory.Faker('paragraph')
    city = factory.Faker('city')
    capacity = factory.Faker('random_int', min=10, max=500)
    
# In tests
def test_venue_search():
    VenueFactory.create_batch(5, city='New York')
    VenueFactory.create_batch(3, city='Chicago')
    
    self.assertEqual(Venue.objects.filter(city='New York').count(), 5)

Security
Store secrets in environment variables
# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')

Validate all user inputs
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'guest_count', 'event_type']
        
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError("Booking date cannot be in the past")
        return date
        
    def clean_guest_count(self):
        guest_count = self.cleaned_data.get('guest_count')
        venue = self.cleaned_data.get('venue')
        if venue and guest_count > venue.capacity:
            raise forms.ValidationError(f"Guest count exceeds venue capacity of {venue.capacity}")
        return guest_count

Use proper permissions
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class VenueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]





