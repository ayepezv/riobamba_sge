# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "Revalorizacion de activos",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite:
        -Revalorizar los activos fijos
    """,
    "category" : "Financiero - Activos",
    "website" : "mariofchogllo@gmail.com",
    "depends" : ['gt_account_asset','retention'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'asset_view.xml',
        "rev_sequence.xml",
        "report/report_view.xml",
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
