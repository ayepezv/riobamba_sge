# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################


{
    'name': "Recursos Humanos - Vacaciones",
    'version': '1.0',
    'category': 'Human Resources',
    'complexity': "normal",
    'description': """
Collect all information about employee vacations - Legal leaves.
================================================================

    * Vacations,
    * Legal Leaves,

This information in used for payroll.
    """,
    'author': 'Gnuthink Software Labs Cia. Ltda.',
    'website': 'http://www.gnuthink.com',
    'depends': ['gt_tool',
                'gt_document_manager',
                'gt_hr_ie',
                'hr_payroll',
                'hr_holidays',
                'gt_hr_base'],
    'init_xml': [],
    'update_xml': [
        'security/holidays_group.xml',
        'gt_hr_holidays_view.xml',
        'data/holiday_status.xml',
        'acciones_planificadas.xml',
        'security/ir.model.access.csv',
        'report/report.xml',
        'sequence.xml',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
