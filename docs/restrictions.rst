############
Restrictions
############

*******
General
*******

Any django-sekizai template tag will fail if the context processor is not used.

************
render_block
************

Following restrictions apply to this tag:

* The tag *must* be in the base template. It cannot be used in an included
  template.
* The tag *must not* be placed within a ``{% block ... %}`` tag.

Generally it is recommended to have all ``render_block`` tags in your base
template (the one that get's extended by all others). Having it in a template
that itself extends another template is *not* recommended. Since the most
common use case for django-sekizai is css and javascript files/snippets, you
would most likely want those in your base template anyway.