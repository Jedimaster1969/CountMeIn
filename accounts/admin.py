from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
	
	model = User
	
	fieldsets = (
		(None, {'fields':('email','password', 'last_login')}),
		('Additional Info', {'fields':(('first_name','last_name'), 'phone','date_joined')}),
		('Permissions', {'fields':('is_active', 'is_staff','is_superuser','groups', 'user_permissions',)}),
	)
	
	add_fieldsets = (
		(None, {'fields': ('email', 'password1', 'password2'), 'classes': ('wide',)}),
	)
	
	list_display = ('email', 'is_staff', 'is_superuser', 'last_login')
	
	list_filter = ('is_staff', 'is_active')
	
	search_fields = ('email',)
	
	ordering = ('email',)
	
	filter_horizontal = ('groups', 'user_permissions')
	
	readonly_fields =  ('last_login','date_joined',)
