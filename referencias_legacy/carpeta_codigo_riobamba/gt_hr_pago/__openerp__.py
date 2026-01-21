# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "RRHH PAGOS VARIOS",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad que permite registrar, o generar pagos a diferentes beneficiariosm habilitado para la gente de TTHH
    """,
    "category" : "Human Resources",
    "website" : "http://gnuthink.com",
    "depends" : ['retention','hr'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'varios_view.xml',
        'security/ir.model.access.csv',
        ],
    "installable": True,
}
