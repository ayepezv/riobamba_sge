from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
from common import AdditionalDiscountable

class sale_order(AdditionalDiscountable, osv.osv):

    _inherit = 'sale.order'

    _tax_column = 'tax_id'
    _line_column = 'order_line'

    def _amount_all(self, *args, **kwargs):
        return self._amount_all_generic(sale_order, *args, **kwargs)

    _columns = {
            'add_disc':fields.float('Additional Discount(%)',digits=(4,2), readonly=True, states={'draft': [('readonly', False)]}),
            'add_disc_amt': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Additional Disc Amt',
                                            store =True,multi='sums', help="The additional discount on untaxed amount."),
            'amount_untaxed': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Untaxed Amount',
                                              store = True,multi='sums', help="The amount without tax."),
            'amount_net': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Net Amount',
                                              store = True,multi='sums', help="The amount after additional discount."),
            'amount_tax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Taxes',
                                          store = True,multi='sums', help="The tax amount."),
            'amount_total': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Total',
                                            store = True,multi='sums', help="The total amount."),
        }

    _defaults={
               'add_disc': 0.0,
               }

    def _make_invoice(self, cr, uid, order, lines, context=None):
        """Add a discount in the invoice after creation, and recompute the total
        """
        inv_obj = self.pool.get('account.invoice')
        # create the invoice
        inv_id = super(sale_order, self)._make_invoice(cr, uid, order, lines, context)
        # modify the invoice
        inv_obj.write(cr, uid, [inv_id], {'add_disc': order.add_disc or 0.0}, context)
        inv_obj.button_compute(cr, uid, [inv_id])
        return inv_id

