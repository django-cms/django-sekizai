from typing import Dict, Union

from django.http import HttpRequest

from sekizai.data import UniqueSequence


def sekizai(request: Union[None, HttpRequest]) -> Dict[str, UniqueSequence]: ...
