from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# If the SECRET_KEY isn't defined we get the misleading error message
# CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False.
SECRET_KEY = "3*+d^_kjnr2gz)4q2m(&&^%$p4fj5dk3%lz4pl3g4m-%6!gf&)"

DEBUG = False
ALLOWED_HOSTS = ["*"]
# Must set ROOT_URLCONF else we get
# AttributeError: 'Settings' object has no attribute 'ROOT_URLCONF'
ROOT_URLCONF = "djangoapp.urls"

# Turn off deprecation warning
USE_TZ = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
