#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():

    #os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CountMeIn_site.settings')

    if os.environ.get('DJANGO_ENV') == 'production_az_maria':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE','CountMeIn_site.production_az_maria')
    elif os.environ.get('DJANGO_ENV') == 'production_pa':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE','CountMeIn_site.production_pa')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE','CountMeIn_site.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
