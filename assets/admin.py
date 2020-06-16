from django.contrib import admin
from .models import Asset, AssetType, Asset_User_Mapping,AssetOpeningDay,AssetSlotDuration,Asset_OpenDays_Exception

admin.site.register(Asset)
admin.site.register(Asset_User_Mapping)
admin.site.register(AssetOpeningDay)
admin.site.register(AssetType)
admin.site.register(AssetSlotDuration)
admin.site.register(Asset_OpenDays_Exception)