# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

{
    "name" : "Conciliacion Bancaria para Ecuador",
    "version" : "1.0",
    "author" : 'Gnuthink Software Cia. Ltda.',
    "description": """ 
   Este módulo implementa la funcionalidad para realizar conciliaciones bancarias
    """,
    "category" : "Account",
    "website" : "http://gnuthink.com",
    "depends" : ['account'],
    "demo_xml" : [],
    "init_xml": [
                'data/tipo.conciliacion.csv',
                 ],
    "update_xml" : [
        'security/ir.model.access.csv',
        'conciliation_view.xml',
        'report/concilia_report.xml',
        ],
    "installable": True,
}
