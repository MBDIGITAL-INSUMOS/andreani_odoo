# -*- coding: utf-8 -*-
{
    'name': "Andreani Odoo Connector",

    'summary': """
        Connector Odoo-Andreani for Shipping Payment""",

    'description': """
        Connector Odoo-Andreani for Shipping Payment
    """,

    'author': "Moldeo Interactive",
    'website': "https://www.moldeointeractive.com.ar",

    'category': 'Sales',
    'version': '0.1',

    'depends': ['base', 'sale', 'delivery'],

    'data': [
        'views/res_company.xml',
        'views/sale_order_line.xml',
    ]
}
