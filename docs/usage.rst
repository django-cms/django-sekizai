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

************
In Templates
************
.. highlight:: html+django

All sekizai template tags require the ``sekizai_tags`` template tag library to
be loaded.

Example::

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
