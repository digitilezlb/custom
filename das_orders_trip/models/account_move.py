from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = "account.move"
    _order = 'sequence, id'

    is_delivered = fields.Boolean(default=False, string='Delivered')
    sequence = fields.Integer('Sequence', help="Used to order the 'All Operations' kanban view")
    sorting_inv = fields.Integer()
