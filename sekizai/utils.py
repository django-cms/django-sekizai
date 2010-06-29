class UniqueList(list):
    def append(self, data):
        if data not in self:
            super(UniqueList, self).append(data)


class BlockHolder(dict):
    def __getitem__(self, item):
        if item not in self:
            self[item] = UniqueList()
        return super(BlockHolder, self).__getitem__(item)
