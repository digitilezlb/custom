{
    'name': 'Add Plat Du Jour To Notification',
    'description': 'Add Plat Du Jour To Notification',
    'version': '16.0.0.0',
    'summary': 'Chef',
    'website': 'https://digitile.com',
    'depends': ['base','das_user_notification'],
    'data': [
        "views/plat_de_jour.xml",

    ],
    "author": "Digitile",
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}