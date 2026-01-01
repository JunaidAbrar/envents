from django import forms
from apps.venues.models import Venue, VenueCategory, Amenity, VenuePhoto, VenueCateringPackage
from apps.services.models import Service, ServiceCategory, ServicePhoto


class VenueSubmissionForm(forms.ModelForm):
    """Form for venue owners to submit their venues for approval"""
    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    # Add multiple category selection
    categories = forms.ModelMultipleChoiceField(
        queryset=VenueCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select all categories that apply to your venue"
    )
    
    class Meta:
        model = Venue
        fields = [
            'name', 'description', 'categories', 'location', 'city', 
            'address', 'capacity', 'pricing_type', 'hourly_price', 'flat_price', 
            'contact_number', 'email', 'amenities'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'General Location'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500', 'min': 1}),
            'pricing_type': forms.Select(attrs={'class': 'form-control w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500', 'id': 'id_pricing_type_venue'}),
            'hourly_price': forms.NumberInput(attrs={'class': 'form-control w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500', 'id': 'id_hourly_price_venue', 'min': 0, 'step': '0.01'}),
            'flat_price': forms.NumberInput(attrs={'class': 'form-control w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500', 'id': 'id_flat_price_venue', 'min': 0, 'step': '0.01'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500', 'placeholder': 'Contact Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Contact Email'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        # No need for initializing category field as we're using categories field now
    
    def clean(self):
        """Validate pricing fields based on pricing_type"""
        cleaned_data = super().clean()
        pricing_type = cleaned_data.get('pricing_type')
        hourly_price = cleaned_data.get('hourly_price')
        flat_price = cleaned_data.get('flat_price')
        
        if pricing_type == 'HOURLY':
            if not hourly_price or hourly_price <= 0:
                raise forms.ValidationError("Hourly price is required and must be greater than 0 for hourly pricing.")
            # Clear the unused field
            cleaned_data['flat_price'] = None
        elif pricing_type == 'FLAT':
            if not flat_price or flat_price <= 0:
                raise forms.ValidationError("Flat price is required and must be greater than 0 for flat rate pricing.")
            # Clear the unused field
            cleaned_data['hourly_price'] = None
        
        return cleaned_data
    
    def save(self, commit=True):
        venue = super().save(commit=False)
        venue.owner = self.owner
        venue.status = 'pending'  # Default status is pending approval
        
        if commit:
            venue.save()
            # Save the categories many-to-many relationship
            venue.category.set(self.cleaned_data['categories'])
            # Save other many-to-many relationships
            self.save_m2m()
        return venue


class ServiceSubmissionForm(forms.ModelForm):
    """Form for service providers to submit their services for approval"""
    
    class Meta:
        model = Service
        fields = [
            'name', 'description', 'category', 'pricing_type', 'hourly_price', 'flat_price', 
            'contact_number', 'email'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'pricing_type': forms.Select(attrs={'class': 'form-control w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500', 'id': 'id_pricing_type_service'}),
            'hourly_price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_hourly_price_service', 'min': 0, 'step': '0.01'}),
            'flat_price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_flat_price_service', 'min': 0, 'step': '0.01'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Contact Email'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.provider = kwargs.pop('provider', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ServiceCategory.objects.all()
        self.fields['category'].empty_label = "Select a category"
    
    def clean(self):
        """Validate pricing fields based on pricing_type"""
        cleaned_data = super().clean()
        pricing_type = cleaned_data.get('pricing_type')
        hourly_price = cleaned_data.get('hourly_price')
        flat_price = cleaned_data.get('flat_price')
        
        if pricing_type == 'HOURLY':
            if not hourly_price or hourly_price <= 0:
                raise forms.ValidationError("Hourly price is required and must be greater than 0 for hourly pricing.")
            # Clear the unused field
            cleaned_data['flat_price'] = None
        elif pricing_type == 'FLAT':
            if not flat_price or flat_price <= 0:
                raise forms.ValidationError("Flat price is required and must be greater than 0 for flat rate pricing.")
            # Clear the unused field
            cleaned_data['hourly_price'] = None
        
        return cleaned_data
    
    def save(self, commit=True):
        service = super().save(commit=False)
        service.provider = self.provider
        service.status = 'pending'  # Default status is pending approval
        if commit:
            service.save()
        return service


class VenuePhotoForm(forms.ModelForm):
    """Form for uploading venue photos"""
    
    class Meta:
        model = VenuePhoto
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Photo caption (optional)'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ServicePhotoForm(forms.ModelForm):
    """Form for uploading service photos"""
    
    class Meta:
        model = ServicePhoto
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Photo caption (optional)'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VenueCateringPackageForm(forms.ModelForm):
    """Form for adding catering packages to venues"""
    
    class Meta:
        model = VenueCateringPackage
        fields = ['name', 'description', 'price', 'price_type', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500', 
                'placeholder': 'Package Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500', 
                'rows': 3, 
                'placeholder': 'Describe what is included in this package'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500', 
                'min': 0, 
                'step': 0.01
            }),
            'price_type': forms.TextInput(attrs={
                'class': 'form-control w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500', 
                'placeholder': 'per person, per plate, flat rate, etc.'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            }),
        }


# Form for the image upload
VenuePhotoFormSet = forms.modelformset_factory(
    VenuePhoto, 
    form=VenuePhotoForm,
    extra=3,  # Number of empty forms to display
    max_num=5,  # Maximum number of forms to display
    can_delete=True  # Allow deleting images
)

ServicePhotoFormSet = forms.modelformset_factory(
    ServicePhoto, 
    form=ServicePhotoForm,
    extra=3,  # Number of empty forms to display
    max_num=5,  # Maximum number of forms to display
    can_delete=True  # Allow deleting images
)

# Form for catering packages
VenueCateringPackageFormSet = forms.modelformset_factory(
    VenueCateringPackage,
    form=VenueCateringPackageForm,
    extra=2,  # Number of empty forms to display
    max_num=5,  # Maximum number of forms to display
    can_delete=True  # Allow deleting packages
)