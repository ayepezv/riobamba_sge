# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

{
    "name" : "Recursos Humanos - Caculo Decimos",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Módulo implementa la funcionalidad para calcular los valores acumulados de decimo tercero
   y decimo cuarto sueldo, en base los dias laborados, es un calculo proporcional. 
    """,
    "category" : "Human Resources",
    "website" : "http://gnuthink.com",
    "depends" : ['gt_hr_payroll_account'],
    "update_xml" : [
        'security/ir.model.access.csv',
        'decimo_view.xml',
        'report/report.xml',
        'wizard/import_xls_d4_view.xml',
        ],
    "installable": True,
}
