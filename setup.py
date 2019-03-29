from setuptools import setup, find_packages

version = __import__('sekizai').__version__


setup(
    name='django-sekizai',
    version=version,
    description='Django Sekizai',
    author='Jonas Obrist',
    author_email='ojiidotch@gmail.com',
    url='http://github.com/ojii/django-sekizai',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'django>=1.11',
        'django-classy-tags>=0.3.1',
    ],
    test_suite='runtests.main',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
