# -*- coding: utf-8 -*-
# A prdouct of DX-8, module resricted as per the license.

{
    "name": "HMB Newsletter",
    "version": "17.0.1.0.3",
    "category": "Website",
    "summary": """HMB Website Customization""",
    "description": """HMB Website Customization""",
    'website': 'https://www.dxeight.com/odoo',
    "license": "LGPL-3",
    "depends": ['website_mass_mailing', 'hmb_website'],
    "data": [
        "views/mailing_list_views.xml",
        "views/snippets_themes.xml",
        "views/snippets/s_dynamic_button.xml"
    ],
    "installable": True,
}
