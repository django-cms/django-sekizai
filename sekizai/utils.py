from django.utils.importlib import import_module

def load_filter(name):
    modname, classname = name.rsplit('.', 1)
    mod = import_module(modname)
    return getattr(mod, classname)