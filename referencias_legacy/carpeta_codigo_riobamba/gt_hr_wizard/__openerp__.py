# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "RRHH WIZARD",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo incluye algunos asistentes base:
        -Actualizaciones de salario
        -Actualizaciones de puesto de trabajo
    """,
    "category" : "RRHH",
    "website" : "http://gnuthink.com",
    "depends" : ['gt_hr_base','gt_hr_holidays'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'hr_wizard.xml',
        'wizard/hr_update_job_view.xml',
        'wizard/hr_update_wage_view.xml',
        'wizard/ejecuta_ie_view.xml',
        'wizard/ejecuta_holi.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
