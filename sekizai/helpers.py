# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import TextNode, VariableNode, NodeList, Variable
from django.template.loader import get_template
from django.template.loader_tags import BlockNode, ExtendsNode
from sekizai.templatetags.sekizai_tags import RenderBlock


def is_variable_extend_node(node):
    if hasattr(node, 'parent_name_expr') and node.parent_name_expr:
        return True
    if hasattr(node, 'parent_name') and hasattr(node.parent_name, 'filters'):
        if node.parent_name.filters or isinstance(node.parent_name.var, Variable):
            return True
    return False

def _extend_blocks(extend_node, blocks):
    """
    Extends the dictionary `blocks` with *new* blocks in the parent node (recursive)
    """
    # we don't support variable extensions
    if is_variable_extend_node(extend_node):
        return
    parent = extend_node.get_parent(None)
    # Search for new blocks
    for node in parent.nodelist.get_nodes_by_type(BlockNode):
        if not node.name in blocks:
            blocks[node.name] = node
        else:
            # set this node as the super node (for {{ block.super }})
            block = blocks[node.name]
            seen_supers = []
            while hasattr(block.super, 'nodelist') and block.super not in seen_supers:
                seen_supers.append(block.super)
                block = block.super
            block.super = node
    # search for further ExtendsNodes
    for node in parent.nodelist.get_nodes_by_type(ExtendsNode):
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
        found += _scan_namespaces(block.nodelist, block, blocks.keys())

    parent_template = extend_node.get_parent({})
    # if this is the topmost template, check for namespaces outside of blocks
    if not parent_template.nodelist.get_nodes_by_type(ExtendsNode):
        found += _scan_namespaces(parent_template.nodelist, None, blocks.keys())
    else:
        found += _scan_namespaces(parent_template.nodelist, extend_node, blocks.keys())
    return found

def _scan_namespaces(nodelist, current_block=None, ignore_blocks=None):
    if ignore_blocks is None:
        ignore_blocks = []
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
                    found += _scan_namespaces(current_block.super.nodelist, current_block.super)
    return found

def get_namespaces(template):
    compiled_template = get_template(template)
    return _scan_namespaces(compiled_template.nodelist)

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

