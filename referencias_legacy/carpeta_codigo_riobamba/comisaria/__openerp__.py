# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "COMISARIA",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
    """,
    "category" : "GAD",
    "website" : "http://gnuthink.com",
    "depends" : ['gt_hr_base'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "security/comisaria_group.xml",
        "security/ir.model.access.csv",
        'comisaria_view.xml',
        'ordenanza_view.xml',
        'multa_view.xml',
        'predio_view.xml',
        'notificacion_view.xml',
	'report.xml',
	'report_all.xml',
        'report_multa.xml',
	'sequence.xml',
	#'template_reporte_cliente.xml',
	#'qweb': ['template_reporte_cliente.xml'],
	#'reportes/reporte_cliente.xml',
],
    "installable": True,
}
