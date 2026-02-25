"""
WSGI config for hiremind_admin project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hiremind_admin.settings')

application = get_wsgi_application()
