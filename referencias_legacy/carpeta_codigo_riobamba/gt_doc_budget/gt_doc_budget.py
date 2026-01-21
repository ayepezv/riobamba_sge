# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2014 Gnuthink Software Cia. Ltda. (<http://gnuthink.com>).
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

import time

from osv import osv, fields

class ProjectPaymentRequest(osv.Model):
    _name = 'project.payment.request'
    _columns = dict(
        sequence = fields.char('Número', size=32, required=True, readonly=True),
        name = fields.char('Concepto', size=128, required=True),        
        date = fields.datetime('Fecha de Solicitud', required=True, readonly=True),
        user_id = fields.many2one('res.users', 'Elaborado Por', required=True, readonly=True),
        partner_id = fields.many2one('res.partner', 'Proveedor',
                                     required=True,
                                     select=True, domain=[('supplier','=',True)]),
        date_invoice = fields.date('Fecha de Emisión de Factura', required=True),
        invoice_number = fields.char('Número de Factura', size=17, required=True, help="Formato a usar: 001-001-0000000001"),
        amount = fields.float('Monto'),
        certificate_id = fields.many2one('crossovered.budget.certificate',
                                         string='Presupuesto Referencial',
                                         required=True, select=True),
        department_id = fields.many2one('hr.department','Unidad Operativa', required=True),
        project_id = fields.many2one('project.project', string='Proyecto', required=True),
        state = fields.selection([('draft','Borrador'),
                                  ('request','Solicitado'),
                                  ('approved', 'Aprobado')], string='Estado', readonly=True),
        )

    def _get_user(self, cr, uid, context):
        return uid

    _defaults = dict(
        date = time.strftime('%Y-%m-%d %H:%M:%S'),
        sequence = '/',
        state = 'draft',
        user_id = _get_user
        )





