# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "RRHH IMPUESTO A LA RENTA",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite:
        -Calcular el IR
    """,
    "category" : "Human Resources",
    "website" : "http://gnuthink.com",
    "depends" : ['gt_hr_ie','retention'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'ir_view.xml',
#        'ir_report.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
