#######
Example
#######

.. highlight:: html+django

A full example on how to use django-sekizai and when.

Let's assume you have a website, where all templates extend base.html, which
just contains your basic HTML structure. Now you also have a small template
which gets included on some pages. This template needs to load a javascript 
library and execute some specific javascript code.

Your "base.html" might look like this::

    {% load sekizai_tags %}<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <meta http-equiv="x-ua-compatible" content="ie=8" />
        <title>Your website</title>
        <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico" />
        <link rel="stylesheet" type="text/css" href="{{ MEDIA_URL }}css/base.css" media="all" />
        <link rel="stylesheet" type="text/css" href="{{ MEDIA_URL }}css/print.css" media="print" />
        {% render_block "css" %}
    </head>
    <body>
    {% block "content" %}
    {% endblock %}
    <script type="text/javascript" src="{{ MEDIA_URL }}js/libs/jquery-1.4.2.js"></script>
    {% render_block "js" %}
    </body>
    </html>
    
As you can see, we load ``sekizai_tags`` at the very beginning. We have two
sekizai namespaces: "css" and "js". The "css" namespace is rendered in the head
right after the base css files, the "js" namespace is rendered at the very
bottom of the body, right after we load jQuery.


Now to our included template. We assume there's a context variable called
``userid`` which will be used with the javascript code.

Your template ("inc.html") might look like this::

    {% load sekizai_tags %}
    <div class="my-div">
        <ul id="dynamic-content-{{ userid }}"></ul>
    </div>
    
    {% addtoblock "js" %}
    <script type="text/javascript" src="{{ MEDIA_URL }}js/libs/mylib.js"></script>
    {% endaddtoblock %}
    
    {% addtoblock "js" %}
    <script type="text/javascript">
    $(document).ready(function(){
        $('#dynamic-conent-{{ userid }}').do_something();
    }
    </script>
    {% endaddtoblock %}
    
The important thing to notice here is that we split the javascript into two
``addtoblock`` blocks. Like this, the library 'mylib.js' is only included once,
and the userid specific code will be included once per userid.


Now to put it all together let's assume we render a third template with 
``[1, 2, 3]`` as ``my_userids`` variable.

The third template looks like this::

    {% extends "base.html" %}
    
    {% block "content" %}
    {% for userid in my_userids %}
        {% include "inc.html" %}
    {% endfor %}
    {% endblock %}
    
And here's the rendered template::

    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <meta http-equiv="x-ua-compatible" content="ie=8" />
        <title>Your website</title>
        <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico" />
        <link rel="stylesheet" type="text/css" href="/media/css/base.css" media="all" />
        <link rel="stylesheet" type="text/css" href="/media/css/print.css" media="print" />
    </head>
    <body>
    <div class="my-div">
        <ul id="dynamic-content-1"></ul>
    </div>
    <div class="my-div">
        <ul id="dynamic-content-2"></ul>
    </div>
    <div class="my-div">
        <ul id="dynamic-content-3"></ul>
    </div>
    <script type="text/javascript" src="/media/js/libs/jquery-1.4.2.js"></script>
    <script type="text/javascript" src="{{ MEDIA_URL }}js/libs/mylib.js"></script>
    <script type="text/javascript">
    $(document).ready(function(){
        $('#dynamic-conent-1').do_something();
    }
    </script>
    <script type="text/javascript">
    $(document).ready(function(){
        $('#dynamic-conent-2').do_something();
    }
    </script>
    <script type="text/javascript">
    $(document).ready(function(){
        $('#dynamic-conent-3').do_something();
    }
    </script>
    </body>
    </html>
