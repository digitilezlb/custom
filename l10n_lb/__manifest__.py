# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Lebanon - Accounting',
    'author': 'DAS-360',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
Lebanon accounting chart and localization.
=======================================================
    """,
    'depends': ['base', 'account'],
    'data': [
        'data/l10n_lb_chart_data.xml',
        'data/account.account.template.csv',
        'data/l10n_lb_chart_post_data.xml',
        'data/account_chart_template_data.xml',
        'data/account_groups.xml',
        'data/accounts_taxes.xml'
    ],
    'demo': [

    ],
    'license': 'LGPL-3',
}
