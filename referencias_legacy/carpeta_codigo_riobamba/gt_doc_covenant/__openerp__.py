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
    "name": "Covenants Management",
    "version": "1.0",
    "author": "Gnuthink Soft. Labs Cia Ltda",
    'website': 'http://www.gnuthink.com',
    "category": "GPA",
    'complexity': "easy",
    'images': [],
    'depends': ['email_template', 'gt_doc_contract'],
    "website": "http://www.gnuthink.com",
    "description": """
Módulo de Gestion de Convenios, permite llevar un control de los convenios que se generan en el Gobierno
Provincial 
========================================================================================================
""",
    
    'init_xml': [],
    'data': ['doc_covenant_action_data.xml'],
    'update_xml': ['wizard/doc_covenant_cancel_view.xml',
                   'wizard/invoice_relate_view.xml',
                   'doc_covenant_sequence.xml',
                   'doc_covenant_view.xml',
#                   'doc_covenant_workflow.xml',
                   'doc_covenant_directory_data.xml',
                   'security/ir.model.access.csv',
                   'doc_covenant_stage_data.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
