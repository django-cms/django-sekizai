from sekizai.data import SekizaiDictionary
from sekizai.settings import VARNAME

def sekizai(request=None):
    """
    Simple context processor which makes sure that the SekizaiDictionary is
    available in all templates.
    """
    return {VARNAME: SekizaiDictionary()}