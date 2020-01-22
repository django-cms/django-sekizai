==============
Django Sekizai
==============

|pypi| |build| |coverage|

Sekizai means "blocks" in Japanese, and that's what this app provides. A fresh
look at blocks. With django-sekizai you can define placeholders where your
blocks get rendered and at different places in your templates append to those
blocks. This is especially useful for css and javascript. Your sub-templates can
now define css and Javascript files to be included, and the css will be nicely
put at the top and the Javascript to the bottom, just like you should. Also
sekizai will ignore any duplicate content in a single block.

There are some issue/restrictions with this implementation due to how the
django template language works, but if used properly it can be very useful and
it is the media handling framework for the django CMS (since version 2.2).


Contributing
============

This is a an open-source project. We'll be delighted to receive your
feedback in the form of issues and pull requests. Before submitting your
pull request, please review our `contribution guidelines
<http://docs.django-cms.org/en/latest/contributing/index.html>`_.

We're grateful to all contributors who have helped create and maintain this package.
Contributors are listed at the `contributors <https://github.com/divio/django-sekizai/graphs/contributors>`_
section.


Documentation
=============

See ``REQUIREMENTS`` in the `setup.py <https://github.com/divio/django-sekizai/blob/master/setup.py>`_
file for additional dependencies:

|python| |django|

Please refer to the documentation in the docs/ directory for more information or visit our
`online documentation <https://django-sekizai.readthedocs.io/en/latest/>`_.


Running Tests
-------------

You can run tests by executing::

    virtualenv env
    source env/bin/activate
    pip install -r tests/requirements.txt
    python setup.py test


.. |pypi| image:: https://badge.fury.io/py/django-sekizai.svg
    :target: http://badge.fury.io/py/django-sekizai
.. |build| image:: https://travis-ci.org/divio/django-sekizai.svg?branch=master
    :target: https://travis-ci.org/divio/django-sekizai
.. |coverage| image:: https://codecov.io/gh/divio/django-sekizai/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/divio/django-sekizai

.. |python| image:: https://img.shields.io/badge/python-2.7%20%7C%203.4+-blue.svg
    :target: https://pypi.org/project/django-sekizai/
.. |django| image:: https://img.shields.io/badge/django-1.11%20%7C%202.2%20%7C%203.0-blue.svg
    :target: https://www.djangoproject.com/
