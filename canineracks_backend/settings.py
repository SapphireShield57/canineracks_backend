from pathlib import Path
from datetime import timedelta
import dj_database_url
from decouple import config
import os
from corsheaders.defaults import default_headers  # ✅ Required for custom headers
import re

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = True

ALLOWED_HOSTS = ['*']  # Optional: restrict in production

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'users',
    'inventory',

    'corsheaders',  # ✅ CORS support
    'django_cleanup.apps.CleanupConfig',
    'imagekit',
    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✅ Must be at the top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

ROOT_URLCONF = 'canineracks_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'canineracks_backend.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://canineracks_db_user:9cquGr9C9s03YyAfEiVU4A51rpvqjMuh@dpg-d1st51h5pdvs73cue5f0-a.oregon-postgres.render.com/canineracks_db'
    )
}

# Password validation
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

AUTH_USER_MODEL = 'users.CustomUser'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'EXCEPTION_HANDLER': 'inventory.views.custom_exception_handler',
}

# SimpleJWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Djoser Configuration
DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SEND_ACTIVATION_EMAIL': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'PASSWORD_RESET_CONFIRM_URL': 'password-reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SERIALIZERS': {
        'user_create': 'users.serializers.UserCreateSerializer',
        'user': 'users.serializers.UserSerializer',
        'current_user': 'users.serializers.UserSerializer',
    },
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'users.backends.EmailBackend',
]

# ✅ CORS CONFIGURATION
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost:\d+$",  # ✅ Allows ALL localhost ports
]

CORS_ALLOWED_ORIGINS = [
    "https://canineracks-inventory-web.vercel.app",  # Production frontend
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'Authorization',
]

CORS_ALLOW_CREDENTIALS = True

# ✅ CSRF Trusted (still useful if CSRF enabled later)
CSRF_TRUSTED_ORIGINS = [
    'https://canineracks-backend.onrender.com',
    'https://canineracks-inventory-web.vercel.app',
]

# ✅ EMAIL SETTINGS (use App Passwords for Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'canineracks@gmail.com'
EMAIL_HOST_PASSWORD = 'chhn ymjj kwwq gtng'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'CanineRacks <canineracks@gmail.com>'

# ✅ CLOUDINARY STORAGE
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dcpelmlhu',
    'API_KEY': '746747611987718',
    'API_SECRET': 'vtVhjkCkrbLn7jHSoLC7et083aI'
}
