from difflib import SequenceMatcher
from django.template.loader import render_to_string
from sekizai.context import SekizaiContext
from unittest import TestCase


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
    def _test(self, tpl, res, ctx={}):
        """
        Helper method to render template and compare it's bits
        """
        rendered = render_to_string(tpl, SekizaiContext(ctx))
        bits = [bit for bit in [bit.strip('\n') for bit in rendered.split('\n')] if bit]
        differ = BitDiff(res)
        result = differ.test(bits)
        self.assertTrue(result.status, result.message)
        return rendered
        
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
        self.assertRaises(AssertionError, render_to_string, 'basic.html', {})
        
    def test_05_template_inheritance(self):
        """
        Test that (complex) template inheritances work properly
        """
        bits = ["head start", "some css file", "head end", "include start",
                "inc add js", "include end", "block main start", "extinc",
                "block main end", "body pre-end", "inc js file", "body end"]
        self._test("inherit/extend.html", bits)