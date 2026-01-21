# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################


{
    'name': "Recursos Humanos - Cierre de rol",
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
    'author': 'Gnuthink Software Labs Cia. Ltda.',
    'website': 'http://www.gnuthink.com',
    'depends': ['gt_hr_payroll_ec','gt_hr_pago','gt_budget'],
    'init_xml': [],
    'update_xml': [
        'security/ir.model.access.csv',
        'gt_hr_payroll_account_view.xml',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
