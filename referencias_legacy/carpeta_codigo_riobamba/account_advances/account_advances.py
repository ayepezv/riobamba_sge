# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
#
##############################################################################

from time import strftime

from osv import osv, fields
import decimal_precision as dp
from tools.translate import _
import netsvc

class AccountVoucher(osv.osv):
    _inherit = 'account.voucher'

    def action_print_report(self, cr, uid, ids, context):
        if context is None:
            context = {}        
        report_name = context.get('report', 'report_account_advances')
        data = self.read(cr, uid, ids, [], context=context)[0]
        data['voucher_id'] = ids
        voucher = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [voucher.move_id.id], 'model': 'account.move','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.move',
            'model': 'account.move',
            'datas': datas,
            'nodestroy': True,                              
            }
     

    def onchange_journal(self, cr, uid, ids, journal_id,line_ids,tax_id,partner_id,date,amount,ttype,company_id,context=None):
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        line_obj = self.pool.get('account.voucher.line')
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        if context.get('extra_type') and context.get('extra_type') in ['advances','advances_custom']:
            return {'value': {'account_id': account_id.id} }        
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id
        vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
        vals['value'].update({'tax_id':tax_id,'amount': amount})
        currency_id = False
        if journal.currency:
            currency_id = journal.currency.id
        vals['value'].update({'currency_id': currency_id})   
        res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
        for key in res.keys():
            vals[key].update(res[key])
        if context.has_key('default_certificate_id'):
            aux = 0
            for vals_line in vals['value']['line_dr_ids']:
                move_line = move_line_obj.browse(cr, uid, vals_line['move_line_id'])
                vals['value']['line_dr_ids'][aux]['budget_id'] = move_line.budget_id_cert.id
                aux += 1
        return vals

    _columns = dict(
        extra_type = fields.char('Tipo Anticipos', size=32),
        thirdparty_name = fields.char('A nombre de', size=64),
        thirdparty = fields.boolean('Girado a otra persona ?'),
        )

    def _get_ext(self, cr, uid, context):
        return context.get('extra_type','ninguno')

    _defaults = dict(
        extra_type = _get_ext
        )





