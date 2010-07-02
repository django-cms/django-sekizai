from sekizai.filters.base import registry

class SekizaiList(list):
    def __init__(self, namespace):
        self._namespace = namespace
        super(SekizaiList, self).__init__()

    def append(self, obj):
        for f in registry.get_filters(self._namespace):
            obj = f.append(self, obj, self._namespace)
            if not obj:
                return
        super(SekizaiList, self).append(obj)
        
    def render(self, between='\n'):
        data = '\n'.join(self)
        for f in registry.get_filters(self._namespace):
            data = f.postprocess(data, self._namespace)
        return data

class SekizaiDictionary(dict):
    def __init__(self):
        super(SekizaiDictionary, self).__init__()

    def __getitem__(self, item):
        if item not in self:
            self[item] = SekizaiList(item)
        return super(SekizaiDictionary, self).__getitem__(item)