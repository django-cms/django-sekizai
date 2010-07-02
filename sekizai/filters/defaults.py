from sekizai.filters.base import BaseFilter


class UniqueFilter(BaseFilter):
    def append(self, stack, new, namespace):
        if new in stack:
            return False
        return new