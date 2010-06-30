from unittest import TestCase
from django.template import RequestContext
from django.template.loader import render_to_string

class TestTestCase(TestCase):
    def _test(self, tpl, res, ctx={}):
        rendered = render_to_string(tpl, ctx, RequestContext({}))
        bits = [bit for bit in [bit.strip('\n') for bit in rendered.split('\n')] if bit]
        self.assertEqual([unicode(b) for b in bits], [unicode(r) for r in res])
        return rendered
        
    def test_01_basic(self):
        bits = ['my css file', 'some content', 'more content', 
            'final content', 'my js file']
        self._test('basic.html', bits)

    def test_02_named_end(self):
        bits = ["mycontent"]
        self._test('named_end.html', bits)

    def test_03_eat(self):
        bits = ["mycontent"]
        self._test("eat.html", bits)