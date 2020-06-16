from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

class CustUserManager(BaseUserManager):

	def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
		
		if not email:
			raise ValueError('Email address is required')

		email = self.normalize_email(email)
		user = self.model(
			email=email,
			is_active=True,
			is_staff=is_staff,
			is_superuser=is_superuser,
			**extra_fields
			)
		user.set_password(password)
		user.save()
		return user

	def create_user(self, email, password, **extra_fields):
		return self._create_user(email, password, False, False, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		return self._create_user(email, password, True, True, **extra_fields)


class User(AbstractUser):
	
	email = models.EmailField(max_length=254, unique=True)
	username = models.CharField(max_length=150, blank=True, unique=False)
	date_joined = models.DateTimeField(default=timezone.now)
	phone= models.CharField(blank=True, max_length=30)

	USERNAME_FIELD = 'email'
	EMAIL_FIELD = 'email'
	REQUIRED_FIELDS = []

	objects = CustUserManager()

	def __str__(self):
		return self.email
