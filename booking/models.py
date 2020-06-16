from django.db import models
from assets.models import Asset
from django.utils import timezone
from django.conf import settings
from datetime import datetime

class Booking(models.Model):

	class Meta:
		app_label="booking"
		constraints=[models.UniqueConstraint(fields=['requested_date','asset_ID','requested_start_time'], name="unique session")]

	asset_ID = models.ForeignKey(Asset,on_delete=models.CASCADE, related_name="venue_booked")
	requested_by_user_ID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requested_by")
	requested_date = models.DateField(blank=False)
	requested_start_time = models.TimeField(blank=False)
	date_booking_created = models.DateTimeField(default=timezone.now)
	#the following fields are in the table but not used for V1
	#in V1 it is the USER that is verified (or not) and not each individual booking
	is_auto_approved = models.BooleanField(default=False)
	is_pending = models.BooleanField(default=False)
	is_approved = models.BooleanField(default=False)
	date_approved = models.DateTimeField(blank=True, null=True)
	approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,blank=True, null=True, related_name="approved_by")
	is_denied = models.BooleanField(default=False)
	date_denied = models.DateTimeField(blank=True, null=True)
	denied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,blank=True, null=True, related_name="denied_by")

	def __str__(self):
		return "%s at %s for %s requested by %s %s " % (self.requested_date.strftime('%d %b, %Y'), self.requested_start_time.strftime('%H:%S'), self.asset_ID.asset_display_name, self.requested_by_user_ID.first_name, self.requested_by_user_ID.last_name)
