from sekizai.filters.utils.minifiers import Minifier, BaseMinifierFilter
from django.conf import settings

COMMAND = getattr(settings, 'SEKIZAI_JAVASCRIPT_MINIFIER_COMMAND', None)

class JavascriptMinfier(BaseMinifierFilter):
    """
    Inline javascript minfier filter.
    """
    tag = 'script'
    restrictions = {
        'type': lambda x: x == 'text/javascript',
        'src': lambda x: not x,
    }
    minifier = Minifier(COMMAND) if COMMAND else None