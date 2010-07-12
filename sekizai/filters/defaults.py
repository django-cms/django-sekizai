from sekizai.filters.base import BaseFilter


class UniqueFilter(BaseFilter):
    """
    Make sure that contents of a namespace are unique
    """
    def append(self, stack, new, namespace):
        if new in stack:
            return False
        return new