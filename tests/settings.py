import os
import sys


urlpatterns = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

INSTALLED_APPS = [
    'sekizai',
    'tests',
]

ROOT_URLCONF = 'tests.settings'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(__file__), 'templates')
        ],
        'OPTIONS': {
            'context_processors': ['sekizai.context_processors.sekizai'],
            'debug': True,
        },
    },
]


def runtests():
    from django import setup
    from django.conf import settings
    from django.test.utils import get_runner
    settings.configure(
        INSTALLED_APPS=INSTALLED_APPS,
        ROOT_URLCONF=ROOT_URLCONF,
        DATABASES=DATABASES,
        TEST_RUNNER='django.test.runner.DiscoverRunner',
        TEMPLATES=TEMPLATES,
    )
    setup()

    # Run the test suite, including the extra validation tests.
    TestRunner = get_runner(settings)

    test_runner = TestRunner(verbosity=1, interactive=False, failfast=False)
    failures = test_runner.run_tests(INSTALLED_APPS)
    return failures


def run():
    failures = runtests()
    sys.exit(failures)


if __name__ == '__main__':
    run()
