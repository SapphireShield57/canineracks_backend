from pathlib import Path
from datetime import timedelta
import os

import dj_database_url
from decouple import config
from corsheaders.defaults import default_headers


BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY / ENVIRONMENT
# ============================================================

SECRET_KEY = config("DJANGO_SECRET_KEY")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = ["*"]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",

    "corsheaders",
    "django_cleanup.apps.CleanupConfig",
    "imagekit",
    "cloudinary",
    "cloudinary_storage",

    # Local apps
    "users",
    "inventory",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    # CSRF middleware intentionally remains disabled
    # "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]


# ============================================================
# URL / TEMPLATE / WSGI
# ============================================================

ROOT_URLCONF = "canineracks_backend.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "canineracks_backend.wsgi.application"


# ============================================================
# DATABASE
# ============================================================
#
# Render supplies DATABASE_URL through the environment.
#
# We intentionally DO NOT hard-code the old PostgreSQL URL here.
#
# ============================================================

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600
    )
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# CUSTOM USER MODEL
# ============================================================

AUTH_USER_MODEL = "users.CustomUser"


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Manila"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "EXCEPTION_HANDLER": "inventory.views.custom_exception_handler",
}


# ============================================================
# SIMPLE JWT
# ============================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ============================================================
# DJOSER
# ============================================================

DJOSER = {
    "LOGIN_FIELD": "email",
    "USER_CREATE_PASSWORD_RETYPE": True,

    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": True,

    "PASSWORD_RESET_CONFIRM_URL": (
        "password-reset/confirm/{uid}/{token}"
    ),

    "ACTIVATION_URL": "activate/{uid}/{token}",

    "SERIALIZERS": {
        "user_create": "users.serializers.UserCreateSerializer",
        "user": "users.serializers.UserSerializer",
        "current_user": "users.serializers.UserSerializer",
    },
}


# ============================================================
# AUTHENTICATION BACKENDS
# ============================================================

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "users.backends.EmailBackend",
]


# ============================================================
# CORS
# ============================================================

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost:\d+$",
    r"^http://127\.0\.0\.1:\d+$",
]

CORS_ALLOWED_ORIGINS = [
    "https://canineracks-inventory-web.vercel.app",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "Authorization",
]

CORS_ALLOW_CREDENTIALS = True


# ============================================================
# CSRF TRUSTED ORIGINS
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    "https://canineracks-backend.onrender.com",
    "https://canineracks-inventory-web.vercel.app",
]


# ============================================================
# EMAIL / GMAIL SMTP
# ============================================================
#
# Credentials are supplied through Render environment variables.
# Do NOT put the Gmail App Password in this file.
#
# ============================================================

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = config(
    "EMAIL_HOST",
    default="smtp.gmail.com",
)

EMAIL_PORT = config(
    "EMAIL_PORT",
    default=587,
    cast=int,
)

EMAIL_HOST_USER = config(
    "EMAIL_HOST_USER"
)

EMAIL_HOST_PASSWORD = config(
    "EMAIL_HOST_PASSWORD"
)

EMAIL_USE_TLS = config(
    "EMAIL_USE_TLS",
    default=True,
    cast=bool,
)

DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default="CanineRacks <canineracks@gmail.com>",
)


# ============================================================
# CLOUDINARY
# ============================================================
#
# Credentials are supplied through Render environment variables.
# Do NOT put the Cloudinary API secret in this file.
#
# ============================================================

DEFAULT_FILE_STORAGE = (
    "cloudinary_storage.storage.MediaCloudinaryStorage"
)

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config(
        "CLOUDINARY_CLOUD_NAME"
    ),

    "API_KEY": config(
        "CLOUDINARY_API_KEY"
    ),

    "API_SECRET": config(
        "CLOUDINARY_API_SECRET"
    ),
}
