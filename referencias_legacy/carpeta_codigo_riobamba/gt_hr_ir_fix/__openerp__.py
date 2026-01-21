# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "RRHH IMPUESTO A LA RENTA 2022",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite:
        -Calcular el IR 2022
    """,
    "category" : "Human Resources",
    "website" : "http://www.goberp.com",
    "depends" : ['gt_hr_ir'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'ir_view.xml',
#        'ir_report.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
