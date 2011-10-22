from django.conf import settings
from sekizai.data import SekizaiDictionary

def sekizai(request=None):
    """
    Simple context processor which makes sure that the SekizaiDictionary is
    available in all templates.
    """
    varname = getattr(settings, 'SEKIZAI_VARNAME', 'SEKIZAI_CONTENT_HOLDER')
    return {varname: SekizaiDictionary()}
