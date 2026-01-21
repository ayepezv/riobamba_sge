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
    "name": "Tramitologia",
    "version": "1.0",
    "author": "Gnuthink Soft. Labs Cia Ltda",
    'website': 'http://www.gnuthink.com',
    "category": "GPA",
    'complexity': "easy",
    'images': [],
    'depends': ['process','board','gt_document','gt_document_manager','email_template','hr','document',
                'report_webkit','account','country_ec'],
    "website": "http://www.gnuthink.com",
    "description": """
Módulo de Gestion de Tramites, permite llevar un control de tramites internos y externos que se generan en el gobierno
provincial 
========================================================================================================
""",
    
    'init_xml': [],
    'data': ['doc_expedient_action_data.xml','doc_expedient_task_action_data.xml'],
    'update_xml': [#'wizard/doc_expedient_task_init_view.xml',
                   'wizard/doc_expedient_cancel_view.xml',
                   'wizard/doc_expedient_draft_view.xml',
                   'wizard/doc_task_cancel_view.xml',
                   'security/ir.model.access.csv',
                   'doc_expedient_sequence.xml',
                   'doc_expedient_view.xml',
                   'doc_expedient_workflow.xml',
                   'doc_expedient_directory_data.xml',
                   'doc_expedient_request.data.xml',
                   'report/report_webkit_html_view.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
