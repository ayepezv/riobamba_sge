# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "GESTION DE CURSOS INSTITUCION",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite:
        -Registrar Cursos dictados por la entidad
    """,
    "category" : "Human Resources",
    "website" : "http://www.goberp.com",
    "depends" : ['gt_hr_base'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'academic_view.xml',
#        'ir_report.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
