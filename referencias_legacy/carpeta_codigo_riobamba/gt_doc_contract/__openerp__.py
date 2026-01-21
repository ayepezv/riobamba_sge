# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Contract Management",
    "version": "1.0",
    "author": "Gnuthink Soft. Labs Cia Ltda",
    'website': 'http://www.gnuthink.com',
    "category": "GPA",
    'complexity': "easy",
    'images': [],
    'depends': ['gt_warranty_base','gt_account_budget'],
    "website": "http://www.gnuthink.com",
    "description": """
Módulo de Gestion de Contratos, permite llevar un control de los contratos que se generan en el gobierno
provincial 
========================================================================================================
""",
    
    'init_xml': [],
    'data': ['doc_contract_action_data.xml'],
    'update_xml': ['wizard/doc_contract_cancel_view.xml',
                   'wizard/invoice_relate_view.xml',
                   'doc_contract_view.xml', 
                   'doc_contract_workflow.xml',
                   'report/contract_report.xml',
                   'doc_contract_sequence.xml',
                   'security/ir.model.access.csv',
                   'doc_contract_document_storage_data.xml',
                   'doc_contract_directory_data.xml',
                   ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
