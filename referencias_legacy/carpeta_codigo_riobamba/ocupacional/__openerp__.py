# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
# mariofchogllo@gmail.com
##############################################################################

{
    "name" : "SALUD OCUPACIONAL",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite:
        -PLANIFICAY, REGISTRAR Y EVALUAR politicas de salud ocupacional.
    """,
    "category" : "Talento Humano",
    "website" : "",
    "depends" : ['gt_hr_base','oemedical'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'ocupacional_view.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
