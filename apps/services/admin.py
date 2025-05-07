from django.contrib import admin
from .models import (
    ServiceCategory,
    Service,
    ServicePhoto,
    ServiceReview,
    FavoriteService
)

class ServicePhotoInline(admin.TabularInline):
    model = ServicePhoto
    extra = 1

class ServiceReviewInline(admin.TabularInline):
    model = ServiceReview
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = False
    max_num = 0  # Don't show "add" button

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'provider', 'base_price', 'price_type', 'status', 'is_featured')
    list_filter = ('status', 'is_featured', 'category', 'price_type')
    search_fields = ('name', 'description', 'provider__username', 'provider__business_name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServicePhotoInline, ServiceReviewInline]
    list_editable = ('status', 'is_featured')
    raw_id_fields = ('provider',)
    actions = ['approve_services', 'reject_services', 'feature_services', 'unfeature_services']
    
    def approve_services(self, request, queryset):
        queryset.update(status='approved')
    approve_services.short_description = "Mark selected services as approved"
    
    def reject_services(self, request, queryset):
        queryset.update(status='rejected')
    reject_services.short_description = "Mark selected services as rejected"
    
    def feature_services(self, request, queryset):
        queryset.update(is_featured=True)
    feature_services.short_description = "Mark selected services as featured"
    
    def unfeature_services(self, request, queryset):
        queryset.update(is_featured=False)
    unfeature_services.short_description = "Unmark selected services as featured"

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ServicePhoto)
class ServicePhotoAdmin(admin.ModelAdmin):
    list_display = ('service', 'caption', 'is_primary')
    list_filter = ('is_primary', 'service')
    raw_id_fields = ('service',)

@admin.register(ServiceReview)
class ServiceReviewAdmin(admin.ModelAdmin):
    list_display = ('service', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('service__name', 'user__username', 'comment')
    raw_id_fields = ('service', 'user')

@admin.register(FavoriteService)
class FavoriteServiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'service__name')
    raw_id_fields = ('user', 'service')
