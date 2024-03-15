from pathlib import Path

import django
import django.conf

django.conf.settings.configure(
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    MIDDLEWARE=["django.middleware.http.ConditionalGetMiddleware"],
    ROOT_URLCONF="djangoapp.urls",
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [Path(__file__).parent],
        }
    ],
    SECRET_KEY="not-a-secret",
)

django.setup()
