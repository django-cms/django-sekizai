from difflib import SequenceMatcher
from django import template
from django.conf import settings
from django.template.loader import render_to_string
from sekizai.context import SekizaiContext
from unittest import TestCase
import subprocess

def _is_installed(command):
    return subprocess.call(['which', command]) == 0

class BitDiffResult(object):
    def __init__(self, status, message):
        self.status = status
        self.message = message


class BitDiff(object):
    def __init__(self, expected):
        self.expected = [unicode(bit) for bit in expected]
        
    def test(self, result):
        if self.expected == result:
            return BitDiffResult(True, "success")
        longest = max([len(x) for x in self.expected] + [len(x) for x in result] + [len('Expected')])
        sm = SequenceMatcher()
        sm.set_seqs(self.expected, result)
        matches = sm.get_matching_blocks()
        lasta = 0
        lastb = 0
        data = []
        for match in matches:
            unmatcheda = self.expected[lasta:match.a]
            unmatchedb = result[lastb:match.b]
            unmatchedlen = max([len(unmatcheda), len(unmatchedb)])
            unmatcheda += ['' for x in range(unmatchedlen)]
            unmatchedb += ['' for x in range(unmatchedlen)]
            for i in range(unmatchedlen):
                data.append((False, unmatcheda[i], unmatchedb[i]))
            for i in range(match.size):
                data.append((True, self.expected[match.a + i], result[match.b + i]))
            lasta = match.a + match.size
            lastb = match.b + match.size
        padlen = (longest - len('Expected'))
        padding = ' ' * padlen
        line1 = '-' * padlen
        line2 = '-' * (longest - len('Result'))
        msg = '\nExpected%s |   | Result' % padding
        msg += '\n--------%s-|---|-------%s' % (line1, line2)
        for success, a, b in data:
            pad = ' ' * (longest - len(a))
            if success:
                msg += '\n%s%s |   | %s' % (a, pad, b)
            else:
                msg += '\n%s%s | ! | %s' % (a, pad, b)
        return BitDiffResult(False, msg)


class TestTestCase(TestCase):
    def _render(self, tpl, ctx={}, ctxinstance=SekizaiContext):
        return render_to_string(tpl, ctxinstance(ctx))
        
    def _test(self, tpl, res, ctx={}):
        """
        Helper method to render template and compare it's bits
        """
        rendered = self._render(tpl, ctx)
        bits = [bit for bit in [bit.strip('\n') for bit in rendered.split('\n')] if bit]
        differ = BitDiff(res)
        result = differ.test(bits)
        self.assertTrue(result.status, result.message)
        return rendered
    
    def _load_filter(self, import_path, namespace):
        from sekizai.filters.base import Namespace, registry
        from sekizai.utils import load_filter
        filter_instance = load_filter(import_path)
        registry.namespaces[namespace] = Namespace(True, filter_instance)
        return registry, filter_instance
        
    def test_01_basic(self):
        """
        Basic dual block testing
        """
        bits = ['my css file', 'some content', 'more content', 
            'final content', 'my js file']
        self._test('basic.html', bits)

    def test_02_named_end(self):
        """
        Testing with named endaddblock
        """
        bits = ["mycontent"]
        self._test('named_end.html', bits)

    def test_03_eat(self):
        """
        Testing that content get's eaten if no render_blocks is available
        """
        bits = ["mycontent"]
        self._test("eat.html", bits)
        
    def test_04_fail(self):
        """
        Test that the template tags properly fail if not used with either 
        SekizaiContext or the context processor.
        """
        self.assertRaises(AssertionError, self._render, 'basic.html', {}, template.Context)
        
    def test_05_template_inheritance(self):
        """
        Test that (complex) template inheritances work properly
        """
        bits = ["head start", "some css file", "head end", "include start",
                "inc add js", "include end", "block main start", "extinc",
                "block main end", "body pre-end", "inc js file", "body end"]
        self._test("inherit/extend.html", bits)
        
    def test_06_namespace_isolation(self):
        """
        Tests that namespace isolation works
        """
        bits = ["the same file", "the same file"]
        self._test('namespaces.html', bits)
        
    def test_07_variable_namespaces(self):
        """
        Tests variables and filtered variables as block names.
        """
        bits = ["file one", "file two"]
        self._test('variables.html', bits, {'blockname': 'one'})
        
    def test_08_yui(self):
        if not _is_installed('yui-compressor'):
            return
        registry, filter_instance = self._load_filter('sekizai.filters.javascript.JavascriptMinfier', 'js')
        self.assertEqual(len(list(registry.get_filters('js'))), 2)
        js = """<script type='text/javascript'>var a = 1;

        var b = a + 2;</script>"""
        self.assertNotEqual(js, filter_instance().postprocess(js, 'js'))
        bits = ['<script type="text/javascript">var a=1;var b=a+2;</script>',
                '<script type="text/javascript" src="somefile.js"></script>']
        self._test('yui.html', bits)

    def test_09_template_errors(self):
        """
        Tests that template syntax errors are raised properly in templates
        rendered by sekizai tags
        """
        self.assertRaises(template.TemplateSyntaxError, self._render, 'errors/failinc.html')
        self.assertRaises(template.TemplateSyntaxError, self._render, 'errors/failbase.html')
        self.assertRaises(template.TemplateSyntaxError, self._render, 'errors/failbase2.html')

    def test_10_css_to_file(self):
        import hashlib
        from sekizai.filters.css import DIR
        import os
        filename = '%s.css' % hashlib.sha1('body { color: red; }').hexdigest()
        filepath = os.path.join(DIR, filename)
        fileurl = os.path.relpath(filepath, settings.MEDIA_ROOT)
        link = u'<link rel="stylesheet" href="%s%s" />' % (settings.MEDIA_URL, fileurl)
        registry, filter_instance = self._load_filter('sekizai.filters.css.CSSInlineToFileFilter', 'css-to-file')
        self.assertEqual(len(list(registry.get_filters('css-to-file'))), 2)
        css = '<style type="text/css">body { color: red; }</style>'
        self.assertNotEqual(css, filter_instance().postprocess(css, 'css-to-file'))
        self._test('css.html', [link])