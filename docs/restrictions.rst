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