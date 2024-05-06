{
    "name": "Team",
    "description": "Team",
    "summary": "Team",
    "version": "16.0.1.0.1",
    "author": "Digitile",
    "depends": ['base','das_template_settings'],
    "data": [
        'views/team.xml',
        'views/team_member.xml',
        'data/data.xml',
        "security/ir.model.access.csv",
    ],

    'installable': True,
    'sequence': -100,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'company': 'Digitile',
    'maintainer': 'Digitile',
    'website': "https://digitile.com",

}
