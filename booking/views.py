from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError
from assets.models import Asset, Asset_User_Mapping
from home.myAuth import check_user_linked_to_asset,check_user_activated
from .models import Booking
import datetime
import calendar
import booking.templatetags.booking_extras as booking_extras
from booking.templatetags.booking_extras import get_total_bookings_venue, get_first_date_in_booking_list, get_booking_date, get_booking_status,time_slot_fully_booked,clear_date_and_time_from_session, get_bookings,is_booking_related_to_this_user
from assets.templatetags.assets_extras import is_asset_verifying_members, get_user_verification_status,get_display_time_period_for_booking,get_asset_booking_dates_for_display,get_asset_booking_time_links,is_user_also_owner
import assets.templatetags.assets_extras as assets_extras
from booking.forms import BookingForm
from django.core.mail import send_mail, get_connection

from django.http import JsonResponse
import csv

@login_required(login_url='/login/')
def update_selected_date_and_time(request,**kwargs):
    #get the selected calendar date so that the review_a_booking view
    #has the date
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)
    day = request.GET.get('day', None)
    hour = request.GET.get('hour', None)
    minute = request.GET.get('minute', None)

    #empty the session variables
    request.session['selected_year_cal']=[]
    request.session['selected_month_cal']=[]
    request.session['selected_day_cal']=[]
    request.session['selected_hour_cal']=[]
    request.session['selected_minute_cal']=[]

    try:
        request.session['selected_year_cal']=year
        request.session['selected_month_cal']=month
        request.session['selected_day_cal']=day
        request.session['selected_hour_cal']=hour
        request.session['selected_minute_cal']=minute

        data = {'year': "is " + request.session['selected_year_cal'],
                'month': " is " + request.session['selected_month_cal'],
                'day': " is " + request.session['selected_day_cal'],
                'hour': "is " + request.session['selected_hour_cal'],
                'minute': " is " + request.session['selected_minute_cal']}

    except:

        data_date = {'problem': "Date/Time not added to session"}

    return JsonResponse(data)

@login_required(login_url='/login/')
def update_exception_date_and_time(request,**kwargs):

    #get the selected calendar date so that the asset_exception_detail view
    #has the exception date
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)
    day = request.GET.get('day', None)
    hour = request.GET.get('hour', None)
    minute = request.GET.get('minute', None)

    #empty the session variables
    request.session['exception_year_cal']=[]
    request.session['exception_month_cal']=[]
    request.session['exception_day_cal']=[]

    try:
        request.session['exception_year_cal']=year
        request.session['exception_month_cal']=month
        request.session['exception_day_cal']=day

        data = {'year': "is " + request.session['exception_year_cal'],
                'month': " is " + request.session['exception_month_cal'],
                'day': " is " + request.session['exception_day_cal']}

    except:

        data_date = {'problem': "Exception Date/Time not added to session"}

    return JsonResponse(data)

@login_required(login_url='/login/')
def print_bookings(request, **kwargs):

    asset_id = 0  
    my_id = request.user.id
    is_owner = False
    is_linked = False
    time_period = "future"
    selected_date = ""
    year = 0
    month = 0
    day = 0

    #prepare the query
    if 'the_year' in kwargs:
        year = kwargs['the_year']
        print(year)
    if 'the_month' in kwargs:
        month = kwargs['the_month']
        print(month)
    if 'the_day' in kwargs:
        day = kwargs['the_day']
        print(day)
    check = year + month + day
    print (check)
    if check > 0:
    
        selected_date = datetime.date(year, month, day)
        time_period = ""
    
    print ("date is:")
    print (selected_date)

    #prepare the query
    if 'asset_id' in kwargs:
        asset_id = kwargs['asset_id']

    #prepare the query
    if 'time_period' in kwargs:
        time_period = kwargs['time_period']

    #can only print if an owner
    is_owner = is_user_also_owner(my_id, asset_id)

    #is the requestor linked to this asset?
    is_linked = check_user_linked_to_asset(my_id, asset_id)

    #format file name
    now = datetime.datetime.now()
    format_now_date = now.strftime("%d-%b-%y")         
    format_now_time_in_file = now.strftime("%H:%M:%S")
    format_now_time_filename = now.strftime("_%H%M%S")
    format_file_name = "bookings_as_of_" + format_now_date + format_now_time_filename + ".csv"


    if is_owner and is_linked:
   
        the_output = get_bookings(asset_id = asset_id, time_period = time_period, selected_date = selected_date)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + format_file_name

        writer = csv.writer(response)
        writer.writerow(['Venue','Booking Date',' Booking Time', 'First Name', 'Surname', 'Membership Number', 'Swipe ID'])

        for item in the_output:

            if not type(item.requested_date) is datetime.date:
                print("its not a date")

            format_date = item.requested_date.strftime("%d-%b-%y")

            format_time = item.requested_start_time.strftime("%H:%M")

            user_membership_ID = assets_extras.get_membership_id(item.requested_by_user_ID,item.asset_ID)
            user_swipe_ID = assets_extras.get_swipe_id(item.requested_by_user_ID,item.asset_ID)

            writer.writerow([item.asset_ID.asset_display_name, format_date, format_time, item.requested_by_user_ID.first_name, item.requested_by_user_ID.last_name,user_membership_ID, user_swipe_ID])

        writer.writerow([]) 
        writer.writerow([]) 
                 
        writer.writerow(['Printed:',format_now_date]) 
        writer.writerow(['At:',format_now_time_in_file]) 
        
    return response


@login_required(login_url='/login/')
def my_bookings(request, **kwargs):

    #set all initial values regardless of kwargs
    
    #start with who has requested this page
    #all bookings returned are requested by this user
    #it doesn't matter if the user is the owner - they will see what all other members see
    #(if they are the owner they can view it through my_venue_bookings view to get special owner view)

    my_id = request.user.id

    booking_requested_by = 0
    errors = []
    booking_id = 0
    booked_date = ""
    asset_id = 0
    the_asset = []
    time_period = "future" #assume future always unless provided
    future_bookings = []
    past_bookings = []
    num_bookings_future = 0
    num_bookings_past = 0

    # get all bookings for the request.user

    if 'booking_id' in kwargs: 
        booking_id = kwargs['booking_id']
        booked_date = get_booking_date(booking_id)

    # used in query - search for all bookings for this particular asset/venue
    # checks the id of the person who called this query to make sure they are linked to it
    if 'asset_id' in kwargs: 
        asset_id = kwargs['asset_id']

        #does asset exist?
        the_asset = get_object_or_404(Asset, id=asset_id)

        #is the requestor linked to this asset?
        is_linked = check_user_linked_to_asset(my_id, asset_id)

         #is the requestor activated?
        is_activated = check_user_activated(my_id, asset_id)

        if not is_linked:
            errors.append("You are not authorised to view this Bookings page")

        if not is_activated:
            errors.append("Account deactivated")
    else:

        errors.append("Please provide the Venue details")

    if not errors:
        # used in query - search for all bookings past or future from now
        # time period can be either: 'past' or 'future'
        if 'time_period' in kwargs:  
            time_period = kwargs['time_period']

        if len(errors)==0:

            # if no time_period is provided then this view must return two record sets (past AND future)
            # if time_period is 'past' or 'future', then this view returns just one record set
            
            if time_period == "future":

                # this is all FUTURE bookings  (>=today and >current time)
                future_bookings = get_bookings(user_id=my_id,time_period=time_period, asset_id = asset_id)
                num_bookings_future = len(future_bookings)

            elif time_period == "past":

                # this is all PAST bookings  (<=today and <current_time)
                past_bookings = get_bookings(user_id=my_id, time_period=time_period,asset_id = asset_id)
                num_bookings_past = len(past_bookings)

            else:

                #this is ALL bookings (but still in separate past/future objects)
                future_bookings = get_bookings(user_id=my_id,time_period="future", asset_id = asset_id)
                num_bookings_future = len(future_bookings)

                past_bookings = get_bookings(user_id=my_id, time_period="past",asset_id = asset_id)
                num_bookings_past = len(past_bookings)        
        

    return render(request, "booking/bookings.html", {"future_bookings": future_bookings,
                                         "num_bookings_future": num_bookings_future,
                                         "past_bookings": past_bookings,
                                         "num_bookings_past": num_bookings_past,
                                         "booking_id_to_highlight": booking_id, 
                                         "booked_date_to_highlight": booked_date, "the_asset":the_asset, "errors": errors})


@login_required(login_url='/login/')
def my_venue_bookings(request, asset_id, **kwargs):

    #set all initial values regardless of kwargs
    
    errors = []
    is_owner = False
    time_period = "future" #assume always future
    future_bookings = []
    past_bookings = []
    num_bookings_future = 0
    num_bookings_past = 0
    the_asset = []
    first_future_date = ""
    first_past_date = ""

    #start with who has requested this page
    #all bookings are returned for the venue provided
    #so the requestor should only be an OWNER

    #does asset exist?
    the_asset = get_object_or_404(Asset, id=asset_id)

    my_id = request.user.id
    
    # used in query - search for all bookings past or future from now
    # time period can be either: 'past' or 'future'
    if 'time_period' in kwargs:  
        time_period = kwargs['time_period']

    is_owner = is_user_also_owner(my_id, asset_id)

    if not is_owner:
        
        errors.append("You are not authorised to view this Bookings page")
    
    

    if len(errors)==0:

        # if no time_period is provided then this view must return two record sets (past AND future)
        # if time_period is 'past' or 'future', then this view returns just one record set
        
        if time_period == "future":

            # this is all FUTURE bookings  (>=today and >current time)
            future_bookings = get_bookings(time_period=time_period, asset_id = asset_id)
            num_bookings_future = len(future_bookings)
            first_future_date = get_first_date_in_booking_list(future_bookings)

        elif time_period == "past":

            # this is all PAST bookings  (<=today and <current_time)
            past_bookings = get_bookings(time_period=time_period,asset_id = asset_id)
            num_bookings_past = len(past_bookings)
            first_past_date = get_first_date_in_booking_list(past_bookings)

        else:

            #this is ALL bookings (but still in separate past/future objects)
            future_bookings = get_bookings(time_period="future", asset_id = asset_id)
            num_bookings_future = len(future_bookings)
            first_future_date = get_first_date_in_booking_list(future_bookings)

            past_bookings = get_bookings(time_period="past",asset_id = asset_id)
            num_bookings_past = len(past_bookings)
            first_past_date = get_first_date_in_booking_list(past_bookings)

    return render(request, "booking/bookings.html", {"future_bookings": future_bookings,
                                         "num_bookings_future": num_bookings_future,
                                         "past_bookings": past_bookings,
                                         "num_bookings_past": num_bookings_past, 
                                         "first_future_date":first_future_date,
                                         "first_past_date": first_past_date,
                                         "is_owner":is_owner, "the_asset":the_asset})





@login_required(login_url='/login/')
def delete_a_booking(request, booking_id):

    #check if the booking id belongs to this user (it could be from an email link)
    booking_exists = is_booking_related_to_this_user(request.user, booking_id)
    
    if booking_exists:
       
        the_booking = Booking.objects.get(id = booking_id)
        the_booking_date = the_booking.requested_date
        the_booking_time = the_booking.requested_start_time
        the_booking_venue = the_booking.asset_ID.asset_display_name
        message_str = "Your booking on %s at %s for %s has been deleted" % (the_booking_date.strftime("%a, %d %b %Y "),the_booking_time.strftime("%H:%M"), the_booking_venue)
        if request.method == "POST":

            #user has confirmed
            the_booking.delete()

            messages.add_message(request, messages.SUCCESS, message_str)
            return redirect('my_bookings', asset_id=the_booking.asset_ID.id)
           
        else:

            return render(request, "booking/booking_confirm_delete.html", {"the_booking": the_booking})

    else:
        code_message = "This is not a valid booking reference."
        messages.add_message(request, messages.ERROR, code_message)
        #this is not a valid booking id
        return redirect(reverse_lazy('my_bookings'))







@login_required(login_url='/login/')
def review_a_booking(request, asset_id):
   
    bookingform = BookingForm()
    user_ok  = False
    the_asset = get_object_or_404(Asset, id=asset_id)

     #check user is linked to the asset provided
    if check_user_linked_to_asset(request.user, asset_id):
        
        #is the requestor activated?
        if check_user_activated(request.user, asset_id):

            user_ok = True

        else:

            user_ok = False
            messages.add_message(request, messages.ERROR, "Account Deactivated")

    else:

        user_ok = False
        messages.add_message(request, messages.ERROR, "You are not authorised to view this page")

    if user_ok:

        #sessions variables must exist

        #variables from the session
        if 'selected_day_cal' in request.session:
            day = (request.session['selected_day_cal'])
            
        if 'selected_month_cal' in request.session:
            month = (request.session['selected_month_cal'])
            
        if 'selected_year_cal' in request.session:
            year = (request.session['selected_year_cal'])
            
        if 'selected_hour_cal' in request.session:
            hour = (request.session['selected_hour_cal'])
            
        if 'selected_minute_cal' in request.session:
            minute = (request.session['selected_minute_cal'])
            
        try:

            the_values = "%s - %s - %s - %s - %s" % (year, month, day, hour, minute)
            url_date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))

        except: 

            clear_date_and_time_from_session
            code_message = "There was a problem with the date, please re-select from the booking calendar " + the_values 
            messages.add_message(request, messages.ERROR, code_message)
            return redirect(reverse_lazy('make_a_booking', kwargs={"asset_id": the_asset.id}))

        else:

            show_date_format = url_date.strftime("%A, %d %B")
            show_time_format = url_date.strftime("%H:%M")
      
            if request.method == "POST":

                form = BookingForm(request.POST)

                if form.is_valid():
                    
                    cd = form.cleaned_data

                    hour = int(cd['hour'])
                    minute = int(cd['minute'])
                    day = int(cd['day'])
                    month = int(cd['month'])
                    year = int(cd['year'])
                    url_date = datetime.datetime(year, month, day, hour, minute)
                    the_request_date = datetime.datetime(year, month, day)
                    the_request_time = datetime.time(hour, minute)

                    #check things about the date first here before saving
                    #the date has already been checked before being saved to the session 
                    #check if the time-slot is still available (could be a delay with confirming the booking)

                    new_booking = Booking(requested_by_user_ID=request.user,asset_ID=the_asset,requested_date=the_request_date, requested_start_time=the_request_time)
                    
                    try:
                        new_booking.save()
                        new_id = new_booking.pk
                        #redirect to bookings page

                        clear_date_and_time_from_session
                        #send email to user
                        user_email = request.user.email

                        current_site = get_current_site(request)
                        domain = current_site.domain
                        delete_link = "%s/%s/%s/" % (domain, "booking/delete", new_id)
                        message_body = "Here are the details of your recent booking: " + show_date_format + " at " + show_time_format
                        message_body += "  To delete this booking at any time, click <a href='" + delete_link + "'>here</a>"

                        con = get_connection()
                        send_mail("Count Me In = booking",
                                    message_body,
                                    "admin@countmein.ie",['siteowner@countmein.ie', user_email],
                                    connection=con)

                        return redirect(reverse_lazy('my_bookings', kwargs={"asset_id": the_asset.id, "booking_id": new_id} ))

                    except IntegrityError as code_message:

                        code_message = "You have already booked that particular time slot, please choose another"
                        messages.add_message(request, messages.ERROR, code_message)

                        clear_date_and_time_from_session

                        #redirect to bookings page
                        return redirect(reverse_lazy('make_a_booking', kwargs={"asset_id": the_asset.id}))

                   
                else:
                    
                    print(form.errors)
                   
                    #form not valid

            
            else:

                bookingform = BookingForm(initial={'requested_date':show_date_format, 'requested_start_time':show_time_format, 'hour': hour, 'minute':minute, 'day':day, 'year':year, 'month':month})

        
    return render(request, "booking/confirm_booking.html", {"asset": the_asset,'bookingform':bookingform, 'request_date': show_date_format, 'request_time': show_time_format, "user_ok": user_ok})   
   

@login_required(login_url='/login/')
def venue_calendar_admin(request, asset_id):

    the_asset = get_object_or_404(Asset, id=asset_id)
    errors = []
    user_ok = False
    cal_data = {}
    dates_to_show = set()

    if check_user_linked_to_asset(request.user, asset_id):

        if is_user_also_owner(request.user, asset_id):

            user_ok = True

        else:

            errors.append("Restricted Access")
            messages.add_message(request, messages.ERROR, "Restricted Access")
            user_ok = False

    else:

        errors.append("You are not authorised to view this page")
        messages.add_message(request, messages.ERROR, "You are not authorised to view this page")
        user_ok = False


    if user_ok:

        #remove any selected dates/times from the session in case they exist already
        #empty session variables
        booking_extras.clear_exception_date_from_session
        
        # each day there are bookings, the calendar shows "Bookings <the number>"
        # and a link with "add an exception"
        # if the date is already in the exception table, the link will say "edit exception" (or something like that)
        # unlike the calendar for users (make_a_booking view), there are no modals on this calendar - each item on the date will be a separate link

        # create the object that the calendar needs (cal_data)
        # this is a series of dates and links

        #distict query below is not allowed in sqlite3 so will get individual dates by populating a set() which can only have unique values
        #dates_to_show = Bookings.objects.all().filter(asset_ID = the_asset.id, requested_date__gte=datetime.date.today()).order_by('requested_date').distinct('asset_ID', 'requested_date')

        
        #there will be multiple bookings per date so to get individual dates put into a set()
        all_future_bookings = Booking.objects.all().filter(asset_ID = the_asset.id, requested_date__gte=datetime.date.today())
        
        if all_future_bookings:

            for item in all_future_bookings:
               # print(item.requested_date)
                dates_to_show.add(item.requested_date)

            if dates_to_show:

                for item in dates_to_show:

                    num_future_bookings = get_total_bookings_venue(the_asset.id, selected_date=item)
                    todays_date = datetime.date(datetime.datetime.now().year,datetime.datetime.now().month, datetime.datetime.now().day)

                    is_exception_date = assets_extras.is_date_in_exception_table(the_asset.id, item)

                    entry_date_str = item.strftime("%m-%d-%Y")

                    if is_exception_date:
                        click_link = onclick='UpdateExceptionDate(this," + str(entry_date.day) + "," + the_asset.id + ")'
                        href_link = "%s%s/" % ("/asset/exception/", asset_id)
                        exception_link = "<a style='background-color:#f44336; font-size:12px;border-radius: 25px;padding:4px 6px 4px 6px;' href='" + href_link + "'>View Exception Details</a>"

                    else:

                        exception_link = ""

                    
                    if num_future_bookings == 1:
                        text_desc = "Booking"
                    else:
                        text_desc = "Bookings"

                    cal_data[entry_date_str] = "<div>%s %s</div> <div>%s</div>" % (num_future_bookings, text_desc, exception_link) 

                print(cal_data)

        else:

            #no dates to show, so empty calendar!
            messages.add_message(request, messages.INFO, "Click on any date to add an exception")


    return render(request, "booking/booking_calendar_venue.html", {"the_asset": the_asset, "errors":errors, "cal_data":cal_data, 'user_ok': user_ok})


@login_required(login_url='/login/')
def make_a_booking(request, asset_id):

    clear_date_and_time_from_session
    user_ok = False

    the_asset = get_object_or_404(Asset, id=asset_id)
    errors = []
    asset_booking_dates = [] 
    asset_booking_dates_times = []
    cal_data = {}
    the_modals = []

    year = datetime.date.today().year
    month = datetime.date.today().month
    month_name = calendar.month_name[month]
    
    if check_user_linked_to_asset(request.user, asset_id):

        #is the requestor activated?
        if check_user_activated(request.user, asset_id):

            user_ok = True

            #remove any selected dates/times from the session in case they exist already
            #empty session variables
            request.session['selected_year_cal']=[]
            request.session['selected_month_cal']=[]
            request.session['selected_day_cal']=[]
            request.session['selected_hour_cal']=[]
            request.session['selected_minute_cal']=[]

        else:

            user_ok = False
            messages.add_message(request, messages.ERROR, "Account deactivated")    

    else:
        user_ok = False
        errors.append("You are not authorised to view this page")
        messages.add_message(request, messages.ERROR, "You are not authorised to view this page")

    if user_ok:

        time_period_to_display = get_display_time_period_for_booking(asset_id)

        #create the object that the calendar needs (cal_data)
        #this is a series of dates and links
        #also create the MODAL object (the_modals)
        #this is the set of booking links that will pop up when the user clicks on the calendar date
        #both of these need to only show the dates that the venue has set
        #so this could be 5, 6 or 7 day weeks (and not EVERY DAY)
        #so cal_dat and the_modals may not have consecutive dates

        asset_booking_dates = get_asset_booking_dates_for_display(asset_id)

        for entry_date in asset_booking_dates:

            #------prepare the cal_data------#

            entry_date_index = asset_booking_dates.index(entry_date)
            entry_date_str = entry_date.strftime("%m-%d-%Y")
              
            #------prepare the cal_data end------#

            #------prepare the_modals start------#

            header_message = "Available times on " + entry_date.strftime("%A %d %b")
           

            the_modal_start = "<div class='modal fade bs-example-modal-lg' id='myTimeModal" + str(entry_date_index) + "' role='dialog'>"
            the_modal_start += "<div class='modal-dialog modal-lg'>"
            the_modal_start += "<div class= 'modal-content'>"
            the_modal_start += "<div class= 'modal-header'>"
            the_modal_start += "<h3 class='modal-title'>" + header_message + "</h3>"
            the_modal_start += "<button type='button' class='close' data-dismiss='modal'>&times;</button>"
            the_modal_start += "</div>"
            the_modal_start += "<div class='modal-body'>"

            asset_booking_dates_times = get_asset_booking_time_links(asset_id, entry_date)
            num_items = len(asset_booking_dates_times)
            
            #only run the rest of this function if there are times provided
            #(someone could be looking at the site after-hours)
            if num_items>0:

                the_modal_middle = ""
                the_count = 0
                for item in asset_booking_dates_times:
                    #print ("%s: %s" % ("the", item))
                    #need to display all the items except last one
                    #last time-slot should be closing time, so it can't be booked
                    the_count +=1

                    if the_count < num_items:
                       # print ("%s:%s" %(item.hour, item.minute))
                        display_time = datetime.datetime.strftime(item,"%H:%M")
                        extend_url= "review/"
                        
                        #if fully booked, don't include a link ***STILL TO CODE MH ***
                        if time_slot_fully_booked(asset_id, entry_date, item):

                            the_modal_middle += "%s%s%s" % ("<type='button' onclick='alert('This slot is fully booked')' class='btn-dark btn-sm' disabled='disabled' href='#'>", display_time, "</button>")

                        else:

                            
                            the_modal_middle += "%s%s%s" % ("<a type='button' onclick='updateDateAndTime(this," + str(entry_date.day) + ")' class='button button-dark button-circle btn-lg' href='review/'>", display_time, "</a>")
                    
                    

                
                
                the_modal_end = "</div>"
                the_modal_end += "<div class='modal-footer'>"
                the_modal_end += "<button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>"
                the_modal_end += "</div></div></div></div>"

                the_modal = the_modal_start + the_modal_middle + the_modal_end
                
                the_modals.append({"detail": the_modal})

                #------prepare the modal end------#

                #------populate the cal_data------#
                
                the_first_slot = "%s" % (datetime.datetime.strftime(asset_booking_dates_times[0],"%H:%M"))
                the_last_slot = "%s" % (datetime.datetime.strftime(asset_booking_dates_times[len(asset_booking_dates_times)-1],"%H:%M"))
                opening_times_for_display = "%s to %s" % (the_first_slot,the_last_slot)

                # issue with button on calendar in large view if date is TODAY - model doesn't open (3rd party code)
                # so changing entry text for TODAY only to an <a> tag and styling like a button
                # all other dates work
                if entry_date_index == 0:
                    entry_message = "<a style='background-color:#f44336; font-size:16px;border-radius: 25px;padding:8px 12px 8px 12px;' data-toggle='modal' data-target='#myTimeModal" + str(entry_date_index) + "'>" + opening_times_for_display +"</a>"
                else:
                    entry_message = "<button type='button' style='border-radius: 25px;'class='btn btn-primary' data-toggle='modal' data-target='#myTimeModal" + str(entry_date_index) + "'>" + opening_times_for_display +"</button>"
               
                #populate cal_data
                cal_data[entry_date_str]= entry_message 

                #------populate the cal_data end--#


    args = {
        'the_asset': the_asset,
        'errors': errors,
        'user_ok': user_ok,
        'cal_data': cal_data,
        'the_modals': the_modals
    }

    #args.update(csrf(request))

    return render(request, "booking/new_booking.html", args)
   




