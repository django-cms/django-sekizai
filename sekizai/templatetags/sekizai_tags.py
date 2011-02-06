from classytags.arguments import Argument
from classytags.core import Tag, Options
from classytags.parser import Parser
from django import template
from django.conf import settings
from sekizai.data import get_content_holder

register = template.Library()


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
        rendered_contents = nodelist.render(context)
        data = get_content_holder()[name].render()
        return '%s\n%s' % (data, rendered_contents)
register.tag(RenderBlock)


class AddData(Tag):
    name = 'add_data'
    
    options = Options(
        Argument('key'),
        Argument('value'),
    )
    
    def render_tag(self, context, key, value):
        content_holder = get_content_holder()
        content_holder[key].append(value)
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
        rendered_contents = nodelist.render(context)
        data = get_content_holder()[name]
        context.push()
        context[varname] = data
        inner_contents = inner_nodelist.render(context)
        context.pop()
        return '%s\n%s' % (inner_contents, rendered_contents)
register.tag(WithData)


class Addtoblock(Tag):
    name = 'addtoblock'

    options = Options(
        Argument('name'),
        parser_class=AddtoblockParser,
    )
    
    def render_tag(self, context, name, nodelist):
        rendered_contents = nodelist.render(context)
        content_holder = get_content_holder()
        content_holder[name].append(rendered_contents)
        return ""
register.tag(Addtoblock)
