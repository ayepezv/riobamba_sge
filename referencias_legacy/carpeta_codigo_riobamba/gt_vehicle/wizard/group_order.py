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

class groupOrder(osv.osv_memory):
   _name = 'group.order'
   _description="Agrupar Solicitudes"

   _columns = dict(
       employee_id = fields.many2one('hr.employee', 'Responsable',required=True),
       order_id = fields.many2one('movilization.order','Solicitud Movilización',required=True,help="En esta solicitud serán agrupadas las demas solicitudes de movilización"),
       order_ids = fields.many2many('movilization.order', 'order_mov_rel', 'mov_id', 'order_id', 'Solicitudes'),
       )

   def group_order(self, cr, uid, ids, context):
       detalle_act=""
       detalle_obs=""
       order_obj = self.pool.get('movilization.order')
       order_obj_padre = self.pool.get('movilization.order')
       line_employee_obj = self.pool.get('movilization.order.employee')
       pos=0       
       if context is None:
           context = {}
       for this in self.browse(cr, uid, ids):
          detalle_act=this.order_id.desc
          if this.order_id.observaciones:
              detalle_obs=this.order_id.observaciones
          else:
              detalle_obs="--"
          for line in this.order_ids:
             detalle_act=detalle_act+"\n"+line.desc
             if not line.observaciones:
                 detalle_obs=detalle_obs+"\n"+"--"
             else:                                
                 detalle_obs=detalle_obs+"\n"+str(line.observaciones)
             order_obj.write(cr, uid, line.id,{
                   'origin':this.order_id.ref,
                   'movilization_order_id':this.order_id.id,
                   'state':"agrupado"
                   })
             ind=0             
             for line_employee in line.employee_ids:                   
                line_employee_obj.create(cr,uid,{"mov_id":this.order_id.id,
                                        "employee_id":line_employee.id,                                                                        
                                        })
                
                rel= cr.execute('select * from employee_movi_rel')
                rel = cr.dictfetchall()
                for rel_line in rel:                   
                    if (str(this.order_id.id)==str(rel_line['mov_id']) and str(line_employee.id)==str(rel_line['emp_id'])):
                        ind=0
                        break                                
                    else:
                        ind=1
                if ind==1:
                    cr.execute('INSERT INTO employee_movi_rel (mov_id, emp_id) VALUES ('+str(this.order_id.id)+','+ str(line_employee.id)+')')                 
             if line.id==this.order_id.id:
                 raise osv.except_osv('Error', 'No puede agrupar la Órden de Movilización que ya es padre '+ str(this.order_id.ref))
           
          order_obj.write(cr, uid, this.order_id.id,{
                'responsable_id':this.employee_id.id,
                'desc':detalle_act,
                'observaciones':detalle_obs,
                'padre':'t',
             })
       return {'type':'ir.actions.act_window_close'}

groupOrder()


