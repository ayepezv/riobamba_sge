# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "NOTA DE CREDITO",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite:
        -Registrar notas de credito de proveedores
        -Bajar el valor a pagar aplicando nota de credito
    """,
    "category" : "Contabilidad",
    "website" : "http://mariofchogllo@gmail.com",
    "depends" : ['retention_ext'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'nc_view.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
