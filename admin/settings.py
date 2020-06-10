"""
Django settings for admin project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4yksl!_2$*u@o#!pf_5xy*(gl=1gt=i1xryh+h$yboiid)5$$x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'module',
    'session',
    'media',
    'authenticate'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS_ORIGIN_WHITELIST = [
#     "http://localhost:3000",
# ]
CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK  =  { 
    'DEFAULT_AUTHENTICATION_CLASSES' :  ('rest_framework_simplejwt.authentication.JWTAuthentication',),
}

''' 
    Para generar una clave RSA nueva ejecute en la consola
        ssh-keygen -t rsa -b 4096 -m PEM -f jwtRS256.key

    Le pedira una frase, si desea puede agregarla o no, es opcional, luego ejecute este comando
        openssl rsa -in jwtRS256.key -pubout -outform PEM -out jwtRS256.key.pub

    Se generaran dos archivos, uno contiene la clave publica y la otra la privada
 '''
SIMPLE_JWT = {
    'ALGORITHM': 'HS256',
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=20),
    # 'SIGNING_KEY': "-----BEGIN RSA PRIVATE KEY-----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-----END RSA PRIVATE KEY-----",
    # 'VERIFYING_KEY': "-----BEGIN PUBLIC KEY-----MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA0b+RYwjDUQak77rXmWPFNPHttuEDacUMd5KMRtEnBsOTRXB64Fnvd8lgWlGIeCzDFe/krr4TSS530vW19QahjFVLIwS8U7Kqo/uDbtnzXtagHMjOb+HJ7QzdOd6A/59q1YWBeRqfGBdra6AaRu63cNyu5fRqII96CQlyxGsVufjCuDwFmap3Cvh1fnsjIUUONtMKEeWotxUGPcjgAXQf6kCQLwuWYANCLLbUetXP5JDkfTWcR7OTEebaNvsDHBksb1RCFaVeTBQ9j7G6gdwsUWtf9YNQKCcFtwRk58sXwU6vLRA5sQCkyyHb/rA8PJtWP2NhR6At8KM3jzkcbCfZPq9K7KXk7v362dQ7+J7HrJOqdu85HjmO46cGQLinT9U9qm9g2tgavJX0ohZ5Edrd0AsjnIKBriOp7gXDTGM4Oo4DLwTxp/QIN/MgdHqIuJ4SNa5MbaQCNGCqwnleKx9TXmLvF2t0FG8eKtxmSn9wxk3zvzA7MBAubpZ7nGN2btTLm/fmjOZMSP5g7lK1AM/trAaLgCmQivVEqYo/bG87LCiNG/DwQHUTJzTLH1nliR2JLZUg11HU+0MWkMb8c6EbjJVF6aYZ+LBTuBYdOgZeBfIxmN1LJ3dE7CnXVlhrJdSIEm5KtEtobpDPU3JAzaWtmw3a/qcKWmA1tKyLB3pTH1MCAwEAAQ==-----END PUBLIC KEY-----",
    }


ROOT_URLCONF = 'admin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'admin.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'admin', 
        'USER': 'root', #Your username
        'PASSWORD': 'password',  #Your password in db
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AUTH_USER_MODEL = 'authenticate.User'

ENV_ROOT = '/home/juanarcon/Proyectos/Project/venv/lib/python3.8/site-packages/'
