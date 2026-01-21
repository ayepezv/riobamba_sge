# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "INTEGRACION SIIM APLICATIVOS MUNICIPALES",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite:
        -Interactuar con los aplicativos municipales como una sola plataforma
    """,
    "category" : "Base",
    "website" : "http://mariochogllo.com",
    "depends" : ['base','account','retention','gt_budget'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'partner_view.xml',
        'recaudacion_view.xml',
        'reportes_view.xml',
        "security/ir.model.access.csv",
        ],
    "installable": True,
}
