from sekizai.utils import BlockHolder
from sekizai.settings import VARNAME

def sekizai(request):
    return {VARNAME: BlockHolder()}