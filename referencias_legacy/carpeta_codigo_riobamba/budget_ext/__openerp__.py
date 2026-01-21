# -*- coding: utf-8 -*-
##############################################################################
#
#    Obras - Ecuador
#    Mario Chogllo
#    mariofchogllo@gmail.com
##############################################################################

{
    'name' : 'Ext. Budget',
    'version' : '3',
    "category": 'Generic Modules/Accounting',    
    'depends' : ['gt_budget','gt_project_project','gt_pac'],
    'author' : 'Mario Chogllo',
    'description': '''
    Extencion de funcionalidad de presupuestos
    ''',
    'website': 'http://www.goberp.com',
    'update_xml': [
        'security/ir.model.access.csv',
        'budget_view.xml',
        'report.xml',
    ],
    'installable': True,
    'active': False,
}
