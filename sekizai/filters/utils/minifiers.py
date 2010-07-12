from BeautifulSoup import BeautifulSoup
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from sekizai.filters.base import BaseFilter
from subprocess import Popen, PIPE

class Minifier(object):
    """
    A class wrapping a command line tool to minify data
    """
    def __init__(self, command):
        self.command = command.split(' ')
        
    def __call__(self, data):
        """
        Call the command with given data and return the output of the command if
        successful. Otherwise return the input data.
        """
        process = Popen(self.command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout = process.communicate(data)[0]
        if process.returncode != 0: # pragma: no cover 
            return data
        return stdout
    
    
class NullMinifier(object):
    """
    Dummy minifier class.
    """
    def __call__(self, data):
        return data
    
    
class BaseMinifierFilter(BaseFilter):
    """
    Base class for writing minifier filters.
    """
    tag = None
    minifier = None
    restrictions = {
    }
    debugskip_default = True
    
    def __init__(self, **configs):
        super(BaseMinifierFilter, self).__init__(**configs)
        if self.tag is None: # pragma: no cover 
            raise ImproperlyConfigured(
                "BaseMinifierFilters require the 'tag' property to be set"
            )
        self.debugskip = configs.get('skip_on_debug', self.debugskip_default)
    
    def postprocess(self, data, namespace):
        """
        Minfiy the contents
        """
        if self.minifier is None: # pragma: no cover 
            return data
        if self.debugskip and settings.DEBUG: # pragma: no cover 
            return data
        this = {}
        return self._minify(data, this)
    
    def _minify(self, data, this):
        """
        Run the actual minification if possible.
        """
        try:
            soup = BeautifulSoup(data)
        except: # pragma: no cover 
            return data
        for tag in soup.findAll(self.tag):
            self._handle_tag(tag, this)
        return unicode(soup)
            
    def _handle_tag(self, tag, this):
        """
        Handle a single tag which should be minified.
        """
        for attr, checker in self.restrictions.items():
            if not checker(tag.get(attr)):
                continue
        data = u''.join(tag.contents)
        try:
            minified = self.minifier(data)
        except: # pragma: no cover 
            return data
        self._handle_minified_data(tag, minified, this)
        
    def _handle_minified_data(self, tag, minified, this):
        """
        Handle the minified data of a tag.
        """
        soup = BeautifulSoup('<%s>%s</%s>' % (self.tag, minified, self.tag))
        new = soup.find(self.tag)
        for key, val in tag.attrs:
            new[key] = val
        tag.replaceWith(new)