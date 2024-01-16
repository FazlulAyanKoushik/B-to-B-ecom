import os
from datetime import timedelta
from pathlib import Path

from corsheaders.defaults import default_headers

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The root of the git repo - Could be ~/project or ~/repo
REPO_DIR = os.path.realpath(os.path.join(BASE_DIR, ".."))
# The directory of the current user ie /home/django a.k.a. ~
HOME_DIR = os.path.realpath(os.path.join(REPO_DIR, ".."))
# The directory where collectstatic command copies/symlinks the files to
# This can/should be located at ~/staticfiles, preferrably outside the git repo
STATIC_DIR = os.path.realpath(os.path.join(HOME_DIR, "staticfiles"))
# The directory where different applications uploads media files to
# This can/should be located at ~/media, preferrably outside the git repo
MEDIA_DIR = os.path.realpath(os.path.join(HOME_DIR, "media"))


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = STATIC_DIR
STATIC_URL = "/static/"

MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = "/media/"

STATICFILES_DIRS = [os.path.join(REPO_DIR, "assets")]

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
INTERNAL_IPS = [
    "127.0.0.1",
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-1(k)dd710l%!w&r=1@5kl%c_1r97bun#*mcnk-y2l^%s%!gh+4"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "django_filters",
    "versatileimagefield",
    "django_cleanup.apps.CleanupConfig",
    "axes",
    "simple_history",
]

PROJECT_APPS = [
    "mediaroomio.apps.MediaroomioConfig",
    "core.apps.CoreConfig",
    "catalogio.apps.CatalogioConfig",
    "otpio.apps.OtpioConfig",
    "accountio.apps.AccountioConfig",
    "orderio.apps.OrderioConfig",
    "weapi.apps.WeapiConfig",
    "addressio.apps.AddressioConfig",
    "paymentio.apps.PaymentioConfig",
    "tagio.apps.TagioConfig",
    "notificationio.apps.NotificationioConfig",
    "reviewio.apps.ReviewioConfig",
    "threadio.apps.ThreadioConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

# set base auth user model
AUTH_USER_MODEL = "core.User"

# middlewares
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]


if os.environ.get("ENABLE_CORS_HEADERS", False) == "True":
    INSTALLED_APPS = [
        "corsheaders",
    ] + INSTALLED_APPS
    MIDDLEWARE = [
        "corsheaders.middleware.CorsMiddleware",
    ] + MIDDLEWARE

    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:4000",
        "http://127.0.0.1:5173",
    ]
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:4000",
        "http://127.0.0.1:5173",
    ]
    CORS_ALLOW_HEADERS = (
        *default_headers,
        "accept",
        "authorization",
        "content-type",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
        "x-domain",
    )
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^http://\w+\.localhost:3000",
    ]
    CORS_ALLOW_ALL_ORIGINS = True

if os.environ.get("ENABLE_DEBUG_TOOLBAR", False) == "True":
    INSTALLED_APPS = [
        "debug_toolbar",
    ] + INSTALLED_APPS
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE


ROOT_URLCONF = "projectile.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "projectile.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# DJANGO REDIS
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ["REDIS_URL"],
        "TIMEOUT": None,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Dhaka"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "TEST_REQUEST_RENDERER_CLASSES": [
        "rest_framework.renderers.MultiPartRenderer",
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "3000/minute", "user": "1200/minute"},
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 40,
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=3),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
}

SPECTACULAR_SETTINGS = {
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
}

APPEND_SLASH = False

AXES_FAILURE_LIMIT = 10
AXES_ENABLED = False

# otp
OTP_EXPIRATION_TIME_SEC = 120
OTP_CHARACTER_LENGTH = 6

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "default": {"level": "INFO", "handlers": ["console"]},
        "common": {"level": "DEBUG", "handlers": ["console"]},
        "core": {"level": "DEBUG", "handlers": ["console"]},
        "accountio": {"level": "DEBUG", "handlers": ["console"]},
        "catalogio": {"level": "DEBUG", "handlers": ["console"]},
        "mediaroomio": {"level": "DEBUG", "handlers": ["console"]},
        "weapi": {"level": "DEBUG", "handlers": ["console"]},
    },
}
