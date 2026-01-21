# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import osv, fields

class WizardPaymentTaxes(osv.TransientModel):
    _inherit = 'account.common.report'
    _name = 'wizard.payment.taxes'
    _description = 'Asistente para Pago de Impuestos'

    _columns = {
        'partner_id': fields.many2one('res.partner',
                                      string='Servicio de Rentas Internas',
                                      readonly=True),
        'certificate_id': fields.many2one('budget.certificate',
                                          string='Compromiso Presupuestario'),
        'journal_id': fields.many2one('account.journal', string='Banco', required=True),
        'date': fields.date('Fecha de Pago', required=True)
        }

    def _get_partner(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id.tax_company_id and user.company_id.tax_company_id.id or False

    _defaults = {
        'partner_id': _get_partner
        }

    def action_payment_taxes(self, cr, uid, ids, context=None):
        currency_obj = self.pool.get('res.currency')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        move_line_obj = self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        currency_pool = self.pool.get('res.currency')

        wiz = self.browse(cr, uid, ids, context)[0]
        period = wiz.period_from
        sri = wiz.partner_id
        journal = wiz.journal_id
        amount = 0.00
        currency_id = journal.company_id.currency_id.id
        company_currency = journal.company_id.currency_id.id
        mov_ids = move_line_obj.search(cr, uid, [('partner_id','=',sri.id),
                                                ('period_id','=',period.id),
                                                ('reconcile_id','=',False),
                                                ('date','>=', period.date_start),
                                                ('date','<=',period.date_stop)])
        context.update({'move_line_ids': mov_ids})
        data_lines = []
        periodp_id = period_obj.find(cr, uid, dt=wiz.date)[0]
        voucher_res = {
            'type': 'payment',
            'name': 'Pago SRI %s' % period.name,
            'journal_id': journal.id,
            'account_id': journal.default_credit_account_id.id,
            'company_id': journal.company_id.id,
            'partner_id': sri.id,
            'currency_id': currency_id,
            'date': wiz.date,
            'period_id': periodp_id,
            'state': 'draft',
            'narration': 'Por pago de impuestos del mes de %s, desde cuenta: %s' % (period.name, journal.name)
            }
        voucher_id = voucher_obj.create(cr, uid, voucher_res, context=context)
        for line in move_line_obj.browse(cr, uid, mov_ids):
            if line.reconcile_partial_id and line.amount_residual_currency < 0:
                # skip line that are totally used within partial reconcile
                continue
            if line.currency_id and currency_id==line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = line.amount_residual_currency and abs(line.amount_residual_currency) or amount_original
            else:
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual))
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': amount_original,#amount_unreconciled, #(move_line_found == line.id) and min(price, amount_unreconciled) or 0.0,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
                'budget_id': False,
                'voucher_id': voucher_id,
                'reconcile': True,
            }
            voucher_line_obj.create(cr, uid, rs)
        return {
              'name': "Pago de Impuestos del mes de %s" % period.name,
              'view_type': 'form',
              "view_mode": 'tree,form',
              'res_model': 'account.voucher',
              'type': 'ir.actions.act_window',
              'domain': [('id','=',voucher_id),('type','=','payment')],
              'context': {'type':'payment'},
              }            

