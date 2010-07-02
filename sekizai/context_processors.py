from sekizai.data import SekizaiDictionary
from sekizai.settings import VARNAME

def sekizai(request=None):
    return {VARNAME: SekizaiDictionary()}