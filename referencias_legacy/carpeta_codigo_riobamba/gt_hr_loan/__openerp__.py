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
    'name': "Recursos Humanos - Prestamo",
    'version': '1.0',
    'category': 'Human Resources',
    'complexity': "normal",
    'description': """
Usa la informacion sobre prestamos y otros pagos del empleado.
==============================================================

    * Prestamos,
    * Pagos Diferenciados,

Esta informacion es utilizada para el rol de pagos.
    """,
    'author': 'Gnuthink Software Labs Cia. Ltda.',
    'website': 'http://www.gnuthink.com',
    'depends': ['hr_payroll',
                'gt_hr_base',
                'gt_hr_ie'],
    'init_xml': [],
    'update_xml': [
        'gt_hr_loan_view.xml',
        'security/ir.model.access.csv',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
