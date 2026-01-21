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
from datetime import datetime
from osv.orm import browse_record, browse_null

class incidentDriverW(osv.osv_memory):
    _name = "incident.driver.w"
    _description = "Incidentes"
    _columns = dict(
        driver_id = fields.many2one('vehicle.driver','Chofer'),
        date = fields.datetime('Fecha Incidente'),
        desc = fields.text('Descripción del Incidente'),
        tipo = fields.char('Tipo', size=28),
        )
    
    def _get_type(self, cr, uid, context):               
        res=''             
        if 'vehicle_type' in context:
            if context['vehicle_type']=='planta_mod':
                res='planta'
            else:              
                res = context['vehicle_type']
        return res
    
    def validar_tiempo(self, cr, uid, ids, fecha1,context=None):
        res_value = {}        
        if fecha1:
            time_fecha1 = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_fecha1 = time_fecha1.replace(second=00)
            res_value['date']=str(time_fecha1)
            if str(time_fecha1)>str(time.strftime('%Y-%m-%d %H:%M:%S')):
                return {'warning': {'title':'Advertencia','message':'La fecha no puede ser mayor a la actual'},'value':res_value}                    
        return {'value':res_value}
    
    def create_incident(self, cr, uid, ids, context=None):
        active_id = context['active_id']
        vehicle_incident = self.pool.get('vehicle.incident')
        incident_driver = self.pool.get('incident.driver')
        for this in self.browse(cr, uid, ids):
            if str(this.date)>str(time.strftime('%Y-%m-%d %H:%M:%S')):
                    raise osv.except_osv('Error', 'La fecha del incidente no puede ser mayor a la actual')
            else:
                    vehicle_incident.create(cr, uid, {
                            'user_id':uid,
                            'driver_id':this.driver_id.id,
                            'name':this.date,
                            'detail':this.desc,
                            'vehicle_id':active_id,
                            })
                    incident_driver.create(cr, uid, {
                            'name':active_id,
                            'fecha':this.date,
                            'desc':this.desc,
                            'driver_id':this.driver_id.id,
                            })
        return {'type': 'ir.actions.act_window_close'}
    
    _defaults = dict(
        
        date = time.strftime('%Y-%m-%d %H:%M:%S'),
        tipo = _get_type, 
        )
incidentDriverW()
