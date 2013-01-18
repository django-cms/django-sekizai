Please refer to the documentation in the docs/ directory for help.


About this project:

The main reason I started this project was the lack of a good media (css/js)
framework in django and the django-cms. Yes there is the Media class used in
forms in django, but really that doesn't work that well. Usually the frontend
guys want to decide on css and javascript files to be included and they don't
want to have to edit Python files to change that neither did I want them to
change my Python files. Therefor there was a need to allow you to edit contents
of templates which are before or after the point where you are now. Also I
wanted duplicates to be removed. As a result I wrote django-sekizai, which does
exactly that. It's similar to blocks, just instead of inheriting them, you
extend them.

There are some issue/restrictions with this implementation due to how the
django template language works, but if used properly it can be very useful and
it is the media handling framework for the django CMS (since version 2.2).

.. image:: https://secure.travis-ci.org/ojii/django-sekizai.png?branch=master
