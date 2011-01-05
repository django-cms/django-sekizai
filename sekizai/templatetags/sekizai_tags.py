from classytags.arguments import Argument
from classytags.core import Tag, Options
from classytags.parser import Parser
from django import template
from sekizai.settings import VARNAME

register = template.Library()

CONTEXT_PROCESSOR_ERROR_MESSAGE = (
    "You must enable the 'sekizai.context_processor.sekizai' template context "
    "processor or 'sekizai.context.SekizaiContext' to render your templates.")


class SekizaiParser(Parser):
    def parse_blocks(self):
        super(SekizaiParser, self).parse_blocks()
        self.blocks['nodelist'] = self.parser.parse()


class RenderBlock(Tag):
    name = 'render_block'
    
    options = Options(
        Argument('name'),
        parser_class=SekizaiParser,
    )

    @property
    def nodelist(self):
        return self.blocks['nodelist']
        
    def render_tag(self, context, name, nodelist):
        assert VARNAME in context, CONTEXT_PROCESSOR_ERROR_MESSAGE
        rendered_contents = nodelist.render(context)
        data = context[VARNAME][name].render()
        return '%s\n%s' % (data, rendered_contents)
register.tag(RenderBlock)


class AddData(Tag):
    name = 'add_data'
    
    options = Options(
        Argument('key'),
        Argument('value'),
    )
    
    def render_tag(self, context, key, value):
        assert VARNAME in context, CONTEXT_PROCESSOR_ERROR_MESSAGE
        context[VARNAME][key].append(value)
        return ''
register.tag(AddData)


class WithData(Tag):
    name = 'with_data'
    
    options = Options(
        Argument('name'),
        'as', 
        Argument('varname', resolve=False),
        blocks=[
            ('end_with_data', 'inner_nodelist'),
        ],
        parser_class=SekizaiParser,
    )
    
    def render_tag(self, context, name, varname, inner_nodelist, nodelist):
        assert VARNAME in context, CONTEXT_PROCESSOR_ERROR_MESSAGE
        rendered_contents = nodelist.render(context)
        data = context[VARNAME][name]
        context.push()
        context[varname] = data
        inner_contents = inner_nodelist.render(context)
        context.pop()
        return '%s\n%s' % (inner_contents, rendered_contents)
register.tag(WithData)


class AddToBlockNode(template.Node):    
    def __init__(self, nodelist, name):
        self.nodelist = nodelist
        self.name = name
        
    def render(self, context):
        assert VARNAME in context, CONTEXT_PROCESSOR_ERROR_MESSAGE
        rendered_contents = self.nodelist.render(context)
        name = self.name.resolve(context)
        context[VARNAME][name].append(rendered_contents)
        return ""

@register.tag
def addtoblock(parser, token):
    """
    {% addtoblock <name> %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError(
            "The 'addtoblock' tag requires one argument"
        )
    name = parser.compile_filter(bits[1])
    nodelist = parser.parse(('endaddtoblock', 'endaddtoblock %s' % name))
    parser.delete_first_token()
    return AddToBlockNode(nodelist, name)