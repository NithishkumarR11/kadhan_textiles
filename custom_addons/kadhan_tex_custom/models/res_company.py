from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    kadhan_reference = fields.Char(string="Kadhan Reference")
    report_contact_name = fields.Char(string="Report Contact Name")
    report_footer_note = fields.Text(string="Report Footer Note")
    delivery_terms = fields.Text(string="Delivery Challan Terms")
