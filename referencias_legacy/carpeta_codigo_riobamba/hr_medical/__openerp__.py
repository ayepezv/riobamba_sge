# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "TTHH MEDICAL",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite:
        -Registro de fichas medicas de empleados
        -Diagnostico y recetas medicas
        -Generacion de egresos de bodega
    """,
    "category" : "Human Resources",
    "website" : "http://mariofchogllo@gmail.com",
    "depends" : ['gt_hr_base','gt_stock'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'medical_view.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
