from django import forms
from django.utils import timezone
from .models import Booking, BookingService
from apps.services.models import Service

class BookingForm(forms.ModelForm):
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
    
    class Meta:
        model = Booking
        fields = ['event_date', 'start_time', 'end_time', 'guest_count', 'event_type', 'phone_number', 'special_requests']
    
    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get('event_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if event_date and event_date < timezone.now().date():
            self.add_error('event_date', "You cannot book a date in the past.")
        
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', "End time must be after start time.")
            
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
    
    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        quantity = cleaned_data.get('quantity')
        
        if service and not quantity:
            self.add_error('quantity', "Please specify a quantity.")
        elif quantity and not service:
            self.add_error('service', "Please select a service.")
            
        return cleaned_data