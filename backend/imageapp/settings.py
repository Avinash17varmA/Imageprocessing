import os
from pathlib import Path

# -----------------------------
# BASE DIRECTORY
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# SECURITY
# -----------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = ["*"]  # For development, adjust in production

# -----------------------------
# APPLICATIONS
# -----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',

    # Your app
    'processing',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be at top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'imageapp.urls'

# -----------------------------
# TEMPLATES (not much for API, but needed)
# -----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Add templates here if needed
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

WSGI_APPLICATION = 'imageapp.wsgi.application'

# -----------------------------
# DATABASE (MongoDB via Djongo or PyMongo)
# -----------------------------
# Option 1: Using PyMongo (recommended for DRF API)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
# Use PyMongo in your views for connecting to MongoDB

# Option 2: Djongo (if you want Django ORM with MongoDB)
# DATABASES = {
#     'default': {
#         'ENGINE': 'djongo',
#         'NAME': 'imageprocessing_db',
#         'ENFORCE_SCHEMA': False,
#         'CLIENT': {
#             'host': MONGO_URI,
#         }
#     }
# }

# -----------------------------
# PASSWORD VALIDATION
# -----------------------------
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

# -----------------------------
# INTERNATIONALIZATION
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------
# STATIC FILES
# -----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# -----------------------------
# MEDIA FILES (for uploaded images)
# -----------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -----------------------------
# REST FRAMEWORK SETTINGS
# -----------------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Change for production
    ]
}

# -----------------------------
# CORS SETTINGS (allow React frontend)
# -----------------------------
CORS_ALLOW_ALL_ORIGINS = True  # For dev only
# For production: CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]

# -----------------------------
# REDIS SETTINGS (optional caching)
# -----------------------------
# REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
# Example usage: import redis; r = redis.Redis.from_url(settings.REDIS_URL)
