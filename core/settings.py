"""
Django settings for core project.

Finance Dashboard Backend - Configuration
Includes: DRF, JWT Authentication, django-filter
"""

from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-sm4*3u2+ccne18&n2nu5ir+08j)+1ykhy&&2n=(@1#^)c(-pk@'

DEBUG = True

ALLOWED_HOSTS = []


# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',           # Django REST Framework for building APIs
    'rest_framework_simplejwt', # JWT token authentication
    'django_filters',           # Filtering support for DRF
    
    # Local apps
    'users',                    # Custom user management with roles
    'finance',                  # Financial records management
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'


# =============================================================================
# DATABASE - Using SQLite for simplicity
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

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


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = 'static/'


# =============================================================================
# CUSTOM USER MODEL
# Tell Django to use our custom User model instead of the default one
# =============================================================================

AUTH_USER_MODEL = 'users.User'


# =============================================================================
# DJANGO REST FRAMEWORK CONFIGURATION
# =============================================================================

REST_FRAMEWORK = {
    # Use JWT tokens for authentication (not session-based)
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    # Require authentication by default for all endpoints
    # Individual views can override this if needed
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Enable django-filter for filtering querysets
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Standard pagination - 10 items per page
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}


# =============================================================================
# JWT TOKEN CONFIGURATION
# =============================================================================

SIMPLE_JWT = {
    # Access token expires in 1 day (for development convenience)
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    
    # Refresh token expires in 7 days
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    
    # Generate new refresh token when refreshing
    'ROTATE_REFRESH_TOKENS': True,
    
    # Blacklist old refresh tokens after rotation
    'BLACKLIST_AFTER_ROTATION': True,
    
    # Token type in header: "Bearer <token>"
    'AUTH_HEADER_TYPES': ('Bearer',),
}
