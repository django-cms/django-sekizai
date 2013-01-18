#####
Usage
#####

*************
Configuration
*************

In order to get started with django-sekizai, you'll need to do the following
steps:

* Put 'sekizai' into your ``INSTALLED_APPS`` setting.
* Use one of the following:
    * Put ``sekizai.context_processors.sekizai`` into your
      ``TEMPLATE_CONTEXT_PROCESSORS`` setting and use
      ``django.template.RequestContext`` when rendering your templates.
    * Use ``sekizai.context.SekizaiContext`` when rendering your templates.

**********************
Template Tag Reference
**********************
.. highlight:: html+django

.. note:: All sekizai template tags require the ``sekizai_tags`` template tag
          library to be loaded.
          

Handling code snippets
======================

.. versionadded:: 0.7
    The ``strip`` flag was added.

Sekizai uses ``render_block`` and ``addtoblock`` to handle unique code snippets.
Define your blocks using ``{% render_block <name> %}`` and add data to that
block using ``{% addtoblock <name> [strip] %}...{% endaddotblock %}``. If the
strip flag is set, leading and trailing whitespace will be removed.

Example Template::

    {% load sekizai_tags %}
    
    <html>
    <head>
    {% render_block "css" %}
    </head>
    <body>
    Your content comes here.
    Maybe you want to throw in some css:
    {% addtoblock "css" %}
    <link href="/media/css/stylesheet.css" media="screen" rel="stylesheet" type="text/css" />
    {% endaddtoblock %}
    Some more content here.
    {% addtoblock "js" %}
    <script type="text/javascript">
    alert("Hello django-sekizai");
    </script>
    {% endaddtoblock %}
    And even more content.
    {% render_block "js" %}
    <body>
    </html>
    
Above example would roughly render like this::

    <html>
    <head>
    <link href="/media/css/stylesheet.css" media="screen" rel="stylesheet" type="text/css" />
    </head>
    <body>
    Your content comes here.
    Maybe you want to throw in some css:
    Some more content here.
    And even more content.
    <script type="text/javascript">
    alert("Hello django-sekizai");
    </script>
    <body>
    </html>


Handling data
=============

Sometimes you might not want to use code snippets but rather just add a value to
a list. For this purpose there are the
``{% with_data <name> as <varname> %}...{% end_with_data %}`` and
``{% add_data <name> <value> %}`` template tags.

Example::

    {% load sekizai_tags %}
    
    <html>
    <head>
    {% with_data "css-data" as stylesheets %}
    {% for stylesheet in stylesheets %}
        <link href="{{ MEDIA_URL }}{{ stylesheet }}" media="screen" rel="stylesheet" type="text/css" />
    {% endfor %}
    {% end_with_data %}
    </head>
    <body>
    Your content comes here.
    Maybe you want to throw in some css:
    {% add_data "css-data" "css/stylesheet.css" %}
    Some more content here.
    <body>
    </html>
    
Above example would roughly render like this::

    <html>
    <head>
    <link href="/media/css/stylesheet.css" media="screen" rel="stylesheet" type="text/css" />
    </head>
    <body>
    Your content comes here.
    Maybe you want to throw in some css:
    Some more content here.
    And even more content.
    <body>
    </html>


Sekizai data is unique
======================

All data in sekizai is enforced to be unique within its block namespace. This
is because the main purpose of sekizai is to handle javascript and css
dependencies in templates. 

A simple example using ``addtoblock`` and ``render_block`` would be::

    {% load sekizai_tags %} 

    {% addtoblock "js" %}
        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/mootools/1.3.0/mootools-yui-compressed.js"></script>
    {% endaddtoblock %}

    {% addtoblock "js" %}
        <script type="text/javascript">
            $('firstelement').set('class', 'active');
        </script>
    {% endaddtoblock %}

    {% addtoblock "js" %}
        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/mootools/1.3.0/mootools-yui-compressed.js"></script>
    {% endaddtoblock %}

    {% addtoblock "js" %}
        <script type="text/javascript">
            $('secondelement').set('class', 'active');
        </script>
    {% endaddtoblock %}
    
    {% render_block "js" %}

Above template would roughly render to::

    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/mootools/1.3.0/mootools-yui-compressed.js"></script>
    <script type="text/javascript">
        $('firstelement').set('class', 'active');
    </script>
    <script type="text/javascript">
        $('secondelement').set('class', 'active');
    </script>


.. versionadded:: 0.5

Processing sekizai data
=======================

Because of the :ref:`render-block-restrictions` restrictions it is not possible
to use sekizai with libraries such as django-compressor directly. For that
reason, sekizai added postprocessing capabilities to ``render_block`` in
version 0.5.

Postprocessors are callable Python objects (usually functions) that get the
render context, the data in a sekizai namespace and the name of the namespace
passed as arguments and should return a string.

An example for a processor that uses the Django builtin spaceless functionality
would be:

.. code-block:: python

    def spaceless_post_processor(context, data, namespace):
        from django.utils.html import strip_spaces_between_tags
        return strip_spaces_between_tags(data)


To use this post processor you have to tell ``render_block`` where it's
located. If above code sample lives in the Python module
``myapp.sekizai_processors`` you could use it like this::

    ...
    {% render_block "js" postprocessor "myapp.sekizai_processors.spaceless_post_processor" %}
    ...
