from django import forms
from .models import ServiceReview

class ServiceReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1, 
        max_value=5, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rating (1-5)'
        })
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': 'Write your review here...',
            'rows': 4
        })
    )
    
    class Meta:
        model = ServiceReview
        fields = ['rating', 'comment']