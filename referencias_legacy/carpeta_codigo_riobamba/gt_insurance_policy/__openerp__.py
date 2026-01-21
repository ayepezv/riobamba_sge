# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

{
    "name": "gt_insurance_policy",
    "version": "1.1",
    "author": "Mario Chogllo",
    "category": "asset",
    "sequence": 12,
    'complexity': "easy",
    "website": "http://www.gnuthink.com",
    "description": """
Modulo para gestion de polizas.
=====================================

You can manage:    
    * Registro de pólizas de sus activos fijos.
    * Gestión de tipo y ramo de pólizas.
    * Muestra el listado de activos asegurados
    * Permite trasnferir activos de una póliza a otra; guardando dentro de cada activo el historial de polzias a las que ha pertenecido.
    * Manejo de notificaciónes en base a fecha de caducidad de pólizas
    """,
    'images': [],
    'depends': ['gt_account_asset'],
    'init_xml': [],
    'update_xml': [        
        'security/gt_insurance_policy_security.xml',
        'security/ir.model.access.csv',
        'view/gt_insurance_policy_view.xml',                     
        'view/gt_insurance_policy_workflow.xml',
        'view/gt_insurance_policy_sequence.xml',        
        'view/gt_insurance_policy_task.xml',
        'view/gt_insurance_policy_mail_template.xml',
        'report/report.xml',           
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
