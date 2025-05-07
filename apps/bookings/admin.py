from django.contrib import admin
from .models import Booking, BookingService

class BookingServiceInline(admin.TabularInline):
    model = BookingService
    extra = 1
    raw_id_fields = ('service',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'venue', 'event_date', 'status', 'payment_status', 'total_cost')
    list_filter = ('status', 'payment_status', 'event_date')
    search_fields = ('venue__name', 'user__username', 'user__email', 'event_type')
    date_hierarchy = 'event_date'
    inlines = [BookingServiceInline]
    raw_id_fields = ('user', 'venue')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'venue', 'status')
        }),
        ('Event Details', {
            'fields': ('event_date', 'start_time', 'end_time', 'guest_count', 'event_type')
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'venue_cost', 'services_cost', 'total_cost')
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'created_at', 'updated_at')
        }),
    )
    actions = ['confirm_bookings', 'cancel_bookings', 'mark_as_completed', 
              'mark_as_unpaid', 'mark_as_partially_paid', 'mark_as_fully_paid', 'mark_as_refunded']
    
    # Booking status actions
    def confirm_bookings(self, request, queryset):
        queryset.update(status='confirmed')
    confirm_bookings.short_description = "Mark selected bookings as confirmed"
    
    def cancel_bookings(self, request, queryset):
        queryset.update(status='cancelled')
    cancel_bookings.short_description = "Mark selected bookings as cancelled"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected bookings as completed"
    
    # Payment status actions
    def mark_as_unpaid(self, request, queryset):
        queryset.update(payment_status='unpaid')
    mark_as_unpaid.short_description = "Mark payment status as Unpaid"
    
    def mark_as_partially_paid(self, request, queryset):
        queryset.update(payment_status='partial')
    mark_as_partially_paid.short_description = "Mark payment status as Partially Paid"
    
    def mark_as_fully_paid(self, request, queryset):
        queryset.update(payment_status='paid')
    mark_as_fully_paid.short_description = "Mark payment status as Fully Paid"
    
    def mark_as_refunded(self, request, queryset):
        queryset.update(payment_status='refunded')
    mark_as_refunded.short_description = "Mark payment status as Refunded"

@admin.register(BookingService)
class BookingServiceAdmin(admin.ModelAdmin):
    list_display = ('booking', 'service', 'quantity', 'price')
    list_filter = ('booking__status',)
    search_fields = ('booking__id', 'service__name')
    raw_id_fields = ('booking', 'service')
