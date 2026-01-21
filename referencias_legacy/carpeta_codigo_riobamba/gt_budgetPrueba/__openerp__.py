# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
{
    "name": "Government Budget",
    "version": "0.1",
    "author": "Mario Chogllo",
    "category": "Accounting & Finance",
    "website": "http://www.gnuthink.com",
    "description": """
    This module allows manage Government Bugdget
    ============================================
    """,
    "depends": ["report_webkit", "project", "hr", "account", "gt_document_manager","gt_payment_request","base_headers_webkit"],
    "init_xml": ["data/budget_sequence.xml",
                "data/budget_data.xml",
                 "data/budget_account_type.xml",
                 "data/budget.user.type.csv",
                "data/budget.post.csv",
                 ],
    "update_xml": [
        "security/budget_security.xml",
        "budget_view.xml",
        "payment_view.xml",
        "wizard/wizard_view.xml",
        "security/ir.model.access.csv",
        "wizard/cierre_view.xml",
        "wizard/reports_view.xml",
        "voucher_workflow.xml",
        "budget_report.xml",
        "report/report_view.xml",
        "wizard/gasto_programado_view.xml"
    ],
    "active": False,
    "installable": True,
}
