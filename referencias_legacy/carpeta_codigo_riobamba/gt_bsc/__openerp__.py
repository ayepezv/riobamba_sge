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
    'name': 'Balanced Score Card',
    'version': '0.1',
    'category': 'Proyectos',
    'complexity': "expert",
    'description': "Balanced Score Card",
    'author': 'Mario Chogllo & Carlos Ordoñez',
    'depends': ['gt_hr_base','gt_project_project'],
    'init_xml': [],
    'update_xml': [
                   'security/bsc_groups.xml',
                   'bsc_view.xml',
                   ],
    'demo_xml': [],
    'test': [],
    'js': [
           'static/src/js/amcharts/amcharts.js',
           'static/src/js/amcharts/serial.js',
           'static/src/js/amcharts/gauge.js',
           'static/src/js/main.js',
           ],
    'css': [
            'static/src/css/main.css',
            ],
    'qweb': [
             'static/src/xml/main.xml',
             ],
    'installable': True,
    'auto_install': False,
    }
