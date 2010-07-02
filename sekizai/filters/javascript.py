from sekizai.filters.base import BaseFilter
from BeautifulSoup import BeautifulSoup
from django.conf import settings
from subprocess import Popen, PIPE
import sys

COMMAND = getattr(settings, 'SEKIZAI_JAVASCRIPT_MINIFIER_COMMAND', None)


class Minifier(object):
    def __init__(self, command):
        self.command = command.split(' ')
        
    def __call__(self, data):
        p = Popen(self.command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(data)
        if p.returncode != 0:
            print >>sys.stderr, stderr
            return data
        return stdout
    
MINIFIER = Minifier(COMMAND) if COMMAND else None

class JavascriptMinfier(BaseFilter):
    def postprocess(self, data, namespace):
        """
        Minfiy the 
        """
        if MINIFIER is None:
            return data
        try:
            soup = BeautifulSoup(data)
        except: 
            return data
        for js in soup.findAll('script'):
            if js.get('type') != 'text/javascript':
                continue
            if js.get('src'):
                continue
            data = u''.join(js.contents)
            try:
                minified = MINIFIER(data)
            except:
                continue
            new = BeautifulSoup('<script>%s</script>' % minified).find('script')
            for key, val in js.attrs:
                new[key] = val
            js.replaceWith(new)
        return unicode(soup)