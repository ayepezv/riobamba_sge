# -*- coding: utf-8 -*-
##############################################################################
#
#    Mario Chogllo
#    mariofchogllo@gmail.com
##############################################################################

{
    'name' : 'Documentos contables - folder',
    'version' : '3',
    "category": 'Generic Modules/Accounting',    
    'depends' : ['retention'],
    'author' : 'Mario Chogllo',
    'description': '''
    Organizacion de comprobantes contables en carpetas
    ''',
    'website': 'http://www.planerp.ec',
    'update_xml': [
        'security/ir.model.access.csv',
        'folder_view.xml',
        'report/documento.xml',
    ],
    'installable': True,
    'active': False,
}
