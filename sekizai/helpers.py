# -*- coding: utf-8 -*-

from django.conf import settings
from django.template.base import VariableNode, Variable, Context, Template
from django.template.loader import get_template
from django.template.loader_tags import BlockNode, ExtendsNode


def _get_nodelist(tpl):
    if isinstance(tpl, Template):
        return tpl.nodelist
    else:
        return tpl.template.nodelist


def is_variable_extend_node(node):
    if hasattr(node, 'parent_name_expr') and node.parent_name_expr:
        return True
    if hasattr(node, 'parent_name') and hasattr(node.parent_name, 'filters'):
        if (node.parent_name.filters or
                isinstance(node.parent_name.var, Variable)):
            return True
    return False


def get_context():
    context = Context()
    context.template = Template('')
    return context


def _extend_blocks(extend_node, blocks):
    """
    Extends the dictionary `blocks` with *new* blocks in the parent node
    (recursive)
    """
    # we don't support variable extensions
    if is_variable_extend_node(extend_node):
        return
    parent = extend_node.get_parent(get_context())
    # Search for new blocks
    for node in _get_nodelist(parent).get_nodes_by_type(BlockNode):
        if node.name not in blocks:
            blocks[node.name] = node
        else:
            # set this node as the super node (for {{ block.super }})
            block = blocks[node.name]
            seen_supers = []
            while (hasattr(block.super, 'nodelist') and
                   block.super not in seen_supers):
                seen_supers.append(block.super)
                block = block.super
            block.super = node
    # search for further ExtendsNodes
    for node in _get_nodelist(parent).get_nodes_by_type(ExtendsNode):
        _extend_blocks(node, blocks)
        break


def _extend_nodelist(extend_node):
    """
    Returns a list of namespaces found in the parent template(s) of this
    ExtendsNode
    """
    # we don't support variable extensions (1.3 way)
    if is_variable_extend_node(extend_node):
        return []
    blocks = extend_node.blocks
    _extend_blocks(extend_node, blocks)
    found = []

    for block in blocks.values():
        found += _scan_namespaces(block.nodelist, block)

    parent_template = extend_node.get_parent(get_context())
    # if this is the topmost template, check for namespaces outside of blocks
    if not _get_nodelist(parent_template).get_nodes_by_type(ExtendsNode):
        found += _scan_namespaces(
            _get_nodelist(parent_template),
            None
        )
    else:
        found += _scan_namespaces(
            _get_nodelist(parent_template),
            extend_node
        )
    return found


def _scan_namespaces(nodelist, current_block=None):
    from sekizai.templatetags.sekizai_tags import RenderBlock
    found = []

    for node in nodelist:
        # check if this is RenderBlock node
        if isinstance(node, RenderBlock):
            # resolve it's name against a dummy context
            found.append(node.kwargs['name'].resolve({}))
            found += _scan_namespaces(node.blocks['nodelist'], node)
        # handle {% extends ... %} tags if check_inheritance is True
        elif isinstance(node, ExtendsNode):
            found += _extend_nodelist(node)
        # in block nodes we have to scan for super blocks
        elif isinstance(node, VariableNode) and current_block:
            if node.filter_expression.token == 'block.super':
                if hasattr(current_block.super, 'nodelist'):
                    found += _scan_namespaces(
                        current_block.super.nodelist,
                        current_block.super
                    )
    return found


def get_namespaces(template):
    compiled_template = get_template(template)
    return _scan_namespaces(_get_nodelist(compiled_template))


def validate_template(template, namespaces):
    """
    Validates that a template (or it's parents if check_inheritance is True)
    contain all given namespaces
    """
    if getattr(settings, 'SEKIZAI_IGNORE_VALIDATION', False):
        return True
    found = get_namespaces(template)
    for namespace in namespaces:
        if namespace not in found:
            return False
    return True


def get_varname():
    return getattr(settings, 'SEKIZAI_VARNAME', 'SEKIZAI_CONTENT_HOLDER')


class Watcher(object):
    """
    Watches a context for changes to the sekizai data, so it can be replayed
    later. This is useful for caching.

    NOTE: This class assumes you ONLY ADD, NEVER REMOVE data from the context!
    """
    def __init__(self, context):
        self.context = context
        self.frozen = dict(
            (key, list(value)) for key, value in self.data.items()
        )

    @property
    def data(self):
        return self.context.get(get_varname(), {})

    def get_changes(self):
        sfrozen = set(self.frozen)
        sdata = set(self.data)
        new_keys = sfrozen ^ sdata
        changes = {}
        for key in new_keys:
            changes[key] = list(self.data[key])
        shared_keys = sfrozen & sdata
        for key in shared_keys:
            old_set = set(self.frozen[key])
            new_values = [
                item for item in self.data[key] if item not in old_set
            ]
            changes[key] = new_values
        return changes
