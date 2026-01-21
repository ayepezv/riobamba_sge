# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################


{
    'name': "Recursos Humanos - Rol de Pagos",
    'version': '1.0',
    'category': 'Human Resources',
    'complexity': "normal",
    'description': """
Presenta la informacion correspondiente al rol de pagos.
=============================================================

    * Roles,
    * Provisiones,

    """,
    'author': 'Gnuthink Software Labs Cia. Ltda.',
    'website': 'http://www.gnuthink.com',
    'depends': ['gt_tool',
                'gt_hr_holidays',
                'gt_hr_base',
                'hr_payroll'],
    'init_xml': [],
    'update_xml': [
        'contract_view.xml',
        'gt_hr_payroll_ec_view.xml',
        'data/provision_data.xml',
        'data/salary_structure.xml',
        'data/hr_security.xml',
        'report/report.xml',
        'security/ir.model.access.csv',
        'extra_view.xml',
        'wizard/inherit_wizard_payslips_by_employees_view.xml',
        'edi/payslip_action_data.xml',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
