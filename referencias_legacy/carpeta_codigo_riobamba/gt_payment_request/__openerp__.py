# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################
{
    "name" : "Solicitud de Pago",
    "version" : "0.1",
    "author" : "Gnuthink Co. Ltd.",
    "category" : "Account Modules",
    "website" : "http://www.gnuthink.com",
    "description": """
    
    """,
    "depends" : ["gt_document_manager","hr","account"],
    "init_xml" : [],
    "update_xml" : [
        'security/payment_groups_security.xml',
        "payment_request_view.xml",  
        'report/report_webkit_html_view.xml',  
#        'security/ir.model.access.csv',      
        "payment_request_sequence.xml",                                            
                   
           
     ],
    "active": False,
    "installable": True,
}
