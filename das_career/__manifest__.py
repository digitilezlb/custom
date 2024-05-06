{
    'name': 'Website Career',
    'description': 'Website Career',
    'version': '16.0.0.0',
    'summary': 'Website Career Information',
    'website': 'https://das-360.com',
    'depends': ['hr_recruitment','das_template_settings', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        "data/data.xml",
        "views/career_information.xml",
         "views/hr_job.xml"	
    ],
    "author": "Das360",
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
