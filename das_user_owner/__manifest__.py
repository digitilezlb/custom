{
    "name": "User Owner",
    "summary": "User Owner",
    "description": "User Owner",
    "version": "16.0.1.0.1",
    "author": "Digitile",
    "depends": ['base','base_setup','das_sh_message'],
    "data": [
        'views/res_users.xml',
        "security/owner_security.xml"
    ],

    'installable': True,
    'sequence': -100,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
    'company': 'Digitile',
    'maintainer': 'Digitile',
    'website': "https://digitile.com",

}
