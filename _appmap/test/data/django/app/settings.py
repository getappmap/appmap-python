# If the SECRET_KEY isn't defined we get the misleading error message
# CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False.
SECRET_KEY = "3*+d^_kjnr2gz)4q2m(&&^%$p4fj5dk3%lz4pl3g4m-%6!gf&)"

# Must set DEBUG=True else we get the error
# $ python manage.py runserver 0.0.0.0:8000
# CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False.
DEBUG = True

# Must set ROOT_URLCONF else we get
# AttributeError: 'Settings' object has no attribute 'ROOT_URLCONF'
ROOT_URLCONF = "app.urls"
