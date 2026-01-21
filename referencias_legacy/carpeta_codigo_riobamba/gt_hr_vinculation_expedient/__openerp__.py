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
    "name": "Vinculation Expedient",
    "version": "1.0",
    "author": "Mario Chogllo",
    'website': 'http://www.gnuthink.com',
    "category": "TTHH",
    'complexity': "easy",
    'images': [],
    'depends': ['gt_hr_vinculation','gt_doc_expedient'],
    "website": "http://www.gnuthink.com",
    "description": """
Módulo de proceso de seleccion y contratacion, integrado con tramites 
========================================================================================================
""",
    
    'init_xml': [],
    'data': [],
    'update_xml': [
        'vinculation_view.xml',
        'security/ir.model.access.csv',
                   ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
