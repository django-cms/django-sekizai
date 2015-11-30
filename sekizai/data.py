from collections.abc import MutableSequence


class UniqueSequence(MutableSequence):
    def __init__(self):
        self.data = []

    def __contains__(self, item):
        return item in self.data

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __len__(self):
        return len(self.data)

    def insert(self, index, value):
        if value not in self:
            self.data.insert(index, value)
