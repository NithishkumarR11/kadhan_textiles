from odoo import api, fields, models
from odoo.tools.image import image_data_uri

try:
    from num2words import num2words
except ImportError:
    num2words = None


class AccountMove(models.Model):
    _inherit = "account.move"

    kadhan_eway_bill_no = fields.Char(string="E-way Bill Number", copy=False)
    kadhan_vehicle_no = fields.Char(string="Vehicle Number", copy=False)
    kadhan_ship_to_address = fields.Text(
        string="Ship To Address",
        compute="_compute_kadhan_ship_to_address", store=True, readonly=False, precompute=True,
        copy=True,
        help="Printed as Ship To on the invoice. Filled from the Ship To contact; "
             "edit it to enter any other address.",
    )

    @api.depends("partner_shipping_id")
    def _compute_kadhan_ship_to_address(self):
        for move in self:
            shipping = move.partner_shipping_id
            if not shipping:
                move.kadhan_ship_to_address = False
                continue
            address = " ".join(p for p in [shipping.street, shipping.street2, shipping.city] if p)
            if shipping.zip:
                address += " -%s" % shipping.zip
            name = shipping.name if shipping != move.partner_id else ""
            move.kadhan_ship_to_address = "\n".join(p for p in [name, address] if p) or False

    def _kadhan_bank_details(self):
        """Bank details for the invoice footer: the company's report bank details,
        falling back to the invoice's recipient bank account."""
        self.ensure_one()
        company = self.company_id
        if company.kadhan_bank_name or company.kadhan_bank_acc_number:
            return {
                "name": company.kadhan_bank_name,
                "acc_number": company.kadhan_bank_acc_number,
                "ifsc": company.kadhan_bank_ifsc,
                "holder": company.kadhan_bank_acc_holder,
            }
        bank = self.partner_bank_id
        if bank:
            return {
                "name": bank.bank_id.name,
                "acc_number": bank.acc_number,
                "ifsc": bank.bank_id.bic,
                "holder": bank.acc_holder_name or bank.partner_id.name,
            }
        return {}

    def _kadhan_payment_qr_src(self):
        """The company's uploaded payment QR; no QR is printed without one."""
        self.ensure_one()
        qr = self.company_id.kadhan_payment_qr
        return image_data_uri(qr) if qr else False

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
