from sekizai.utils import load_filter

class BaseFilter(object):
    def append(self, stack, new, namespace):
        """
        Return False if it should not be appended, otherwise return the to be
        appended data
        """
        return new
    
    def postprocess(self, data, namespace):
        return data


class Namespace(object):
    def __init__(self, run_defaults, *filters):
        self.run_defaults = run_defaults
        self.filters = [load_filter(f)() if isinstance(f, basestring) else f for f  in filters]
        
    def add(self, filter):
        if isinstance(filter, basestring):
            filter = load_filter(filter)
        self.filters.append(filter)
        
    def __iter__(self):
        if self.run_defaults:
            for f in registry.get('__default__'):
                yield f
        for f in self.filters:
            yield f


class Registry(object):
    def __init__(self):
        self.namespaces = {}
        
    def init(self, filters):
        if filters is None:
            self._init_default()
        else:
            self._init(filters)
            
    def _init_default(self):
        self.namespaces['__default__'] = Namespace(False, 'sekizai.filters.defaults.UniqueFilter')
        
    def _init(self, settings):
        self._init_default()
        for namespace, config in settings.items():
            self.namespaces[namespace] = Namespace(config.get('run_defaults', True), *config.get('filters', []))
            
    def get_filters(self, namespace):
        return self.namespaces.get(namespace, self.namespaces['__default__'])
    
registry = Registry()