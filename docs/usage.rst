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

Sekizai uses ``render_block`` and ``addtoblock`` to handle unique code snippets.
Define your blocks using ``{% render_block <name> %}`` and add data to that
block using ``{% addtoblock <name> %}...{% endaddotblock %}``.

Example Template::

    {% load sekizai %}
    
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

    {% load sekizai %}
    
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

All data in sekizai is enforced to be unique within it's block namespace. This
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