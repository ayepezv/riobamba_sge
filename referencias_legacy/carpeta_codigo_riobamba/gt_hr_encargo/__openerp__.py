# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################


{
    'name': "Talento Humano - Encargo y subrogacion",
    'version': '1.0',
    'category': 'Human Resources',
    'complexity': "easy",
    'description': """
Agrega la informacion de Encargo y Subrogacion de cargos dentro de la institucion.
=============================================================

    * Registro de un Encargo,
    * Informacion registrada en el contrato del empelado
    """,
    'author': 'GnuThink Cia. Ltda.',
    'website': 'http://www.openerp.com',
    'images': [],
    'depends': ['gt_hr_base','gt_hr_ie'],
    'init_xml': [],
    'update_xml': [
                   'security/ir.model.access.csv',
                   'encargo_view.xml',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
