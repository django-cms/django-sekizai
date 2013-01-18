from sekizai.data import SekizaiDictionary
from sekizai.helpers import get_varname

def sekizai(request=None):
    """
    Simple context processor which makes sure that the SekizaiDictionary is
    available in all templates.
    """
    return {get_varname(): SekizaiDictionary()}
