from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy

from .forms import (
    VenueSubmissionForm, ServiceSubmissionForm, 
    VenuePhotoFormSet, ServicePhotoFormSet,
    VenueCateringPackageFormSet
)
from apps.venues.models import Venue, VenueCateringPackage
from apps.services.models import Service

class BusinessDashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view for venue owners and service providers to submit listings."""
    template_name = 'business/dashboard.html'


class VenueSubmissionView(LoginRequiredMixin, TemplateView):
    """View for venue owners to submit their venues for approval."""
    template_name = 'business/venue_submission.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venue_form'] = VenueSubmissionForm()
        context['photo_formset'] = VenuePhotoFormSet(queryset=Venue.objects.none())
        context['catering_formset'] = VenueCateringPackageFormSet(
            queryset=VenueCateringPackage.objects.none(),
            prefix='catering'
        )
        return context
    
    def post(self, request, *args, **kwargs):
        venue_form = VenueSubmissionForm(request.POST, owner=request.user)
        photo_formset = VenuePhotoFormSet(request.POST, request.FILES, queryset=Venue.objects.none())
        catering_formset = VenueCateringPackageFormSet(
            request.POST, queryset=VenueCateringPackage.objects.none(), prefix='catering'
        )
        
        if venue_form.is_valid() and photo_formset.is_valid() and catering_formset.is_valid():
            return self._form_valid(venue_form, photo_formset, catering_formset)
        else:
            return self._form_invalid(venue_form, photo_formset, catering_formset)
    
    def _form_valid(self, venue_form, photo_formset, catering_formset):
        try:
            with transaction.atomic():
                # Save the venue
                venue = venue_form.save()
                
                # Process the photo formset
                photo_instances = photo_formset.save(commit=False)
                for instance in photo_instances:
                    instance.venue = venue
                    instance.save()
                
                # Handle deleted images
                for obj in photo_formset.deleted_objects:
                    obj.delete()
                
                # Process the catering package formset
                catering_instances = catering_formset.save(commit=False)
                for instance in catering_instances:
                    instance.venue = venue
                    instance.save()
                
                # Handle deleted catering packages
                for obj in catering_formset.deleted_objects:
                    obj.delete()
                
                messages.success(self.request, "Your venue has been submitted for review. We'll notify you once it's approved.")
                return redirect('business:dashboard')
        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return self._form_invalid(venue_form, photo_formset, catering_formset)
    
    def _form_invalid(self, venue_form, photo_formset, catering_formset):
        context = self.get_context_data()
        context['venue_form'] = venue_form
        context['photo_formset'] = photo_formset
        context['catering_formset'] = catering_formset
        return render(self.request, self.template_name, context)


class ServiceSubmissionView(LoginRequiredMixin, TemplateView):
    """View for service providers to submit their services for approval."""
    template_name = 'business/service_submission.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_form'] = ServiceSubmissionForm()
        context['photo_formset'] = ServicePhotoFormSet(queryset=Service.objects.none())
        return context
    
    def post(self, request, *args, **kwargs):
        service_form = ServiceSubmissionForm(request.POST, provider=request.user)
        photo_formset = ServicePhotoFormSet(request.POST, request.FILES, queryset=Service.objects.none())
        
        if service_form.is_valid() and photo_formset.is_valid():
            return self._form_valid(service_form, photo_formset)
        else:
            return self._form_invalid(service_form, photo_formset)
    
    def _form_valid(self, service_form, photo_formset):
        try:
            with transaction.atomic():
                # Save the service
                service = service_form.save()
                
                # Process the photo formset
                instances = photo_formset.save(commit=False)
                for instance in instances:
                    instance.service = service
                    instance.save()
                
                # Handle deleted images
                for obj in photo_formset.deleted_objects:
                    obj.delete()
                
                messages.success(self.request, "Your service has been submitted for review. We'll notify you once it's approved.")
                return redirect('business:dashboard')
        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return self._form_invalid(service_form, photo_formset)
    
    def _form_invalid(self, service_form, photo_formset):
        context = self.get_context_data()
        context['service_form'] = service_form
        context['photo_formset'] = photo_formset
        return render(self.request, self.template_name, context)
