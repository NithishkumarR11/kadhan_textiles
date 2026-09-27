from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    kadhan_reference = fields.Char(string="Kadhan Reference")
    report_contact_name = fields.Char(string="Report Contact Name")
    report_footer_note = fields.Text(string="Report Footer Note")
    delivery_terms = fields.Text(string="Delivery Challan Terms")
    kadhan_bank_name = fields.Char(string="Bank Name")
    kadhan_bank_acc_number = fields.Char(string="Account No.")
    kadhan_bank_ifsc = fields.Char(string="IFSC Code")
    kadhan_bank_acc_holder = fields.Char(string="Account Holder's Name")
    kadhan_payment_qr = fields.Image(string="Payment QR Code", max_width=512, max_height=512)
