#######
Filters
#######

django-sekizai supports filters for block content. By default a filter is used
that ensures that no duplicate content is added to a block. However there are
also some other built-in filters available for use and it is very easy to write
own filters.

*************
Configuration
*************

In your settings module you can define the ``SEKIZAI_FILTERS`` setting, which is
a Python dictionary consisting of namespaces as keys and a Python dictionary as
value holding the configuration of filters for this namespace.

An example would be::

    SEKIZAI_FILTERS = {
        'external-css': {
            'filters': ['sekizai.filters.css.CSSSingleFileFilter'],
        },
        'inline-css': {
            'filters': ['sekizai.filters.css.CSSInlineToFileFilter'],
        },
        'minified-js': {
            'filters': ['sekizai.filters.js.JavascriptMinifier'],
        },
    }
    
This will apply the filters defined in the settings for those three namespaces
on top of the default filter. To disable the default filter (which will allow
you to add duplicate content to a block) set ``run_defaults`` to ``False`` for
that namespace.

The ``filters`` of a namespace is a list of import paths to a filter class which
should be a subclass of ``sekizai.filters.base.BaseFilter``.

To add more default filters to *all* namespaces, use the ``__default__``
namespace in your settings dictionary.


***************
Builtin Filters
***************

.. class:: sekizai.filters.css.CSSInlineToFileFilter

    A filter that searchs for all inline styles within it's blocks and turns
    them into a (optionally) minified single external css file. You may use the 
    ``SEKIZAI_CSS_MINIFIER_COMMAND`` setting to specify a console command to be
    run to minify the css. The command should accept css from standard input and
    print the minified version of it to standard output. Per default, no
    minification happens.
    
    .. warning:: The ``render_block`` tags of namespaces used with this filter
        must be placed into the head of a website, since it will insert a link
        tag at the beginning of it's output.

.. class:: sekizai.filters.css.CSSSingleFileFilter

    Packs all external stylesheets found in link tags within it's blocks into a
    single css file.
    
    .. warning:: The ``render_block`` tags of namespaces used with this filter
        must be placed into the head of a website, since it will insert a link
        tag at the beginning of it's output.

.. class:: sekizai.filters.defaults.UniqueFilter

    Filters out all duplicate content from a block. This filter is active by
    default.

.. class:: sekizai.filters.js.JavascriptMinifier

    Minifies all inline javascripts using a command line minifier of your
    choice. Use the ``SEKIZAI_JAVASCRIPT_MINIFIER_COMMAND`` setting to specify a
    console command that minifies javascript taken from standard input and
    prints the minified javascript to standard output.

************************
Writing your own Filters
************************

You may write your own filters by sub-classing
``sekizai.filters.base.BaseFilter``. Your class may implement two methods
``append`` and ``postprocess``.

.. classmethod:: append(self, stack, new, namespace)

    Called when a ``addtoblock`` tag gets rendered.
    
    :param stack: List of unicode objects already in this namespace
    :param new: A unicode object that should be added to this namespace
    :param namespace: The name of this namespace.
    :rtype: A unicode object or False if the content should be ignored.

.. classmethod:: postprocess(self, data, namespace)

    This method gets called in ``render_block`` after all blocks have been added
    to this namespace.
    
    :param data: A unicode object containing the contents of this namespace.
    :param namespace: The name of this namespace.
    :rtype: A unicode object.