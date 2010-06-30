from sekizai.utils import BlockHolder
from sekizai.settings import VARNAME

def sekizai(request=None):
    return {VARNAME: BlockHolder()}