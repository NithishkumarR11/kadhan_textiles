from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    kadhan_hsn_code = fields.Char(string="HSN/SAC Code")
