# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
#
##############################################################################

{
    "name" : "Assets Management Extension",
    "version" : "1.0",
    "depends" : ["account_asset",'hr','gt_budget','gt_asset_stock','gt_stock','report_webkit','base_headers_webkit'],
    "author" : "Gnuthink Co. Ltd.",
    "description": """Financial and accounting asset management.
    This module improve the asset module allowing manage:
    * Guardian Assets
    * Location for assets
    * Transfer for Assets between locations it will update the guardian
    """,
    "website" : "http://www.gnuthink.com",
    "category" : "Accounting & Finance",
    "init_xml" : [],    
#    "demo_xml" : [ 'account_asset_demo.xml'],
    "update_xml" : [
#        "security/account_asset_security.xml",
#        "security/ir.model.access.csv",
        "sequence.xml",
        "wizard/depreciacion_view.xml",
        "wizard/gt_account_im_category_view.xml",
        'security/account_security.xml',
        'security/ir.model.access.csv',
        "view/account_asset_view.xml",
        "view/gt_account_asset_task.xml",
        "view/account_asset_sequence.xml",
        "account_asset_workflow.xml", 
        'report/report_webkit_html_view.xml',
#        "report/account_asset_report_view.xml",
        "wizard/invoice_relate_asset_view.xml",
        "wizard/valorado_departamento_view.xml",
    ],
    "active": False,
    "installable": True,
}
