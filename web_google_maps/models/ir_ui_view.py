# -*- coding: utf-8 -*-
# License AGPL-3
from lxml import etree
from odoo import fields, models, _
from odoo.addons.base.models.ir_ui_view import (
    safe_eval,
    transfer_field_to_modifiers,
)
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast
import collections
import datetime
import functools
import inspect
import json
import logging
import math
import pprint
import re
import time
import uuid
import warnings

from lxml import etree
from lxml.etree import LxmlError
from lxml.builder import E

import odoo
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.http import request
from odoo.modules.module import get_resource_from_path, get_resource_path
from odoo.tools import config, ConstantMapping, get_diff, pycompat, apply_inheritance_specs, locate_node, str2bool
from odoo.tools.convert import _fix_multiple_roots
from odoo.tools import safe_eval, lazy, lazy_property, frozendict
from odoo.tools.view_validation import valid_view, get_variable_names, get_domain_identifiers, get_dict_asts
from odoo.tools.translate import xml_translate, TRANSLATED_ATTRS
from odoo.models import check_method_name
from odoo.osv.expression import expression


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('google_map', 'Google Maps')])

    # FIXME: this is a deep copy of the original method
    # added 'google_map' as list of original views to be validated are hardcoded :/
    def _validate_tag_field(self, node, name_manager, node_info):
        validate = node_info['validate']

        name = node.get('name')
        if not name:
            self._raise_view_error(_("Field tag must have a \"name\" attribute defined"), node)

        field = name_manager.model._fields.get(name)
        if field:
            if validate and field.relational:
                domain = (
                        node.get('domain')
                        or node_info['editable'] and field._description_domain(self.env)
                )
                if isinstance(domain, str):
                    # dynamic domain: in [('foo', '=', bar)], field 'foo' must
                    # exist on the comodel and field 'bar' must be in the view
                    desc = (f'domain of <field name="{name}">' if node.get('domain')
                            else f"domain of field '{name}'")
                    fnames, vnames = self._get_domain_identifiers(node, domain, desc)
                    self._check_field_paths(node, fnames, field.comodel_name, f"{desc} ({domain})")
                    if vnames:
                        name_manager.must_have_fields(node, vnames, f"{desc} ({domain})")

            elif validate and node.get('domain'):
                msg = _(
                    'Domain on non-relational field "%(name)s" makes no sense (domain:%(domain)s)',
                    name=name, domain=node.get('domain'),
                )
                self._raise_view_error(msg, node)

            for child in node:
                if child.tag not in ('form', 'tree', 'graph', 'kanban', 'calendar','google_map'):
                    continue
                node.remove(child)
                sub_manager = self._validate_view(
                    child, field.comodel_name, editable=node_info['editable'], full=validate,
                )
                for fname, groups_uses in sub_manager.mandatory_parent_fields.items():
                    for groups, use in groups_uses.items():
                        name_manager.must_have_field(node, fname, use, groups=groups)

        elif validate and name not in name_manager.field_info:
            msg = _(
                'Field "%(field_name)s" does not exist in model "%(model_name)s"',
                field_name=name, model_name=name_manager.model._name,
            )
            self._raise_view_error(msg, node)

        name_manager.has_field(node, name, {'id': node.get('id'), 'select': node.get('select')})

        if validate:
            for attribute in ('invisible', 'readonly', 'required'):
                val = node.get(attribute)
                if val:
                    try:
                        # most (~95%) elements are 1/True/0/False
                        res = str2bool(val)
                    except ValueError:
                        res = safe_eval.safe_eval(val, {'context': self._context})
                    if res not in (1, 0, True, False, None):
                        msg = _(
                            'Attribute %(attribute)s evaluation expects a boolean, got %(value)s',
                            attribute=attribute, value=val,
                        )
                        self._raise_view_error(msg, node)

    # FIXME: this is a deep copy of the original method
    # added 'google_map' as list of original views to be validated are hardcoded :/
    def _postprocess_tag_field(self, node, name_manager, node_info):
        if node.get('name'):
            attrs = {'id': node.get('id'), 'select': node.get('select')}
            field = name_manager.model._fields.get(node.get('name'))
            if field:
                if field.groups:
                    if node.get('groups'):
                        node_t = E.t(groups=field.groups, postprocess_added='1')
                        node.getparent().replace(node, node_t)
                        node_t.append(node)
                    else:
                        node.set('groups', field.groups)
                if (
                        node_info.get('view_type') == 'form'
                        and field.type in ('one2many', 'many2many')
                        and not node.get('widget')
                        and not node.get('invisible')
                        and not name_manager.parent
                ):
                    # Embed kanban/tree/form views for visible x2many fields in form views
                    # if no widget or the widget requires it.
                    # So the web client doesn't have to call `get_views` for x2many fields not embedding their view
                    # in the main form view.
                    for arch, _view in self._get_x2many_missing_view_archs(field, node, node_info):
                        node.append(arch)

                for child in node:
                    if child.tag in ('form', 'tree', 'graph', 'kanban', 'calendar', 'google_map'):
                        node_info['children'] = []
                        self._postprocess_view(
                            child, field.comodel_name, editable=node_info['editable'], parent_name_manager=name_manager,
                        )
                if node_info['editable'] and field.type in ('many2one', 'many2many'):
                    node.set('model_access_rights', field.comodel_name)

            name_manager.has_field(node, node.get('name'), attrs)

            field_info = name_manager.field_info.get(node.get('name'))
            if field_info:
                transfer_field_to_modifiers(field_info, node_info['modifiers'], node_info['view_modifiers_from_model'])

