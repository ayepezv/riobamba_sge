#-*- coding:utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################
{
    'name': 'Sol. Compra Sin Producto',
    'version': '1.0',
    'category': 'Compras',
    'description': """Solicitudes de compra
    * Sin producto en linea, solo descripcion
     """,
    'author':'Mario Chogllo',
    'website':'http://www.mariofchogllo.com',
    'depends': ['gt_government_procedure','gt_account_asset'],
    'init_xml': [
    ],
    'update_xml': [
        'security/groups_req.xml',
        "security/ir.model.access.csv",
        'sequence.xml',
        'purchase_view.xml',
        'report.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
