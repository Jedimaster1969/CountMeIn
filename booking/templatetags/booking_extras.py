from django import template
import datetime
from assets.models import Asset_User_Mapping, Asset_OpenDays_Exception
from booking.models import Booking
from assets.templatetags.assets_extras import get_exception_table_max_bookings, get_asset_table_max_bookings
from django.db.models import Q

register = template.Library()

@register.simple_tag
def return_user_asset_ids(request):

    assets = Asset_User_Mapping.objects.all().filter(user_ID=request.user,asset_ID_id__is_activated=True)

    return assets


@register.filter
def get_num_asset_grids(assets):

    total_assets = 0

    for asset in assets:
        total_assets += 1

    #display max 4 in the grid
    if total_assets > 4:
        total_assets = 4

    return total_assets

@register.simple_tag
def get_booking_asset_name(booking_id):

    item = Booking.objects.get(id=booking_id)
    asset = item.asset_ID.asset_display_name

    return asset

@register.simple_tag
def get_booking_asset_id(booking_id):
    item = Booking.objects.get(id=booking_id)
    asset = item.asset_ID

    return asset

@register.simple_tag
def get_booking_date(booking_id):

    try:
        item = Booking.objects.get(id=booking_id)

    except Booking.DoesNotExist:

        the_date = 0

    else:

        the_date = item.requested_date

    return the_date

@register.simple_tag
def get_booking_start_time(booking_id):

    item = Booking.objects.get(id=booking_id)
    the_time = item.requested_start_time

    return the_time

@register.simple_tag
def get_booking_status(booking_id):

    if is_booking_approved(booking_id):

        return "Approved"

    elif is_booking_pending(booking_id):

        return "Pending"

    elif is_booking_denied(booking_id):

        return "Denied"
    
    else:

        return "N/A"    


@register.simple_tag
def is_booking_approved(booking_id):

    approved_status = Booking.objects.all().filter(id=booking_id, is_approved=True)
    auto_approved_status = Booking.objects.all().filter(id=booking_id, is_auto_approved=True)

    # if either are True then the booking is aproved
    if approved_status or auto_approved_status:

        return True

    else:

        return False

@register.simple_tag
def is_booking_pending(booking_id):

    pending_status = Booking.objects.all().filter(id=booking_id, is_pending=True)

    if pending_status:

        return True

    else:

        return False

@register.simple_tag
def is_booking_denied(booking_id):

    denied_status = Booking.objects.all().filter(id=booking_id, is_denied=True)

    if denied_status:

        return True

    else:

        return False

@register.simple_tag
def get_total_bookings_venue(asset_id, **kwargs):
    
    # this function returns the number of booking refs
    # for the Asset
    time_period = ""
    selected_date = ""

    if 'time_period' in kwargs:
        time_period = kwargs['time_period']
     
    if 'selected_date' in kwargs:
        selected_date = kwargs['selected_date']    

    the_bookings_num = 0

    the_bookings = get_bookings(time_period=time_period, selected_date=selected_date, asset_id = asset_id)
    
    the_bookings_num = len(the_bookings)

    return the_bookings_num





@register.simple_tag
def get_total_bookings_user(user_id, **kwargs):
  
    # this function returns the number of booking refs
    # for the Asset and user
    time_period = ""
    selected_date = ""
    asset_id = 0

    if 'asset_id' in kwargs:
        asset_id = kwargs['asset_id']

    if 'time_period' in kwargs:
        time_period = kwargs['time_period']

    if 'selected_date' in kwargs:
        selected_date = kwargs['selected_date']  
            
    the_bookings_num = 0
    
    the_bookings = get_bookings(time_period=time_period, selected_date=selected_date, asset_id = asset_id, user_id = user_id)
    
    the_bookings_num = len(the_bookings)

    return the_bookings_num

    
def is_booking_related_to_this_user(user_id, booking_id):

    try:

        the_booking = Booking.objects.get(id=booking_id, requested_by_user_ID=user_id) 
    
    except Booking.DoesNotExist:

        return False

    else:

        return True

def is_date_a_weekday(selected_date):

    if selected_date.weekday() == 5 or selected_date.weekday() == 6:

        return False

    else:

        return True




def clear_date_and_time_from_session():

    try:
        #empty the session variables
        request.session['selected_year_cal']=[]
        request.session['selected_month_cal']=[]
        request.session['selected_day_cal']=[]
        request.session['selected_hour_cal']=[]
        request.session['selected_minute_cal']=[]

        return True

    except:

        return False


def clear_exception_date_from_session():

    try:
        #empty the session variables
        request.session['exception_year_cal']=[]
        request.session['exception_month_cal']=[]
        request.session['exception_day_cal']=[]

        return True

    except:

        return False


def time_slot_fully_booked(the_asset, the_date, the_time):
    pass

def time_slot_fully_booked_WIP(the_asset, the_date, the_time):
   
    #count the number of bookings for an asset on a given date and timeslot

    booking_detail = Booking.objects.all().filter(requested_date=the_date, asset_ID =the_asset, requested_start_time=the_time)

    the_count = booking_detail.count()

    #compare the_count to the allowed number for the date/venue checking Asset table and also Asset Exception table
    exception_table_slot_max = get_exception_table_max_bookings(the_asset, the_date)
    asset_table_slot_max = get_asset_table_max_bookings(the_asset)

    if exception_table_slot_max > 0:

        if the_count < exception_table_slot_max:
            fully_booked = False

        else:
            fully_booked = True

    else:

        if the_count < asset_table_slot_max:
            fully_booked = False

        else:
            fully_booked = True
        


    return fully_booked

def get_first_date_in_booking_list(bookings):

    first_booking = bookings[0]
    first_date = first_booking.requested_date

    return first_date

def get_bookings(**kwargs):

    # by default, this query if sent NO kwargs will return a set of dates and ids for
    # all future dates for all assets for all users
    # using the optional parameters can return a set of dates and ids for
    # all dates OR all past OR all futures dates, one or all users, one or all assets
    # or for just one date

    requested_by = 0
    this_asset = 0
    time_period = ""
    is_pending = ""
    is_approved = ""
    selected_date = ""

    #owned_by = 0

    #if kwargs.has_key("user_id"): PYTHON 2
    if 'user_id' in kwargs: 
        requested_by = kwargs['user_id']

    #if kwargs.has_key("asset_id"):
    if 'asset_id' in kwargs:     
        this_asset = kwargs['asset_id']

    # time period expected: 'all', 'past', or 'future'
    #if kwargs.has_key("time_period"):
    if 'time_period' in kwargs:  
        time_period = kwargs['time_period']

    #if kwargs.has_key("pending"):
    if 'pending' in kwargs:  
        is_pending = kwargs['pending']

    #if kwargs.has_key("approving"):
    if 'approving' in kwargs:  
        is_approved = kwargs['approving']

    #if kwargs.has_key("owner_id"):
    #if 'owner_id' in kwargs: 
    #    owned_by = kwargs['owner_id']

    if 'selected_date' in kwargs:
        selected_date = kwargs['selected_date']
        if not type(selected_date) is datetime.date:
            selected_date = ""
           

    # from http://stackoverflow.com/questions/852414/how-to-dynamically-compose-an-or-query-filter-in-django
    query_params = Q()

   #if owned_by > 0:
   #     query_params.add(Q(slot_owner_id_id=owned_by), Q.AND)

    if requested_by != 0:
        query_params.add(Q(requested_by_user_ID=requested_by), Q.AND)

    if this_asset != 0:
        query_params.add(Q(asset_ID=this_asset), Q.AND)

    if selected_date:
        # checking one date only
        # but check if it's TODAY

        if selected_date == datetime.date.today():
            # time matters - only send back future bookings from current point in time
            query_params.add(Q(requested_date=selected_date) & Q(requested_start_time__gte=datetime.datetime.now()), Q.AND)

        else:  
            # it's not today so 
            # time of day doesn't matter    
            query_params.add(Q(requested_date=selected_date), Q.AND)



    else:
        # can't have a date AND a time-period, so it's one or the other
        if time_period == "past":
            #only want to give max one month in the past
            #and have to take into account the current time (past from now)
            delta = datetime.timedelta(days=30)
            query_params.add(Q(requested_date__lt=datetime.date.today()) | Q(requested_date=datetime.date.today()) & Q(requested_start_time__lt=datetime.datetime.now()), Q.AND)
            query_params.add(Q(requested_date__gt=(datetime.date.today()-delta)), Q.AND)


        #have to take into account the current time (future from now)
        if time_period == "future":
            query_params.add(Q(requested_date__gt=datetime.date.today()) | Q(requested_date=datetime.date.today()) & Q(requested_start_time__gte=datetime.datetime.now()), Q.AND)
    


    #if is_pending != "":
    #    query_params.add(Q(is_pending=is_pending), Q.AND)

    #if is_approved != "":
    #    query_params.add(Q(is_approved=is_approved), Q.AND)

    the_bookings = Booking.objects.all().filter(query_params).order_by("requested_date", "requested_start_time")
    #print(the_bookings.query)    
    return the_bookings


@register.simple_tag
def get_slot_desc_summary(asset_id):
    pass

@register.simple_tag
def get_asset_invitor_for_display(asset_id, user_id):
    pass

@register.simple_tag
def get_next_slot_start(asset_id, owner_id):
    pass

@register.simple_tag
def get_total_for_confirmation(asset_id, user_id, **kwargs):
    pass

@register.simple_tag
def get_total_confirmed_bookings(asset_id, user_id):
    pass



@register.simple_tag
def get_total_for_approval(asset_id, user_id, **kwargs):
    pass

@register.simple_tag
def get_total_for_approval_linked(asset_id, user_id, **kwargs):
    pass