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
from osv import fields, osv
from time import strftime

class wizard_group_req(osv.osv_memory):
   _name='wizard.group.req'

   def group_req(self, cr, uid, ids, context):
      #tomo el producto y le busco en cada solicitud para agrupar y crea una sola linea
      purchase_req_obj = self.pool.get('purchase.requisition')
      purchase_req_line_obj = self.pool.get('purchase.requisition.line')
      req_son_obj = self.pool.get('req.son.line')
      res_partner = self.pool.get('res.partner')
      if context is None:
         context = {}
      for this in self.browse(cr, uid, ids):
         req_id = purchase_req_obj.create(cr, uid, {
                  'origin' : "SOL-AGR",
                  'description' : this.desc,
                  })
         #qty_group = 0
         for solicitud in this.name:
            for line in solicitud.line_ids:
               #qty_group
               purchase_req_line_obj.create(cr, uid, {
                     'product_qty' : line.product_qty,
                     'product_uom_id' : line.product_uom_id.id,
                     'product_id' : line.product_id.id,
                     'presp_ref':line.presp_ref,
                     'requisition_id': req_id,
                       })
            purchase_req_obj.write(cr, uid, solicitud.id,{
                  'active':False,
                  })
            son_id = req_son_obj.create(cr, uid, {
                  'req_id' : req_id,
                  'r_id' : solicitud.id,
                  })

      value = {
         'name':'Solicitud de compra',
         'view_type': 'form',
         'view_mode': 'tree,form',
         'res_model': 'purchase.requisition',
         'res_id': req_id,
         'type': 'ir.actions.act_window',
         }
      return value


   _columns = dict( 
      date = fields.date('Fecha'),
      name = fields.many2many('purchase.requisition','po_req_sol','po_id','req_id','Solicitudes'),
      desc = fields.text('Descripción'),
      )
   
   _defaults = dict(
       date = time.strftime("%Y-%m-%d"),
    )

wizard_group_req()

