from sekizai.filters.base import BaseFilter
from django.utils.html import strip_spaces_between_tags

class SpacelessFilter(BaseFilter):
    def postprocess(self, data, namespace):
        return strip_spaces_between_tags(data)