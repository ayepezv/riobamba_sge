#-*- coding:utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################
{
    'name': 'RRHH - Acceso Anticipo para contabilidad',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """Registro de anticipos
    * Anticipos Tipo C
    * cartera descuentos
     """,
    'author':'Mario Chogllo',
    'website':'http://www.mariofchogllo.com',
    'depends': ['gt_hr_advance','retention'],
    'init_xml': [
    ],
    'update_xml': [
        'security/ir.model.access.csv',
        'wizard/crea_view.xml',
        'anticipo_view.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
