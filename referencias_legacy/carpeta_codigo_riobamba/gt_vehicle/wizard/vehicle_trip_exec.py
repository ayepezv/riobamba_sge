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

class vehicle_exec_line(osv.TransientModel):

    _name = "vehicle.exec.line"
    _description="Procesamiento de las Rutas"

    _columns = dict(
        sec = fields.integer('Secuencia'),
        desde = fields.char('Desde',size=32,required=True),
        hasta = fields.char('Hasta',size=32,required=True),
        km_inicial = fields.integer('Km. Inicial'),
        km_final = fields.integer('Km. Final'),
        wizard_id =  fields.many2one('vehicle.exec', string="Wizard", ondelete='CASCADE'),
        )


class vehicle_exec(osv.osv_memory):
    _name = "vehicle.exec"
    _description = "Procesamiento de las Rutas"
    
    _columns = dict(
        date = fields.datetime('Date', required=True),
        route_ids = fields.one2many('vehicle.exec.line', 'wizard_id', 'Detalle Ruta'),
        order_id = fields.many2one('movilization.order', 'Solicitud de movilización', required=True, ondelete='CASCADE'),
        )

    def _route_line_for(self, cr, uid, line,km_start):
        if line.sec==1:
            route_line = {
                'sec':line.sec,
                'desde':line.desde,
                'hasta':line.hasta,
                'km_inicial':km_start,
                'km_final':line.km_final,
            }
        else:
            route_line = {
                'sec':line.sec,
                'desde':line.desde,
                'hasta':line.hasta,
                'km_inicial':line.km_inicial,
                'km_final':line.km_final,
            }
        return route_line

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(vehicle_exec, self).default_get(cr, uid, fields, context=context)
        order_ids = context.get('active_ids', [])
        if not order_ids or (not context.get('active_model') == 'movilization.order') \
            or len(order_ids) != 1:
            return res   
        order_id, = order_ids            
        if 'order_id' in fields:
            res.update(order_id=order_id)
        if 'route_ids' in fields:
            order = self.pool.get('movilization.order').browse(cr, uid, order_id, context=context)
            routes = [self._route_line_for(cr, uid, m,order.km_start) for m in order.route_ids]
            res.update(route_ids=routes)
        if 'date' in fields:
            res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        return res
    
    def do_exec(self, cr, uid, ids, context):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        
        assert len(ids) == 1, 'Solo puede procesar una solicitud a la vez'
        order = self.pool.get('movilization.order')
        route_line = self.pool.get('route.line')
        vehicle_obj = self.pool.get('vehicle.vehicle')
        vehicle_route_km_obj = self.pool.get('vehicle.route.km')
        partial = self.browse(cr, uid, ids[0], context=context)
        mov_order = order.browse(cr, uid, context['active_ids'][0])
        context_ve = {}
        context_ve['vehicle_type']='contratado'        
        pos=1;
        l=len(partial.route_ids)
        i=0 
        posicion = 0    
        for line in partial.route_ids:                    
            posicion = posicion + 1
            if posicion==1:
                anterior_desde = line.desde
                anterior_hasta = line.hasta
            else:
                if line.desde.upper()==anterior_hasta.upper():
                    anterior_desde = line.desde
                    anterior_hasta = line.hasta
                else:
                    raise osv.except_osv(('Advertencia!'),('Debe coincidir el destino y la llegadas de las rutas'))       
        for i in range(l-1):            
            if partial.route_ids[i].km_final<partial.route_ids[i+1].km_inicial or partial.route_ids[i].km_final!=partial.route_ids[i+1].km_inicial:
                raise osv.except_osv(('Advertencia!'), ('Por favor verifique que lo kilómetros tengan consistencia'))
#            if partial.route_ids[0].km_inicial!=mov_order.km_start:
#                raise osv.except_osv(('Advertencia!'), ('Km Inicial del vehiculo no puede ser modificado'))
      
        for line in mov_order.route_ids:
            route_line.unlink(cr, uid, line.id)            
        for wizard_line in partial.route_ids:
            #Quantiny must be Positive                    
            if wizard_line.km_inicial <= 0 or wizard_line.km_final <= 0 or wizard_line.km_final<=wizard_line.km_inicial:
                raise osv.except_osv(('Advertencia!'), ('Por favor ingrese valores positivos en el kilometraje y verifique que el final sea mayor al inicial!'))
            route_line.create(cr, uid, {
                    'desde':wizard_line.desde,
                    'hasta':wizard_line.hasta,
                    'km_inicial':wizard_line.km_inicial,
                    'km_final':wizard_line.km_final,
                    'mov_id':context['active_ids'][0],
                    })
        
       
        order.write(cr, uid, mov_order.id,{
                'state':'realizado',
                'km_end':partial.route_ids[l-1].km_final     
                })            
        if mov_order.asigned_depart==True:
            vehicle_id_id=mov_order.vehicle_id_asigned.id
            cadena=mov_order.vehicle_id_asigned.cadena
            line=vehicle_obj.browse(cr,uid,mov_order.vehicle_id_asigned.id)
            km_total=int(line.km)+ int(mov_order.km_total)
        if mov_order.asigned_depart==False:
            vehicle_id_id=mov_order.vehicle_id.id
            cadena=mov_order.vehicle_id.cadena
            line=vehicle_obj.browse(cr,uid,mov_order.vehicle_id.id)
            km_total=int(line.km)+ int(mov_order.km_total)        
        order.write(cr, uid, mov_order.id,{
                'vehicle_des': cadena
                })                                
        vehicle_obj.write(cr, uid, vehicle_id_id,{
                'state':'disponible',
                'km':km_total,
                },context_ve)        
        name_route=partial.route_ids[0].desde        
        for wizard_line in partial.route_ids:
            name_route=name_route+"-"+wizard_line.hasta                        
        vehicle_route_km_obj.create(cr, uid, {
            'responsable_id':mov_order.responsable_id.id,
            'name':name_route,
            'date_start':mov_order.movilization_date,
            'date_end':mov_order.return_date,
            'km_start':partial.route_ids[0].km_inicial,
            'km_end':partial.route_ids[len(partial.route_ids)-1].km_final,
            'vehicle_id':vehicle_id_id,
                })              
        result = mod_obj.get_object_reference(cr, uid, 'gt_vehicle', context['view_id'])
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context={})[0]            
        return result
