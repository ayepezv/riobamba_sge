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
import time
import datetime
from datetime import date
from osv.orm import browse_record, browse_null

class vehicleRepairOkW(osv.osv_memory):
   _name = 'vehicle.repair.ok.w'
   _description = "Vehículo Reparado"

   _columns = dict(
        vehicle_id = fields.many2one('vehicle.vehicle','Vehiculo'),
        descripcion = fields.text('Descripcion de la Reparación'),
        )
    

   def vehicle_repair_ok(self, cr, uid, ids, context=None):       
        active_id = context['active_id']
        vehicle_obj = self.pool.get('vehicle.vehicle')        
        repair_obj = self.pool.get('vehicle.repair')
        vehicle = vehicle_obj.browse(cr, uid, active_id)
        for this in self.browse(cr, uid, ids):
            if not vehicle.state=='ocupado':
                fecha = time.strftime("%Y-%m-%d %H:%M:%S")
                vehicle_obj.write(cr, uid, vehicle.id,{'state' : 'disponible'},context={'create_opc':'t'})
                repair_obj.create(cr, uid,{
                        'user_id':uid,
                        'name':fecha,
                        'opc':'reparado',
                        'vehicle_id':active_id,
                        'desc':this.descripcion})
            else:
                raise osv.except_osv('Error de usuario', 'No pueden pasar a reparado si el vehículo se encuentra ocupado')
        return {'type':'ir.actions.act_window_close'}

vehicleRepairOkW()

