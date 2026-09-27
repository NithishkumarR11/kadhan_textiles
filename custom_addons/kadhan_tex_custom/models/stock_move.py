from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    kadhan_size = fields.Char(string="Size")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("kadhan_size") and vals.get("sale_line_id"):
                sale_line = self.env["sale.order.line"].browse(vals["sale_line_id"])
                vals["kadhan_size"] = sale_line.kadhan_size
        return super().create(vals_list)
