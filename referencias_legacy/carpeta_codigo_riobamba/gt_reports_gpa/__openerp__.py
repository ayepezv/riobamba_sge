# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Cristian Salamea.
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
    "name" : "Reportes GPA",
    "version" : "0.1.0",
    "author" : "Gnuthink Cia. Ltda.",
    "category": 'Reports',
    'website': 'www.gnuthink.com',
    "description": "Reportes GPA",
    'init_xml': [],
    "depends" : ['gt_doc_contract', 'gt_doc_covenant'],
    "update_xml": ['gt_reports_gpa_view.xml'],
    'installable': True,
}
