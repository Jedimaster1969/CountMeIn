from django import forms
from django.views.generic.edit import FormView
from django.core.mail import send_mail, get_connection
from django.contrib import messages

class ContactForm(forms.Form):
    yourname = forms.CharField(max_length=100, label='Your Name')
    email = forms.EmailField(required=False,label='Your e-mail address')
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

class ContactUs(FormView):
	
	template_name = 'home/contact.html'
	form_class = ContactForm
	success_url = '/contact'

	def form_valid(self, form):

		cd = form.cleaned_data
		con = get_connection()
		send_mail(
			cd['subject'],
			cd['message'],
			cd.get('email', 'maria@databasis.ie'),['siteowner@example.com'],
			connection=con
		)
		messages.add_message(self.request, messages.SUCCESS, "Your message was submitted. Thank you.")
		return super().form_valid(form)

	def form_invalid(self, form):
		messages.add_message(self.request, messages.ERROR, "You have errors in your submission")
		return super().form_invalid(form)
