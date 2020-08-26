from importlib import import_module

from django import template

from classytags.arguments import Argument, Flag
from classytags.core import Options, Tag
from classytags.parser import Parser

from sekizai.helpers import get_varname


register = template.Library()


def validate_context(context):
    """
    Validates a given context.

    Returns True if the context is valid.

    Returns False if the context is invalid but the error should be silently
    ignored.

    Raises a TemplateSyntaxError if the context is invalid and we're in debug
    mode.
    """
    try:
        template_debug = context.template.engine.debug
    except AttributeError:
        # Get the default engine debug value
        template_debug = template.Engine.get_default().debug

    if get_varname() in context:
        return True
    if not template_debug:
        return False
    raise template.TemplateSyntaxError(
        "You must enable the 'sekizai.context_processors.sekizai' template "
        "context processor or use 'sekizai.context.SekizaiContext' to "
        "render your templates."
    )


def import_processor(import_path):
    if '.' not in import_path:
        raise TypeError("Import paths must contain at least one '.'")
    module_name, object_name = import_path.rsplit('.', 1)
    module = import_module(module_name)
    return getattr(module, object_name)


class SekizaiParser(Parser):
    def parse_blocks(self):
        super(SekizaiParser, self).parse_blocks()
        self.blocks['nodelist'] = self.parser.parse()


class AddtoblockParser(Parser):
    def parse_blocks(self):
        name = self.kwargs['name'].var.token
        self.blocks['nodelist'] = self.parser.parse(
            ('endaddtoblock', 'endaddtoblock %s' % name)
        )
        self.parser.delete_first_token()


class SekizaiTag(Tag):
    def render(self, context):
        if validate_context(context):
            return super(SekizaiTag, self).render(context)
        return ''


class RenderBlock(Tag):
    name = 'render_block'

    options = Options(
        Argument('name'),
        'postprocessor',
        Argument('postprocessor', required=False, default=None, resolve=False),
        parser_class=SekizaiParser,
    )

    def render_tag(self, context, name, postprocessor, nodelist):
        if not validate_context(context):
            return nodelist.render(context)
        rendered_contents = nodelist.render(context)
        varname = get_varname()
        data = '\n'.join(context[varname][name])
        if postprocessor:
            func = import_processor(postprocessor)
            data = func(context, data, name)
        return '%s\n%s' % (data, rendered_contents)


register.tag('render_block', RenderBlock)


class AddData(SekizaiTag):
    name = 'add_data'

    options = Options(
        Argument('key'),
        Argument('value'),
    )

    def render_tag(self, context, key, value):
        varname = get_varname()
        context[varname][key].append(value)
        return ''


register.tag('add_data', AddData)


class WithData(SekizaiTag):
    name = 'with_data'

    options = Options(
        Argument('name'),
        'as',
        Argument('variable', resolve=False),
        blocks=[
            ('end_with_data', 'inner_nodelist'),
        ],
        parser_class=SekizaiParser,
    )

    def render_tag(self, context, name, variable, inner_nodelist, nodelist):
        rendered_contents = nodelist.render(context)
        varname = get_varname()
        data = context[varname][name]
        context.push()
        context[variable] = data
        inner_contents = inner_nodelist.render(context)
        context.pop()
        return '%s\n%s' % (inner_contents, rendered_contents)


register.tag('with_data', WithData)


class Addtoblock(SekizaiTag):
    name = 'addtoblock'

    options = Options(
        Argument('name'),
        Flag('strip', default=False, true_values=['strip']),
        'preprocessor',
        Argument('preprocessor', required=False, default=None, resolve=False),
        parser_class=AddtoblockParser,
    )

    def render_tag(self, context, name, strip, preprocessor, nodelist):
        rendered_contents = nodelist.render(context)
        if strip:
            rendered_contents = rendered_contents.strip()
        if preprocessor:
            func = import_processor(preprocessor)
            rendered_contents = func(context, rendered_contents, name)
        varname = get_varname()
        context[varname][name].append(rendered_contents)
        return ""


register.tag('addtoblock', Addtoblock)
