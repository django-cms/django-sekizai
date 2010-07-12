from django.utils.importlib import import_module

def load_filter(name):
    """
    Loads a filter class and returns that class (not an instance of it)
    """
    modname, classname = name.rsplit('.', 1)
    mod = import_module(modname)
    return getattr(mod, classname)