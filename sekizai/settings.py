from django.conf import settings

VARNAME = getattr(settings, 'SEKIZAI_VARNAME', 'SEKIZAI_CONTENT_HOLDER')

FILTERS = getattr(settings, 'SEKIZAI_FILTERS', None)