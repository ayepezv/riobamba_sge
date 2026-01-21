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

import time

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp

class AccountBankStLine(osv.osv):
    _inherit = 'account.bank.statement.line'

    def onchange_amount(self, cr, uid, ids, amount, voucher_id):
        res = {'value': {}}
        voucher_obj = self.pool.get('account.voucher')
        vline_obj = self.pool.get('account.voucher.line')
        if not voucher_id:
            return {}
        voucher = voucher_obj.browse(cr, uid, voucher_id)
        if abs(amount) > voucher.amount:
            return {'warning': {'title': 'Alerta',
                                'message': 'No puede superar el monto.'},
                    'value': {'amount': 0}}
        voucher_obj.write(cr, uid, voucher_id, {'amount': abs(amount)})
        vline_obj.write(cr, uid, voucher.line_dr_ids[0].id, {'amount': abs(amount)})
        return {}

class StatementInvoiceLine(osv.osv_memory):
    _inherit = 'account.statement.from.invoice.lines'

    def populate_statement(self, cr, uid, ids, context=None):
        """Redefinicion de wizard para considerar las partidas presupuestarias
        """
        if context is None:
            context = {}
        statement_id = context.get('statement_id', False)
        if not statement_id:
            return {'type': 'ir.actions.act_window_close'}
        data =  self.read(cr, uid, ids, context=context)[0]
        line_ids = data['line_ids']
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}

        line_obj = self.pool.get('account.move.line')
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        currency_obj = self.pool.get('res.currency')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        line_date = time.strftime('%Y-%m-%d')
        statement = statement_obj.browse(cr, uid, statement_id, context=context)

        # for each selected move lines
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            voucher_res = {}
            ctx = context.copy()
            #  take the date for computation of currency => use payment date
            ctx['date'] = line_date
            amount = 0.0

            if line.debit > 0:
                amount = line.debit
            elif line.credit > 0:
                amount = -line.credit

            if line.amount_currency:
                amount = currency_obj.compute(cr, uid, line.currency_id.id,
                    statement.currency.id, line.amount_currency, context=ctx)
            elif (line.invoice and line.invoice.currency_id.id <> statement.currency.id):
                amount = currency_obj.compute(cr, uid, line.invoice.currency_id.id,
                    statement.currency.id, amount, context=ctx)
            context.update({'move_line_ids': [line.id],
                            'invoice_id': line.invoice.id, 'default_certificate_id': statement.certificate_id.id})
            result = voucher_obj.onchange_partner_id(cr, uid, [], partner_id=line.partner_id.id, journal_id=statement.journal_id.id, amount=abs(amount), currency_id= statement.currency.id, ttype=(amount < 0 and 'payment' or 'receipt'), date=line_date, context=context)
            voucher_res = { 'type':(amount < 0 and 'payment' or 'receipt'),
                            'name': line.name,
                            'partner_id': line.partner_id.id,
                            'journal_id': statement.journal_id.id,
                            'account_id': result.get('account_id', statement.journal_id.default_credit_account_id.id), # improve me: statement.journal_id.default_credit_account_id.id
                            'company_id':statement.company_id.id,
                            'currency_id':statement.currency.id,
                            'date':line.date,
                            'amount':abs(amount),
                            'payment_rate': result['value']['payment_rate'],
                            'payment_rate_currency_id': result['value']['payment_rate_currency_id'],
                            'period_id':statement.period_id.id,
                            'certificate_id': statement.certificate_id.id}
            voucher_id = voucher_obj.create(cr, uid, voucher_res, context=context)

            voucher_line_dict =  {}
            for line_dict in result['value']['line_cr_ids'] + result['value']['line_dr_ids']:
                move_line = line_obj.browse(cr, uid, line_dict['move_line_id'], context)
                if line.move_id.id == move_line.move_id.id:
                    voucher_line_dict = line_dict

            if voucher_line_dict:
                voucher_line_dict.update({'voucher_id': voucher_id})
                voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)

            #Updated the amount of voucher in case of partially paid invoice
            amount_res = voucher_line_dict.get('amount_unreconciled',amount)
            voucher_obj.write(cr, uid, voucher_id, {'amount':amount_res}, context=context)

            if line.journal_id.type == 'sale':
                type = 'customer'
            elif line.journal_id.type == 'purchase':
                type = 'supplier'
            else:
                type = 'general'
            statement_line_obj.create(cr, uid, {
                'name': line.name or '?',
                'amount': amount_res if amount >= 0 else -amount_res,
                'type': type,
                'partner_id': line.partner_id.id,
                'account_id': line.account_id.id,
                'statement_id': statement_id,
                'ref': line.ref,
                'voucher_id': voucher_id,
                'date': statement.date,
            }, context=context)
        return {'type': 'ir.actions.act_window_close'}    

class accountBankStatement(osv.osv):
    _inherit = 'account.bank.statement'

    _columns = {
        'certificate_id': fields.many2one('crossovered.budget.certificate',domain=[('state','=','compromised')], string="Compromiso Presupuestario"),
        'notes': fields.text('Detalle de Comprobante'),
        'reference': fields.char('Ref. Documento', size=32),
        }

    def _get_journal(self, cr, uid, context=None):
        cr.execute("SELECT journal_id FROM account_bank_statement WHERE state='confirm' ORDER BY date LIMIT 2")
        res = cr.fetchone()
        return res[0]

    _defaults = {
        'journal_id': _get_journal
        }

    _sql_constraints = [
        ('unique_reference', 'unique(reference)', 'El documento de referencia debe ser unico.')
        ]

    def print_move_multi_pay(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir la solicitud de compra
        '''        
        if not context:
            context = {}
        payment = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [payment.id], 'model': 'account.bank.statement'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.statement.move',
            'model': 'account.bank.statement',
            'datas': datas,
            'nodestroy': True,                        
            }        
        return True

    def check_lines(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if not obj.line_ids:
                raise osv.except_osv('Aviso', 'No ha ingresado un detalle de cobro/pago')
        return True

    def button_confirm_bank(self, cr, uid, ids, context=None):
        obj_seq = self.pool.get('ir.sequence')
        if context is None:
            context = {}

        for st in self.browse(cr, uid, ids, context=context):
            j_type = st.journal_id.type
            company_currency_id = st.journal_id.company_id.currency_id.id
            if not self.check_status_condition(cr, uid, st.state, journal_type=j_type):
                continue
            self.check_lines(cr, uid, [st.id], context)
#            self.balance_check(cr, uid, st.id, journal_type=j_type, context=context)
            if (not st.journal_id.default_credit_account_id) \
                    or (not st.journal_id.default_debit_account_id):
                raise osv.except_osv(_('Configuration Error !'),
                        _('Please verify that an account is defined in the journal.'))

            if not st.name == '/':
                st_number = st.name
            else:
                c = {'fiscalyear_id': st.period_id.fiscalyear_id.id}
                if st.journal_id.sequence_id:
                    st_number = obj_seq.next_by_id(cr, uid, st.journal_id.sequence_id.id, context=c)
                else:
                    st_number = obj_seq.next_by_code(cr, uid, 'account.bank.statement', context=c)

            for line in st.move_line_ids:
                if line.state <> 'valid':
                    raise osv.except_osv(_('Error !'),
                            _('The account entries lines are not in valid state.'))
            for st_line in st.line_ids:
                if st_line.analytic_account_id:
                    if not st.journal_id.analytic_journal_id:
                        raise osv.except_osv(_('No Analytic Journal !'),_("You have to assign an analytic journal on the '%s' journal!") % (st.journal_id.name,))
                if not st_line.amount:
                    continue
                st_line_number = self.get_next_st_line_number(cr, uid, st_number, st_line, context)
                self.create_move_from_st_line(cr, uid, st_line.id, company_currency_id, st_line_number, context)

            self.write(cr, uid, [st.id], {
                    'name': st_number,
                    'balance_end_real': st.balance_end
            }, context=context)
            self.log(cr, uid, st.id, _('Statement %s is confirmed, journal items are created.') % (st_number,))
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)    




