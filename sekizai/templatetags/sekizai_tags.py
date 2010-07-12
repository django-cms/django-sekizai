from django import template
from sekizai.settings import VARNAME

register = template.Library()

CONTEXT_PROCESSOR_ERROR_MESSAGE = (
    "You must enable the 'sekizai.context_processor.sekizai' template context "
    "processor or 'sekizai.context.SekizaiContext' to render your templates.")


class RenderBlockNode(template.Node):
    def __init__(self, nodelist, name):
        self.nodelist = nodelist
        self.name = name
        
    def render(self, context):
        assert VARNAME in context, CONTEXT_PROCESSOR_ERROR_MESSAGE
        rendered_contents = self.nodelist.render(context)
        name = self.name.resolve(context)
        data = context[VARNAME][name].render()
        return '%s\n%s' % (data, rendered_contents)
    
    
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
def render_block(parser, token):
    """
    {% render_block <name> %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError(
            "The 'render_block' tag requires one argument"
        )
    name = parser.compile_filter(bits[1])
    nodelist = parser.parse()
    return RenderBlockNode(nodelist, name)

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
