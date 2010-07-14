from django.utils.importlib import import_module

def load_filter(name):
    """
    Loads a filter class and returns that class (not an instance of it)
    """
    modname, classname = name.rsplit('.', 1)
    mod = import_module(modname)
    return getattr(mod, classname)

import os
try:
    relpath = os.path.relpath
except:
    from posixpath import curdir, sep, pardir, join
    def relpath(path, start=curdir):
        """Return a relative version of a path"""
        if not path:
            raise ValueError("no path specified")
        start_list = posixpath.abspath(start).split(sep)
        path_list = posixpath.abspath(path).split(sep)
        # Work out how much of the filepath is shared by start and path.
        i = len(posixpath.commonprefix([start_list, path_list]))
        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        if not rel_list:
            return curdir
        return join(*rel_list)