{
    'name': 'Drivers API',
    'description': 'Drivers API',
    'version': '16.0.0.0',
    'summary': 'Drivers API',
    'website': 'https://digitile.com',
    'depends': ['base','sale','das_template_settings'],
    'data': [
        "views/driver_chat.xml",
        "views/show_images.xml",
        "security/ir.model.access.csv",

    ],
    "author": "Digitile",
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}