"""CountMeIn_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.generic.base import RedirectView
from django.views.generic.base import TemplateView
from accounts.views import register
from django.contrib import admin
from django.urls import include, path, re_path
from accounts import views as accounts_views
from home import views as home_views
from django.contrib.auth import views as auth_views
from home import contact
from .settings import MEDIA_ROOT, MEDIA_URL, STATIC_URL, STATIC_ROOT
from django.conf.urls.static import static
 

urlpatterns = [
    path('home/', RedirectView.as_view(url='/', permanent=True)),
    path('admin/', admin.site.urls),
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset',),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done',),
    path('admin/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm',),
    path('admin/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete',),
    path('admin/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change',),
    path('admin/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done',),
    path('profile/', accounts_views.profile, name='profile'),
    path('login/', accounts_views.login, name='login'),
    path('my_details/', accounts_views.my_details, name='my_details'),
    re_path(r'^profile/(?P<invite_code>\d+)/$', accounts_views.profile, name='profile'),
    
    path('', include('booking.urls')),
    path('', include('assets.urls')),  
    path('register/', register.as_view(), name='register'),
    path('', include('django.contrib.auth.urls')),
    path('contact/', contact.ContactUs.as_view(), name='contact'),
    path('', home_views.get_index, name='index'),
    
] + static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL, document_root=STATIC_ROOT)

#path('login/', signin.as_view(), name='login'),