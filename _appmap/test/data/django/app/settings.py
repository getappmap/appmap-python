# If the SECRET_KEY isn't defined we get the misleading error message
# CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False.
SECRET_KEY = "3*+d^_kjnr2gz)4q2m(&&^%$p4fj5dk3%lz4pl3g4m-%6!gf&)"

DEBUG = False
ALLOWED_HOSTS = ["*"]
# Must set ROOT_URLCONF else we get
# AttributeError: 'Settings' object has no attribute 'ROOT_URLCONF'
ROOT_URLCONF = "app.urls"

# Turn off deprecation warning
USE_TZ = True
