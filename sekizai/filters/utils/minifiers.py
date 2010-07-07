from BeautifulSoup import BeautifulSoup
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from sekizai.filters.base import BaseFilter
from subprocess import Popen, PIPE

class Minifier(object):
    def __init__(self, command):
        self.command = command.split(' ')
        
    def __call__(self, data):
        p = Popen(self.command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout = p.communicate(data)[0]
        if p.returncode != 0:
            return data
        return stdout
    
    
class NullMinifier(object):
    def __call__(self, data):
        return data
    
    
class BaseMinifierFilter(BaseFilter):
    tag = None
    minifier = None
    restrictions = {
    }
    skip_in_debug = True
    
    def __init__(self):
        if self.tag is None:
            raise ImproperlyConfigured(
                "BaseMinifierFilters require the 'tag' property to be set"
            )
    
    def postprocess(self, data, namespace):
        """
        Minfiy the 
        """
        if self.minifier is None:
            return data
        if self.skip_in_debug and settings.DEBUG:
            return data
        this = {}
        return self._minify(data, this)
    
    def _minify(self, data, this):
        try:
            soup = BeautifulSoup(data)
        except: 
            return data
        for tag in soup.findAll(self.tag):
            self._handle_tag(tag, this)
        return unicode(soup)
            
    def _handle_tag(self, tag, this):
        for attr, checker in self.restrictions.items():
            if not checker(tag.get(attr)):
                continue
        data = u''.join(tag.contents)
        try:
            minified = self.minifier(data)
        except:
            return data
        self._handle_minified_data(tag, minified, this)
        
    def _handle_minified_data(self, tag, minified, this):
        new = BeautifulSoup('<%s>%s</%s>' % (self.tag, minified, self.tag)).find(self.tag)
        for key, val in tag.attrs:
            new[key] = val
        tag.replaceWith(new)