# -*- coding: utf-8 -*-
##############################################################################
#
#    Obras - Ecuador
#    Mario Chogllo
#    mariofchogllo@gmail.com
#    www.goberp.com
##############################################################################

{
    'name' : 'Comprobante con Ivas automatico',
    'version' : '3',
    "category": 'Generic Modules/Accounting',    
    'depends' : ['retention'],
    'author' : 'Mario Chogllo',
    'description': '''
    Extension de asientos calculo de retencion e iva
    ''',
    'website': 'http://www.goberp.com',
    'update_xml': [
        'security/ir.model.access.csv',
        'move_view.xml',
    ],
    'installable': True,
    'active': False,
}
