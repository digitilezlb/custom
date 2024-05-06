{
    'name': 'Customers Feedback',
    'description': 'Customers Feedback',
    'version': '16.0.0.0',
    'summary': 'Delivery Fees',
    'website': 'https://digitile.com',
    'depends': ['base','das_template_settings'],
    'data': [
        "views/customer_feedback.xml",
        "security/ir.model.access.csv",
    ],
    "author": "Digitile",
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}