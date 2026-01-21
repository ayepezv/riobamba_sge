# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

{
    "name" : "FINANCIAL DOCU GOB",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
    """,
    "category" : "Account",
    "website" : "http://mariofchogllo@gmail.com",
    "depends" : ['gt_document_manager','retention','gt_gob_report'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'security/financial_groups.xml',
        'auditoria_view.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
