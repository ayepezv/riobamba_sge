# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    "name" : "Modificaciones Riobamba",
    "version" : "1.0",
    "author" : 'Mario Chogllo',
    "description": """ 
   Este módulo implementa funcionalidad unica para el GAD Riobamba
    """,
    "category" : "GAD",
    "website" : "http://www.goberp.com",
    "depends" : ['gt_hr_payroll_ec'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'rio_report.xml',
        ],
    "installable": True,
}
