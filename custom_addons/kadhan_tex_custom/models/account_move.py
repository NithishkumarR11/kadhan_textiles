from odoo import fields, models

try:
    from num2words import num2words
except ImportError:
    num2words = None


class AccountMove(models.Model):
    _inherit = "account.move"

    kadhan_eway_bill_no = fields.Char(string="E-way Bill Number", copy=False)
    kadhan_vehicle_no = fields.Char(string="Vehicle Number", copy=False)

    def _kadhan_amount_in_words(self):
        """Total in words using the Indian numbering system (lakh / crore)."""
        self.ensure_one()
        currency = self.currency_id
        if num2words is None or currency.name != "INR":
            return currency.amount_to_text(self.amount_total)
        rupees, _sep, paise = f"{self.amount_total:.2f}".partition(".")
        words = "%s Rupees" % num2words(int(rupees), lang="en_IN").title()
        if int(paise):
            words += " and %s Paise" % num2words(int(paise), lang="en_IN").title()
        return words + " only"

    def _kadhan_state_label(self, state):
        """'33-Tamil Nadu' style label used on the invoice."""
        if not state:
            return ""
        return "%s-%s" % (state.l10n_in_tin, state.name) if state.l10n_in_tin else state.name

    def _kadhan_line_hsn(self, line):
        return line.l10n_in_hsn_code or line.product_id.product_tmpl_id.kadhan_hsn_code or ""

    @staticmethod
    def _kadhan_flat_taxes(taxes):
        return taxes.filtered(lambda t: t.amount_type != "group") | taxes.filtered(
            lambda t: t.amount_type == "group"
        ).children_tax_ids

    def _kadhan_hsn_summary(self):
        """Taxable value and CGST/SGST/IGST per (HSN, GST rate) for the tax summary table."""
        self.ensure_one()
        rows = {}
        lines = self.invoice_line_ids.filtered(lambda l: l.display_type == "product")
        for line in lines:
            taxes = self._kadhan_flat_taxes(line.tax_ids)
            rates = {
                kind: sum(taxes.filtered(lambda t, k=kind: t.l10n_in_gst_tax_type == k).mapped("amount"))
                for kind in ("cgst", "sgst", "igst")
            }
            key = (self._kadhan_line_hsn(line), rates["cgst"], rates["sgst"], rates["igst"])
            row = rows.setdefault(key, {
                "hsn": key[0],
                "taxable": 0.0,
                "cgst_rate": rates["cgst"],
                "sgst_rate": rates["sgst"],
                "igst_rate": rates["igst"],
                "cgst": 0.0,
                "sgst": 0.0,
                "igst": 0.0,
            })
            row["taxable"] += line.price_subtotal
            for kind in ("cgst", "sgst", "igst"):
                row[kind] += self.currency_id.round(line.price_subtotal * rates[kind] / 100.0)
        result = list(rows.values())
        for row in result:
            row["total_tax"] = row["cgst"] + row["sgst"] + row["igst"]
        return result


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_allowed_uom_ids(self):
        """Lines without a product can use any unit; product lines keep the
        product's own units so Odoo's price conversions stay valid."""
        super()._compute_allowed_uom_ids()
        lines_without_product = self.filtered(lambda l: not l.product_id)
        if lines_without_product:
            lines_without_product.allowed_uom_ids = self.env["uom.uom"].search([])
