from BeautifulSoup import BeautifulSoup
from django.conf import settings
from sekizai.filters.utils.minifiers import BaseMinifierFilter, Minifier, \
    NullMinifier
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
        
        
class CSSSingleFileFilter(BaseMinifierFilter):
    tag = 'link'
    minifier = NullMinifier()
    restrictions = {
        'rel': lambda x: x == 'stylesheet',
        'href': lambda x: bool(x),
    }
    
    def _minify(self, data, this):
        this[self] = []
        result = super(CSSSingleFileFilter, self)._minify(data, this)
        # create the css file
        files = this[self]
        hashbase = ''.join(files)
        filename = '%s.css' % hashlib.sha1(hashbase).hexdigest()
        filepath = os.path.join(DIR, filename)
        if not os.path.exists(filepath):
            self._build(files, filepath)
        fileurl = os.path.relpath(filepath, settings.MEDIA_ROOT)
        link = u'<link rel="stylesheet" href="%s%s" />' % (settings.MEDIA_URL, fileurl)
        return u'%s\n%s' % (link, result)
    
    def _handle_tag(self, tag, this):
        for attr, checker in self.restrictions.items():
            if not checker(tag.get(attr)):
                continue
        href = tag.get('href')
        this[self].append(href)
        tag.extract()
        
    def _build(self, files, filepath):
        data = []
        for file in files:
            fpath = os.path.join(settings.MEDIA_ROOT, os.path.relpath(file, settings.MEDIA_URL))
            f = open(fpath, 'r')
            data.append(f.read())
            f.close()
        f = open(filepath, 'w')
        f.write('\n'.join(data))
        f.close()
            