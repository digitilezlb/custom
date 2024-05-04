{
    "name": "Main Page Sections",
    "description": "Main Page Sections",
    "version": "16.0.0.0",
    "author": "Digitile",
    "website": "https://digitile.com",
    "license": 'AGPL-3',
    "auto_install": False,
    "installable": True,
    "depends": ['das_template_settings','base','product','das_sale_order_product'],
    "data": [
        "security/ir.model.access.csv",
        "views/main_page_section.xml",
    ],
}
