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

class vehicleActivate(osv.osv_memory):
   _name = 'vehicle.activate'
   _description="Activar un Vehículo"

   _columns = dict(
       vehicle_id = fields.many2one('vehicle.vehicle', 'Vehículo',required=True),
       option = fields.selection([('True','Activar'),('False','Desactivar')],'Opción',required=True),
       )
   _defaults=dict(                  
        option='True'                  
                  )
   
   def onchange_vehicle_id(self, cr, uid, ids, vehicle_id):
        ind=0
        if not vehicle_id:
            return {}
        vehicle = self.pool.get('vehicle.vehicle').browse(cr, uid, vehicle_id)  
        if vehicle.activo==True:
            return {'value':{'option': "False"}}
        if vehicle.activo==False:
            return {'value':{'option': "True"}}

   def activate_vehicle(self, cr, uid, ids, context):
       vehicle_obj = self.pool.get('vehicle.vehicle')
       if context is None:
           context = {}
       context['vehicle_type']='contratado'
       for this in self.browse(cr, uid, ids):
          vehicle = this.vehicle_id
          if this.option=="True":         
              vehicle_obj.write(cr, uid, vehicle.id, {
                      'activo':True,
                      },context)
          if this.option=="False":         
              vehicle_obj.write(cr, uid, vehicle.id, {
                      'activo':False,
                      },context)
       return {'type':'ir.actions.act_window_close'}

vehicleActivate()


