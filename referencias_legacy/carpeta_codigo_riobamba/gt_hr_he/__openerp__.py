#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'RRHH - Ingreso de Horas Laboradas y Extras',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """Ingreso de Horas
    * Horas Laboradas
    * Horas Extras
     """,
    'author':'Gnuthink Software Cia. Ltda',
    'website':'http://www.gnuthink.com',
    'depends': ['gt_hr_base','gt_hr_ie','gt_hr_payroll_ec'],
    'init_xml': [
    ],
    'update_xml': [
        'security/he_group.xml',
        'security/ir.model.access.csv',
        'security/security_ir_rule.xml',
        'wizard/return_alone_view.xml',
        'hr_payroll_he_view.xml',
        'he_data.xml',
#        'report/report.xml',
        'wizard/he_import_xls_view.xml',
        'he_report.xml',
        'alone_sequence.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
