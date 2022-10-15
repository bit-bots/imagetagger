import os
from os.path import join as path_join
from configurations import Configuration, values
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_in_docker() -> bool:
    return os.getenv('IN_DOCKER', '') != ''


class Base(Configuration):
    ########################################################################
    #
    # General django settings
    # https://docs.djangoproject.com/en/3.1/topics/settings/
    #
    ########################################################################
    INSTALLED_APPS = [
        'imagetagger.annotations',
        'imagetagger.base',
        'imagetagger.images',
        'imagetagger.users',
        'imagetagger.tools',
        'imagetagger.administration',
        'django.contrib.admin',
        'imagetagger.tagger_messages',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'widget_tweaks',
        'friendlytagloader',
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
                    'imagetagger.base.context_processors.base_data',
                ],
            },
        },
    ]

    ROOT_URLCONF = 'imagetagger.urls'
    WSGI_APPLICATION = 'imagetagger.wsgi.application'

    FILE_UPLOAD_HANDLERS = [
        "django.core.files.uploadhandler.MemoryFileUploadHandler",
        "django.core.files.uploadhandler.TemporaryFileUploadHandler",
    ]

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

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    AUTH_USER_MODEL = 'users.User'

    PROBLEMS_URL = 'https://github.com/bit-bots/imagetagger/issues'
    PROBLEMS_TEXT = ''

    LOGIN_URL = '/user/login/'
    LOGIN_REDIRECT_URL = '/images/'

    # Flash Messages
    # https://docs.djangoproject.com/en/3.1/ref/contrib/messages/

    MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
    MESSAGE_TAGS = {
        messages.INFO: 'info',
        messages.ERROR: 'danger',
        messages.WARNING: 'warning',
        messages.SUCCESS: 'success',
    }

    # Sets the default expire time for new messages in days
    DEFAULT_EXPIRE_TIME = 7

    # Sets the default number of messages per page
    MESSAGES_PER_PAGE = 10

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.10/howto/static-files/

    STATIC_URL = '/static/'

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

    ########################################################################
    #
    # Computed properties and hooks
    #
    ########################################################################
    @property
    def DATABASES(self):
        """https://docs.djangoproject.com/en/1.10/ref/settings/#databases"""
        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'HOST': self.DB_HOST,
                'PORT': self.DB_PORT,
                'NAME': self.DB_NAME,
                'USER': self.DB_USER,
                'PASSWORD': self.DB_PASSWORD
            }
        }

    @classmethod
    def post_setup(cls):
        super().post_setup()

        if cls.SENTRY_REPORTING_ENABLED:
            try:
                import sentry_sdk
                from sentry_sdk.integrations.django import DjangoIntegration
                sentry_sdk.init(
                    dsn=cls.SENTRY_DSN,
                    integrations=[DjangoIntegration()],
                    # If you wish to associate users to errors you may enable sending PII data.
                    send_default_pii=cls.SENTRY_SEND_DEFAULT_PII
                )
            except ImportError:
                raise ImproperlyConfigured("Could not import sentry although the server is configured to use it")

    ########################################################################
    #
    # User-adaptable settings
    #
    ########################################################################
    DEBUG = values.BooleanValue(environ_prefix='IT', default=False)
    SECRET_KEY = values.SecretValue(environ_prefix='IT')
    DB_HOST = values.Value(environ_prefix='IT', environ_required=True)
    DB_PORT = values.PositiveIntegerValue(environ_prefix='IT', default=5432)
    DB_NAME = values.Value(environ_prefix='IT', default='imagetagger')
    DB_USER = values.Value(environ_prefix='IT', default=DB_NAME)
    DB_PASSWORD = values.Value(environ_prefix='IT', environ_required=True)
    ALLOWED_HOSTS = values.ListValue(environ_prefix='IT', environ_required=True)
    LANGUAGE_CODE = values.Value(environ_prefix='IT', default='en-us')
    TIME_ZONE = values.Value(environ_prefix='IT', default='Europe/Berlin')
    STATIC_ROOT = values.Value(environ_prefix='IT', default=path_join(BASE_DIR, 'static'))
    USE_IMPRINT = values.BooleanValue(environ_prefix='IT', default=False)
    IMPRINT_NAME = values.Value(environ_prefix='IT')
    IMPRINT_URL = values.Value(environ_prefix='IT')
    # the URL where the ImageTagger is hosted e.g. https://imagetagger.bit-bots.de
    DOWNLOAD_BASE_URL = values.Value(environ_prefix='IT', environ_required=True)
    TOOLS_ENABLED = values.BooleanValue(environ_prefix='IT', default=True)
    TOOL_UPLOAD_NOTICE = values.Value(environ_prefix='IT', default='')
    ENABLE_ZIP_DOWNLOAD = values.BooleanValue(environ_prefix='IT', default=is_in_docker())
    USE_NGINX_IMAGE_PROVISION = values.BooleanValue(environ_prefix='IT', default=is_in_docker())
    FS_URL = values.Value(environ_prefix='IT', default=path_join(BASE_DIR, 'data'))
    TMP_FS_URL = values.Value(environ_prefix='IT', default='temp://imagetagger')
    UPLOAD_NOTICE = values.Value(environ_prefix='IT', default='By uploading images to this tool you accept that '
                                                              'the images get published under creative commons license '
                                                              'and confirm that you have the permission to do so.')
    EXPORT_SEPARATOR = values.Value(environ_prefix='IT', default='|')
    # the path to the folder with the imagesets relative to the filesystem root (see FS_URL)
    IMAGE_PATH = values.Value(environ_prefix='IT', default='images')
    # the path to use for temporary image files relative to the temp filesystem (see TMP_FS_URL)
    TMP_IMAGE_PATH = values.Value(environ_prefix='IT', default='images')
    # the path to the folder with the tools relative to the filesystem root (see FS_URL)
    TOOLS_PATH = values.Value(environ_prefix='IT', default='tools')
    # filename extension of accepted imagefiles
    IMAGE_EXTENSION = values.ListValue(environ_prefix='IT', default=['png', 'jpeg'])
    ACCOUNT_ACTIVATION_DAYS = values.PositiveIntegerValue(environ_prefix='IT', default=7)

    SENTRY_REPORTING_ENABLED = values.BooleanValue(environ_prefix='IT', default=False)
    SENTRY_DSN = values.Value(environ_prefix='IT', environ_required=SENTRY_REPORTING_ENABLED)
    SENTRY_SEND_DEFAULT_PII = values.BooleanValue(environ_prefix='IT', default=False)


class Dev(Base):
    DEBUG = values.BooleanValue(environ_prefix='IT', default=True)
    SECRET_KEY = values.Value(environ_prefix='IT', default='DEV-KEY ONLY! DONT USE IN PRODUCTION!')
    DB_HOST = values.Value(environ_prefix='IT', default='localhost')
    DB_PASSWORD = values.Value(environ_prefix='IT', default='imagetagger')
    ALLOWED_HOSTS = values.ListValue(environ_prefix='IT', default=['localhost', '127.0.0.1'])
    DOWNLOAD_BASE_URL = values.Value(environ_prefix='IT', default='localhost')


class Prod(Base):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = values.Value(environ_prefix='IT', environ_required=True)
    EMAIL_PORT = values.Value(environ_prefix='IT')
    EMAIL_HOST_USER = values.Value(environ_prefix='IT')
    EMAIL_HOST_PASSWORD = values.Value(environ_prefix='IT')
    DEFAULT_FROM_EMAIL = values.Value(environ_prefix='IT')
