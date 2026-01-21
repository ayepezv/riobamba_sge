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
from report import report_sxw
from osv import osv
import pooler
import itertools
import operator
from operator import itemgetter

class move(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(move, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.sum_acurred = 0.00
        self.sum_paid = 0.00      
        self.localcontext.update({
            'time': time,
            'get_analytic_lines': self.get_analytic_lines,
            'get_lines': self.get_lines,
            'get_budget_lines': self.get_budget_lines,
            'get_user': self.get_user,
            'get_invoice_data': self.get_invoice_data,
            'suma_debit': self.suma_debit,
            'suma_credit': self.suma_credit,
            'suma_acurred': self.suma_acurred,
            'suma_paid': self.suma_paid,
            'get_budget_title': self.get_budget_title,
            'get_partners': self.get_partners
        })

    def get_partners(self, move):
        partners = [line.partner_id.name for line in move.line_ids]
        return ', '.join(partners)
        
    def get_budget_title(self, move):
        """
        Decide entre PAGADO - RECAUDADO
        """
        title = "PAGADO"
        if move.journal_id.type in ['bank', 'cash']:
            def_acc = move.journal_id.default_debit_account_id
            for line in move.move_line_ids:
                if line.account_id.id == def_acc.id:
                    if line.debit > 0:
                        title = "RECAUDADO"
                        break
        return title

    def suma_debit(self):
        return self.sum_debit or 0.00

    def suma_credit(self):
        return self.sum_credit or 0.00
    
    def suma_acurred(self):
        return self.sum_acurred or 0.00
    
    def suma_paid(self):
        return self.sum_paid or 0.00
    
    def set_context(self, objects, data, ids, report_type=None):
        #Your code goes here
        return super(move, self).set_context(objects, data, ids, report_type=report_type)

    def get_invoice_data(self, move):
        """
        Informacion de documentos de pago en asiento contable
        Factura
        Retencion
        """
        data = []
        invoice = move.line_id[0] and move.line_id[0].invoice and move.line_id[0].invoice
        if not invoice:
            return data
        if invoice.reference_type == 'invoice_partner':
            texto = ' '.join(['FACTURA', invoice.supplier_number, 'AUTORIZACION', invoice.auth_inv_id.name])
            data.append({'date': invoice.date_invoice, 'name': texto, 'amount': invoice.amount_pay})
        if invoice.reference_type == 'multi_invoice':
            for line in invoice.invoice_line:
                texto = ' '.join(['FACTURA', line.invoice_number, 'AUTORIZACION', line.auth_id.name])
                data.append({'date': line.date_invoice, 'name': texto, 'amount': line.price_total})    
        if invoice.retention_id:
            ret = invoice.retention_id
            data.append({'date': ret.date, 'name': 'RETENCION %s' % ret.number, 'amount': ret.amount_total})
        return data

    def get_analytic_lines(self, move, data, use):
        """
        Informacion de centros de costos en asiento contable
        cada linea del asiento tiene lineas analiticas
        """
        line_data = {}
        lines = []
        amount=0
        for line in move.line_id:
            for al in line.analytic_lines:
                if al.amount == 0:
                    continue
                if not al.account_id.usage == use:
                    continue
                amount+=abs(al.amount)
                line_data = {'acc_name': al.account_id.complete_name,
                             'code': use=='budget' and al.account_id.code or al.general_account_id.code,
                             'amount': abs(al.amount),
                             'name': al.name}                            
                lines.append(line_data)
        if not lines:
            lines.append({'code':'*', 'acc_name': 'SIN APLICACION'})
            return lines   
        return lines

    def get_budget_lines(self, move, data, use):
        """
        Informacion de presupuestos aplicados a los detalles
        budget_id: relacion contra linea de compromiso presupuestario
        return: [{'code_completo': 'ABCD', 'name': 'PARTIDA', 'amount_acurred': 0, 'amount_paid': 0}]
        """
        datas = []
        data_budget = {}
        self.sum_acurred = 0
        self.sum_paid = 0
        for line in move.move_line_ids:
            if not line.budget_id:
                continue
            budget = line.budget_id.budget_line_id            
            if not data_budget.get(budget.id):
#                data_budget.update({budget.id: {'code': budget.code, 'name': budget.name, 'amount_acurred': 0, 'amount_paid': 0}})
                data_budget[budget.id] = {'code': budget.code, 'name': budget.name, 'amount_acurred': 0, 'amount_paid': 0}
            accured = line.budget_accrued and line.debit+line.credit or 0.00
            paid = line.budget_paid and line.debit+line.credit or 0.00
            data_budget[budget.id]['amount_acurred'] += accured
            data_budget[budget.id]['amount_paid'] += paid
            self.sum_acurred += accured
            self.sum_paid += paid            
        datas = [val for k, val in data_budget.items()]
        return datas        
    
    def get_lines(self, statement):   
        data_lines = {}
        data_lines_c = {}
        move_lines = []
        lines_data = []
        lines_data_c = []
        # payable - receivable
        inv_id = False
        move_lines += statement.move_line_ids
        for line in statement.line_ids:
            if not line.voucher_id:
                continue
            move_lines += line.voucher_id.move_ids
            for li in line.voucher_id.line_cr_ids:
                if li.move_line_id.journal_id.type in ['bank','cash']:
                    continue
                if not inv_id:
                    inv_id = li.move_line_id.invoice.id
                elif li.move_line_id.invoice.id == inv_id:
                    continue
                if not li.move_line_id.period_id.special:
                    move_lines += li.move_line_id.move_id.line_id
            for li in line.voucher_id.line_dr_ids:
                if not li.move_line_id.period_id.special:
                    move_lines += li.move_line_id.move_id.line_id
        move_lines = list(set(move_lines))
        for line in move_lines:
            if line.debit == 0 and line.credit == 0:
                continue
            if line.debit != 0:
                if not data_lines.get(line.account_id.code):
                    data_lines[line.account_id.code] = {'code': line.account_id.code, 'name': line.account_id.name, 'debit': line.debit, 'credit': 0}
                else:
                    data_lines[line.account_id.code]['debit']+=line.debit
            else:
                if not data_lines_c.get(line.account_id.code) and line.credit != 0:
                    data_lines_c[line.account_id.code] = {'code': line.account_id.code, 'name': line.account_id.name, 'credit': line.credit, 'debit': 0}
                else:
                    data_lines_c[line.account_id.code]['credit']+=line.credit
        values = data_lines.itervalues()
        values_c = data_lines_c.itervalues()
        for line in values_c:
            lines_data_c.append(line)
            self.sum_credit += line['credit']
        for line in values:
            lines_data.append(line)
            self.sum_debit += line['debit']
        newlistc = sorted(lines_data_c, key=itemgetter('debit','code'))
        newlist = sorted(lines_data, key=itemgetter('credit','code'))
        return newlist+newlistc

    def get_user(self, move):
        user_name = '*'
        user_pool = pooler.get_pool(self.cr.dbname).get('res.users')
        if move.line_id and move.line_id[0] and move.line_id[0].invoice:
            user_name = move.line_id[0].invoice.user_id.name
        else:
            self.cr.execute("select create_uid from account_move where id=%s" % move.id)
            data = self.cr.fetchone()
            user = user_pool.browse(self.cr, self.uid, data[0])
            user_name = user.name
        return user_name
   
report_sxw.report_sxw('report.account.statement.move','account.bank.statement','addons/gt_payment_multi/report_move.rml',parser=move)

