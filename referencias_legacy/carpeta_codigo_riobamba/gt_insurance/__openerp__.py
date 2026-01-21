# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
{
    "name": "gt_insurance",
    "version": "1.1",
    "author": "Mario Chogllo",
    "category": "asset",
    "sequence": 12,
    'complexity': "easy",
    "website": "http://www.gnuthink.com",
    "description": """
Module for policy.
=====================================

Se puede gestionar:
    * Manejo de Siniestos
    * Manejo de tipo de Solicitudes de informe para siniestros
    """,    
    'images': [],
    'depends': ['account_asset','gt_insurance_policy'],
    'init_xml': [],
    'update_xml': [        
        'security/gt_insurance_security.xml',
        'security/ir.model.access.csv',
        'view/gt_insurance_view.xml',    
        'view/gt_insurance_directory.xml',
        'view/gt_insurance_workflow.xml',            
        'view/gt_insurance_sequence.xml',
        'view/gt_insurance_mail_template.xml',
        'report/report.xml',
    ],
    'demo_xml': [],
    #'test': ['test/gt_insurance.yml'],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
