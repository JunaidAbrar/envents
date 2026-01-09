from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Amenities"
    
    def __str__(self):
        return self.name

class VenueCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Venue Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Venue(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    # Changed from ForeignKey to ManyToManyField
    category = models.ManyToManyField(VenueCategory, related_name='venues')
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100, db_index=True)
    address = models.TextField()
    capacity = models.PositiveIntegerField(help_text="Maximum number of guests")
    
    # Dynamic pricing fields - unified structure with services
    PRICING_TYPE_CHOICES = [
        ('HOURLY', 'Hourly Rate'),
        ('FLAT', 'Flat Rate'),
    ]
    pricing_type = models.CharField(max_length=10, choices=PRICING_TYPE_CHOICES, default='HOURLY')
    hourly_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price per hour")
    flat_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Flat rate price")
    
    contact_number = models.CharField(max_length=20, blank=True, help_text="Contact phone number for this venue")
    email = models.EmailField(blank=True, help_text="Contact email for this venue")
    amenities = models.ManyToManyField(Amenity, related_name='venues', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    
    # Owner field links to User model 
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='owned_venues'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'capacity']),
            models.Index(fields=['status']),
            models.Index(fields=['is_featured', 'status']),  # Optimize homepage featured query
            models.Index(fields=['-created_at']),  # Optimize ordering
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('venues:venue_detail', kwargs={'slug': self.slug})
    
    @property
    def main_photo(self):
        return self.photos.filter(is_primary=True).first() or self.photos.first()
    
    @property
    def display_price(self):
        """Unified price display for templates"""
        if self.pricing_type == 'HOURLY':
            return f"৳{self.hourly_price} / hour"
        else:
            return f"৳{self.flat_price} flat"
    
    def get_effective_price(self):
        """Returns the active price based on pricing_type"""
        return self.hourly_price if self.pricing_type == 'HOURLY' else self.flat_price
    
    def calculate_cost(self, hours):
        """Calculate cost based on duration and pricing type.
        For HOURLY: returns hourly_price * hours
        For FLAT: returns flat_price (duration doesn't affect cost)"""
        if self.pricing_type == 'HOURLY':
            return self.hourly_price * hours
        else:
            return self.flat_price

class VenuePhoto(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='venues/photos/')
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', '-uploaded_at']

    def __str__(self):
        return f"Photo for {self.venue.name}"
    
    def save(self, *args, **kwargs):
        print(f"VenuePhoto.save called for venue: {self.venue}")
        print(f"Image field: {self.image.name if self.image else 'No image'}")
        print(f"Caption: {self.caption}")
        super().save(*args, **kwargs)
        print(f"VenuePhoto saved with ID: {self.id}")

class DisabledDate(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='disabled_dates')
    date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)
    
    class Meta:
        unique_together = ('venue', 'date')
        
    def __str__(self):
        return f"{self.venue.name} - {self.date}"

class VenueReview(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='venue_reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('venue', 'user')
    
    def __str__(self):
        return f"{self.user.username}'s review for {self.venue.name}"

class FavoriteVenue(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_venues'
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'venue')
    
    def __str__(self):
        return f"{self.user.username}'s favorite: {self.venue.name}"

class VenueCateringPackage(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='catering_packages')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_type = models.CharField(max_length=50, default='per person')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price', 'name']
        unique_together = ('venue', 'name')
    
    def __str__(self):
        return f"{self.venue.name}: {self.name}"
