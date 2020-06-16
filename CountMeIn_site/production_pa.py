from .settings import *

ALLOWED_HOSTS = [
    '127.0.0.1',
    'databasis.eu.pythonanywhere.com',
]


STATIC_ROOT = os.path.join(BASE_DIR,'static')


DATABASES = {
	'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'databasis$countmein',
        'USER': 'databasis',
        'PASSWORD': 'invotech',
        'HOST': 'databasis.mysql.eu.pythonanywhere-services.com',
    }
}


INVITE_START_LINK = "http://databasis.eu.pythonanywhere.com/invite/"