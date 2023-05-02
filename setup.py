#!/usr/bin/env python
from pathlib import Path

from setuptools import find_packages, setup


REQUIREMENTS = [
    'django>=3.2',
    'django-classy-tags>=3.0',
]


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Framework :: Django',
    'Framework :: Django :: 3.2',
    'Framework :: Django :: 4.0',
    'Framework :: Django :: 4.1',
    'Framework :: Django :: 4.2',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
]

this_directory = Path(__file__).parent
long_description = (this_directory / "README.rst").read_text()

setup(
    name='django-sekizai',
    version='4.1.0',
    author='Jonas Obrist',
    author_email='ojiidotch@gmail.com',
    maintainer='Django CMS Association and contributors',
    maintainer_email='info@django-cms.org',
    url='https://github.com/django-cms/django-sekizai',
    license='BSD-3-Clause',
    description='Django Sekizai',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    test_suite='tests.settings.run',
)
