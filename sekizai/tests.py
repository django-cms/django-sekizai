from __future__ import with_statement
from difflib import SequenceMatcher
from django import template
from django.conf import settings
from django.template.loader import render_to_string
from sekizai.context import SekizaiContext
from sekizai.helpers import validate_template, get_namespaces
from sekizai.templatetags.sekizai_tags import validate_context
from unittest import TestCase


class SettingsOverride(object):
    """
    Overrides Django settings within a context and resets them to their inital
    values on exit.
    
    Example:
    
        with SettingsOverride(DEBUG=True):
            # do something
    """
    def __init__(self, **overrides):
        self.overrides = overrides
        
    def __enter__(self):
        self.old = {}
        for key, value in self.overrides.items():
            self.old[key] = getattr(settings, key)
            setattr(settings, key, value)
        
    def __exit__(self, type, value, traceback):
        for key, value in self.old.items():
            setattr(settings, key, value)


class Match(tuple): # pragma: no cover
    @property
    def a(self):
        return self[0]
    
    @property
    def b(self):
        return self[1]
    
    @property
    def size(self):
        return self[2]


def _backwards_compat_match(thing): # pragma: no cover
    if isinstance(thing, tuple):
        return Match(thing)
    return thing

class BitDiffResult(object):
    def __init__(self, status, message):
        self.status = status
        self.message = message


class BitDiff(object):
    """
    Visual aid for failing tests
    """
    def __init__(self, expected):
        self.expected = [repr(unicode(bit)) for bit in expected]
        
    def test(self, result):
        result = [repr(unicode(bit)) for bit in result]
        if self.expected == result:
            return BitDiffResult(True, "success")
        else: # pragma: no cover
            longest = max([len(x) for x in self.expected] + [len(x) for x in result] + [len('Expected')])
            sm = SequenceMatcher()
            sm.set_seqs(self.expected, result)
            matches = sm.get_matching_blocks()
            lasta = 0
            lastb = 0
            data = []
            for match in [_backwards_compat_match(match) for match in matches]:
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


class SekizaiTestCase(TestCase):
    def _render(self, tpl, ctx={}, ctxclass=SekizaiContext):
        return render_to_string(tpl, ctxclass(ctx))
    
    def _get_bits(self, tpl, ctx={}, ctxclass=SekizaiContext):
        rendered = self._render(tpl, ctx, ctxclass)
        bits = [bit for bit in [bit.strip('\n') for bit in rendered.split('\n')] if bit]
        return bits, rendered
        
    def _test(self, tpl, res, ctx={}, ctxclass=SekizaiContext):
        """
        Helper method to render template and compare it's bits
        """
        bits, rendered = self._get_bits(tpl, ctx, ctxclass)
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
        self.assertRaises(template.TemplateSyntaxError, self._render, 'basic.html', {}, template.Context)
        
    def test_05_template_inheritance(self):
        """
        Test that (complex) template inheritances work properly
        """
        bits = [
            "head start",
            "some css file",
            "head end",
            "include start",
            "inc add js",
            "include end",
            "block main start",
            "extinc",
            "block main end",
            "body pre-end",
            "inc js file",
            "body end"
        ]
        self._test("inherit/extend.html", bits)
        """
        Test that blocks (and block.super) work properly with sekizai
        """
        bits = [
            "head start",
            "visible css file",
            "some css file",
            "head end",
            "include start",
            "inc add js",
            "include end",
            "block main start",
            "block main base contents",
            "more contents",
            "block main end",
            "body pre-end",
            "inc js file",
            "body end"
        ]
        self._test("inherit/super_blocks.html", bits)
        
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

    def test_09_template_errors(self):
        """
        Tests that template syntax errors are raised properly in templates
        rendered by sekizai tags
        """
        self.assertRaises(template.TemplateSyntaxError, self._render, 'errors/failadd.html')
        self.assertRaises(template.TemplateSyntaxError, self._render, 'errors/failrender.html')
        self.assertRaises(template.TemplateSyntaxError, self._render, 'errors/failinc.html')
        self.assertRaises(template.TemplateSyntaxError, self._render, 'errors/failbase.html')
        self.assertRaises(template.TemplateSyntaxError, self._render, 'errors/failbase2.html')
        
    def test_10_with_data(self):
        """
        Tests the with_data/add_data tags.
        """
        bits = ["1", "2"]
        self._test('with_data.html', bits)
        
    def test_11_easy_inherit(self):
        self.assertEqual('content', self._render("easy_inherit.html").strip())
        
    def test_12_validate_context(self):
        sekizai_ctx = SekizaiContext()
        django_ctx = template.Context()
        self.assertRaises(template.TemplateSyntaxError, validate_context, django_ctx)
        self.assertEqual(validate_context(sekizai_ctx), True)
        with SettingsOverride(TEMPLATE_DEBUG=False):
            self.assertEqual(validate_context(django_ctx), False)
            self.assertEqual(validate_context(sekizai_ctx), True)
            bits = ['some content', 'more content', 'final content']
            self._test('basic.html', bits, ctxclass=template.Context)


class HelperTests(TestCase):
    def test_validate_template(self):
        self.assertTrue(validate_template('basic.html', ['js', 'css']))
        self.assertTrue(validate_template('basic.html', ['js']))
        self.assertTrue(validate_template('basic.html', ['css']))
        self.assertTrue(validate_template('basic.html', []))
        self.assertFalse(validate_template('basic.html', ['notfound']))

    def test_get_namespaces(self):
        self.assertEqual(get_namespaces('easy_inherit.html'), ['css'])
        self.assertEqual(get_namespaces('inherit/chain.html'), ['css', 'js'])
        self.assertEqual(get_namespaces('inherit/spacechain.html'), ['css', 'js'])
        self.assertEqual(get_namespaces('inherit/varchain.html'), [])
        self.assertEqual(get_namespaces('inherit/subvarchain.html'), [])
        self.assertEqual(get_namespaces('inherit/nullext.html'), [])