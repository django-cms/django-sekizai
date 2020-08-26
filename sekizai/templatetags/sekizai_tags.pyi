from types import ModuleType

from django.template import Context


def validate_context(context: Context) -> bool: ...

def import_processor(import_path: str) -> ModuleType: ...
