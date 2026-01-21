# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

{
    'name' : 'Stock for Ecuador',
    'version' : '3',
    "category": 'Generic Modules/Accounting',    
    'depends' : ['account_asset','gt_hr_base','analytic',
                 'gt_document_manager','gt_budget','purchase'],
    'author' : 'Gnuthink Software Cia. Ltda.',
    'description': '''
    Guías de Remisión para Ecuador
    ''',
    'website': 'http://www.gnuthink.com',
    'update_xml': [
        "security/ir.model.access.csv",
        'requisition_view.xml',
        'stock_report.xml',
        'rqm_sequence.xml',
        'stock_view.xml',
        'product_view.xml',
        'report_moves_view.xml',
        'report/report.xml',
        'stock_partial_view.xml',
        'invoice_view.xml',
        'wizard/import_rqm_view.xml',
        'wizard/invoice_onshipping.xml',
        ],
    'installable': True,
    'active': False,
}
