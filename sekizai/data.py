from sekizai.filters.base import registry

class SekizaiList(list):
    """
    A sekizai namespace in a template.
    """
    def __init__(self, namespace):
        self._namespace = namespace
        self._filters = registry.get_filters(self._namespace)
        super(SekizaiList, self).__init__()

    def append(self, obj):
        """
        When content gets added, run the filters for this namespace.
        """
        for filter_instance in self._filters:
            obj = filter_instance.append(self, obj, self._namespace)
            if not obj:
                return
        super(SekizaiList, self).append(obj)
        
    def render(self, between='\n'):
        """
        When the data get's rendered, run the postprocess filters.
        """
        data = between.join(self)
        for filter_instance in self._filters:
            data = filter_instance.postprocess(data, self._namespace)
        return data

class SekizaiDictionary(dict):
    """
    A dictionary which auto fills itself instead of raising key errors.
    """
    def __init__(self):
        super(SekizaiDictionary, self).__init__()

    def __getitem__(self, item):
        if item not in self:
            self[item] = SekizaiList(item)
        return super(SekizaiDictionary, self).__getitem__(item)