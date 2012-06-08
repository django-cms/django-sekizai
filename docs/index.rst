.. django-sekizai documentation master file, created by
   sphinx-quickstart on Tue Jun 29 23:12:20 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-sekizai's documentation!
==========================================

.. toctree::
    :maxdepth: 2
    
    installation
    usage
    restrictions
    helpers
    example

Sekizai means "blocks" in Japanese, and that's what this app provides. A fresh
look at blocks. With django-sekizai you can define placeholders where your
blocks get rendered and at different places in your templates append to those
blocks. This is especially useful for css and javascript. Your subtemplates can
now define css and javscript files to be included, and the css will be nicely
put at the top and the javascript to the bottom, just like you should. Also
sekizai will ignore any duplicate content in a single block. 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

