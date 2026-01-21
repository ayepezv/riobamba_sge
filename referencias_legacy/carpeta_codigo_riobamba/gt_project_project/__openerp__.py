# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
#
##############################################################################
{
    "name": "Projects and Budget Integration",
    "version": "0.1",
    "author": "Gnuthink Co. Ltd.",
    "category": "Generic Project",
    "website": "http://www.gnuthink.com",
    "description": """
    This module integrate the projects and budget area
    """,
    "depends": ["gt_budget", "country_ec"],
    "init_xml": [],
    "update_xml": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "project_project_view.xml",
        "project_info_view.xml",
        "project_budget_view.xml",
        "project_exec_view.xml",
        "project_project_sequence.xml",
        "project_project_workflow.xml",
        "project_report.xml",
        "wizard/wizard_report_view.xml",
        "wizard/wizards_view.xml",
        "project_project_data.xml",
        "wizard/reforma_programa_view.xml",
    ],
    "active": False,
    "installable": True,
}
