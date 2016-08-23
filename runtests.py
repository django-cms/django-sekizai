# -*- coding: utf-8 -*-
import os
import sys

urlpatterns = []

TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}


INSTALLED_APPS = [
    'sekizai',
]

TEMPLATE_DIRS = [
    os.path.join(os.path.dirname(__file__), 'sekizai', 'test_templates'),
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'sekizai.context_processors.sekizai',
]
    

ROOT_URLCONF = 'runtests'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATE_DIRS,
        'OPTIONS': {
            'context_processors': TEMPLATE_CONTEXT_PROCESSORS,
            'debug': TEMPLATE_DEBUG
        },
    },
]


def runtests():
    from django import VERSION
    from django.conf import settings
    if VERSION[0] == 1 and VERSION[1] < 6:
        runner = 'django.test.simple.DjangoTestSuiteRunner'
    else:
        runner = 'django.test.runner.DiscoverRunner'
    settings.configure(
        INSTALLED_APPS=INSTALLED_APPS,
        ROOT_URLCONF=ROOT_URLCONF,
        DATABASES=DATABASES,
        TEST_RUNNER=runner,
        TEMPLATE_DIRS=TEMPLATE_DIRS,
        TEMPLATE_CONTEXT_PROCESSORS=TEMPLATE_CONTEXT_PROCESSORS,
        TEMPLATE_DEBUG=TEMPLATE_DEBUG,
        MIDDLEWARE_CLASSES=[],
        TEMPLATES=TEMPLATES,
    )
    if VERSION[1] >= 7:
        from django import setup
        setup()

    # Run the test suite, including the extra validation tests.
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)

    test_runner = TestRunner(verbosity=1, interactive=False, failfast=False)
    failures = test_runner.run_tests(INSTALLED_APPS)
    return failures


def main():
    failures = runtests()
    sys.exit(failures)


if __name__ == "__main__":
    main()
