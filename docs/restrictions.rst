############
Restrictions
############

*******
General
*******

If ``TEMPLATE_DEBUG`` is True and you do not use either ``SekizaiContext`` or
``RequestContext`` and the ``sekizai`` context processor, a
``TemplateSyntaxError`` will be raised in any template using a sekizai tag.


.. _render-block-restrictions:

************
render_block
************

Following restrictions apply to this tag:

* The tag **must** be in the base template. It cannot be used in an included
  template.
* The tag **must not** be placed within a block tag (a template tag with an end
  tag, for example ``{% block name %}...{% endblock %}``).

Generally it is recommended to have all ``render_block`` tags in your base
template (the one that get's extended by all others). Having it in a template
that itself extends another template is **not** recommended. Since the most
common use case for django-sekizai is css and javascript files/snippets, you
would most likely want those in your base template anyway.

**********
addtoblock
**********

Following restrictions apply to this tag:

* If used in a template which *extends another template*, the ``addtoblock`` tag
  **must** be within one of the ``block`` tags.