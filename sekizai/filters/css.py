from django.conf import settings
from sekizai.filters.utils.minifiers import BaseMinifierFilter, Minifier, \
    NullMinifier
import hashlib
import os


COMMAND = getattr(settings, 'SEKIZAI_CSS_MINIFIER_COMMAND', None)
DEFAULT_DIR = os.path.join(settings.MEDIA_ROOT, 'sekizai_css_minifier/')
DIR = getattr(settings, 'SEKIZAI_CSS_MINIFIER_DIR', DEFAULT_DIR)

if not os.path.exists(DIR): # pragma: no cover 
    os.makedirs(DIR)
    
def media_url_to_filepath(url):
    """
    Convert a media url to a (absolute) file path
    """
    rel_path = url.lstrip('/')
    project_dir = os.path.join(settings.MEDIA_ROOT, '../')
    return os.path.abspath(os.path.join(project_dir, rel_path))

class CSSInlineToFileFilter(BaseMinifierFilter):
    """
    Filter which turns inline CSS into an external css file and optionally 
    minifies that CSS.
    """
    tag = 'style'
    minifier = Minifier(COMMAND) if COMMAND else NullMinifier()
    restrictions = {
        'type': lambda x: x == 'text/css',
    }
    
    def _minify(self, data, this):
        """
        Make sure we actually have to do anything by checking sha1 hashes.
        """
        this[self] = []
        result = super(CSSInlineToFileFilter, self)._minify(data, this)
        # create the css file
        new = '\n'.join(this[self])
        filename = '%s.css' % hashlib.sha1(new).hexdigest()
        filepath = os.path.join(DIR, filename)
        if not os.path.exists(filepath):
            fhandler = open(filepath, 'w')
            fhandler.write(new)
            fhandler.close()
        fileurl = os.path.relpath(filepath, settings.MEDIA_ROOT)
        data = (settings.MEDIA_URL, fileurl)
        link = u'<link rel="stylesheet" href="%s%s" />' % data
        return u'%s\n%s' % (link, result)
        
    def _handle_minified_data(self, tag, minified, this):
        """
        Remove the tag from the soup and append to the current list
        """
        this[self].append(minified)
        tag.extract()
        
        
class CSSSingleFileFilter(BaseMinifierFilter):
    """
    Compress multiple external CSS files into a single one
    """
    tag = 'link'
    minifier = NullMinifier()
    restrictions = {
        'rel': lambda x: x == 'stylesheet',
        'href': bool,
    }
    
    def _minify(self, data, this):
        this[self] = []
        result = super(CSSSingleFileFilter, self)._minify(data, this)
        # create the css file
        files = this[self]
        hashbase = ''.join(files)
        filename = '%s.css' % hashlib.sha1(hashbase).hexdigest()
        filepath = os.path.join(DIR, filename)
        if (not os.path.exists(filepath)) or self._check_dates(filepath, files):
            self._build(files, filepath)
        fileurl = os.path.relpath(filepath, settings.MEDIA_ROOT)
        data = (settings.MEDIA_URL, fileurl)
        link = u'<link rel="stylesheet" href="%s%s" />' % data
        return u'%s\n%s' % (link, result)
    
    def _handle_tag(self, tag, this):
        for attr, checker in self.restrictions.items():
            if not checker(tag.get(attr)): # pragma: no cover 
                return
        href = tag.get('href')
        this[self].append(href)
        tag.extract()
        
    def _build(self, files, filepath):
        data = []
        for filename in files:
            relfile = os.path.relpath(filename, settings.MEDIA_URL)
            fpath = os.path.join(settings.MEDIA_ROOT, relfile)
            fhandler = open(fpath, 'r')
            data.append(fhandler.read())
            fhandler.close()
        fhandler = open(filepath, 'w')
        fhandler.write('\n'.join(data))
        fhandler.close()
            
    def _check_dates(self, master, files):
        """
        Check modification times of files involved here and make sure the master
        file get's rebuilt if any other file is newer.
        """
        mtime = os.path.getmtime(master)
        for fname in files:
            fpath = media_url_to_filepath(fname)
            if os.path.getmtime(fpath) >= mtime:
                return True
        return False