from django import forms
from booking.models import Booking
import datetime


class BookingForm(forms.Form):
    year = forms.CharField(widget=forms.HiddenInput())
    month = forms.CharField(widget=forms.HiddenInput())
    day = forms.CharField(widget=forms.HiddenInput())
    hour = forms.CharField(widget=forms.HiddenInput())
    minute = forms.CharField(widget=forms.HiddenInput())
  


