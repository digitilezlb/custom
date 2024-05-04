# -*- coding: utf-8 -*-
{
    'name': 'Retailer Orders',
    'description': 'Retailer Orders',
    'license': 'LGPL-3',
    'version': '15.0.1.0.1',
    'author': 'DAS360',
    'depends': [
        'website_sale_wishlist','product','sale','das_zone_location','sale_discount_total','das_company_undermaintenance','das_kitchen_notes'
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'views/res_partner.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
