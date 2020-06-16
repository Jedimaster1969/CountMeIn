"""
WSGI config for CountMeIn_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CountMeIn_site.settings')

if os.environ.get('DJANGO_ENV') == 'production_az_maria':

	os.environ.setdefault('DJANGO_SETTINGS_MODULE','CountMeIn_site.production_az_maria')

elif os.environ.get('DJANGO_ENV') == 'production_pa':

	os.environ.setdefault('DJANGO_SETTINGS_MODULE','CountMeIn_site.production_pa')

else:

	os.environ.setdefault('DJANGO_SETTINGS_MODULE','CountMeIn_site.settings')



application = get_wsgi_application()
