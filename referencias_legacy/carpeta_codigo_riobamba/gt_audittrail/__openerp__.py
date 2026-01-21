# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
#
##############################################################################


{
    'name': 'Auditoria',
    'version': '0.1',
    'category': 'Audotoria',
    'complexity': "easy",
    'description': "Suscripcion masiva de registros de auditoria",
    'author': 'Mario Chogllo',
    'depends': ["audittrail"],
    'init_xml': [],
    'update_xml': [
        'audit_view.xml',
        "security/ir.model.access.csv",
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
