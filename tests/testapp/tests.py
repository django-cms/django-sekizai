from unittest import TestCase
from django.template.loader import render_to_string

class TestTestCase(TestCase):
    def _test(self, tpl, res, ctx={}):
        rendered = render_to_string(tpl, ctx)
        bits = [bit for bit in [bit.strip('\n') for bit in rendered.split('\n')] if bit]
        self.assertEqual(bits, res)
        return rendered
        
    def test_01_base(self):
        self._test('insert_base.html', ['my css file', 'my other css file', 'hello world'])

    def test_02_dual(self):
        self._test('dual_insert.html', ['my css file', 'my js file', 'hello world'])