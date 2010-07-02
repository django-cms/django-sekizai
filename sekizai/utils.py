class UniqueList(list):
    """
    INTERNAL
    """
    def append(self, data):
        if data not in self:
            super(UniqueList, self).append(data)


class BlockHolder(dict):
    """
    INTERNAL
    """
    def __getitem__(self, item):
        if item not in self:
            self[item] = UniqueList()
        return super(BlockHolder, self).__getitem__(item)

def load_filter(name):
    pass