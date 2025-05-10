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
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
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
