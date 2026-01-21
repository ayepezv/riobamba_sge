# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "ACTIVO MANTENIMIENTO",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite:
        -Registrar un activo para su mantenimiento
    """,
    "category" : "Financiero",
    "website" : "http://gnuthink.com",
    "depends" : ['gt_account_asset','gt_hr_base'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'mnt_view.xml',
#        'security/ir.model.access.csv',
        ],
    "installable": True,
}
