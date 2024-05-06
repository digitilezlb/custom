{
    "name": "Wizard Trip",
    "version": "16.0.0.0",
    "author": "Digitile",
    "website": "https://digitile.com",
    "license": 'AGPL-3',
    "auto_install": False,
    "installable": True,
    "depends": ["das_orders_trip",'base'],
    "data": [
        'security/ir.model.access.csv',
        'views/trip.xml',
        'wizard/trip.xml',
    ],
}
