from django.core.exceptions import ImproperlyConfigured
from sekizai.utils import load_filter
import inspect

DEFAULT_FILTERS = ['sekizai.filters.defaults.UniqueFilter']

class BaseFilter(object):
    """
    Base filter class, must be subclassed to write own filters.
    """
    def __init__(self, **configs):
        """
        A filter may get configuration values from the settings.
        """
        self.configs = configs
        
    def append(self, stack, new, namespace):
        """
        Return False if it should not be appended, otherwise return the to be
        appended data
        """
        return new
    
    def postprocess(self, data, namespace):
        """
        Postprocess the data in this namespace and return it.
        """
        return data


class Namespace(object):
    """
    A namespace configuration holding the filters
    """
    def __init__(self, run_defaults, filters, configs={}):
        self.run_defaults = run_defaults
        self.configs = configs
        def _load(filter_class):
            if isinstance(filter_class, basestring):
                filter_class = load_filter(filter_class)
            if inspect.isclass(filter_class):
                return filter_class(**self.configs)
            else: # pragma: no cover
                return filter_class
        self.filters = [_load(filter_class) for filter_class in filters]
        
    def add(self, finstance):
        """
        Add a filter on runtime.
        """
        if isinstance(finstance, basestring):
            finstance = load_filter(finstance)(**self.configs)
        if not isinstance(finstance, BaseFilter): # pragma: no cover
            raise ImproperlyConfigured(
                "django-sekizai filters must subclass "
                "'sekizai.filteres.base.BaseFilter'"
            )
        self.filters.append(finstance)
        
    def __iter__(self):
        """
        Iterate over filters in this namespace.
        """
        if self.run_defaults:
            for filter_instance in registry.get_filters('__default__'):
                yield filter_instance
        for default_filter_instance in self.filters:
            yield default_filter_instance


class Registry(object):
    """
    The filter registry.
    """
    def __init__(self):
        self.namespaces = {}
        
    def init(self, filters):
        """
        Actual initialization
        """
        self._init_default()
        if filters is not None:
            self._init(filters)
            
    def _init_default(self):
        """
        Initialize default filters
        """
        if '__default__' in self.namespaces: # pragma: no cover
            for filter_class in DEFAULT_FILTERS:
                self.namespaces['__default__'].add(filter_class)
        else:
            self.namespaces['__default__'] = Namespace(False, DEFAULT_FILTERS)
        
    def _init(self, settings):
        """
        Initialize custom filters
        """
        for namespace, config in settings.items():
            nsinstance = Namespace(
                config.get('run_defaults', True),
                config.get('filters', []),
                config.get('configs', {}),
            )
            self.namespaces[namespace] = nsinstance
            
    def add(self, namespace, filter_class):
        """
        Add a filter to a namespace.
        """
        self.namespaces[namespace].add(filter_class)
            
    def get_filters(self, namespace):
        """
        Get filters for a namespace
        """
        return self.namespaces.get(namespace, self.namespaces['__default__'])
    
registry = Registry()