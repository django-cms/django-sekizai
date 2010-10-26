#############
Handling Data
#############

If you need to handle data as opposed to template snippets, there are the
`with_data` and `add_data` tags.

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
    {% with_data "css-data" as stylesheets %}
    {% for stylesheet in stylesheets %}
    	<link href="{{ MEDIA_URL }}{{ stylesheet %}" media="screen" rel="stylesheet" type="text/css" />
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