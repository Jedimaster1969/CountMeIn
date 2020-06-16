from django.contrib import messages, auth
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm, UserRegistrationForm
from django.template.context_processors import csrf
#from django.contrib.auth import logout, login, authenticate
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from accounts.forms import InviteCodeForm
from assets.models import Asset, Asset_User_Mapping
from assets.templatetags.assets_extras import get_asset_from_invite_code
from django.core import serializers
import datetime
from django.utils import timezone
from home.myAuth import check_user_linked_to_asset,check_user_activated
from accounts.models import User
from django.shortcuts import render, get_object_or_404

@login_required(login_url='/register/')
def profile(request,**kwargs):

	#'invite_code' will be in kwargs if the user has 
	#requested to be linked to an asset via a URL (they are redirected to this view)
	if 'invite_code' in kwargs: 
		
		invite = kwargs['invite_code']

	else:
		invite=0

	invitecodeform = InviteCodeForm()
	code_message = ""
	
	if request.method == "POST":
		form = InviteCodeForm(request.POST)
		if form.is_valid():
			
			cd = form.cleaned_data
			the_code = cd['invitecode']
			the_date = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
			
			#check if the invitecode is in the Asset table
			#return the AssetID if it is
			the_venue = get_asset_from_invite_code(the_code)

			if the_venue:
				#check if the venue has been activated
				the_venue_activated = is_asset_activated(the_venue.id)
				if the_venue_activated:
				
					the_venue_id = the_venue.id
					the_venue_name = the_venue.asset_display_name

					#check if the user is already linked to this asset  
					if check_user_linked_to_asset(request.user,the_venue_id) == False:
						new_mapping = Asset_User_Mapping(user_ID=request.user,asset_ID=the_venue,is_owner=0,invite_code_used=the_code)
						new_mapping.save()
						code_message = "You have just been counted in to " + the_venue_name + "!"
						messages.add_message(request, messages.SUCCESS, code_message)

					else:
						code_message = "You are already a Member of " + the_venue_name + "!"
						messages.add_message(request, messages.ERROR, code_message)
				else:

					code_message = "This is not a active code. Please confirm the code with your Gym."
					messages.add_message(request, messages.ERROR, code_message)

			else:
				code_message = "This is not a valid code. Please check and try again."
				messages.add_message(request, messages.ERROR, code_message) 
	
	elif invite:

		#user has entered a VALID invite_code via the url, so add them to this asset (if they are not already linked to it)
		#return the AssetID if it is
		the_venue = get_asset_from_invite_code(invite)

		if the_venue:
			#check if the venue has been activated
			the_venue_activated = is_asset_activated(the_venue.id)
			if the_venue_activated:
			
				the_venue_id = the_venue.id
				the_venue_name = the_venue.asset_display_name

				#check if the user is already linked to this asset  
				if check_user_linked_to_asset(request.user,the_venue_id) == False:
					new_mapping = Asset_User_Mapping(user_ID=request.user,asset_ID=the_venue,is_owner=0,invite_code_used=invite)
					new_mapping.save()

					code_message = "You have just been counted in to " + the_venue_name + "!"
					messages.add_message(request, messages.SUCCESS, code_message)

				else:
					code_message = "You are already a Member of " + the_venue_name + "!"
					messages.add_message(request, messages.ERROR, code_message)
			else:

				code_message = "This is not a active code. Please confirm the code with your Gym."
				messages.add_message(request, messages.ERROR, code_message)

		else:
			code_message = "This is not a valid code. Please check and try again."
			messages.add_message(request, messages.ERROR, code_message)

	else:
		
		invitecodeform = InviteCodeForm()


	# set session values to be used until user logs out
	# store the asset ids they are linked to

	# create empty session list
	request.session['linked_assets']=[]
	linked_asset_count = Asset.objects.all().filter(asset_users=request.user).count()

	# want to store a list in the session
	# http://stackoverflow.com/questions/6720121/serializing-result-of-a-queryset-with-json-raises-error
	class LinkedAssets(object):
		def __init__(self,asset_id):
			self.asset_id = asset_id

		def serialize(self):
			return self.__dict__

	if linked_asset_count > 0:
		# fill the linked_assets session list
		linked_assets = serializers.serialize('json',Asset.objects.all().filter(asset_users = request.user), fields=('id,'))
		request.session['linked_assets'] = linked_assets

	assets = Asset_User_Mapping.objects.all().filter(user_ID=request.user, asset_ID_id__is_activated=True)

	return render(request, 'home/profile.html',
				  {'assets': assets, 'invitecodeform': invitecodeform, 'code_message': code_message})

class register(FormView):

	template_name = 'home/register.html'
	form_class = UserRegistrationForm
	success_url = '/profile'

	def form_valid(self, form):
		form.save()
				
		user = auth.authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
		auth.login(self.request, user)
		messages.add_message(self.request, messages.SUCCESS, "You have registered. Thank you.")
		
		#check the 'next' value of the signin
		next_url = self.request.GET.get('next')
		print("next url is:")
		print(next_url)
		if next_url:
			return HttpResponseRedirect(next_url)
		else:
			return HttpResponseRedirect(self.success_url)

	def form_invalid(self, form):
		messages.add_message(self.request, messages.ERROR, "You have errors in your form. Please check below.")
		return super().form_invalid(form)


def login(request):
	errors = []

	if request.method == 'POST':

		if request.session.test_cookie_worked():

			form = UserLoginForm(request.POST)
			if form.is_valid():
				user = auth.authenticate(email=request.POST.get('email'),
										 password=request.POST.get('password'))

				if user is not None:
					auth.login(request, user)
					#check the 'next' value of the signin
					next_url = request.GET.get('next')
					if next_url:
						return HttpResponseRedirect(next_url)
					else:
						return HttpResponseRedirect('/profile')
					
				else:
					errors.append("Your details were not recognised")
		else:
			messages.add_message(request, messages.ERROR, "Please enable cookies and try again.")
			return HttpResponseRedirect('/login')

	else:
		request.session.set_test_cookie()
		form = UserLoginForm()

	args = {'form': form,
			'errors':errors}

	args.update(csrf(request))
	return render(request, 'home/login.html', args)



@login_required(login_url='/login/')
def my_details(request):

	#display the details for the user who is logged in
	#details of their Venues (if any) will be in request.session['linked_assets'] = linked_assets
	#details of their account will be populated here

	user_details = []
	user_details = get_object_or_404(User, pk=request.user.id)
	#user_details = User.objects.get(email=request.user)

	return render(request, "home/user_details.html",{"user_details": user_details})








