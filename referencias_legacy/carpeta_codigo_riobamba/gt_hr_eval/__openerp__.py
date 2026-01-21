# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "EVALUACION PERSONAL",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite:
        -Generar Encuestas para evaluacion 360
        -Estadisticas de encuestas
    """,
    "category" : "Talento Humano",
    "website" : "",
    "depends" : ['gt_hr_base','survey','hr_evaluation'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'eval_view.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
