import os

SECRET_KEY = 'django-insecure-k2v)ww7k0$l3gkd@e*rs%hp1nggl)4dev761f(ovsh#!p$5rv-'

# settings.pyからそのままコピー
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# settings.pyからそのままコピー
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django3',
        'USER': 'nakaiyuki',
        'PASSWORD': 'PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


DEBUG = True