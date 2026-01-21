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

class stock_location(osv.osv):
    """Implement search methods for quantities"""

    _inherit = "stock.location"

    def _stock_real_search(self, cr, uid, obj, name, args, context=None):
        """Search Locations by real stock"""
        # XXX: maybe refactor with product.get_product_available()?
        if context is None:
            context = {}
        fieldname, operator, value = args[0]
        
        # Sanitize input to protect from SQL injection
        if operator not in ('=', '!=', '<>', '<=', '<', '>', '>=', 'in', 'not in'):
            raise osv.except_osv(
               _('Invalid operator!'),
               _("The operator '%s' cannot be used to filter the field '%s'.") % (operator, field))
        
        # Product conditions
        if context.get('product_id'):
            product_where = "AND product_id=%s "
            product_value = [context.get('product_id')]
        else:
            product_where = "AND %s "
            product_value = ['TRUE']
        
        # Production lot conditions
        if context.get('prodlot_id'):
            prodlot_where = "AND prodlot_id=%s "
            prodlot_value = [context.get('prodlot_id')]
        else:
            prodlot_where = "AND %s "
            prodlot_value = ['TRUE']
        
        # Date conditions
        from_date = context.get('from_date', False)
        to_date = context.get('to_date', False)
        date_where = ''
        date_values = []
        if from_date and to_date:
            date_where = "AND date>=%s and date<=%s "
            date_values = [from_date, to_date]
        elif from_date:
            date_where = "AND date>=%s "
            date_values = [from_date]
        elif to_date:
            date_where = "and date<=%s "
            date_values = [to_date]
        
        cr.execute('''
            SELECT
                s.location_id,
                sum(s.qty) as qty_available
            FROM
                (
                SELECT
                    sl.id as location_id, 
                    COALESCE (-(sm.product_qty / uo.factor), 0) as qty
                FROM
                    stock_location sl
                    LEFT JOIN (stock_move sm
                        INNER JOIN product_product pp ON sm.product_id = pp.id
                        INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                        INNER JOIN product_uom uo ON sm.product_uom = uo.id
                    ) ON sl.id = sm.location_id
                        AND sm.state = 'done'
                        ''' + product_where + '''
                        ''' + prodlot_where + '''
                        ''' + date_where + '''
                WHERE sl.usage = 'internal'
                
                UNION ALL
                
                SELECT
                    sl.id as location_id, 
                    COALESCE (sm.product_qty / uo.factor, 0) as qty
                FROM
                    stock_location sl
                    LEFT JOIN (stock_move sm
                            INNER JOIN product_product pp ON sm.product_id = pp.id
                            INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                            INNER JOIN product_uom uo ON sm.product_uom = uo.id
                    ) ON sl.id = sm.location_dest_id
                        AND sm.state = 'done'
                        ''' + product_where + '''
                        ''' + prodlot_where + '''
                        ''' + date_where + '''
                WHERE sl.usage = 'internal'
            ) AS s
            GROUP BY
                s.location_id
            HAVING     sum(s.qty) ''' + operator + " %s",
            tuple(2*(product_value + prodlot_value + date_values)) + (value,))

        res = cr.fetchall()
        ids = [('id', 'in', map(lambda x: x[0], res))]
        return ids
        
    def _stock_virtual_search(self, cr, uid, obj, name, args, context=None):
        """Search Locations by real stock"""
        # XXX: refactor with _stock_real_search()
        # XXX: maybe refactor with product.get_product_available()?
        if context is None:
            context = {}
        fieldname, operator, value = args[0]
        
        # Sanitize input to protect from SQL injection
        if operator not in ('=', '!=', '<>', '<=', '<', '>', '>=', 'in', 'not in'):
            raise osv.except_osv(
               _('Invalid operator!'),
               _("The operator '%s' cannot be used to filter the field '%s'.") % (operator, field))
        
        # Product conditions
        if context.get('product_id'):
            product_where = "AND product_id=%s "
            product_value = [context.get('product_id')]
        else:
            product_where = "AND %s "
            product_value = ['TRUE']
        
        # Production lot conditions
        if context.get('prodlot_id'):
            prodlot_where = "and prodlot_id=%s"
            prodlot_value = [context.get('prodlot_id')]

        else:
            prodlot_where = "and %s"
            prodlot_value = ['TRUE']

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
        
        cr.execute('''
            SELECT
                s.location_id,
                sum(s.qty) as qty_available
            FROM
            (
                SELECT
                    sl.id as location_id, 
                    COALESCE (-(sm.product_qty / uo.factor), 0) as qty
                FROM
                    stock_location sl
                    LEFT JOIN (stock_move sm 
                        INNER JOIN product_product pp ON sm.product_id = pp.id
                        INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                        INNER JOIN product_uom uo ON sm.product_uom = uo.id
                    ) ON sl.id = sm.location_id
                        AND sm.state in ('confirmed','waiting','assigned','done')
                        ''' + product_where + '''
                        ''' + prodlot_where + '''
                        ''' + date_where + '''
                WHERE sl.usage = 'internal'
                
                UNION ALL
                
                SELECT
                    sl.id as location_id, 
                    COALESCE (sm.product_qty / uo.factor, 0) as qty
                FROM
                    stock_location sl
                    LEFT JOIN (stock_move sm 
                        INNER JOIN product_product pp ON sm.product_id = pp.id
                        INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                        INNER JOIN product_uom uo ON sm.product_uom = uo.id
                    ) ON sl.id = sm.location_dest_id
                        AND sm.state in ('confirmed','waiting','assigned','done')
                        ''' + product_where + '''
                        ''' + prodlot_where + '''
                        ''' + date_where + '''
                WHERE sl.usage = 'internal'
                ) AS s
            GROUP BY
                s.location_id
            HAVING     sum(s.qty) ''' + operator + " %s",
            tuple(2*(product_value + prodlot_value + date_values)) + (value,))
        
        res = cr.fetchall()
        ids = [('id', 'in', map(lambda x: x[0], res))]
        return ids

    def _product_value(self, cr, uid, ids, field_names, arg, context=None):
        """Proxy to the parent model's method"""
        return super(stock_location, self)._product_value(
            cr, uid, ids, field_names=field_names, arg=arg, context=context)
    
    _columns = {
        'stock_real': fields.function(
            _product_value, fnct_search=_stock_real_search,
            method=True, type='float', string='Real Stock', multi="stock"),
        'stock_virtual': fields.function(
            _product_value, fnct_search=_stock_virtual_search,
            method=True, type='float', string='Virtual Stock', multi="stock"),
    }
stock_location()

class stock_location_product(osv.osv_memory):
    """Customize the behavior of the report wizard"""

    _inherit = "stock.location.product"
    
    def action_open_window(self, cr, uid, ids, context=None):
        """By default, report only the available products in the wizard 'Products by Location'."""
        # Get normal view data
        result = super(stock_location_product, self).action_open_window(cr, uid, ids, context=context)
        if isinstance(result, dict):
            if not result.get('context'):
                result['context'] = {}
            # Activate the filter
            result['context']['search_default_filter_available'] = 1
        return result
stock_location_product()
