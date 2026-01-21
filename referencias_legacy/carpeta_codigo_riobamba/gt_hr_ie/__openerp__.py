# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "RRHH ALLOWANCE/DEDUCTION ECUADOR",
    "version" : "1.0",
    "author" : 'Gnuthink Software Cia. Ltda.',
    "description": """ 
   Este módulo implementa funcionalidad que permite registrar:
        -Ingresos/Egresos empleado
        -Ingresos/Egresos empleado(s)
    """,
    "category" : "Human Resources",
    "website" : "http://gnuthink.com",
    "depends" : ['gt_hr_base','hr_payroll','retention'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'hr_ie_view.xml',
        'hr_import_xls_view.xml',
        'ie_report.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
