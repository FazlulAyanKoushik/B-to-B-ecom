import os
import sys
import site
import dotenv
import sysconfig


# The home directory of the user
USERHOME_DIR = '/home/django'

dotenv.read_dotenv(os.path.join(USERHOME_DIR, '.env'))

# Django directory, where manage.py resides
DJANGO_PROJECT_DIR = os.path.join(USERHOME_DIR, 'project/projectile')

# Site-packages under virtualenv directory
SITEPACK_DIR = sysconfig.get_paths()["purelib"]
site.addsitedir(SITEPACK_DIR)

if DJANGO_PROJECT_DIR not in sys.path:
    sys.path.append(DJANGO_PROJECT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectile.settings_live')

# os.environ["CELERY_LOADER"] = "django"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()