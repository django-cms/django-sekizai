# -*- coding: utf-8 -*-
import os
import sys

urlpatterns = []

TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'sqlite3',
        'NAME': ':memory:'
    }
}


INSTALLED_APPS = [
    'sekizai',
]

TEMPLATE_DIRS = [
    os.path.join(os.path.dirname(__file__), 'test_templates'),
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'sekizai.context_processors.sekizai',
]
    

ROOT_URLCONF = 'runtests'

def runtests():
    from django.conf import settings
    settings.configure(
        INSTALLED_APPS = INSTALLED_APPS,
        ROOT_URLCONF = ROOT_URLCONF,
        DATABASES = DATABASES,
        TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner',
        TEMPLATE_DIRS = TEMPLATE_DIRS,
        TEMPLATE_CONTEXT_PROCESSORS = TEMPLATE_CONTEXT_PROCESSORS,
        TEMPLATE_DEBUG = TEMPLATE_DEBUG
    )

    # Run the test suite, including the extra validation tests.
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)

    test_runner = TestRunner(verbosity=1, interactive=False, failfast=False)
    failures = test_runner.run_tests(INSTALLED_APPS)
    return failures


if __name__ == "__main__":
    failures = runtests()
    if failures:
        sys.exit(bool(failures))
