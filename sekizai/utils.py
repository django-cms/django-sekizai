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
    import posixpath
    def relpath(path, start=posixpath.curdir):
        """Return a relative version of a path"""
        if not path: # pragma: no cover
            raise ValueError("no path specified")
        start_list = posixpath.abspath(start).split(posixpath.sep)
        path_list = posixpath.abspath(path).split(posixpath.sep)
        # Work out how much of the filepath is shared by start and path.
        i = len(posixpath.commonprefix([start_list, path_list]))
        rel_list = [posixpath.pardir] * (len(start_list)-i) + path_list[i:]
        if not rel_list: # pragma: no cover
            return posixpath.curdir
        return posixpath.join(*rel_list)