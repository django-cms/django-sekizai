from django.conf import settings
from sekizai.filters.utils.minifiers import BaseMinifierFilter, Minifier, NullMinifier
import hashlib
import os

COMMAND = getattr(settings, 'SEKIZAI_CSS_MINIFIER_COMMAND', None)
DIR = getattr(settings, 'SEKIZAI_CSS_MINIFIER_DIR', os.path.join(settings.MEDIA_ROOT, 'sekizai_css_minifier/'))

if not os.path.exists(DIR):
    os.makedirs(DIR)

class CSSInlineToFileFilter(BaseMinifierFilter):
    tag = 'style'
    minifier = Minifier(COMMAND) if COMMAND else NullMinifier()
    restrictions = {
        'type': lambda x: x == 'text/css',
    }
    
    def _minify(self, data, this):
        this[self] = []
        result = super(CSSInlineToFileFilter, self)._minify(data, this)
        # create the css file
        new = '\n'.join(this[self])
        filename = '%s.css' % hashlib.sha1(new).hexdigest()
        filepath = os.path.join(DIR, filename)
        if not os.path.exists(filepath):
            f = open(filepath, 'w')
            f.write(new)
            f.close()
        fileurl = os.path.relpath(filepath, settings.MEDIA_ROOT)
        link = u'<link rel="stylesheet" href="%s%s" />' % (settings.MEDIA_URL, fileurl)
        return u'%s\n%s' % (link, result)
        
    def _handle_minified_data(self, tag, minified, this):
        """
        Remove the tag from the soup and append to the current list
        """
        this[self].append(minified)
        tag.extract()