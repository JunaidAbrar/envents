from django.contrib import admin
from .models import (
    Amenity, 
    VenueCategory, 
    Venue, 
    VenuePhoto, 
    DisabledDate, 
    VenueReview,
    FavoriteVenue,
    VenueCateringPackage
)

class VenuePhotoInline(admin.TabularInline):
    model = VenuePhoto
    extra = 1
    fields = ('image', 'caption', 'is_primary')
    
    def save_model(self, request, obj, form, change):
        """Override to add debugging for inline saves"""
        print(f"VenuePhotoInline.save_model called for {obj}")
        if hasattr(obj, 'image') and obj.image:
            print(f"Image field: {obj.image.name}")
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Override to ensure inline forms are saved properly"""
        print(f"VenuePhotoInline.save_formset called")
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            print(f"Saving VenuePhoto instance: {instance}")
            if hasattr(instance, 'image') and instance.image:
                print(f"Image to save: {instance.image.name}")
            instance.save()
        formset.save_m2m()

class DisabledDateInline(admin.TabularInline):
    model = DisabledDate
    extra = 1

class VenueReviewInline(admin.TabularInline):
    model = VenueReview
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = False
    max_num = 0  # Don't show "add" button

class VenueCateringPackageInline(admin.TabularInline):
    model = VenueCateringPackage
    extra = 1

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_categories', 'city', 'capacity', 'formatted_price', 'contact_number', 'email', 'status', 'is_featured')
    list_filter = ('status', 'is_featured', 'city', 'category', 'pricing_type')
    search_fields = ('name', 'description', 'address', 'city')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VenuePhotoInline, DisabledDateInline, VenueReviewInline, VenueCateringPackageInline]
    filter_horizontal = ('amenities', 'category')
    list_editable = ('status', 'is_featured')
    actions = ['approve_venues', 'reject_venues', 'feature_venues', 'unfeature_venues']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category', 'owner')
        }),
        ('Location', {
            'fields': ('location', 'city', 'address')
        }),
        ('Capacity & Pricing', {
            'fields': ('capacity', 'pricing_type', 'hourly_price', 'flat_price'),
            'classes': ('pricing-section',),
        }),
        ('Contact Information', {
            'fields': ('contact_number', 'email')
        }),
        ('Features & Status', {
            'fields': ('amenities', 'status', 'is_featured')
        }),
    )
    
    class Media:
        js = ('admin/js/venue_pricing.js',)
    
    def formatted_price(self, obj):
        """Display formatted price in admin list"""
        return obj.display_price
    formatted_price.short_description = 'Price'
    
    def save_formset(self, request, form, formset, change):
        """
        Override to ensure inline forms are saved properly, especially VenuePhoto
        """
        print(f"VenueAdmin.save_formset called for model: {formset.model.__name__}")
        
        # Special handling for VenuePhoto formset
        if formset.model == VenuePhoto:
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                print(f"Deleting VenuePhoto: {obj}")
                obj.delete()
            for instance in instances:
                print(f"Processing VenuePhoto instance in VenueAdmin: {instance}")
                if hasattr(instance, 'image') and instance.image:
                    print(f"Image file: {instance.image.name}, size: {instance.image.size}")
                instance.save()
                print(f"VenuePhoto saved with ID: {instance.id}")
            formset.save_m2m()
        else:
            # For other inline models, use default behavior
            super().save_formset(request, form, formset, change)
    
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

@admin.register(VenueCateringPackage)
class VenueCateringPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'price', 'price_type', 'is_active')
    list_filter = ('is_active', 'venue')
    search_fields = ('name', 'description', 'venue__name')
    raw_id_fields = ('venue',)
