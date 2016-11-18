"""
Django settings for overseas project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from datetime import timedelta
from celery.schedules import crontab


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s %(asctime)s] (Module: %(module)s, Process: %(process)d, Thread: %(thread)d): %(message)s'
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console1': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/overseas/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'utils.level3_info': {
            'handlers': ['console1'],
            'level': 'INFO',
        },
        'overseas.management.commands.sync_ag': {
            'handlers': ['console1'],
            'level': 'INFO',
        },
        'osverseas.models.access': {
            'handlers': ['console1'],
            'level': 'INFO',
        },
        'osverseas.tasks': {
            'handlers': ['console1'],
            'level': 'INFO',
        },
    }
}

# supervisor
from configparser import ConfigParser

conf = ConfigParser()

# for default we load ../conf/def.ini
conf.readfp(open(BASE_DIR + '/etc/def.ini'))
print('Settings > Load default conf Finished.')

if 'MC_OVERSEAS' in os.environ:
    extra = os.environ['MC_OVERSEAS']
    print('get extra env:', extra)

    try:
        conf.readfp(open(BASE_DIR + '/etc/%s.ini' % extra))
        print('Settings > Load extra conf Finished.')
    except Exception as e:
        print(e)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6kz7tj64b1&vi9i0smo55@l^js4h-gb2!!xmu-qfg+0nz01+t5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = conf.get('overseas', 'DEBUG') == 'True'

ALLOWED_HOSTS = ['*']

ADMIN_SITE_HEADER = 'Overseas administration'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'overseas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'overseas.urls'

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

WSGI_APPLICATION = 'overseas.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 'ENGINE': 'mysql.connector.django',
        'NAME': conf.get('mysql:main', 'DB_NAME'),
        'USER': conf.get('mysql:main', 'DB_USER'),
        'PASSWORD': conf.get('mysql:main', 'DB_PASS'),
        'HOST': conf.get('mysql:main', 'DB_HOST'),
        'PORT': conf.get('mysql:main', 'DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "level3_cache"
    },

    'file_cache': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/home/never/Envs/antique/cache',
        'TIMEOUT': 18000,  # 5 hours
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
            'CULL_FREQUENCY': 3,
        }
    }
}



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Level3
LEVEL3_BASE = 'https://ws.level3.com'
LEVEL3_APIKEY = conf.get('level3', 'LEVEL3_APIKEY')
LEVEL3_SECRET = conf.get('level3', 'LEVEL3_SECRET')
LEVEL3_TIME_SPAN = int(conf.get('level3', 'LEVEL3_TIME_SPAN'))  # minute
LEVEL3_LOG_DIR = conf.get('level3', 'LEVEL3_LOG_DIR')
LEVEL3_BASEURL = conf.get('level3', 'LEVEL3_BASEURL')

# swiftserve
SWIFTSERVE_BASE = 'https://api.swiftserve.com'
SWIFTSERVE_USER = conf.get('swiftserve', 'SWIFTSERVE_USER')
SWIFTSERVE_PASSWORD = conf.get('swiftserve', 'SWIFTSERVE_PASSWORD')

# Celery
BROKER_URL = conf.get('celery', 'CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = conf.get('celery', 'CELERY_RESULT_BACKEND')

CELERY_TASK_SERIALIZER = 'json'

# celery 定时任务过期时间
CELERY_TASK_RESULT_EXPIRES = 3600

CELERYBEAT_SCHEDULE = {
    'level3-every-30min': {
        'task': 'overseas.tasks.sync_level3',
        'schedule': crontab(minute='*/30'),
        'args': ()
    },
    'level3-every-day-log': {
        'task': 'overseas.tasks.sync_level3_log',
        'schedule': crontab(minute=0, hour=9),
        'args': ()
    },
    'level3-every-day': {
        'task': 'overseas.tasks.sync_level3_daily',
        'schedule': crontab(minute=30, hour=8),
        'args': ()
    },
    'level3-every-hour': {
        'task': 'overseas.tasks.sync_level3_hourly',
        'schedule': crontab(minute=10, hour='*'),
        'args': ()
    },
    'level3-every-8hour': {
        'task': 'overseas.tasks.sync_level3_8hourly',
        'schedule': crontab(minute=30, hour='0,16'),
        'args': ()
    },
    'level3-sync-temp': {
        'task': 'overseas.tasks.sync_level3_temp',
        'schedule': crontab(minute=20, hour=3),
        'args': ()
    }
    # 'ipip-every-day': {
    #     'task': 'overseas.tasks.sync_ipip',
    #     'schedule': crontab(minute=1, hour=8),
    #     'args': ()
    # }
}

# youdao translate key
YOUDAO_KEY = '1657216373'
YOUDAO_KEYFROM = 'level3api'
YOUDAO_BASEURL = ('http://fanyi.youdao.com/openapi.do'
                  '?keyfrom=%s&key=%s&type=data&doctype=json'
                  '&version=1.1&q=') % (YOUDAO_KEYFROM, YOUDAO_KEY)

# email settings
EMAIL_HOST = conf.get('sender', 'HOST')
EMAIL_PORT = conf.getint('sender', 'PORT')
EMAIL_USER = conf.get('sender', 'USER')
EMAIL_PASS = conf.get('sender', 'PASSWD')

# IPIP.net
IPIP_DATX_PATH = os.path.join(BASE_DIR, conf.get('ipip', 'IPIP_DATX_PATH'))
IPIP_DOWNLOAD_API_URL = conf.get('ipip', 'IPIP_DOWNLOAD_API_URL')

# login expires
LOGIN_EXPIRES = 3600

# rsync log
RSYNC_LOG_DIR = '/var/log/rsync_level3/maichuang/'
RSYNC_DAILY_DIR = '/var/log/rsync_level3/daily_log/'

# LOG_DATE_SPAN
LOG_DATE_SPAN = 3600

# mcaccount api
TAN14_API_BASE_URL = 'https://if.tan14.cn/'
