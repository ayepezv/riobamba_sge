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

class vehicleRepairW(osv.osv_memory):
   _name = 'vehicle.repair.w'
   _description = "Vehículo en Reparación"

   _columns = dict(
        vehicle_id = fields.many2one('vehicle.vehicle','Vehiculo'),
        descripcion = fields.text('Descripción de la Reparación'),
        )
   
    
   def vehicle_repair(self, cr, uid, ids, context=None):       
        active_id = context['active_id']
        vehicle_obj = self.pool.get('vehicle.vehicle')        
        repair_obj = self.pool.get('vehicle.repair')
        vehicle = vehicle_obj.browse(cr, uid, active_id)
        for this in self.browse(cr, uid, ids):
            if not vehicle.state=='ocupado':
                fecha = time.strftime("%Y-%m-%d %H:%M:%S") 
                vehicle_obj.write(cr, uid, vehicle.id,{'state' : 'danado'},context={'create_opc':'t'})
                repair_obj.create(cr, uid,{
                        'user_id':uid,
                        'name':fecha,
                        'opc':'danio',
                        'vehicle_id':active_id,
                        'desc':this.descripcion})
            else:
                raise osv.except_osv('Error de usuario', 'No pueden pasar a reparación si el vehículo se encuentra ocupado')
        return {'type':'ir.actions.act_window_close'}

vehicleRepairW()

class vehicleResumen(osv.Model):
   _name = 'vehicle.print.resumen'
   _description = "Recorridos"
   
   _MONTHS = [('1','Enero'),('2','Febrero'),
              ('3','Marzo'),('4','Abril'),
              ('5','Mayo'),('6','Junio'),
              ('7','Julio'),('8','Agosto'),
              ('9','Septiembre'),('10','Octubre'),
              ('11','Noviembre'),('12','Diciembre')]

   def _get_years(self, cr, uid, context=None):
       years = []
       for i in range (date.today().year-1,date.today().year+1):           
           years.append((i,i)) 
       years.reverse()  
       return years

   _columns = dict(
        #vehicle_id = fields.many2one('vehicle.vehicle','Vehiculo'),
        vehicle_id= fields.many2many('vehicle.vehicle', 'summary_vehicle_rel', 'sum_id', 'vehicle_id', 'Vehiculos'),
        months = fields.selection(_MONTHS ,'Mes'),
        years = fields.selection(_get_years,  'Año'),
        
        )
      
          
   def _get_vehicle(self, cr, uid, context):   
       if 'active_ids' in context:
           objects=self.pool.get('vehicle.vehicle').browse(cr,uid,context['active_ids'])
           for line in objects:
               if line.vehicle_type=='contratado':                   
                   return context['active_ids']
               else:                    
                   raise osv.except_osv('Error', 'Reporte solo para vehículos contratados')
           
           
   def print_report(self, cr, uid, ids, context):
        
        if context is None:
            context = {}        
        report_name = 'Recorrido'
        data = self.read(cr, uid, ids, [], context=context)[0]
        data['vehicle_id'] = context['active_ids']
        certificate = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [certificate.id], 'model': 'vehicle.print.resumen','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'model': 'vehicle.print.resumen',
            'datas': datas,
            'nodestroy': True,                              
            }
   
   _defaults = dict(       
        vehicle_id = _get_vehicle,                        
        )

vehicleResumen()
