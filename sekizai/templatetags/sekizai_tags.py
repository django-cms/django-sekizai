from django import template
from sekizai.settings import VARNAME

register = template.Library()


class RenderBlockNode(template.Node):
    def __init__(self, nodelist, name):
        self.nodelist = nodelist
        self.name = name
        
    def render(self, context):
        assert VARNAME in context, "You must enable the sekizai template processor"
        rendered_contents = self.nodelist.render(context)
        name = self.name.resolve(context)
        data = '\n'.join(context[VARNAME][name])
        return '%s\n%s' % (data, rendered_contents)
    
    
class AddToBlockNode(template.Node):
    def __init__(self, nodelist, name):
        self.nodelist = nodelist
        self.name = name
        
    def render(self, context):
        assert VARNAME in context, "You must enable the sekizai template processor"
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
