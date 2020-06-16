from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime

class AssetType(models.Model):

	class Meta:
		app_label = "assets"

	asset_type = models.CharField(verbose_name="Venue Classification", max_length=30)

	def __str__(self):
		return "(%s) %s" % (self.id, self.asset_type)

class AssetOpeningDay(models.Model):

	class Meta:
		app_label = "assets"

	asset_opening_days = models.IntegerField(verbose_name="Business Days per Week")
	asset_opening_days_desc = models.CharField(verbose_name="Day Groups", max_length=30)

	def __str__(self):
		return "%s days (%s)" % (self.asset_opening_days, self.asset_opening_days_desc)

class AssetSlotDuration(models.Model):

	class Meta:
		app_label = "assets"

	asset_slot_duration_mins = models.IntegerField(verbose_name="Booking Frequency")
	asset_slot_duration_desc = models.CharField(verbose_name="Frequency Description", max_length=30)

	def __str__(self):
		return "%s mins (%s)" % (self.asset_slot_duration_mins, self.asset_slot_duration_desc)

class Asset(models.Model):

	class Meta:
		app_label = "assets"

	def get_default_invite_code():
		unique_code = datetime.now().strftime("%f%S%M%H")
		return unique_code

	def get_default_invite_url():
		unique_code = datetime.now().strftime("%f%S%M%H")
		#return "%s%s" % ("https://www.countmein.ie/", unique_code)	
		return "%s%s%s" % (settings.INVITE_START_LINK, unique_code,"/")

	asset_display_name = models.CharField(verbose_name="name of venue", max_length=255, blank=False)
	asset_type = models.ForeignKey(AssetType, verbose_name="type of venue", on_delete=models.CASCADE, default=1)
	asset_opening_days = models.ForeignKey(AssetOpeningDay, verbose_name="Days Open per Week", on_delete=models.CASCADE, default=3)
	date_created = models.DateTimeField(default=timezone.now)
	invite_code = models.CharField(max_length=12,verbose_name="invitation code to share with members",default=0, unique=True)
	invite_code_url = models.URLField(verbose_name="link to share with members", default=get_default_invite_url,unique=True)
	asset_users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name = "list of members", through='Asset_User_Mapping', through_fields=('asset_ID','user_ID'))
	asset_image = models.ImageField(upload_to='asset_images', verbose_name="venue_image", blank=True, null=True)
	is_activated = models.BooleanField(blank=True, verbose_name="is this venue activated?", default=False)
	requires_member_verification = models.BooleanField(blank=True, verbose_name="venue requires member verification?", default=False)
	asset_slot_duration = models.ForeignKey(AssetSlotDuration, verbose_name="Booking Slot Duration (Minutes)", on_delete=models.CASCADE, default=1)
	asset_weekday_opening_time = models.TimeField(verbose_name="Opening Time on a Weekday", default="09:00")
	asset_weekday_closing_time = models.TimeField(verbose_name="Closing Time on a Weekday", default="20:00")
	asset_weekend_opening_time = models.TimeField(verbose_name="Opening Time on a Weekend", default="10:00")
	asset_weekend_closing_time = models.TimeField(verbose_name="Closing Time on a Weekend", default="18:00")
	asset_max_bookings = models.IntegerField(verbose_name="Member Limit (per booking slot)", default=3)
	num_days_display_to_users = models.IntegerField(verbose_name="future days bookings allowed", default=30, blank=False)

	def __str__(self):
		return "%s | %s " % (self.id, self.asset_display_name)


class Asset_OpenDays_Exception(models.Model):

	class Meta:
		app_label = "assets"
		constraints=[models.UniqueConstraint(fields=['the_date','asset_ID'], name="unique exception")]

	the_date = models.DateField(verbose_name="exception date")
	asset_ID = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="the_asset")
	asset_slot_duration = models.ForeignKey(AssetSlotDuration, verbose_name="Booking Slot Duration (Minutes)", on_delete=models.CASCADE, default=1)
	asset_opening_time_exception = models.TimeField(verbose_name="Opening Time", default="09:00")
	asset_closing_time_exception = models.TimeField(verbose_name="Closing Time", default="20:00")
	asset_max_bookings = models.IntegerField(verbose_name="Member Booking Limit", default=3)
	is_closed = models.BooleanField(verbose_name="Venue is closed", default = False)

	def __str__(self):
		return self.asset_ID.asset_display_name

class Asset_User_Mapping(models.Model):

	class Meta:
		app_label = "assets"

	user_ID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="asset_users")
	asset_ID = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="the_asset_asset")
	is_owner = models.BooleanField(blank=False, verbose_name="Member is staff?")
	date_created = models.DateTimeField(default=timezone.now)
	asset_membership_ID = models.CharField(max_length=255, verbose_name="Member ID", blank=True, null=True)
	asset_swipe_ID = models.CharField(max_length=255, verbose_name="Swipe ID", blank=True, null=True)
	is_activated = models.BooleanField(blank=False, verbose_name="Activated", default=True)
	is_verified = models.BooleanField(blank=False, verbose_name="is user verified?", default=False)
	invite_code_used = models.CharField(max_length=12,verbose_name="invitation code used")
	admin_notes = models.TextField(verbose_name="Office Notes", blank=True, null=True)

	
	def __str__(self):
		return "ID: %s | %s %s | %s ............ %s" % (self.user_ID_id, self.user_ID.first_name, self.user_ID.last_name, self.user_ID.email, self.asset_ID, )



