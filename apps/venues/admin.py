from django.contrib import admin
from .models import (
    Amenity, 
    VenueCategory, 
    Venue, 
    VenuePhoto, 
    DisabledDate, 
    VenueReview,
    FavoriteVenue
)

class VenuePhotoInline(admin.TabularInline):
    model = VenuePhoto
    extra = 1

class DisabledDateInline(admin.TabularInline):
    model = DisabledDate
    extra = 1

class VenueReviewInline(admin.TabularInline):
    model = VenueReview
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = False
    max_num = 0  # Don't show "add" button

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_categories', 'city', 'capacity', 'price_per_hour', 'status', 'is_featured')
    list_filter = ('status', 'is_featured', 'city', 'category')
    search_fields = ('name', 'description', 'address', 'city')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VenuePhotoInline, DisabledDateInline, VenueReviewInline]
    filter_horizontal = ('amenities', 'category')
    list_editable = ('status', 'is_featured')
    actions = ['approve_venues', 'reject_venues', 'feature_venues', 'unfeature_venues']
    
    def get_categories(self, obj):
        return ", ".join([cat.name for cat in obj.category.all()])
    get_categories.short_description = "Categories"
    
    def approve_venues(self, request, queryset):
        queryset.update(status='approved')
    approve_venues.short_description = "Mark selected venues as approved"
    
    def reject_venues(self, request, queryset):
        queryset.update(status='rejected')
    reject_venues.short_description = "Mark selected venues as rejected"
    
    def feature_venues(self, request, queryset):
        queryset.update(is_featured=True)
    feature_venues.short_description = "Mark selected venues as featured"
    
    def unfeature_venues(self, request, queryset):
        queryset.update(is_featured=False)
    unfeature_venues.short_description = "Unmark selected venues as featured"

@admin.register(VenueCategory)
class VenueCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')

@admin.register(VenuePhoto)
class VenuePhotoAdmin(admin.ModelAdmin):
    list_display = ('venue', 'caption', 'is_primary')
    list_filter = ('is_primary', 'venue')
    raw_id_fields = ('venue',)

@admin.register(DisabledDate)
class DisabledDateAdmin(admin.ModelAdmin):
    list_display = ('venue', 'date', 'reason')
    list_filter = ('venue',)
    date_hierarchy = 'date'

@admin.register(VenueReview)
class VenueReviewAdmin(admin.ModelAdmin):
    list_display = ('venue', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('venue__name', 'user__username', 'comment')
    raw_id_fields = ('venue', 'user')

@admin.register(FavoriteVenue)
class FavoriteVenueAdmin(admin.ModelAdmin):
    list_display = ('user', 'venue', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'venue__name')
