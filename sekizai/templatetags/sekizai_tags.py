from classytags.arguments import Argument
from classytags.core import Tag, Options
from classytags.parser import Parser
from django import template
from django.conf import settings
from django.utils.importlib import import_module

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
    if getattr(settings, 'SEKIZAI_VARNAME', 'SEKIZAI_CONTENT_HOLDER') in context:
        return True
    if not settings.TEMPLATE_DEBUG:
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
        varname = getattr(settings, 'SEKIZAI_VARNAME', 'SEKIZAI_CONTENT_HOLDER')
        data = context[varname][name].render()
        if postprocessor:
            func = import_processor(postprocessor)
            data = func(context, data, name)
        return '%s\n%s' % (data, rendered_contents)
register.tag(RenderBlock)


class AddData(SekizaiTag):
    name = 'add_data'
    
    options = Options(
        Argument('key'),
        Argument('value'),
    )
    
    def render_tag(self, context, key, value):
        varname = getattr(settings, 'SEKIZAI_VARNAME', 'SEKIZAI_CONTENT_HOLDER')
        context[varname][key].append(value)
        return ''
register.tag(AddData)


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
        varname = getattr(settings, 'SEKIZAI_VARNAME', 'SEKIZAI_CONTENT_HOLDER')
        data = context[varname][name]
        context.push()
        context[variable] = data
        inner_contents = inner_nodelist.render(context)
        context.pop()
        return '%s\n%s' % (inner_contents, rendered_contents)
register.tag(WithData)


class Addtoblock(SekizaiTag):
    name = 'addtoblock'
    
    options = Options(
        Argument('name'),
        parser_class=AddtoblockParser,
    )
    
    def render_tag(self, context, name, nodelist):
        rendered_contents = nodelist.render(context)
        varname = getattr(settings, 'SEKIZAI_VARNAME', 'SEKIZAI_CONTENT_HOLDER')
        context[varname][name].append(rendered_contents)
        return ""
register.tag(Addtoblock)
