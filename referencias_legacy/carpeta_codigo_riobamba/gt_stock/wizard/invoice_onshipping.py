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

from osv import fields, osv

class stock_invoice_onshipping(osv.osv_memory):

    _inherit = "stock.invoice.onshipping"

    _columns = dict(
        partner_id = fields.many2one('res.partner','Proveedor'),
        certificate_id = fields.many2one('budget.certificate','Compromiso Presupuestario',required=True),
    )

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = {}
        record_id = context and context.get('active_id', False) or False
        picking = self.pool.get('stock.picking').browse(cr, uid, record_id, context=context)
        res.update({'partner_id':picking.partner_id.id})
        return res

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        res = super(stock_invoice_onshipping, self).view_init(cr, uid, fields_list, context=context)
        pick_obj = self.pool.get('stock.picking')
        count = 0
        active_ids = context.get('active_ids',[])
        for pick in pick_obj.browse(cr, uid, active_ids, context=context):
            if pick.invoice_state != '2binvoiced':
                count += 1
        if len(active_ids) == 1 and count:
            raise osv.except_osv(_('Warning !'), _('This picking list does not require invoicing.'))
        if len(active_ids) == count:
            raise osv.except_osv(_('Warning !'), _('None of these picking lists require invoicing.'))
        return res

    def create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        picking_pool = self.pool.get('stock.picking')
        onshipdata_obj = self.read(cr, uid, ids, ['journal_id', 'group', 'invoice_date','certificate_id'])
        if context.get('new_picking', False):
            onshipdata_obj['id'] = onshipdata_obj.new_picking
            onshipdata_obj[ids] = onshipdata_obj.new_picking
        context['date_inv'] = onshipdata_obj[0]['invoice_date']
        active_ids = context.get('active_ids', [])
        active_picking = picking_pool.browse(cr, uid, context.get('active_id',False), context=context)
        picking_pool.write(cr, uid, active_picking.id,{
            'presp_ref':onshipdata_obj[0]['certificate_id'][0],
        })
        inv_type = picking_pool._get_invoice_type(active_picking)
        context['inv_type'] = inv_type
        if isinstance(onshipdata_obj[0]['journal_id'], tuple):
            onshipdata_obj[0]['journal_id'] = onshipdata_obj[0]['journal_id'][0]
        res = picking_pool.action_invoice_create(cr, uid, active_ids,
              journal_id = onshipdata_obj[0]['journal_id'],
              group = onshipdata_obj[0]['group'],
              type = inv_type,
              context=context)
        return res

stock_invoice_onshipping()
