import decimal_precision as dp
from osv import fields, osv
from common import AdditionalDiscountable
from tools.translate import _

class account_invoice(AdditionalDiscountable, osv.Model):

    _inherit = "account.invoice"
    _description = 'Invoice'

    _line_column = 'invoice_line'
    _tax_column = 'invoice_line_tax_id'

    def record_currency(self, record):
        """Return currency browse record from an invoice record (override)."""
        return record.currency_id

    def _amount_all(self, *args, **kwargs):
         return super(account_invoice, self)._amount_all(*args, **kwargs)

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


#class account_invoice_tax(osv.Model):

#    _inherit = 'account.invoice.tax'

#    def compute(self, cr, uid, invoice_id, context=None):
#        tax_grouped = super(account_invoice_tax, self).compute(cr, uid, invoice_id, context)
#        tax_pool = self.pool.get('account.tax')
#        cur_pool = self.pool.get('res.currency')
#        tax_ids = set([key[0] for key in tax_grouped])
#        taxes = tax_pool.browse(cr, uid, tax_ids)
#        if taxes and not all(t.type == 'percent' for t in taxes):
#            raise osv.except_osv(_('Discount error'),
#                 _('Unable (for now) to compute a global '
#                'discount with non percent-type taxes'))
#        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
#        add_disc = invoice.add_disc
#        cur = invoice.currency_id
#        for line in tax_grouped:
#            for key in ('tax_amount', 'base_amount', 'amount', 'base'): #FIXME?
#                val = tax_grouped[line][key]
#                tax_grouped[line][key] = cur_pool.round(cr, uid, cur, val * (1.0 - add_disc / 100.0))
#        print tax_grouped
#        return tax_grouped

