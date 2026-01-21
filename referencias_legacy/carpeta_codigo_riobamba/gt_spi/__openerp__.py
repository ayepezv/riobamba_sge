# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

{
    'name' : 'Tesoreria',
    'version' : '3',
    "category": 'Generic Modules/Accounting',    
    'depends' : ['retention','gt_hr_payroll_account','gt_hr_quincena','gt_hr_pago','gt_hr_decimo'],
    'author' : 'Mario Chogllo',
    'description': '''
    Formulario para realizar pagos multiples tanto de cliente
    como de proveedor
    ''',
    'website': 'http://www.gnuthink.com',
    'update_xml': [
        'wizard/wizard_spi_view.xml',
        'spi_sequence.xml',
        "security/ir.model.access.csv",
        'spi_view.xml',
        'report.xml',
        ],
    'installable': True,
    'active': False,
}
