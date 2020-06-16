from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from django.core.exceptions import ValidationError


class UserRegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label='Password Confirmation',
        widget=forms.PasswordInput
    )

    first_name = forms.CharField(
        label="First Name"
    )

    last_name = forms.CharField(
        label="Surname"
    )

    email = forms.CharField(
        label="Email",
        widget = forms.EmailInput
    )

    class Meta:
        model = User
        fields = ['email', 'first_name','last_name','password1', 'password2']
        exclude = ['username']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            message = "Passwords do not match"
            raise ValidationError(message)

        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            message = "Please enter your email address"
            raise forms.ValidationError(message)

        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if not first_name:
            message = "Please enter your first name"
            raise forms.ValidationError(message)

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if not last_name:
            message = "Please enter your surname"
            raise forms.ValidationError(message)

        return last_name

    def save(self, commit=True):
        instance = super(UserRegistrationForm, self).save(commit=False)

        instance.username = instance.email

        if commit:
            instance.save()

        return instance

class UserLoginForm(forms.Form):
    email = forms.EmailField(label="")
    password = forms.CharField(widget=forms.PasswordInput, label="")

class InviteCodeForm(forms.Form):
    invitecode = forms.CharField(max_length=12, label="Invited to join?")
