{
    "name": "Kadhan Tex Custom",
    "version": "19.0.1.0.0",
    "summary": "Base customization module for Kadhan Tex",
    "description": """
Base module for project-specific Odoo customizations.
    """,
    "category": "Customization",
    "author": "Kadhan Tex",
    "website": "",
    "license": "LGPL-3",
    "depends": ["account", "product", "sale", "stock", "l10n_in"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
        "views/stock_picking_views.xml",
        "views/account_move_views.xml",
        "reports/report_invoice.xml",
        "reports/report_paperformat.xml",
        "reports/report_delivery_challan.xml",
        "reports/report_invoice_new.xml",
    ],
    "installable": True,
    "application": False,
}
