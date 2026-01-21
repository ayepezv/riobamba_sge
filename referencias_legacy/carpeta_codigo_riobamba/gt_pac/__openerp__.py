# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

{
    "name" : "Plan Anual Compras",
    "version" : "0.1",
    "author" : "Mario Chogllo",
    "category" : "Generic Modules/Compras Publicas",
    "website" : "http://www.planerp.ec",
    "description": """
    Este modulo provee funcionalidad para manejar la gestion del PAC
    PLan Anual de Compras planificado por unidad
    """,
    "depends" : ["gt_government_procedure"],
    "init_xml" : [],
    "update_xml" : [
        'pac_sequence.xml',
        "pac_view.xml",
        "purchase_view.xml",
        "report/report.xml",
        "wizard/agrupa_view.xml",
        "security/ir.model.access.csv",
     ],
    "active": False,
    "installable": True,
}
