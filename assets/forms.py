from django import forms
from django.forms import ModelForm, Textarea, TimeInput
from .models import Asset, Asset_User_Mapping, Asset_OpenDays_Exception

class AssetForm(ModelForm):

	class Meta:
		model = Asset
		fields = ['asset_display_name', 
					'asset_max_bookings', 'num_days_display_to_users']
		
        

class AssetExceptionForm(forms.ModelForm):

    class Meta:
        model = Asset_OpenDays_Exception
        fields = ['the_date','asset_slot_duration','asset_opening_time_exception','asset_closing_time_exception', 'asset_max_bookings', 'is_closed']
        
        year = forms.CharField(widget=forms.HiddenInput())
        month = forms.CharField(widget=forms.HiddenInput())
        day = forms.CharField(widget=forms.HiddenInput())


class AssetMemberForm(forms.ModelForm):

    class Meta:
        model = Asset_User_Mapping
        fields = ['asset_membership_ID','asset_swipe_ID','admin_notes','is_owner','is_activated']
        widgets={
        	'admin_notes':Textarea(attrs={'cols':3, 'rows':5}),
        }
