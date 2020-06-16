from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy, reverse
from assets.models import AssetType, Asset, Asset_User_Mapping,Asset_OpenDays_Exception
from booking.models import Booking
from home.myAuth import check_user_linked_to_asset,check_user_activated
import assets.templatetags.assets_extras as assets_extras
import booking.templatetags.booking_extras as booking_extras
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.models import User
from django.utils import timezone
from .forms import AssetForm, AssetMemberForm,AssetExceptionForm
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.db import IntegrityError, DatabaseError, Error
import datetime

def asset_invite(request, invite_code):
    the_code_url = request.build_absolute_uri()
    
    #check if the invite code is real or send user to 404
    the_invite_asset = get_object_or_404(Asset, invite_code_url=the_code_url)
    
    return redirect(reverse_lazy('profile',kwargs={"invite_code": invite_code}))


@login_required(login_url='/login/')
def assets(request):
    my_id = request.user
    my_assets = Asset.objects.all().filter(asset_users=my_id)
    return render(request,"assets.html", {"assets": my_assets})

class DetailViewAsset(LoginRequiredMixin,DetailView):

    login_url = reverse_lazy('login')
    model = Asset
    context_object_name = "asset"


@login_required(login_url='/login/')
def asset_detail(request, asset_id):

    the_asset = []
    errors = []
    asset_form = []
    
    #check asset exists
    the_asset = get_object_or_404(Asset, pk=asset_id)

    # check if the user is allowed to view this asset
    my_id = request.user
    
    is_linked = check_user_linked_to_asset(request.user, asset_id)
    if is_linked == False:
    
        errors.append("You do not have permission to view this page")

    is_an_owner = assets_extras.is_user_also_owner(request.user, asset_id)
    if is_an_owner == False:
    
        errors.append("Access restricted")

    return render(request, "assets/asset_detail.html",{"asset": the_asset, "errors": errors})

@login_required(login_url='/login/')
def asset_detail_edit(request, asset_id):
    #to edit a venue/asset, must be the owner (staff)
    #check asset exists
    the_asset = get_object_or_404(Asset, pk=asset_id)
    errors = 0
    the_asset_form = []
    the_asset_detail = []

    # check if the user is allowed to view this asset
    my_id = request.user
    is_an_owner = assets_extras.is_user_also_owner(my_id, asset_id)

    if is_an_owner == False:
        messages.add_message(request, messages.ERROR, "You are not authorised to view this page")
        errors += errors

    else:

        the_asset_detail = Asset.objects.get(id = asset_id)

        #this is the only data an owner can edit themselves
        initial_data = {'asset_display_name':the_asset_detail.asset_display_name, 'asset_max_bookings':the_asset_detail.asset_max_bookings, 
                        'num_days_display_to_users': the_asset_detail.num_days_display_to_users}


    if errors == 0: #no errors

        if request.method == "POST":

            form = AssetForm(request.POST,initial=initial_data)

            if form.is_valid():

                cd = form.cleaned_data

                if form.has_changed():


                    if 'is_owner' in form.changed_data:
                        #check various things here like:
                        # if changing opening days...are there already bookings made on those days?
                        # if changing closing/opening times...are there already bookings made at those times?
                        # if changing max_bookings allowed per slot...is it more/less than before and is it over-booked now?
                        changed = True

                    else:
                        asset_display_name = cd['asset_display_name']
                        asset_max_bookings = cd['asset_max_bookings']
                        num_days_display_to_users = cd['num_days_display_to_users']

                        
                        try:

                            Asset.objects.filter(id=asset_id).update(asset_display_name=asset_display_name,  
                                asset_max_bookings=asset_max_bookings,num_days_display_to_users=num_days_display_to_users)

                            code_message = the_asset_detail.asset_display_name + " has been edited"

                            messages.add_message(request, messages.INFO, code_message)
                            #send back to Membership page
                            return redirect(reverse_lazy('asset_detail', kwargs={"asset_id":asset_id}))

                        except Error:

                            code_message ="There was a problem, can you please try that again?"
                            messages.add_message(request, messages.ERROR, code_message)

                return redirect(reverse_lazy('asset_detail', kwargs={"asset_id":asset_id}))

            else:

                print(form.errors)

        else: #not POST
        
            the_asset_form = AssetForm(initial=initial_data)
            

    else: #there are errors

        the_asset_form = []


    return render(request, "assets/asset_detail_edit.html",{"asset": the_asset_detail, "form": the_asset_form})


@login_required(login_url='/login/')
def member_detail_edit(request, asset_id, member_id):

    #to edit a member, must be the owner of the asset
    #check asset exists
    the_asset = get_object_or_404(Asset, pk=asset_id)
    errors = []
    the_member_form = []
    the_member_detail = []
    initial_data = ""

    # check if the user is allowed to view this asset
    my_id = request.user
    is_an_owner = assets_extras.is_user_also_owner(my_id, asset_id)
    
    if is_an_owner == False:

        messages.add_message(request, messages.ERROR, "You are not authorised to view this page")
        errors.append( "You are not authorised to view this page")

    else: 

        #check validity of the member they want to edit
        is_linked = check_user_linked_to_asset(member_id, asset_id)

        if is_linked == False:
            messages.add_message(request, messages.ERROR, "That is not a valid Member ID")
            errors.append( "That is not a valid Member ID")

        else:
            the_member_detail = Asset_User_Mapping.objects.get(asset_ID = asset_id, user_ID=member_id)
            initial_data = {'is_activated':the_member_detail.is_activated,'is_owner':the_member_detail.is_owner, 'asset_membership_ID': the_member_detail.asset_membership_ID, 'asset_swipe_ID':the_member_detail.asset_swipe_ID, 'admin_notes':the_member_detail.admin_notes}

            #for validation after form is POSTED, will need to know if the user_id submitting is the same as the member_id
            if my_id == the_member_detail.user_ID:

                owner_user_same_person = True

            else:

                owner_user_same_person = False


        if len(errors) == 0:    #no errors

            if request.method == "POST":

                form = AssetMemberForm(request.POST,initial=initial_data)

                if form.is_valid():

                    cd = form.cleaned_data

                    is_staff = cd['is_owner']
                    is_activated = cd['is_activated']
                    membership_ID = cd['asset_membership_ID']
                    swipe_ID = cd['asset_swipe_ID']
                    notes = cd['admin_notes']

                    if form.has_changed():


                        if ('is_owner' in form.changed_data or 'is_activated' in form.changed_data) and owner_user_same_person:

                            # check that the current user hasn't changed their own is_staff status to False
                            # if they have send back a warning (or else they will not be able to view the Owner pages)
                            code_message ="You cannot edit your own staff status. Another staff member must do this on your behalf." 
                            messages.add_message(request, messages.WARNING, code_message)
                            return redirect(reverse_lazy('member_detail', kwargs={"asset_id":asset_id}))

                        elif is_staff and not is_activated:

                            code_message ="To deactivate a staff member, you must first remove their staff status"
                            messages.add_message(request, messages.WARNING, code_message)
                            errors.append (code_message)
                            return redirect(reverse_lazy('member_detail', kwargs={"asset_id":asset_id}))

                        else:

                        
                            try:
                                Asset_User_Mapping.objects.filter(user_ID=member_id, asset_ID=asset_id).update(is_owner=is_staff, is_activated=is_activated, asset_membership_ID=membership_ID,asset_swipe_ID=swipe_ID, admin_notes=notes)
                                code_message ="Member " + the_member_detail.user_ID.first_name + " " + the_member_detail.user_ID.last_name + " has been edited"
                                messages.add_message(request, messages.INFO, code_message)
                                #send back to Membership page
                                return redirect(reverse_lazy('member_detail', kwargs={"asset_id":asset_id}))

                            except Error:

                                code_message ="There was a problem, can you please try that again?"
                                messages.add_message(request, messages.ERROR, code_message)

                    return redirect(reverse_lazy('member_detail', kwargs={"asset_id":asset_id}))

                else:

                    print(form.errors)

            else: #not POST
            
                the_member_form = AssetMemberForm(initial=initial_data)
                

        else: #there are errors

            the_member_form = []

    return render(request, "assets/asset_user_mapping_detail_edit.html",{"asset": the_asset, "form": the_member_form, "member": the_member_detail, "errors": errors})



@login_required(login_url='/login/')
def member_detail(request, asset_id,**kwargs):

    #if user_id provided, then show this member
    #otherwise show all members
    the_asset = []
    errors = []
    member_id=0
    the_member_detail = []
    code_message = ""
    is_activated = True

    if 'member_id' in kwargs:
        member_id = kwargs['member_id']

    if 'activated' in kwargs:
        is_activated = kwargs['activated']

    #check asset exists
    the_asset = get_object_or_404(Asset, id=asset_id)

    #check that the person requesting this is the owner of the asset_id
    is_an_owner = assets_extras.is_user_also_owner(request.user, asset_id)
    
    if is_an_owner == False:
    
        code_message = "You are not authorised to view this page"
        messages.add_message(request, messages.ERROR, code_message)

    if member_id > 0:
        
        print("member detail is:")
        print(member_id)
        #check user_id provided is actually linked to the asset_id provided
        # use filter (rather than GET) so that it returns an iterable object for the html page
        the_member_detail = Asset_User_Mapping.objects.all().filter(user_ID = member_id, asset_ID = asset_id)

        if not the_member_detail:

            code_message = "This is not a valid Membership number"
            messages.add_message(request, messages.ERROR, code_message)



    else:
        #all members
        the_member_detail = Asset_User_Mapping.objects.all().filter(asset_ID = asset_id, is_activated=is_activated).order_by('user_ID_id__last_name')

        if not the_member_detail:

            code_message = "There are no Members signed up yet"
            messages.add_message(request, messages.ERROR, code_message)

    if code_message:
        #don't show any details
        print("the code_message is: " + code_message)
        the_member_detail= []

    return render(request, "assets/asset_user_mapping_detail.html",{"asset": the_asset, "members": the_member_detail, "errors": errors})


@login_required(login_url='/login/')
def delete_a_member(request, asset_id, member_id):

    code_message = ""
    errors =[]
    #check asset exists
    the_asset = get_object_or_404(Asset, id=asset_id)
    
    #check if the current user is the same as the member_id
    #no one can delete a user/mapping except the user themselves
    #owners can 'deactivate' members only

    if not member_id == request.user.id:

        code_message = "You are not authorised to do this"
        messages.add_message(request, messages.ERROR, code_message)
        errors.append("You are not authorised to do this")
        
    else: 
        #check if the member id is linked to this asset 
        member_linked = check_user_linked_to_asset(member_id, asset_id)
       
        if member_linked:
            
            the_member = Asset_User_Mapping.objects.get(asset_ID = asset_id, user_ID = member_id)

            if request.method == "POST":

                #user has confirmed
                the_member.delete()
                #delete all bookings for that user
                Booking.objects.filter(asset_ID=asset_id, requested_by_user_ID=member_id).delete()

                messages.add_message(request, messages.SUCCESS, "You have been removed from " + the_asset.asset_display_name)
                return redirect('my_details')
                
            else:

                return render(request, "assets/asset_user_mapping_confirm_delete.html", {"asset_mapping": the_member, "asset": the_asset})

        else:

            code_message = "This is not a valid membership ID"
            messages.add_message(request, messages.ERROR, code_message)

            return render(request, "assets/asset_user_mapping_detail.html", {"asset": the_asset})

    return render(request, "assets/asset_user_mapping_detail.html", {"asset": the_asset, "errors": errors})
    
@login_required(login_url='/login/')
def asset_exception_detail2(request, asset_id, the_year=0, the_month=0, the_day=0):

    the_asset = get_object_or_404(Asset, id=asset_id)
    errors = []
    user_ok = False

    the_year = 2020
    the_month = 6
    the_day=17
    
    if check_user_linked_to_asset(request.user, asset_id):

        if assets_extras.is_user_also_owner(request.user, asset_id):

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

        True


    return render(request, "assets/asset_exception_date.html", {"the_asset": the_asset, "errors":errors, 'user_ok': user_ok})

@login_required(login_url='/login/')
def asset_exception_detail(request, asset_id):

    # this function is called when user wants to add or edit an exception on the date provided
    # the exception date (year, month, day) should be in the session
    # if not then send the user back to re-select

    the_asset = []
    the_exception = []
    errors = []
    asset_exception_form = []
    user_ok = False
    the_values = ""
    exception_date = ""
    is_a_weekday = False

    #check asset exists
    the_asset = get_object_or_404(Asset, pk=asset_id)
    
    # check if the user is allowed to view this asset
    my_id = request.user
    
    if check_user_linked_to_asset(request.user, asset_id):
        
        if assets_extras.is_user_also_owner(request.user, asset_id):
        
            user_ok = True

        else:

            errors.append("Access restricted")
            user_ok = False

    else:

            errors.append("You do not have permission to view this page")
            user_ok = False

    if user_ok:

        #sessions variables must exist

        #variables from the session
        if 'exception_year_cal' in request.session:
            year = (request.session['exception_year_cal'])
            
        if 'exception_month_cal' in request.session:
            month = (request.session['exception_month_cal'])
            
        if 'exception_day_cal' in request.session:
            day = (request.session['exception_day_cal'])
            
        try:
            #create the datetime object from the given parameters
            the_values = "%s - %s - %s" % (year, month, day)
            exception_date = datetime.date(int(year), int(month), int(day))
            show_date_format = exception_date.strftime("%A, %d %B")
            is_a_weekday = booking_extras.is_date_a_weekday(exception_date)
            
        except:

            code_message = "There was a problem with the date. Please re-select from the calendar and try again." + the_values
            messages.add_message(request, messages.ERROR, code_message)
            return redirect(reverse_lazy('venue_calendar_admin', kwargs={"asset_id": the_asset.id}))

        else:

            #check if the exception exists
            exception_record = assets_extras.get_exception_record(the_asset.id, exception_date)

            if request.method == "POST":

                if exception_record:
                    #include initial data so new content can be checked
                    #against existing bookings
                    form = AssetExceptionForm(request.POST,initial=exception_record)

                else:
                    #no initial data so brand new exception
                    form = AssetExceptionForm(request.POST)

                if form.is_valid():

                    cd = form.cleaned_data
                    pass

            else: 

                if exception_record:

                    form = AssetExceptionForm(inital=exception_record)

                else:

                    form= AssetExceptionForm(initial={'the_date':show_date_format, 'day': day, 'year':year, 'month':month})
            


    return render(request, "assets/asset_exception_date.html",{"asset": the_asset, "errors": errors, "user_ok": user_ok, "form":form, "the_date":show_date_format, "is_a_weekday":is_a_weekday})


class DeleteViewMember(LoginRequiredMixin,DeleteView):

    login_url = reverse_lazy('login')
    model = Asset_User_Mapping
    context_object_name = 'asset_mapping'
    success_url = reverse_lazy('member_detail')


class DetailViewAssetMember(LoginRequiredMixin,DetailView):

    pass


@login_required(login_url='/login/')
def get_members(request, asset_id):
    pass

class ListViewAsset(LoginRequiredMixin,ListView):

    login_url = reverse_lazy('login')
    model = Asset
    context_object_name = 'all_assets'





class CreateViewAsset(LoginRequiredMixin,CreateView):
    
    login_url = reverse_lazy('login')
    model = Asset
    fields = ['asset_display_name', 'asset_image', 'asset_type']
    success_url = reverse_lazy('show_assets')


class UpdateViewAsset(LoginRequiredMixin,UpdateView):

    login_url = reverse_lazy('login')
    model = Asset
    fields = ['asset_display_name','asset_image','asset_type', 'invite_code']
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('show_assets')

class DeleteViewAsset(LoginRequiredMixin,DeleteView):

    login_url = reverse_lazy('login')
    model = Asset
    context_object_name = 'asset'
    success_url = reverse_lazy('show_assets')