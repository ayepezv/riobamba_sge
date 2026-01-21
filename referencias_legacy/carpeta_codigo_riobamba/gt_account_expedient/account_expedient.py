# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2014 Cristian Salamea.
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

from osv import osv, fields
from tools.translate import _


class AccountInvoice(osv.osv):

    _inherit = 'account.invoice'

    _columns = {
        'tramite_id': fields.many2one('doc_expedient.expedient', 'Trámite Relacionado'),
        }

    def invoice_pay_customer(self, cr, uid, ids, context=None):
        """
        Redefinicion para cargar por defecto el compromiso
        presupuestario en el voucher
        """
        if not ids: return []
        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'context': {
                'default_partner_id': inv.partner_id.id,
                'default_amount': inv.residual,
                'default_name':inv.name,
                'close_after_process': True,
                'invoice_type':inv.type,
                'invoice_id':inv.id,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'default_certificate_id': inv.certificate_id.id,
                'default_tramite_id': inv.tramite_id.id,
                'narration': inv.certificate_id.description
                }
        }        

    def create_expedient_task(self, cr, uid, ids, context=None):
        """
        Metodo que implementa la creacion de tareas en el tramite
        relacionado.
        """
        expedient_obj = self.pool.get('doc_expedient.expedient')
        task_obj = self.pool.get('doc_expedient.task')
        employee_obj = self.pool.get('hr.employee')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        emp_id = employee_obj.search(cr, uid, [('user_id','=',uid)])
        if not emp_id:
            raise osv.except_osv('Configuración', 'Su usuario no esta configurado correctamente, por favor comuniquese con el administrador.')
        employee = employee_obj.browse(cr, uid, emp_id[0])
        employee_id = emp_id[0]
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context):
            if not inv.tramite_id:
                continue
            task_data = {
                'name': 'done',
                'other_action': 'Validación de Factura',
                'other_action_chk': True,
                'expedient_id': inv.tramite_id.id,
                'department': user.context_department_id.id,
                'employee_id': employee_id,
                'job_id': employee.job_id.id,
                'state': 'done',
                'description': ' '.join(['PROVEEDOR:', inv.partner_id.name, '\nFACTURA N:', inv.supplier_number,
                                         '\nMONTO:', inv.currency_id.symbol, str(inv.amount_total)]),
                'assigned_user_id':uid,
                }
            task_obj.create(cr, uid, task_data)
        return True


class AccountVoucher(osv.osv):

    _inherit = 'account.voucher'

    _columns = {
        'tramite_id': fields.many2one('doc_expedient.expedient', 'Trámite Relacionado')
        }

    def create_expedient_task(self, cr, uid, ids, context=None):
        """
        Metodo que implementa la creacion de tareas en el tramite
        relacionado.
        """
        expedient_obj = self.pool.get('doc_expedient.expedient')
        task_obj = self.pool.get('doc_expedient.task')
        employee_obj = self.pool.get('hr.employee')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        emp_id = employee_obj.search(cr, uid, [('user_id','=',uid)])
        if not emp_id:
            raise osv.except_osv('Configuración', 'Su usuario no esta configurado correctamente, por favor comuniquese con el administrador.')
        employee = employee_obj.browse(cr, uid, emp_id[0])
        employee_id = emp_id[0]
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context):
            if not inv.tramite_id:
                continue
            task_data = {
                'name': 'done',
                'other_action': 'Contabilización de Pago',
                'other_action_chk': True,
                'expedient_id': inv.tramite_id.id,
                'department': user.context_department_id.id,
                'employee_id': employee_id,
                'job_id': employee.job_id.id,
                'state': 'done',
                'description': ' '.join(['PROVEEDOR:', inv.partner_id.name, '\nREF DE PAGO:', inv.name,
                                         '\nFECHA DE PAGO:', inv.date]),
                'assigned_user_id':uid,
                }
            task_obj.create(cr, uid, task_data)
        return True        



