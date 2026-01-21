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
    'name': 'GOB Implementation',
    'version': '1.0',
    'category': 'Modulos Generales/Base',
    'description': """
    """,
    'author': 'Gnuthink Cia. Ltda.',
    'website': 'http://www.gnuthink.com',
    'depends': ['gt_government_procedure','gt_budget','gt_project_project','gt_stock','gt_hr_payroll_account'],
    'init_xml': [],
    'update_xml': [
#        'wizard/gpa_complemento_view.xml',
        'wizard/gob_view.xml',
        ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
