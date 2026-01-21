# -*- coding: utf-8 -*- 
import logging

import decimal_precision as dp

from openerp.osv import fields
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round

from common import AdditionalDiscountable

class account_invoice(AdditionalDiscountable, orm.Model):

    _inherit = 'account.invoice'
    _description = 'Invoice'

    _line_column = 'invoice_line'
    _tax_column = 'invoice_line_tax_id'
    _amount_all_discount_taxes = False # done and written on tax lines

    __logger = logging.getLogger(_inherit)

    def record_currency(self, record):
        """Return currency browse record from an invoice record (override)."""
        return record.currency_id

    def _amount_all(self, *args, **kwargs):
        return self._amount_all_generic(account_invoice, *args, **kwargs)

    def _get_invoice_line(self, cr, uid, ids, context=None):
        """copy pasted from account_invoice"""
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
  
    def _get_invoice_tax(self, cr, uid, ids, context=None):
        """copy pasted from account_invoice"""
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()
    

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines) -> move_lines
        Hook method to be overridden in additional modules to verify and possibly alter the
        move lines to be created by an invoice, for special cases.
        :param invoice_browse: browsable record of the invoice that is generating the move lines
        :param move_lines: list of dictionaries with the account.move.lines (as for create())
        :return: the (possibly updated) final move_lines to create for this invoice
         
        Actually move_lines is a list op tuples with each tuple having three
        elements. The third element is the value dictionary used to create one
        line. So move_lines will look like this:
        [(0, 0, {'debit': ......}), (0, 0, {<values for second line>}), ..]

        Taxes are a special problem, because when this function is called,
        the tax move lines have the discount already applied. There is no
        easy way to recogize these lines, therefore we retrieve all tax
        account_id's used and exclude them from being discounted (again).
        """
        discount = invoice_browse.add_disc
        if  not discount:
            return move_lines
        # Only if there is a additional discount will we loop
        # over all lines to adjust the amounts
        # We assume a line will nly contain either credit, or debit,
        # never both.
        precision_model = self.pool.get('decimal.precision') 
        precision = precision_model.precision_get(cr, uid, 'Account')
        discount_factor = 1.0 - (discount / 100.0)
        balance_credit = True
        total_credit = 0.0
        total_debit = 0.0
        # Get taxt account id's
        tax_account_ids = []
        ait_model = self.pool.get('account.invoice.tax')
        ait_lines = ait_model.move_line_get(cr, uid, invoice_browse.id)
        for ait_line in ait_lines:
            tax_account_ids.append(ait_line['account_id'])
        for move_line in move_lines:
            # Check format
            assert len(move_line) > 2, (
                _('Invalid move line %s') % str(move_line))
            vals = move_line[2]
            # Do not change tax lines (but include them in totals):
            if  vals['account_id'] in tax_account_ids:
                if  vals['debit']:
                    total_debit += vals['debit']
                if  vals['credit']:
                    total_credit += vals['credit']
                continue
            # Handle debtor/creditor
            # We don't want to recompute to make sure open amount will
            # be exactly the same as on invoice.
            if  invoice_browse.account_id.id == vals['account_id']:
                if  vals['debit']:
                    assert not vals['credit'], (
                        _('Can not have credit and debit in same move line'))
                    vals['debit'] = invoice_browse.amount_total
                    total_debit += vals['debit']
                else:
                    assert not vals['debit'], (
                        _('Can not have debit and credit in same move line'))
                    vals['credit'] = invoice_browse.amount_total
                    total_credit += vals['credit']
                    balance_credit = False
            else:
                if  vals['credit']:
                    vals['credit'] = float_round(
                        vals['credit'] * discount_factor, precision)
                    total_credit += vals['credit']
                if  vals['debit']:
                    vals['debit'] = float_round(
                        vals['debit'] * discount_factor, precision)
                    total_debit += vals['debit']
            if  vals['amount_currency']:
                vals['amount_currency'] = float_round(
                    vals['amount_currency'] * discount_factor, precision)
            if  vals['tax_amount']:
                vals['tax_amount'] = float_round(
                    vals['tax_amount'] * discount_factor, precision)                        
        # Check balance
        difference = total_debit - total_credit
        if  abs(difference) > 10 ** -4:
            # Find largest credit or debit amount and adjust for rounding:
            largest_vals = None
            largest_amount = 0.0
            for move_line in move_lines:
                vals = move_line[2]
                if  balance_credit:
                    if  vals['credit'] and vals['credit'] > largest_amount:
                        largest_vals = vals
                else:
                    if  vals['debit'] and vals['debit'] > largest_amount:
                        largest_vals = vals
            assert largest_vals, _('No largest debit or credit found')
            if  balance_credit:
                largest_vals['credit'] = (
                    largest_vals['credit'] + difference)
                if  largest_vals['tax_amount']:
                    largest_vals['tax_amount'] = (
                            largest_vals['tax_amount'] + difference)
            else:
                largest_vals['debit'] = (
                    largest_vals['debit'] - difference)
                if  largest_vals['tax_amount']:
                    largest_vals['tax_amount'] = (
                            largest_vals['tax_amount'] - difference)
            self.__logger.info(
                _('Modified move line %s to prevent unbalanced move with'
                  ' difference %d') % (str(largest_vals), difference))
        return move_lines    

    _columns={
            'add_disc':fields.float('Additional Discount(%)',digits=(4,2),readonly=True, states={'draft':[('readonly',False)]}),
            'add_disc_amt': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Additional Disc Amt',
                                            store =True,multi='sums', help="The additional discount on untaxed amount."),
            'amount_net': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Net Amount',
                                              store = True,multi='sums', help="The amount after additional discount."),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
              },
              multi='all'),
          'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
              },
              multi='all'),
          'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
              store={
                  'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line', 'add_disc'], 20),
                  'account.invoice.tax': (_get_invoice_tax, None, 20),
                  'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
              },
              multi='all'),

              }

    _defaults={
               'add_disc': 0.0,
               }


class account_invoice_tax(orm.Model):

    _inherit = 'account.invoice.tax'

    def compute(self, cr, uid, invoice_id, context=None):
        precision_model = self.pool.get('decimal.precision') 
        precision = precision_model.precision_get(cr, uid, 'Account')
        tax_grouped = super(
            account_invoice_tax, self).compute(cr, uid, invoice_id, context)
        tax_pool = self.pool.get('account.tax')
        cur_pool = self.pool.get('res.currency')
        tax_ids = set([key[0] for key in tax_grouped])
        taxes = tax_pool.browse(cr, uid, tax_ids)
        if taxes and not all(t.type == 'percent' for t in taxes):
            raise osv.except_osv(_('Discount error'),
                 _('Unable (for now) to compute a global '
                'discount with non percent-type taxes'))
        invoice = self.pool.get('account.invoice').browse(
            cr, uid, invoice_id, context=context)
        add_disc = invoice.add_disc
        discount_factor = 1.0 - (add_disc / 100.0)
        for line in tax_grouped:
            for key in ('tax_amount', 'base_amount', 'amount', 'base'):
                val = tax_grouped[line][key]
                tax_grouped[line][key] = float_round(
                    val * discount_factor, precision)
        # print tax_grouped
        return tax_grouped

