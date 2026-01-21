# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "Precios Unitarios",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite:
        -Creacion de proyectos
-Generacion de materiales y costos unitarios
-Costos de proyectos
    """,
    "category" : "Proyectos",
    "website" : "",
    "depends" : ['hr','gt_project_project','retention_ext'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'pu_view.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
