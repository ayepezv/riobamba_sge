# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP SA (<http://openerp.com>).
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
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

class separateOrderLine(osv.TransientModel):

    _name = "separate.order.line"

    _columns = dict(
        name = fields.char('Descripción', size=256),
        product_qty = fields.float('Cantidad'),
        product_uom = fields.many2one('product.uom', 'UdM Producto'),
        price_unit = fields.float('Precio Unitario'),
        price_subtotal = fields.float('Subtotal'),
        wizard_id =  fields.many2one('separate.order', string="Wizard", ondelete='CASCADE'),
        )


class separateOrder(osv.osv_memory):
    _name = "separate.order"
    _description = "Procesar Orden Compra"
    
    _columns = dict(
        partner_id = fields.many2one('res.partner','Proveedor'),
        line_ids = fields.one2many('separate.order.line', 'wizard_id', 'Detalle Lineas'),
        order_id = fields.many2one('purchase.order', 'Orden de Compra', ondelete='CASCADE'),
        )

    def _line_for(self, cr, uid, line):
        order_line = {
            'name':line.name,
            'product_qty':line.product_qty,
            'product_uom':line.product_uom.id,
            'price_unit':line.price_unit,
            'price_subtotal':line.price_subtotal,
            }
        return order_line


    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(separateOrder, self).default_get(cr, uid, fields, context=context)
        order_ids = context.get('active_ids', [])
        if not order_ids or (not context.get('active_model') == 'purchase.order') \
            or len(order_ids) != 1:
            return res
        order_id, = order_ids
        if 'order_id' in fields:
            res.update(order_id=order_id)
        #if 'order_line' in fields:
        order = self.pool.get('purchase.order').browse(cr, uid, order_id, context=context)
        lines_true = []
        for m in order.order_line:
            if m.is_group:
                lines_true.append(m)
        if lines_true:
            lines = [self._line_for(cr, uid, m) for m in lines_true]
            res.update(line_ids=lines)
        return res
    
    def do_exec_(self, cr, uid, ids, context):
        assert len(ids) == 1, 'Solo puede procesar una solicitud a la vez'
        order_obj = self.pool.get('purchase.order')
        order_line_obj = self.pool.get('purchase.order.line')
#        import pdb
#        pdb.set_trace()
        for this in self.browse(cr, uid, ids):
            partner_id = this.partner_id.id
        order = order_obj.browse(cr, uid, context['active_id'])
        new_order_values = order_obj.copy_data(cr, uid, order.id)
        new_order_values['partner_id']=partner_id
        new_order_values['order_ref']=order.id
        new_order_values['is_son']=True
        new_order_id = order_obj.create(cr, uid, new_order_values,context) 
        #delete true values in original order
        for line in order.order_line:
            if line.is_group:
                order_line_obj.unlink(cr, uid, line.id)
        #delete false values in new order
        new_order = order_obj.browse(cr,uid, new_order_id)
        for line in new_order.order_line:
            if not line.is_group:
                order_line_obj.unlink(cr, uid, line.id)
        return {'type': 'ir.acctions.act_window_close'}
