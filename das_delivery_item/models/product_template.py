from odoo import api, fields, models, exceptions


class ProductTemplate(models.Model):
    _inherit = 'product.template'



    is_delivery = fields.Boolean(string="Delivery Item", default=False, store=True)

    def unlink(self):
        for asset in self:
            if asset.is_delivery:
                raise exceptions.UserError("You can't delete this product")
        return super(ProductTemplate, self).unlink()

    # def unlink(self):
    #     for asset in self:
    #         if asset.state in ['open', 'close']:
    #             raise UserError(_('You cannot delete a document that is in %s state.') % (asset.state,))
    #         for depreciation_line in asset.depreciation_line_ids:
    #             if depreciation_line.move_id:
    #                 raise UserError(_('You cannot delete a document that contains posted entries.'))
    #     return super(AccountAssetAsset, self).unlink()
