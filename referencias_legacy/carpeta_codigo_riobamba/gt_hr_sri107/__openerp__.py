#-*- coding:utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
{
    'name': 'RRHH - SRI Formulario 107 - RDEP',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """Datos para el formulario 107
     """,
    'author':'Mario Chogllo',
    'website':'http://www.goberp.com',
    'depends': [
        'retention',
        'gt_hr_base',
    ],
    'init_xml': [
    ],
    'update_xml': [
        'security/ir.model.access.csv',
        'hr_sri107_view.xml',
        'data/secuencias.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
