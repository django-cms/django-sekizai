from __future__ import with_statement
from difflib import SequenceMatcher
from django import template
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.template.base import TemplateDoesNotExist
from django.utils.decorators import method_decorator

from sekizai.context import SekizaiContext
from sekizai.helpers import validate_template, get_namespaces
from sekizai.templatetags.sekizai_tags import (validate_context, 
    import_processor)

from unittest import TestCase

try:
  from unittest import skipUnless
except ImportError:
  from django.utils.unittest.case import skipUnless

try:
    unicode_compat = unicode
except NameError:
    unicode_compat = str


def null_processor(context, data, namespace):
    return ''

def namespace_processor(context, data, namespace):
    return namespace

try:
    get_template("sekizai/tests/basic.html")
    test_templates_exists = True
except TemplateDoesNotExist:
    test_templates_exists = False

def test_template_exists(func):
    def wrap(template_file, *args, **kwargs):
        return skipUnless(
            test_templates_exists,
            "No test templates found {0}".format(template_file)
        )(func)(template_file, *args, **kwargs)
    return wrap

@test_template_exists
def validate_test_template(*args, **kwargs):
    return validate_template(*args, **kwargs)

@test_template_exists
def get_test_namespaces(*args, **kwargs):
    return get_namespaces(*args, **kwargs)

class SettingsOverride(object):
    """
    Overrides Django settings within a context and resets them to their inital
    values on exit.
    
    Example:
    
        with SettingsOverride(DEBUG=True):
            # do something
    """
    class NULL: pass
    
    def __init__(self, **overrides):
        self.overrides = overrides
        
    def __enter__(self):
        self.old = {}
        for key, value in self.overrides.items():
            self.old[key] = getattr(settings, key, self.NULL)
            setattr(settings, key, value)
        
    def __exit__(self, type, value, traceback):
        for key, value in self.old.items():
            if value is self.NULL:
                delattr(settings, key)
            else:
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
        self.expected = [repr(unicode_compat(bit)) for bit in expected]
        
    def test(self, result):
        result = [repr(unicode_compat(bit)) for bit in result]
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
            msg = '\nExpected{0} |   | Result'.format(padding)
            msg += '\n--------{0}-|---|-------{1}'.format(line1, line2)
            for success, a, b in data:
                pad = ' ' * (longest - len(a))
                if success:
                    msg += '\n{0}{1} |   | {2}'.format(a, pad, b)
                else:
                    msg += '\n{0}{1} | ! | {2}'.format(a, pad, b)
            return BitDiffResult(False, msg)


class SekizaiTestCase(TestCase):

    @method_decorator(test_template_exists)
    def _render(self, tpl, ctx={}, ctxclass=SekizaiContext):
        return render_to_string(tpl, ctxclass(ctx))
    
    @method_decorator(test_template_exists)
    def _get_bits(self, tpl, ctx={}, ctxclass=SekizaiContext):
        rendered = self._render(tpl, ctx, ctxclass)
        bits = [bit for bit in [bit.strip('\n') for bit in rendered.split('\n')] if bit]
        return bits, rendered
    
    @method_decorator(test_template_exists)
    def _test(self, tpl, res, ctx={}, ctxclass=SekizaiContext):
        """
        Helper method to render template and compare it's bits
        """
        bits, rendered = self._get_bits(tpl, ctx, ctxclass)
        differ = BitDiff(res)
        result = differ.test(bits)
        self.assertTrue(result.status, result.message)
        return rendered
        
    def test_basic_dual_block(self):
        """
        Basic dual block testing
        """
        bits = ['my css file', 'some content', 'more content', 
            'final content', 'my js file']
        self._test('sekizai/tests/basic.html', bits)

    def test_named_endaddtoblock(self):
        """
        Testing with named endaddblock
        """
        bits = ["mycontent"]
        self._test('sekizai/tests/named_end.html', bits)

    def test_eat_content_before_render_block(self):
        """
        Testing that content get's eaten if no render_blocks is available
        """
        bits = ["mycontent"]
        self._test("sekizai/tests/eat.html", bits)
        
    def test_sekizai_context_required(self):
        """
        Test that the template tags properly fail if not used with either 
        SekizaiContext or the context processor.
        """
        self.assertRaises(template.TemplateSyntaxError, self._render, 'sekizai/tests/basic.html', {}, template.Context)
        
    def test_complex_template_inheritance(self):
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
        self._test("sekizai/tests/inherit/extend.html", bits)
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
        self._test("sekizai/tests/inherit/super_blocks.html", bits)
        
    def test_namespace_isolation(self):
        """
        Tests that namespace isolation works
        """
        bits = ["the same file", "the same file"]
        self._test('sekizai/tests/namespaces.html', bits)
        
    def test_variable_namespaces(self):
        """
        Tests variables and filtered variables as block names.
        """
        bits = ["file one", "file two"]
        self._test('sekizai/tests/variables.html', bits, {'blockname': 'one'})

    def test_invalid_addtoblock(self):
        """
        Tests that template syntax errors are raised properly in templates
        rendered by sekizai tags
        """
        self.assertRaises(template.TemplateSyntaxError, self._render, 'sekizai/tests/errors/failadd.html')
    
    def test_invalid_renderblock(self):
        self.assertRaises(template.TemplateSyntaxError, self._render, 'sekizai/tests/errors/failrender.html')
    
    def test_invalid_include(self):
        self.assertRaises(template.TemplateSyntaxError, self._render, 'sekizai/tests/errors/failinc.html')
        
    def test_invalid_basetemplate(self):
        self.assertRaises(template.TemplateSyntaxError, self._render, 'sekizai/tests/errors/failbase.html')
        
    def test_invalid_basetemplate_two(self):
        self.assertRaises(template.TemplateSyntaxError, self._render, 'sekizai/tests/errors/failbase2.html')
        
    def test_with_data(self):
        """
        Tests the with_data/add_data tags.
        """
        bits = ["1", "2"]
        self._test('sekizai/tests/with_data.html', bits)
        
    def test_easy_inheritance(self):
        self.assertEqual('content', self._render("sekizai/tests/easy_inherit.html").strip())
        
    def test_validate_context(self):
        sekizai_ctx = SekizaiContext()
        django_ctx = template.Context()
        self.assertRaises(template.TemplateSyntaxError, validate_context, django_ctx)
        self.assertEqual(validate_context(sekizai_ctx), True)
        with SettingsOverride(TEMPLATE_DEBUG=False):
            self.assertEqual(validate_context(django_ctx), False)
            self.assertEqual(validate_context(sekizai_ctx), True)
            bits = ['some content', 'more content', 'final content']
            self._test('sekizai/tests/basic.html', bits, ctxclass=template.Context)
            
    def test_post_processor_null(self):
        bits = ['header', 'footer']
        self._test('sekizai/tests/processors/null.html', bits)
            
    def test_post_processor_namespace(self):
        bits = ['header', 'footer', 'js']
        self._test('sekizai/tests/processors/namespace.html', bits)
        
    def test_import_processor_failfast(self):
        self.assertRaises(TypeError, import_processor, 'invalidpath')
        
    def test_unique(self):
        bits = ['unique data']
        self._test('sekizai/tests/unique.html', bits)


class HelperTests(TestCase):
    def test_validate_template_js_css(self):
        self.assertTrue(validate_test_template('sekizai/tests/basic.html', ['js', 'css']))
    
    def test_validate_template_js(self):
        self.assertTrue(validate_test_template('sekizai/tests/basic.html', ['js']))
        
    def test_validate_template_css(self):
        self.assertTrue(validate_test_template('sekizai/tests/basic.html', ['css']))
        
    def test_validate_template_empty(self):
        self.assertTrue(validate_test_template('sekizai/tests/basic.html', []))
        
    def test_validate_template_notfound(self):
        self.assertFalse(validate_test_template('sekizai/tests/basic.html', ['notfound']))

    def test_get_namespaces_easy_inherit(self):
        self.assertEqual(get_test_namespaces('sekizai/tests/easy_inherit.html'), ['css'])

    def test_get_namespaces_chain_inherit(self):
        self.assertEqual(get_test_namespaces('sekizai/tests/inherit/chain.html'), ['css', 'js'])

    def test_get_namespaces_space_chain_inherit(self):
        self.assertEqual(get_test_namespaces('sekizai/tests/inherit/spacechain.html'), ['css', 'js'])

    def test_get_namespaces_var_inherit(self):
        self.assertEqual(get_test_namespaces('sekizai/tests/inherit/varchain.html'), [])

    def test_get_namespaces_sub_var_inherit(self):
        self.assertEqual(get_test_namespaces('sekizai/tests/inherit/subvarchain.html'), [])

    def test_get_namespaces_null_ext(self):
        self.assertEqual(get_test_namespaces('sekizai/tests/inherit/nullext.html'), [])
        
    def test_deactivate_validate_template(self):
        with SettingsOverride(SEKIZAI_IGNORE_VALIDATION=True):
            self.assertTrue(validate_test_template('sekizai/tests/basic.html', ['js', 'css']))
            self.assertTrue(validate_test_template('sekizai/tests/basic.html', ['js']))
            self.assertTrue(validate_test_template('sekizai/tests/basic.html', ['css']))
            self.assertTrue(validate_test_template('sekizai/tests/basic.html', []))
            self.assertTrue(validate_test_template('sekizai/tests/basic.html', ['notfound']))
