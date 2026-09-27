from collections import OrderedDict

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_challan_product_summary(self):
        self.ensure_one()
        summary = OrderedDict()
        candidate_lines = self.move_ids.filtered(
            lambda line: line.product_id and not line.scrap_id
        )
        for move in candidate_lines:
            key = (move.product_id.id, move.kadhan_size or "")
            values = summary.setdefault(
                key,
                {
                    "product": move.product_id,
                    "hsn": move.product_id.product_tmpl_id.kadhan_hsn_code or "",
                    "size": move.kadhan_size or "",
                    "qty": 0.0,
                    "uom": move.product_uom,
                },
            )
            values["qty"] += move.quantity or move.product_uom_qty
        return list(summary.values())
