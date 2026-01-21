# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Numérigraphe SARL.
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

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp

class product_product(osv.osv):
    """Implement search methods for quantities"""
    
    _inherit = "product.product"

    def _qty_available_search(self, cr, uid, obj, name, args, context=None):
        """Search products by real stock"""
        # XXX: refactor with get_product_available?
        if context is None:
            context = {}
        fieldname, operator, value = args[0]
        
        # Sanitize input to protect from SQL injection
        if operator not in ('=', '!=', '<>', '<=', '<', '>', '>=', 'in', 'not in'):
            raise osv.except_osv(
               _('Invalid operator!'),
               _("The operator '%s' cannot be used to filter the field '%s'.") % (operator, field))
        
        # Date conditions
        from_date = context.get('from_date', False)
        to_date = context.get('to_date', False)
        date_where = ''
        date_values = []
        if from_date and to_date:
            date_where = "and date>=%s and date<=%s"
            date_values = [from_date, to_date]
        elif from_date:
            date_where = "and date>=%s"
            date_values = [from_date]
        elif to_date:
            date_where = "and date<=%s"
            date_values = [to_date]
            
        # Find the locations inside the shop/warehouse/location in the context
        if context.get('shop', False):
            cr.execute('select warehouse_id from sale_shop where id=%s', (int(context['shop']),))
            res2 = cr.fetchone()
            if res2:
                context['warehouse'] = res2[0]

        if context.get('warehouse', False):
            cr.execute('select lot_stock_id from stock_warehouse where id=%s', (int(context['warehouse']),))
            res2 = cr.fetchone()
            if res2:
                context['location'] = res2[0]

        if context.get('location', False):
            if type(context['location']) == type(1):
                location_ids = [context['location']]
            elif type(context['location']) in (type(''), type(u'')):
                location_ids = self.pool.get('stock.location').search(cr, uid, [('name','ilike',context['location'])], context=context)
            else:
                location_ids = context['location']
        else:
            location_ids = []
            wids = self.pool.get('stock.warehouse').search(cr, uid, [], context=context)
            for w in self.pool.get('stock.warehouse').browse(cr, uid, wids, context=context):
                location_ids.append(w.lot_stock_id.id)

        # build the list of ids of children of the location given by id
        if context.get('compute_child',True):
            child_location_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_ids)])
            location_ids = child_location_ids or location_ids
        else:
            location_ids = location_ids
        
        cr.execute('''
                SELECT
                    s.product_id,
                    sum(s.qty) as qty_available
                FROM
                (
                SELECT         
                    pp.id product_id,
                    COALESCE(-(sm.product_qty / uo.factor), 0.0) as qty
                FROM product_product pp
                    INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    LEFT JOIN (
                        stock_move sm
                        INNER JOIN product_uom uo ON sm.product_uom = uo.id
                    ) ON (sm.product_id = pp.id
                        AND sm.state = 'done'
                        AND sm.location_id in %s
                        ''' + date_where + ''')
                
                UNION ALL
                
                SELECT         
                    pp.id product_id,
                    COALESCE(sm.product_qty / uo.factor, 0.0) as qty
                FROM product_product pp
                    INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    LEFT JOIN (
                        stock_move sm
                        INNER JOIN product_uom uo ON sm.product_uom = uo.id
                     ) ON (sm.product_id = pp.id
                        AND sm.state = 'done'
                        AND sm.location_dest_id in %s
                        ''' + date_where + ''')
                ) AS s
                GROUP BY
                    s.product_id
                HAVING sum(s.qty) ''' + operator + " %s",
            tuple(2*([tuple(location_ids)] + date_values)) + (value,))
        
        res = cr.fetchall()
        domain = [('id', 'in', map(lambda x: x[0], res))]
        return domain

    def _virtual_available_search(self, cr, uid, obj, name, args, context=None):
        """Search Products by virtual quantity"""
        # XXX: refactor with _qty_available_search()
        # XXX: refactor with get_product_available()?
        if context is None:
            context = {}
        fieldname, operator, value = args[0]
        
        # Sanitize input to protect from SQL injection
        if operator not in ('=', '!=', '<>', '<=', '<', '>', '>=', 'in', 'not in'):
            raise osv.except_osv(
               _('Invalid operator!'),
               _("The operator '%s' cannot be used to filter the field '%s'.") % (operator, field))
        
        # Date conditions
        from_date = context.get('from_date', False)
        to_date = context.get('to_date', False)
        date_where = ''
        date_values = []
        if from_date and to_date:
            date_where = "and date>=%s and date<=%s"
            date_values = [from_date, to_date]
        elif from_date:
            date_where = "and date>=%s"
            date_values = [from_date]
        elif to_date:
            date_where = "and date<=%s"
            date_values = [to_date]
        
        # Find the locations inside the shop/warehouse/location in the context
        if context.get('shop', False):
            cr.execute('select warehouse_id from sale_shop where id=%s', (int(context['shop']),))
            res2 = cr.fetchone()
            if res2:
                context['warehouse'] = res2[0]

        if context.get('warehouse', False):
            cr.execute('select lot_stock_id from stock_warehouse where id=%s', (int(context['warehouse']),))
            res2 = cr.fetchone()
            if res2:
                context['location'] = res2[0]

        if context.get('location', False):
            if type(context['location']) == type(1):
                location_ids = [context['location']]
            elif type(context['location']) in (type(''), type(u'')):
                location_ids = self.pool.get('stock.location').search(cr, uid, [('name','ilike',context['location'])], context=context)
            else:
                location_ids = context['location']
        else:
            location_ids = []
            wids = self.pool.get('stock.warehouse').search(cr, uid, [], context=context)
            for w in self.pool.get('stock.warehouse').browse(cr, uid, wids, context=context):
                location_ids.append(w.lot_stock_id.id)

        # build the list of ids of children of the location given by id
        if context.get('compute_child',True):
            child_location_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_ids)])
            location_ids = child_location_ids or location_ids
        else:
            location_ids = location_ids

        cr.execute('''
                SELECT
                    s.product_id,
                    sum(s.qty) as qty_available
                FROM
                (
                SELECT         
                    pp.id product_id, 
                    COALESCE(-(sm.product_qty / uo.factor), 0.0) as qty
                FROM product_product pp
                    INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    LEFT JOIN (
                        stock_move sm 
                        INNER JOIN product_uom uo ON sm.product_uom = uo.id
                    ) ON sm.product_id = pp.id
                        AND sm.state in ('confirmed','waiting','assigned','done')
                        AND sm.location_id IN %s
                        ''' + date_where + '''
                
                UNION ALL
                
                SELECT         
                    pp.id product_id, 
                    COALESCE(sm.product_qty / uo.factor, 0.0) as qty
                FROM product_product pp
                    INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    LEFT JOIN (
                        stock_move sm 
                        INNER JOIN product_uom uo ON sm.product_uom = uo.id
                    ) ON sm.product_id = pp.id
                        AND sm.state in ('confirmed','waiting','assigned','done')
                        AND sm.location_dest_id IN %s
                        ''' + date_where + '''
                ) AS s 
                GROUP BY
                    s.product_id
                HAVING sum(s.qty) ''' + operator + " %s",
            tuple(2*([tuple(location_ids)] + date_values)) + (value,))
        
        res = cr.fetchall()
        domain = [('id', 'in', map(lambda x: x[0], res))]
        return domain
    
    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """Proxy to the parent model's method"""
        return super(product_product, self)._product_available(
            cr, uid, ids, field_names=field_names, arg=arg, context=context)
    
    _columns = {
        'qty_available': fields.function(
            _product_available, fnct_search=_qty_available_search,
            method=True, type='float', string='Real Stock', multi='qty_available',
            help="Current quantities of products in selected locations "
                 "or all internal if none have been selected.",
            digits_compute=dp.get_precision('Product UoM')),
        'virtual_available': fields.function(
            _product_available, fnct_search=_virtual_available_search,
            method=True, type='float', string='Virtual Stock', multi='qty_available', 
            help="Future stock for this product according to the "
                 "selected locations or all internal if none have been selected. "
                 "Computed as: Real Stock - Outgoing + Incoming.", 
                 digits_compute=dp.get_precision('Product UoM')),
    }
product_product()

