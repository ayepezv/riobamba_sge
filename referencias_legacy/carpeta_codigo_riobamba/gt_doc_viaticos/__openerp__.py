# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo 
# mariofchogllo@gmail.com
##############################################################################


{
    'name': "Documentacion - Viaticos",
    'version': '1.0',
    'category': '',
    'complexity': "normal",
    'description': """
Modulo para el manejo de:
    - Viaticos
    - Salidas al campo
    """,
    'author': 'Mario Chogllo',
    'website': 'mariofchogllo@gmail.com',
    'depends': ['hr_payroll','country_ec', 'gt_document_manager','gt_hr_base'],
    'init_xml': [],
    'update_xml': [
                   'security/groups_viaticos.xml',
                   'wizard/devolver_informe_viatico_view.xml',
                   'viaticos_view.xml',
                   'salidas_view.xml',
#                   'wizard/calculador_viaticos_view.xml',
                   'report/report.xml',
                   'data/secuencias.xml',
                   'security/ir.model.access.csv',
#                   'security/security_ir_rule.xml'
                   ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
