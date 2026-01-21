# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################


{
    'name': "Recursos Humanos - Cierre de rol _EXT",
    'version': '1.0',
    'category': 'Human Resources',
    'complexity': "normal",
    'description': """
Cierra el rol de pagos.
=============================================================

    * Configuracion de cuentas,
    * Cierre de Roles,
    * Cierre de Ingresos/Egresos,
    * Cierre del mes de nomina,

    """,
    'author': 'Mario Chogllo',
    'website': 'mariofchogllo@gmail.com',
    'depends': ['gt_hr_payroll_account'],
    'init_xml': [],
    'update_xml': [
        'payroll_account_view.xml',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
