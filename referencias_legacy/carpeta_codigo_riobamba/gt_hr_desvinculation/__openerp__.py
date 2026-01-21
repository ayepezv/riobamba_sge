# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    'name': 'Employee Vinculation/Desvinculation',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """
    Módulo que permite ejecutar las vinculaciones de prospectos de empleados
    y las desvinculaciones de empleados activos.
    """,
    'author': 'Mario chogllo',
    'website': 'http://www.gnuthink.com',
    'depends': ['gt_hr_base','gt_hr_pago'],
    'init_xml': [],
    'update_xml': [
        'liq_sequence.xml',
        'desvinculation_view.xml',
        'security/ir.model.access.csv',
        'report/report.xml',
        ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
