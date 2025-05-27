from django import forms
from django.utils import timezone
from .models import Booking, BookingService
from apps.services.models import Service, ServiceCategory

class BookingForm(forms.ModelForm):
    booking_type = forms.ChoiceField(
        choices=Booking.BOOKING_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='venue'
    )
    event_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'type': 'date'
        })
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    guest_count = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of guests'
        })
    )
    event_type = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Wedding, Birthday, Conference, etc.'
        })
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your contact number'
        })
    )
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Any special requests...',
            'rows': 3
        })
    )
    uses_venue_catering = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Use venue catering (if available)'
    )
    venue_catering_package = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Select catering package'
    )
    venue_catering_count = forms.IntegerField(
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of servings'
        }),
        label='Number of servings'
    )
    
    class Meta:
        model = Booking
        fields = [
            'booking_type', 'event_date', 'start_time', 'end_time', 
            'guest_count', 'event_type', 'phone_number', 'special_requests',
            'uses_venue_catering', 'venue_catering_package', 'venue_catering_count'
        ]
    
    def __init__(self, *args, **kwargs):
        venue = kwargs.pop('venue', None)
        super().__init__(*args, **kwargs)
        
        if venue:
            # Set the queryset for venue catering packages
            self.fields['venue_catering_package'].queryset = venue.catering_packages.filter(is_active=True)
        else:
            self.fields['venue_catering_package'].queryset = None
            self.fields['uses_venue_catering'].widget = forms.HiddenInput()
            self.fields['venue_catering_package'].widget = forms.HiddenInput()
            self.fields['venue_catering_count'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get('event_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        uses_venue_catering = cleaned_data.get('uses_venue_catering')
        venue_catering_package = cleaned_data.get('venue_catering_package')
        venue_catering_count = cleaned_data.get('venue_catering_count')
        booking_type = cleaned_data.get('booking_type')
        
        if event_date and event_date < timezone.now().date():
            self.add_error('event_date', "You cannot book a date in the past.")
        
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', "End time must be after start time.")
            
        # Validate venue catering options
        if booking_type == 'venue' and uses_venue_catering:
            if not venue_catering_package:
                self.add_error('venue_catering_package', "Please select a catering package.")
                
            if not venue_catering_count:
                self.add_error('venue_catering_count', "Please specify the number of servings.")
            elif venue_catering_count < 1:
                self.add_error('venue_catering_count', "Number of servings must be at least 1.")
                
        return cleaned_data

class BookingServiceForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(status='approved'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        exclude_catering = kwargs.pop('exclude_catering', False)
        super().__init__(*args, **kwargs)
        
        # If venue catering is selected, exclude catering services from options
        if exclude_catering:
            try:
                catering_category = ServiceCategory.objects.get(name='Catering')
                self.fields['service'].queryset = Service.objects.filter(
                    status='approved'
                ).exclude(
                    category=catering_category
                )
            except ServiceCategory.DoesNotExist:
                pass  # If no catering category exists, show all services
    
    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        quantity = cleaned_data.get('quantity')
        
        if service and not quantity:
            self.add_error('quantity', "Please specify a quantity.")
        elif quantity and not service:
            self.add_error('service', "Please select a service.")
            
        return cleaned_data