# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2014 (<http://www.gnuthink.com>).
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
import decimal_precision as dp


class AccountCashfund(osv.Model):
    _name = 'account.cashfund'
    DP = dp.get_precision('Account')

    def action_compute(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {}, context)
        return True

    def action_reconcile(self, cr, uid, ids, context=None):
        """
        Metodo que concilia las cuentas por pagar de
        facturas y egresos, los totales deben ser iguales
        CHECK: revisar si el raise es correcto
        """
        seq_obj = self.pool.get('ir.sequence')
        period_obj = self.pool.get('account.period')
        line_obj = self.pool.get('account.move.line')
        for obj in self.browse(cr, uid, ids, context):
            number = seq_obj.get(cr, uid, 'account.cashfund')
            self.write(cr, uid, [obj.id], {'name': number, 'state': 'posted'})
        return True

    def action_print_report(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir comprobante
        '''        
        if not context:
            context = {}
        cf = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [cf.id], 'model': 'account.cashfund'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.cashfund',
            'model': 'account.cashfund',
            'datas': datas,
            'nodestroy': True,                        
            }                

    def _compute_all(self, cr, uid, ids, fields, args, context):
        """
        Metodo que calcula el total de las facturas y egresos
        a conciliar
        """
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {'invoice_total': 0,
                           'voucher_total': 0}
            for inv in obj.invoice_ids:
                res[obj.id]['invoice_total'] += inv.amount_pay
            for vou in obj.voucher_ids:
                res[obj.id]['voucher_total'] += vou.amount
        return res

    def _get_move_lines(self, cr, uid, ids, fields, args, context):
        res = {}
        for obj in self.browse(cr, uid, ids):
            lines = []
            res[obj.id] = []
            for inv in obj.invoice_ids:
                if inv.move_id:
                    lines += [line.id for line in inv.move_id.line_id]
            for vou in obj.voucher_ids:
                if vou.move_id:
                    lines += [line.id for line in vou.move_id.line_id]
            res[obj.id] = lines
        return res

    _columns = {
        'name': fields.char('Número', size=32, required=True, readonly=True),
        'date': fields.date('Fecha', required=True),
        'type': fields.selection([('caja', 'Caja Chica'),
                                  ('fondo','Fondo Rotativo')], string='Tipo', required=True),
        'period_id': fields.many2one('account.period', string='Periodo', required=True),
        'partner_id': fields.many2one('res.partner', string='Responsable', required=True),
        'invoice_ids': fields.one2many('account.invoice', 'cashfund_id', 'Facturas'),
        'voucher_ids': fields.one2many('account.voucher', 'cashfund_id', 'Egresos'),
        'invoice_total': fields.function(_compute_all, method=True, string='Total Facturas',
                                         multi='cashfund', digits_compute=DP),
        'voucher_total': fields.function(_compute_all, method=True, string='Total Egreso',
                                         multi='cashfund', digits_compute=DP),
        'line_ids': fields.function(_get_move_lines, method=True, string="Detalle Contable",
                                    type="one2many", relation="account.move.line"),
        'notes': fields.text('Observaciones'),
        'state': fields.selection([('draft','Borrador'),
                                   ('posted','Validado')], string='Estado', readonly=True),
        }

    def _get_type(self, cr, uid, context=None):
        return context.get('type')

    _defaults = {
        'name': '/',
        'state': 'draft',
        'type': _get_type,
        }

    def onchange_date(self, cr, uid, ids, date):
        if not date:
            return {}
        res = {'value': {'period_id': False}}
        period_obj = self.pool.get('account.period')
        res['value']['period_id'] = period_obj.find(cr, uid, date)[0]
        if not res:
            res['value']['period_id'] = period_obj.find(cr, uid)[0]
        return res


class AccountInvoice(osv.Model):

    _inherit = 'account.invoice'

    _columns = {
        'cashfund_id': fields.many2one('account.cashfund', 'Fondo'),
        }


class AccountVoucher(osv.Model):

    _inherit = 'account.voucher'

    _columns = {
        'cashfund_id': fields.many2one('account.cashfund', 'Fondo'),
        }

