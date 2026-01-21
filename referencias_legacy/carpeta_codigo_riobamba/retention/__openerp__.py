# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Mario Chogllo
#
##############################################################################

{
    'name' : 'Accounting for Ecuador',
    'version' : '3',
    "category": 'Generic Modules/Accounting',    
    'depends' : ['account_advances', 'report_webkit','gt_budget','analytic','gt_payment_request'],
    'author' : 'Gnuthink Software Cia. Ltda.',
    'description': '''
    Accounting for Ecuador, retention docuements
    ''',
    'website': 'http://www.gnuthink.com',
    'update_xml': [
        'wizard/load_retention.xml',
        'security/payment_groups.xml',
        'security/retention_security.xml',
        'retention_workflow.xml',
        'retention_view.xml',
        'tax_view.xml',
        'voucher_view.xml',
        'config_cxp_view.xml',
        'retention_report.xml',
        'retention_wizard.xml',
        'product_view.xml',
        'wizard/wizard_refund.xml',
        'wizard/validate_move.xml',
        'wizard/pay_move_view.xml',
        'wizard/close_year_view.xml',
        'wizard/revert_move_view.xml',
        'move_view.xml',
        'cxp_view.xml',
        'data/cta.partida.csv',
#        'data/cuenta.partida.csv',
        'data/no.partida.csv',
        'data/regla.line.csv',
        'security/ir.model.access.csv',
        'wizard/saldo_anticipo.xml',
        'reportes_view.xml',
        
    ],
    'installable': True,
    'active': False,
}
