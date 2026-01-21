# -*- coding: utf-8 -*-
##############################################################################
#
# GADMLI
#
##############################################################################

{
    "name" : "Documentacion - funcionarios",
    "version" : "1.0",
    "author" : 'limon',
    "description": """ 
    """,
    "category" : "",
    "website" : "http://gnuthink.com",
    "depends" : ['gt_hr_base','gt_document_manager','gt_hr_holidays'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'security/security.xml',
        "security/ir.model.access.csv",
        'funcionarios_view.xml',
        'roles_funcionario_view.xml',
        'cumpleanios_view.xml',
        'contratos_view.xml',
        'activos_funcionario_view.xml',
        'report/report.xml',
        'acciones_planificadas.xml',
        #'edi/data.xml',
],
    "installable": True,
}
