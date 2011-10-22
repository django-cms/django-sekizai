from django.template import Context
from sekizai.context_processors import sekizai

class SekizaiContext(Context):
    """
    An alternative context to be used instead of RequestContext in places where
    no request is available.
    """
    def __init__(self, *args, **kwargs):
        super(SekizaiContext, self).__init__(*args, **kwargs)
        self.update(sekizai())
