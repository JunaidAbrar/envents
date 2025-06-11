from django.contrib import admin
from django.utils.html import mark_safe
from .models import Booking, BookingService

class BookingServiceInline(admin.TabularInline):
    model = BookingService
    extra = 1
    raw_id_fields = ('service',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_booking_link', 'user', 'venue', 'event_date', 'phone_number', 'status', 'payment_status', 'total_cost', 'quoted_price')
    list_filter = ('status', 'payment_status', 'event_date')
    search_fields = ('venue__name', 'user__username', 'user__email', 'event_type')
    date_hierarchy = 'event_date'
    inlines = [BookingServiceInline]
    raw_id_fields = ('user', 'venue')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'venue', 'booking_type', 'status')
        }),
        ('Event Details', {
            'fields': ('event_date', 'start_time', 'end_time', 'guest_count', 'event_type')
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'venue_cost', 'services_cost', 'total_cost')
        }),
        ('Quotation Information', {
            'fields': ('quoted_price', 'quoted_message'),
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'created_at', 'updated_at')
        }),
    )
    actions = ['confirm_bookings', 'cancel_bookings', 'mark_as_completed', 
              'set_quoted_price', 'mark_as_pending',
              'mark_as_unpaid', 'mark_as_partially_paid', 'mark_as_fully_paid', 'mark_as_refunded']
    
    def get_booking_link(self, obj):
        """Create a clickable link to the booking detail"""
        return mark_safe(f'<a href="{obj.id}/change/">Booking #{obj.id} - View Details</a>')
    get_booking_link.short_description = 'Booking'
    
    # Booking status actions
    def confirm_bookings(self, request, queryset):
        # When confirming bookings, send confirmation email
        from django.core.mail import send_mail
        from django.conf import settings
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.urls import reverse
        from django.contrib.sites.models import Site
        
        for booking in queryset:
            # Send confirmation email
            try:
                subject = f"Your Booking #{booking.id} is Confirmed"
                
                # Get the absolute URL to the booking detail
                current_site = Site.objects.get_current()
                booking_url = f"https://{current_site.domain}{reverse('bookings:booking_detail', args=[booking.id])}"
                
                # Render HTML email
                html_message = render_to_string('emails/booking_confirmation.html', {
                    'booking': booking,
                    'booking_url': booking_url,
                })
                
                # Plain text version for email clients that don't support HTML
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                self.message_user(request, f"Error sending email for booking #{booking.id}: {str(e)}", level='error')
        
        queryset.update(status='confirmed')
        self.message_user(request, f"{queryset.count()} booking(s) marked as confirmed and notification emails sent.")
    confirm_bookings.short_description = "Mark selected bookings as confirmed"
    
    def cancel_bookings(self, request, queryset):
        queryset.update(status='cancelled')
    cancel_bookings.short_description = "Mark selected bookings as cancelled"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected bookings as completed"
    
    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
    mark_as_pending.short_description = "Mark selected bookings as pending (quotation accepted)"
    
    def set_quoted_price(self, request, queryset):
        from django.http import HttpResponseRedirect
        from django.contrib.admin import helpers
        from django import forms
        from django.shortcuts import render
        
        class QuotationForm(forms.Form):
            _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
            quoted_price = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
            quoted_message = forms.CharField(widget=forms.Textarea, required=False, 
                               help_text="Additional message to include with the price quote")
        
        if 'apply' in request.POST:
            form = QuotationForm(request.POST)
            
            if form.is_valid():
                quoted_price = form.cleaned_data['quoted_price']
                quoted_message = form.cleaned_data['quoted_message']
                
                count = 0
                for booking in queryset:
                    booking.quoted_price = quoted_price
                    booking.quoted_message = quoted_message
                    booking.status = 'quotation'  # Ensure status is quotation
                    booking.save()
                    count += 1
                
                self.message_user(request, f"Successfully set quoted price for {count} bookings.")
                return HttpResponseRedirect(request.get_full_path())
        
        form = QuotationForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
        return render(request, 'admin/set_quoted_price.html', {
            'bookings': queryset,
            'quotation_form': form,
            'title': 'Set quoted price',
        })
    set_quoted_price.short_description = "Set quoted price for selected bookings"
    
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
