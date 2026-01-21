# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

{
    "name" : "Government Procedures",
    "version" : "0.1",
    "author" : "Gnuthink Co. Ltd.",
    "category" : "Generic Modules/Sales & Purchases",
    "website" : "http://www.gnuthink.com",
    "description": """
    This module allows you to manage your Procedures: contracts, expense, etc
    """,
    "depends" : ["purchase_requisition","gt_budget","retention",
                 "gt_stock","gt_document_manager",
                 "additional_discount"],
    "init_xml" : [],
    "update_xml" : [
        "cancel_sequence.xml",
        "base_view.xml",
        "security/requisition_group.xml",
        "security/ir.model.access.csv",
        "acciones_planificadas.xml",
        "wizard/wizard_group_req_view.xml",
        "wizard/separate_order_view.xml",
        "wizard/return_state_view.xml",
        "wizard/return_start_view.xml",
        "wizard/cancel_process_view.xml",
        "wizard/wizard_cotizacion.xml",
        "wizard/recomend_process_view.xml",
        "requisition_view.xml",
        "purchase_view.xml",
        "report/report.xml",
        "requisition_report.xml",
     ],
    "active": False,
    "installable": True,
}
