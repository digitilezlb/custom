{
    "name": "Menu",
    "description": "Menu",
    "version": "16.0.0.0",
    "author": "Digitile",
    "website": "https://digitile.com",
    "license": 'AGPL-3',
    "auto_install": False,
    "installable": True,
    "application": True,
    "depends": ['das_template_settings','base','product','das_sale_order_product'],
    "data": [
        "security/ir.model.access.csv",
        "views/das_menu.xml",
        "views/das_category_menu.xml",
    ],
}
