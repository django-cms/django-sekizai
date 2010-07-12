import os
ADMINS = (
)

TEMPLATE_DEBUG = True

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ':memory:'

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/admin_media/'

SECRET_KEY = '_(v_+wp2k^5=hq35(d2qan*)pyid1nfx$ei&x%2e8xjbekzjfq'

ROOT_URLCONF = 'testapp.urls'


INSTALLED_APPS = (
    'testapp',
    'sekizai',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'sekizai.context_processors.sekizai',
)

SEKIZAI_JAVASCRIPT_MINIFIER_COMMAND = 'yui-compressor --type=js'