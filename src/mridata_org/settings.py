"""
Django settings for mridata project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import urllib.parse
import time
import uuid


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if 'DJANGO_SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
else:
    SECRET_KEY = 'dummy_value'

# SECURITY WARNING: don't run with debug turned on in production!
if 'DEBUG' in os.environ:
    DEBUG = os.environ['DEBUG']
else:
    DEBUG = False

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'el_pagination',
    'mridata',
    'django_filters',
    's3direct',
    'taggit',
    'widget_tweaks',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mridata_org.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

INTERNAL_IPS = (
    '127.0.0.1',
)

WSGI_APPLICATION = 'mridata_org.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

if 'RDS_HOSTNAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'postgres',
            'USER': 'postgres',
            'HOST': 'db',
            'PORT': '5432',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# AWS
if 'AWS_ACCESS_KEY_ID' in os.environ:
    USE_AWS = True
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_STORAGE_BUCKET_REGION = os.environ['AWS_STORAGE_BUCKET_REGION']
else:
    USE_AWS = False


# Registration

REGISTRATION_OPEN = True
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# TEMP
TEMP_ROOT = os.environ['TEMP_ROOT']
FILE_UPLOAD_TEMP_DIR = TEMP_ROOT

# Static
if USE_AWS:
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_STATIC_LOCATION = 'static'

    STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)
    STATICFILES_STORAGE = 'mridata_org.storages.StaticStorage'
else:
    STATIC_URL = '/static/'

# Media
if USE_AWS:
    AWS_MEDIA_LOCATION = 'media'
    MEDIA_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_MEDIA_LOCATION)

    AWS_S3_ENDPOINT_URL = 'https://s3.%s.amazonaws.com' % AWS_STORAGE_BUCKET_REGION
    AWS_S3_REGION_NAME = AWS_STORAGE_BUCKET_REGION
    S3DIRECT_DESTINATIONS = {
        'uploads': {
            'key': lambda filename: 'media/uploads/{}_{}'.format(
            uuid.uuid4(), os.path.split(filename)[-1])}
    }
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.environ['MEDIA_ROOT']

# Celery
if USE_AWS:
    BROKER_URL = 'sqs://%s:%s@' % (urllib.parse.quote(AWS_ACCESS_KEY_ID, safe=''),
                                   urllib.parse.quote(AWS_SECRET_ACCESS_KEY, safe=''))
    BROKER_TRANSPORT = 'sqs'
    BROKER_TRANSPORT_OPTIONS = {
        'region': 'us-west-2',
        'port': 9324
    }
    BROKER_USER = AWS_ACCESS_KEY_ID
    BROKER_PASSWORD = AWS_SECRET_ACCESS_KEY
    CELERY_RESULT_BACKEND = None
else:
    BROKER_URL = 'redis://redis:6379'
    CELERY_RESULT_BACKEND = 'redis://redis:6379'

    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'America/Los_Angeles'
