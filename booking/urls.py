from django.urls import path, re_path
from . import views

urlpatterns = [
	path('bookings/', views.my_bookings, name ="my_bookings"),
	path('bookings/<int:asset_id>/', views.my_bookings, name ="my_bookings"),
	path('bookings/<int:asset_id>/<int:booking_id>/', views.my_bookings, name ="my_bookings"),
	path('bookings/<int:asset_id>/<time_period>/', views.my_bookings, name ="my_bookings"),
	path('bookings/<int:asset_id>/<time_period>/<int:booking_id>/', views.my_bookings, name ="my_bookings"),
	path('bookings/venue/<int:asset_id>/', views.my_venue_bookings, name ="my_venue_bookings"),
	path('bookings/venue/<int:asset_id>/<time_period>/', views.my_venue_bookings, name ="my_venue_bookings"),
	path('bookings/venue/<int:asset_id>/<time_period>/<int:booking_id>/', views.my_venue_bookings, name ="my_venue_bookings"),
	path('bookings/venue/calendar/<int:asset_id>/', views.venue_calendar_admin, name="venue_calendar_admin"),
	path('bookings/venue/calendar/<int:asset_id>/update_exception_date_and_time/',views.update_exception_date_and_time, name="exception_date_selection"),
	re_path(r'^booking/new/asset/(?P<asset_id>\d+)/$', views.make_a_booking, name="make_a_booking"),
	path('booking/new/asset/<int:asset_id>/review/', views.review_a_booking, name="review_a_booking"),	
	path('booking/new/asset/<int:asset_id>/update_selected_date_and_time/',views.update_selected_date_and_time, name="requested_date_selection"),
	path('booking/new/asset/<int:asset_id>/update_exception_date_and_time/',views.update_exception_date_and_time, name="exception_date_selection"),
	path('bookings/venue/<int:asset_id>/print_bookings/<time_period>/',views.print_bookings, name="print_date"),
	path('bookings/venue/<int:asset_id>/print_bookings/<int:the_year>/<int:the_month>/<int:the_day>/',views.print_bookings, name="print_date"),
	path('booking/delete/<int:booking_id>/', views.delete_a_booking, name="delete_a_booking"),
	
]
