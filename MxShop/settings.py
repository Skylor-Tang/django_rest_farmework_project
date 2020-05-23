"""
Django settings for MxShop project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
sys.path.insert(0, os.path.join(BASE_DIR, 'extra_apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v!w6%5y26syg34ner)0ly)z#n=ewd2otax)6%awvx^fys=*eri'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
AUTH_USER_MODEL = 'users.UserProfile'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'trade.apps.TradeConfig',
    'goods.apps.GoodsConfig',
    'user_operation.apps.UserOperationConfig',
    'DjangoUeditor',
    'crispy_forms',
    'xadmin.apps.XAdminConfig',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'rest_framework.authtoken',
    'social_django',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'MxShop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # social_django 配置
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'MxShop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "mxshop",
        'USER': 'root',
        'PASSWORD': "739230854tmj",
        'HOST': "39.106.84.56",
        'OPTIONS': { 'init_command': 'SET default_storage_engine=INNODB;' }
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

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# 自定义auth验证函数
AUTHENTICATION_BACKENDS = (
    'users.views.CustomBackend',
    'social_core.backends.weibo.WeiboOAuth2',
    'social_core.backends.qq.QQOAuth2',
    'social_core.backends.weixin.WeixinOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# 静态文件配置
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
# 设置上传文件存储路径，从前端后后台生成的产品图均会存到这里（对应model中image字段upload_to指定的上传路径）
MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# rest_framework 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.AutoSchema',
    # 以下是 throttling 的配置
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
        'user': '1000/day'
    }
}

# rest_framework_extensions 配置
REST_FRAMEWORK_EXTENSIONS = {
    # 缓存过期时间
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 100
}

# Django 缓存配置 ： 使用 django-redis 时使用的设置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:739230854@127.0.0.1:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# JWT 配置
import datetime
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
}

# 手机号码正则表达式
REGEX_MOBILE = "^1[358]\d{9}$|147\d{8}$|^176\d{8}$"

# 云片网api_key
API_KEY = "2269abf14879c7fc226204d1f734a27f"

# 微博第三方认证应用信息
SOCIAL_AUTH_WEIBO_KEY = '2011318855'
SOCIAL_AUTH_WEIBO_SECRET = '405ae53b8fc2703a52770f985e9035aa'

# secial_django 配置文件
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/index/'

# 支付宝相关配置
app_private_key_path = os.path.join(BASE_DIR, 'apps/trade/keys/private_2048.txt')  # 使用该方法拼凑完整的绝对文件路径
alipay_public_key_path = os.path.join(BASE_DIR, 'apps/trade/keys/alipay_key_2048.txt')