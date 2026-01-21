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
import time
import datetime
from datetime import date

class vehicleUpdateKm(osv.osv_memory):
   _name = 'vehicle.update.km'
   _description = "Actualizar Kilometraje"
   

   def _check_number(self,cr,uid,ids):
      for aux in self.browse(cr,uid,ids):
         if aux.km_new<0:
            return False
      return True

   _columns = dict(
       vehicle_id = fields.many2one('vehicle.vehicle', 'Vehículo',required=True),
       km_ant = fields.integer('Km. Anterior',readonly=True),
       km_new = fields.integer('km. Nuevo',required=True),
       note = fields.text('Observaciones',required=True),
       )
   
   def onchange_vehicle(self, cr, uid, ids, vehicle_id, context=None):
      res = {}
      if vehicle_id:
         vehicle = self.pool.get('vehicle.vehicle').browse(cr, uid, vehicle_id, context=context)
         res.update({'km_ant': vehicle.km})
      return {
         'value':res
         }

   def update_km(self, cr, uid, ids, context):
       error=0
       vehicle_obj = self.pool.get('vehicle.vehicle')
       vehicle_update_obj = self.pool.get('vehicle.update')
      # if context is None:
       context = {}
       context['vehicle_type']='contratado'
       for this in self.browse(cr, uid, ids):
          vehicle = this.vehicle_id
          if this.km_new<this.vehicle_id.km:
              error=1          
          else:       
              fecha = time.strftime("%Y-%m-%d %H:%M:%S")
              fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")              
              fecha = fecha.replace(second=00) 
              vehicle_update_obj.create(cr, uid, {
                  'name' : uid,
                  'date' : fecha,
                  'km_ant' : this.vehicle_id.km,
                  'km_new' : this.km_new,
                  'note' : this.note,
                  'vehicle_id' : vehicle.id
                  })
              vehicle_obj.write(cr, uid, [vehicle.id], {
                  'km':this.km_new,
                  },context)
       if error==1:
            raise osv.except_osv('Error', 'El Km. Nuevo debe ser mayor al Km. Anterior')
       return {'type':'ir.actions.act_window_close'}

   _constraints = [
      (_check_number,'Número invalido debe ser mayor a 0',['km_new']),
      ]

vehicleUpdateKm()


