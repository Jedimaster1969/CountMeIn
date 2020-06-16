from django import template
from assets.models import Asset, Asset_User_Mapping, Asset_OpenDays_Exception
from booking.models import Booking
from datetime import date, datetime, timedelta

register = template.Library()

def is_asset_activated(asset_id):
	# it will return value of is_activated field

	try:
		asset_detail = Asset.objects.get(id=asset_id)

	except Asset.DoesNotExist:

		asset_activated = False

	else:
		asset_activated = asset_detail.is_activated

	return asset_activated

@register.simple_tag
def is_asset_verifying_members(asset_id):
	# it will return the value of requires_member_verification field
	#or FALSE if it asset doesn't exist
	
	try:
		asset_detail = Asset.objects.get(id=asset_id)

	except Asset.DoesNotExist:

		member_verification = False

	else:
		member_verification = asset_detail.requires_member_verification

	return member_verification

@register.simple_tag
def num_members_to_be_verified(asset_id):
	# it will return the total number of members that are not yet verified
	#or FALSE if it asset doesn't exist
	
	#only return the total of unverified if the venue has chosen to verify
	if is_asset_verifying_members(asset_id):
		
		members = Asset_User_Mapping.objects.all().filter(asset_ID_id = asset_id, is_verified= False)

		if members:

			return members.count()

		else:

			return 0

	else:

		return 0

@register.simple_tag
def num_members_deactivated(asset_id):
	# it will return the total number of members that have been deactivated
	
	members = Asset_User_Mapping.objects.all().filter(asset_ID_id = asset_id, is_activated = False)

	if members:

		return members.count()

	else:

		return 0

@register.simple_tag
def num_members_activated(asset_id):
	# it will return the total number of members that have been deactivated
	
	members = Asset_User_Mapping.objects.all().filter(asset_ID_id = asset_id, is_activated = True)

	if members:

		return members.count()

	else:

		return 0


@register.simple_tag
def get_user_verification_status(user_id, asset_id):
	# it will return the value of is_verified field in Asset_User_Mapping table
	#or FALSE if it asset doesn't exist

	asset_mapping = Asset_User_Mapping.objects.all().filter(asset_ID_id=asset_id,user_ID_id=user_id)

	if asset_mapping:

		if asset_mapping.count() > 1:

			return False		
		
		else:
			
			for item in asset_mapping:

				return item.is_verified

	else:

		return False

@register.simple_tag
def get_asset_opening_days(asset_id):
	
	try:
		asset = Asset.objects.get(id= asset_id)
	
	except Asset.DoesNotExist:

		return 0

	else:

		return asset.asset_opening_days.asset_opening_days


@register.simple_tag
def get_display_time_period_for_booking(asset_id):
	#the number of days in the future (from current day)
	#that the venue wants to allow users to make bookings

	try:
		asset_detail = Asset.objects.get(id= asset_id)

	except Asset.DoesNotExist:

		time_period = "5"

	else:

		time_period = asset_detail.num_days_display_to_users

	return time_period


def get_asset_booking_dates_for_display(asset_id):
	#this function returns the list of applicable booking dates
	#so they can be display on the calendar
	#it takes into account whether the venue is open on that day
	#(either in the exception table as 'closed' OR 
	# it's in the defaults that it's open 5,6, or 7 days OR
	#there are already bookings on that date*)
	#*this could happen if the venue changed from 5,6, or 7 days but there were already bookings made

	#first get the standard dates and add to an object
	#then make list of all dates to be removed
	#finally remove them from the date object 

	date_list = []

	try:
		
		asset = Asset.objects.get(id=asset_id)
	
	except Asset.DoesNotExist:
		
		return date_list

	else:

		num_display_dates = asset.num_days_display_to_users
		start_date_to_display = datetime.now()
		full_duration = timedelta(days = num_display_dates)
		one_day = timedelta(days = 1)
		end_date_to_display = start_date_to_display + full_duration

		#first add ALL dates in the range
		#loop through from start_date_to_display to end_date_to_display adding each date to date_list
		for item in range((end_date_to_display-start_date_to_display).days):
			
			entry_date = start_date_to_display + item*one_day
			#when appending, only save Year, Month, Day part
			date_list.append(datetime(entry_date.year, entry_date.month, entry_date.day))
		
	
		#now remove days if the asset is not open for business that day
		#check business days with asset_opening_days
		remove_list = []

		business_days = asset.asset_opening_days.asset_opening_days
		

		if business_days == 5:
			#print(business_days)
			for item in date_list:
				#remove Saturdays and Sundays
				if item.weekday() == 5 or item.weekday() == 6:
					#normally these days would be removed BUT
					#don't delete these days if they are in the exception table and open for business
					try:
						additional_open_date = Asset_OpenDays_Exception.objects.get(asset_ID_id=asset_id, 
						the_date=item, is_closed = False)
						
					except Asset_OpenDays_Exception.DoesNotExist:
						
						remove_list.append(item)


		elif business_days == 6:
			#print(business_days)
			for item in date_list:
				#remove Sundays
				if item.weekday() == 6:

					try:
						additional_open_date = Asset_OpenDays_Exception.objects.get(asset_ID_id=asset_id, 
						the_date=item, is_closed = False)

					except Asset_OpenDays_Exception.DoesNotExist:
						
						remove_list.append(item)		
					
		
		#now check if there are any additional dates listed for closing in exception table

		additional_close_dates = Asset_OpenDays_Exception.objects.all().filter(asset_ID_id=asset_id, 
			the_date__gte=start_date_to_display, the_date__lte=end_date_to_display, is_closed = True)
		
		if additional_close_dates:
			#some dates found
			for item in additional_close_dates:
				#print (item.the_date)
				#.strftime("%Y-%m-%d")

				#it may have already been removed (if it was a weekend date and closed) so check first
				if datetime(item.the_date.year, item.the_date.month, item.the_date.day) in date_list:
					remove_list.append(datetime(item.the_date.year, item.the_date.month, item.the_date.day))

	
		if len(remove_list)>0:
			for item in remove_list:
				if item in date_list:
					date_list.remove(item)

		print("date list length:")	
		print(len(date_list))	

		return date_list

def get_asset_booking_time_links(asset_id, the_date):

	#the_date sent to this function MUST come from get_asset_booking_dates_for_display
	#because that function already checked if the venue is open on the date
	#so THIS function doesn't have to do that check as well

	#this function returns a list of booking slot times for the asset based on:
	# 	the_date provided
	#	the current time (because 'past' and 'future' is based on time as well as day)
	#	asset_slot_duration_min (how long the slot is)
	#	asset weekend/weekday opening and closing times
	#	exceptions for the date (already taken care of in get_asset_booking_dates_for_display)
	#	number of other bookings on the_date ***not done yet

	list = []

	try:
		
		asset = Asset.objects.get(id=asset_id)
	
	except Asset.DoesNotExist:
		
		return list

	else:

		#things to check
		#check if the_date is in the exception table (to extract the different start/end times, different slot duration)
		#check if the_date is a weekday or weekend (these may have different start/end times, different slot duration)
		
		try:
			
			exception_date = Asset_OpenDays_Exception.objects.get(asset_ID_id=asset_id, the_date=the_date, is_closed = False)

		except Asset_OpenDays_Exception.DoesNotExist:

			#use variables from the main asset table, checking first if it's a weekend
			asset_slot_mins = asset.asset_slot_duration.asset_slot_duration_mins

			if the_date.weekday() == 5 or the_date.weekday() == 6:

				start_time = asset.asset_weekend_opening_time
				close_time = asset.asset_weekend_closing_time

			else:
			
				start_time = asset.asset_weekday_opening_time
				close_time = asset.asset_weekday_closing_time

		else:
		
			#use variables from this asset exception table
			start_time = exception_date.asset_opening_time_exception
			close_time = exception_date.asset_closing_time_exception
			asset_slot_mins = exception_date.asset_slot_duration.asset_slot_duration_mins	


		formatted_start_time = datetime(the_date.year,the_date.month,the_date.day, start_time.hour, start_time.minute)

		#turn into a datetime object to be easier to manipulate
		formatted_close_time = datetime(the_date.year,the_date.month,the_date.day, close_time.hour, close_time.minute)

		formatted_current_time = datetime.now()

		#loop through times adding interval

		while formatted_start_time <= formatted_close_time:

			#this if... will ensure that no time-slots are added TODAY for times that have passed
			if formatted_start_time > formatted_current_time:

				#list.append({"the_time":formatted_start_time})
				list.append(formatted_start_time)

			formatted_start_time = formatted_start_time + timedelta(minutes = asset_slot_mins)
			#print(formatted_start_time)
	
	return list


def is_date_in_exception_table(asset_id, the_date):
	
	try:
		the_record = Asset_OpenDays_Exception.objects.get(asset_ID=asset_id, 
						the_date=the_date)

	except Asset_OpenDays_Exception.DoesNotExist:

		in_table = False

	else:
		in_table = True

	return in_table 

def get_exception_record(asset_id, the_date):

	try:
		the_record = Asset_OpenDays_Exception.objects.get(asset_ID=asset_id, 
						the_date=the_date)

	except Asset_OpenDays_Exception.DoesNotExist:
		
		return False
	
	else:
		
		the_record


def get_exception_table_max_bookings(asset_id, the_date):

	try:
		the_record = Asset_OpenDays_Exception.objects.get(asset_ID_id=asset_id, 
						the_date=the_date)

	except Asset_OpenDays_Exception.DoesNotExist:

		max_bookings = 0

	else:
		max_bookings = the_record.asset_max_bookings

	return max_bookings 


def get_asset_table_max_bookings(asset_id):

	try:
		the_record = Asset.objects.get(asset_ID_id=asset_id)

	except Asset.DoesNotExist:

		max_bookings = 0

	else:
		max_bookings = the_record.asset_max_bookings

	return max_bookings


def get_asset_from_invite_code(invite_code):
	# this function can be used by any view
	# it will return the Asset if it finds a matching Invite_Code

	try:
	    asset_detail = Asset.objects.get(invite_code_url__contains=invite_code)

	except Asset.DoesNotExist:
	   matching_asset = False

	else:
	   matching_asset = asset_detail

	return matching_asset  

@register.simple_tag
def get_total_asset_members(asset_id):

    total_members = 0
    all_users = Asset_User_Mapping.objects.all().filter(asset_ID_id=asset_id)

    total_members = all_users.count()


    return total_members


@register.simple_tag
def get_total_asset_owners(asset_id):

    total_owners = 0
    all_owners = Asset_User_Mapping.objects.all().filter(asset_ID_id=asset_id, is_owner=True)

    total_owners = all_owners.count()


    return total_owners

@register.simple_tag
def is_user_also_owner(user_id, asset_id):

    # this function checks to see if the user_id is the owner_id
    # for the given asset_id
    # if they are then this function returns TRUE
    try:
        user_linking = Asset_User_Mapping.objects.get(user_ID=user_id, is_owner=True, asset_ID=asset_id)

    except Asset_User_Mapping.DoesNotExist:
        user_is_an_owner = False

    else:
        user_is_an_owner = True

    return user_is_an_owner

@register.simple_tag
def is_an_owner_in_asset_list(asset_list):
	#returns True if there is an owner in one of the assets in the asset list
	has_an_owner = False

	for asset in asset_list:

		if asset.is_owner:
			has_an_owner = True
			break

	return has_an_owner

@register.simple_tag
def get_membership_id(user_id, asset_id):
	
	try:

		user_linking = Asset_User_Mapping.objects.get(user_ID=user_id, asset_ID=asset_id)

	except Asset_User_Mapping.DoesNotExist:

		return ""
		
	return user_linking.asset_membership_ID

@register.simple_tag
def get_swipe_id(user_id, asset_id):
	
	try:

		user_linking = Asset_User_Mapping.objects.get(user_ID=user_id, asset_ID=asset_id)

	except Asset_User_Mapping.DoesNotExist:

		return ""

	return user_linking.asset_swipe_ID