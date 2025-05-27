from django import forms
from .models import VenueReview

class VenueReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1, 
        max_value=5, 
        widget=forms.HiddenInput()  # Changed to hidden input since we're using star UI
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500', 
            'placeholder': 'Share your experience with this venue...',
            'rows': 3
        })
    )
    
    class Meta:
        model = VenueReview
        fields = ['rating', 'comment']