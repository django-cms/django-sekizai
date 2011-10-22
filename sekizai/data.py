class SekizaiList(list):
    """
    A sekizai namespace in a template.
    """
    def __init__(self, namespace):
        self._namespace = namespace
        super(SekizaiList, self).__init__()

    def append(self, obj):
        """
        When content gets added, run the filters for this namespace.
        """
        if obj not in self:
            super(SekizaiList, self).append(obj)
        
    def render(self, between='\n'):
        """
        When the data get's rendered, run the postprocess filters.
        """
        return between.join(self)

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
