from pathlib import Path
from os import path, environ
import logging
from typing import List
from django.conf.locale.ja import formats as ja_formats
import ldap
from django_auth_ldap.config import LDAPSearch

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-d8ci9gtt&svpd9=wewjtz*el6-)l-ur(-9#mjw(%9aw4v#n1k)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS: List[str] = []


# Application definition

INSTALLED_APPS = [
    'cmm',
    'cmm_data',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'simple_history',
    'busking',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cmm.logging.LoggingRequestAttributesMiddleware',
]

ROOT_URLCONF = 'busking.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'busking.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        "ENGINE": 'django.db.backends.postgresql_psycopg2',
        "HOST": "127.0.0.1",
        "NAME": "busking",
        "PORT": 5432,
        "USER": "busking",
        "PASSWORD": environ['POSTGRES_PASSWORD'],
    },
    "test": {
        "ENGINE": 'django.db.backends.postgresql_psycopg2',
        "NAME": "busking",
        "USER": "busking",
        "PASSWORD": environ['POSTGRES_PASSWORD'],
        "HOST": "localhost",
        "PORT": 5432,
    },
    # "sqlserver": {
    #     "ENGINE": "mssql",
    #     "NAME": "busking",
    #     "USER": "busking",
    #     "PASSWORD": 'P09olp09ol',
    #     "HOST": "sqlserver",
    #     "PORT": "1433",
    #     "OPTIONS": {
    #         "driver": "ODBC Driver 17 for SQL Server"
    #     },
    # },
    'postgres': {
        "ENGINE": 'django.db.backends.postgresql_psycopg2',
        "HOST": "127.0.0.1",
        "NAME": "busking",
        "PORT": 5432,
        "USER": "busking",
        "PASSWORD": environ['POSTGRES_PASSWORD'],
    }
}


SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = path.join(BASE_DIR, 'temp')


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "django_auth_ldap.backend.LDAPBackend",
]

# 本番設定はenv.pyにある
AUTH_LDAP_SERVER_URI = environ['AUTH_LDAP_SERVER_URI']
AUTH_LDAP_BIND_DN = environ['AUTH_LDAP_BIND_DN']
AUTH_LDAP_BIND_PASSWORD = environ['AUTH_LDAP_BIND_PASSWORD']

AUTH_LDAP_USER_SEARCH = LDAPSearch('dc=tokyo-u,dc=ac,dc=jp', ldap.SCOPE_SUBTREE, '(uid=%(user)s)')
AUTH_LDAP_CONNECTION_OPTIONS = {ldap.OPT_DEBUG_LEVEL: 1, ldap.OPT_REFERRALS: 0, }
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'userPrincipalName',
}
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_FIND_GROUP_PERMS = False
AUTH_LDAP_CACHE_TIMEOUT = 3600


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'ja'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'cmm.AuthUser'

LANGUAGES = (
    ('en', 'English'),
    ('ja', 'Japanese'),
)

LOCALE_PATHS = (
    path.join(BASE_DIR, 'locale/'),
    path.join(Path(__file__).resolve().parent, 'locale/'),
)

USE_THOUSAND_SEPARATOR = True
NUMBER_GROUPING = (3, 0)

ja_formats.DATE_FORMAT = 'Y/m/d'
ja_formats.DATETIME_FORMAT = 'Y/m/d H:i:s'
ja_formats.SHORT_DATETIME_FORMAT = 'Y/m/d H:i'
ja_formats.DATE_INPUT_FORMATS = ['%Y/%m/%d', '%Y-%m-%d', '%Y%m%d']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}][{process:d}][{thread:d}][{ip_address}][{username}][{levelname}][{module}:{filename}:{funcName}]: {message}',     # noqa
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'style': '{',
        },
        'simple': {
            'format': '[{asctime}][{module}][{levelname}]: {message}',
            'datefmt': '%Y/%m/%d %H:%M:%S',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'extra_attributes': {
            '()': 'cmm.logging.LoggingRequestAttributesFilter',
        }
    },
    'handlers': {
        'sql_log': {
            'level': 'DEBUG',
            'filters': ['require_debug_true', 'extra_attributes'],
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '/temp/django_sql.log',
            'encoding': 'utf8',
        },
        'root_log': {
            'level': 'DEBUG',
            'filters': ['require_debug_true', 'extra_attributes'],
            # # TimedRotatingFileHandler must be used with --noreload option
            # 'class': 'logging.handlers.TimedRotatingFileHandler',
            # 'when': 'midnight',
            # 'interval': 5,
            # 'backupCount': 100,
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '/temp/django_root.log',
            'encoding': 'utf8',
        },
        'app_log': {
            'level': 'DEBUG',
            'filters': ['require_debug_true', 'extra_attributes', ],
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '/temp/app.log',
            'encoding': 'utf8',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true', 'extra_attributes'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'root': {
        'handlers': ['console', 'root_log'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'app_log'],
            # 'level': getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            # 'handlers': ['sql_log'],
            'handlers': ['sql_log'],
            'level': 'DEBUG',
            'propagate': False,
        },
        "django_auth_ldap": {"level": "DEBUG", "handlers": ["console"]}
    }
}

# Disable logging for "Not Found: /favicon.ico"
logging.getLogger('django.request').setLevel(logging.ERROR)
