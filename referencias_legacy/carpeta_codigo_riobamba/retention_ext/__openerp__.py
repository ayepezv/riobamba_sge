# -*- coding: utf-8 -*-
##############################################################################
#
#    Obras - Ecuador
#    Mario Chogllo
#    mariofchogllo@gmail.com
##############################################################################

{
    'name' : 'Gestion de obras Ecuador',
    'version' : '3',
    "category": 'Generic Modules/Accounting',    
    'depends' : ['retention','gt_spi','account_advances','gt_government_procedure','gt_hr_payroll_ec','gt_document_manager'],
    'author' : 'Mario Chogllo',
    'description': '''
    Gestion de contratos/obras integrado con la contabilzacion para manejo de montos, anticipos, 
    certificdos presupuestarios y pagos realizados.
    ''',
    'website': 'http://www.goberp.com',
    'update_xml': [
        'security/ext_groups.xml',
        'security/ir.model.access.csv',
        'obra_view.xml',
        'obra_sequence.xml',
        'report.xml',
    ],
    'installable': True,
    'active': False,
}
