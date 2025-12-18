from .settings_base import *
import os
DEBUG = False

ALLOWED_HOSTS = [
    "educatedowlbooks.com",
    "www.educatedowlbooks.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://educatedowlbooks.com",
    "https://www.educatedowlbooks.com",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "educatedowlbooks",
        "USER": "eob_user",
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": "localhost",
        "PORT": "5432",
    }
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True