#######
Helpers
#######


**********************
:mod:`sekizai.helpers`
**********************


.. function:: get_namespaces(template)

    Returns a list of all sekizai namespaces found in ``template``, which should
    be the name of a template. This method also checks extended templates.
    

.. function:: valdiate_template(template, namespaces)

    Returns ``True`` if all namespaces given are found in the template given.
    Useful to check that the namespaces required by your application are
    available, so you can failfast if they're not.