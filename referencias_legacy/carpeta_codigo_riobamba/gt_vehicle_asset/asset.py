# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Gnuthink Software Labs Cia. Ltda.
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

from osv import osv, fields
import time
from datetime import date
from unicodedata import lookup, name

class vehicleAsset(osv.Model):

    _inherit = 'account.asset.asset'
      
    _columns = dict(
        state_propiedades = fields.boolean('Estado',readonly=True),
        marca_id = fields.many2one('vehicle.mark' ,'Marca'),
        model_id = fields.many2one('vehicle.model' ,'Modelo'),
        color_id = fields.many2one('vehicle.color','Color'),       
        )

    _defaults = dict(
            state_propiedades = False,
        )
   
    def create(self,cr,uid,vals,context):   
        print "Create Vehiculo"     
        configuration_obj = self.pool.get('vehicle.configuration')
        cat_id=self.pool.get('account.asset.category').browse(cr,uid,vals['category_id'],context)
        configuration = configuration_obj.search(cr, uid, [('name','=',cat_id.tipo_id.id)])
        if configuration:
             vals['state_propiedades']=True                     
             return self.pool.get('account.asset.asset').create_activo(cr, uid, vals, context)
        else:
             return self.pool.get('account.asset.asset').create_activo(cr, uid, vals, context)
                                       
    def write(self, cr, uid, ids, vals, context):
        
        vals_c={}   
        vals_pro={}               
        l_values=0
        pos=0
        category_ind=0
        configuration_obj = self.pool.get('vehicle.configuration')
        category_obj = self.pool.get('account.asset.category')            
        this=self.browse(cr, uid, ids)            
        if 'category_id' in vals:
            tipo_id=category_obj.search(cr,uid,[('id','=',vals['category_id'])])
            configuration = configuration_obj.search(cr, uid, [('name','=',tipo_id[0])])
        else:
            configuration = configuration_obj.search(cr, uid, [('name','=',this[0].category_id.tipo_id.id)])                 
        if len(configuration)>0 and configuration[0]==this[0].category_id.tipo_id.id:           
            if 'asset_property_ids' in vals or 'marca_id' in vals or 'model_id' in vals or 'color_id' in vals:              
                vals_v={}
                mensaje=''
                #activo_obj = self.pool.get('account.asset.asset')
                vehicle_obj = self.pool.get('vehicle.vehicle')
                marca_obj = self.pool.get('vehicle.mark')
                modelo_obj = self.pool.get('vehicle.model')
                color_obj = self.pool.get('vehicle.color')
               # tipo_obj = self.pool.get('gt.account.asset.tipo')                                          
                for this in self.browse(cr, uid, ids):
                    if this.tipo_id:
                        l=len(this.tipo_id.property_ids)                       #                           
                values=[]
                value=''                                               
                if 'asset_property_ids' in vals:
                    for i in range(0,l):                        
                        if this.tipo_id.property_ids:
                            name=this.tipo_id.property_ids[i].name                                                                                                            
                        if vals['asset_property_ids'][i][2]:
                            value=vals['asset_property_ids'][i][2]['value']  
                            if value!='':                                       
                                values.append(({'name':name,'value':value}))
                                l_values=len(values)                                                                                                                    
                if 'marca_id' in vals:
                    values.append(({'name':'MARCA','value':vals['marca_id']}))
                if 'model_id' in vals:
                    values.append(({'name':'MODELO_VEHICLE','value':vals['model_id']}))
                if 'color_id' in vals:
                    values.append(({'name':'COLOR','value':vals['color_id']}))                                                
                for this in self.browse(cr, uid, ids):
                    for line in this.asset_property_ids:
                        if line.name.name.upper()=='PLACA':
                            placa_id=line.value
                vehicle_id=vehicle_obj.search(cr,uid,[('name','=',placa_id)])
                #location_obj = self.pool.get('stock.location')
                #location_id=location_obj.search(cr,uid,[('name','=','Vehículo-'+str(placa_id))])                                    
                if mensaje=='':                    
                    for line in values:
                        if line['name'].upper()=='PLACA':
                            placa=line['value']
                            if location_id:
                                location_obj.write(cr, uid,location_id ,{
                                'name':'Vehículo-'+str(placa),                   
                        })
                            vals_v["name"]=placa
                        if line['name'].encode('ascii','replace').upper()=='A?O':
                            if line['value']:
                                if line['value'].isdigit():
                                    anio=line['value']
                                    vals_v["anio"]=anio
                                else:
                                    raise osv.except_osv(('Error'), 'El año debe ser número entero')
                        if line['name'].upper()=='MOTOR':
                            motor=line['value']
                            vals_v["engine"]=motor
                        if line['name'].upper()=='CHASIS':
                            chasis=line['value']
                            vals_v["chasis"]=chasis
                        if line['name'].upper()=='MARCA':
                            marca=line['value']
                            vals_v["marca_id"]=marca
                        if line['name'].upper()=='MODELO_VEHICLE':
                            modelo=line['value']
                            vals_v["model_id"]=modelo
                        if line['name'].upper()=='COLOR':
                            color=line['value']
                            vals_v["color_id"]=color
                    ind=0                                               
                    if l_values==l:                        
                        for i in range(0,len(values)):                         
                                if values[i]['name'].upper()=='PLACA' or values[i]['name'].upper()=='MOTOR' or values[i]['name'].upper()=='CHASIS' or values[i]['name'].encode('ascii','replace').upper()=='A?O':                        
                                    if not values[i]['value']:                                                                            
                                        raise osv.except_osv(('Error'), 'Debe ingresar todas las propiedades del vehiculo')                       
                    else:                     
                        if vehicle_id:
                            for line in vehicle_obj.browse(cr,uid,vehicle_id):
                                if line.km==0 or line.number==0:                       
                                    vals_v['vehicle_type']="planta_mod"
                                    vals_v['estado']="borrador"
                                    if 'marca_id' in vals_v and not vals['marca_id']:                                                 
                                        raise osv.except_osv(('Error'), 'Debe ingresar todas las propiedades del vehiculo') 
                                    if 'model_id' in vals_v and not vals['model_id']:                                         
                                        raise osv.except_osv(('Error'), 'Debe ingresar todas las propiedades del vehiculo')
                                    if 'color_id' in vals_v and not vals['color_id']: 
                                        raise osv.except_osv(('Error'), 'Debe ingresar todas las propiedades del vehiculo')
                                    vehicle_obj.write(cr,uid,vehicle_id,vals_v,context={'vehicle_type':'planta','estado':'borrador','create_opc':'f'})                           
                                else:                                   
                                    vals_v['vehicle_type']="planta_mod"
                                    if 'marca_id' in vals_v and not vals['marca_id']:                                                 
                                        raise osv.except_osv(('Error'), 'Debe ingresar todas las propiedades del vehiculo') 
                                    if 'model_id' in vals_v and not vals['model_id']: 
                                        raise osv.except_osv(('Error'), 'Debe ingresar todas las propiedades del vehiculo')
                                    if 'color_id' in vals_v and not vals['color_id']:                                        
                                        raise osv.except_osv(('Error'), 'Debe ingresar todas las propiedades del vehiculo') 
                                    vehicle_obj.write(cr,uid,vehicle_id,vals_v,context={'vehicle_type':'planta','create_opc':'t'})
                        else:
                            for i in range(0,len(values)):                         
                                if values[i]['name'].upper()=='PLACA' or values[i]['name'].upper()=='MOTOR' or values[i]['name'].upper()=='CHASIS' or values[i]['name'].encode('ascii','replace').upper()=='A?O':                        
                                    if not values[i]['value']:                                                                        
                                        raise osv.except_osv(('Error'), 'Debe ingresar todas las propiedades del vehiculo')                                                               
                    return super(vehicleAsset, self).write(cr, uid, ids, vals, context=None)           
                else:
                    raise osv.except_osv('Propiedades no existentes', mensaje)
                    mensaje=''
            else:
                return super(vehicleAsset, self).write(cr, uid, ids, vals, context=None) 
        else:    
            if len(configuration)>0:   
                if 'category_id' in vals: 
                    if configuration[0]==vals['category_id']:
                        vals_pro['state_propiedades']=True
                        super(vehicleAsset, self).write(cr, uid, ids, vals_pro, context=None)
            else:    
                    vals_pro['state_propiedades']=False
                    vals_pro['marca_id']=0
                    vals_pro['model_id']=0
                    vals_pro['color_id']=0                    
                    super(vehicleAsset, self).write(cr, uid, ids, vals_pro, context=None) 
            return self.pool.get('account.asset.asset').write_activo_poliza(cr, uid, ids, vals, context)
       
   
    def validate(self, cr, uid, ids, context={}):
        # coloca el activo en estado abierto, y genera el código 
        this=self.browse(cr, uid, ids)
        ind=0
        configuration_obj = self.pool.get('vehicle.configuration')                        
        configuration = configuration_obj.search(cr, uid, [('name','=',this[0].tipo_id.id)])
        if configuration:    
            vals_v={}
            vehicle_obj = self.pool.get('vehicle.vehicle')
            marca_obj = self.pool.get('vehicle.mark')
            modelo_obj = self.pool.get('vehicle.model')
            color_obj = self.pool.get('vehicle.color')  
            for this in self.browse(cr, uid, ids):
                    if this.tipo_id:
                        l=len(this.tipo_id.property_ids)                           
            for this in self.browse(cr, uid, ids):                       
                for line in this.asset_property_ids:                                                  
                    if line.name.name.upper()=='PLACA':
                        placa=line['value']
                        vals_v["name"]=placa                     
                    if line.name.name.encode('ascii','replace').upper()=='A?O':
                        if line['value']:
                            if line['value'].isdigit():
                                anio=line['value']
                                vals_v["anio"]=anio
                            else:
                                raise osv.except_osv(('Error'), 'El año debe ser número entero')
                        else:
                            anio=False
                            vals_v["anio"]=anio
                    if line.name.name.upper()=='MOTOR':
                        motor=line['value']
                        vals_v["engine"]=motor
                    if line.name.name.upper()=='CHASIS':
                        chasis=line['value']
                        vals_v["chasis"]=chasis
                if this.marca_id:                                                    
                    vals_v["marca_id"]=this.marca_id.id
                if this.model_id:                                                    
                    vals_v["model_id"]=this.model_id.id
                if this.color_id:                                                    
                    vals_v["color_id"]=this.color_id.id                                                                                
                this = self.browse(cr, uid, ids)
                for i in range(0,l):
                    if this[0]['asset_property_ids'][i]['name']['name'].upper()=='PLACA' or this[0]['asset_property_ids'][i]['name']['name'].upper()=='MOTOR' or this[0]['asset_property_ids'][i]['name']['name'].upper()=='CHASIS' or this[0]['asset_property_ids'][i]['name']['name'].encode('ascii','replace').upper()=='A?O':                        
                        if not this[0]['asset_property_ids'][i]['value']:                                            
                            raise osv.except_osv(('Error'), 'Debe ingresar todas las propiedades del vehiculo')   
                    if not 'marca_id' in vals_v or not 'model_id' in vals_v or not 'color_id' in vals_v:                        
                        raise osv.except_osv(('Error'), 'Debe ingresar todas las propiedades del vehiculo')
                    
                for this in self.browse(cr, uid, ids):
                    for line in this.asset_property_ids:
                        if line.name.name.upper()=='PLACA':
                            placa_id=line.value
                vehicle_id=vehicle_obj.search(cr,uid,[('name','=',placa_id)])                       
                if vehicle_id:                    
                    for line in vehicle_obj.browse(cr,uid,vehicle_id):
                        if line.km==0 or line.number==0:                        
                            vals_v['vehicle_type']="planta_mod"
                            vals_v['estado']="borrador"
                            vehicle_obj.write(cr,uid,vehicle_id,vals_v,context={'vehicle_type':'planta','estado':'borrador','create_opc':'f'})                           
                        else:
                            vals_v['vehicle_type']="planta_mod"
                            vehicle_obj.write(cr,uid,vehicle_id,vals_v,context={'vehicle_type':'planta','create_opc':'t'})
                else:                                                                  
                   # location_obj = self.pool.get('stock.location')               
                    #location_id = location_obj.create(cr, uid, {
                     #   'name':'Vehículo-'+str(placa),
                      #  'usage':'internal',
                       # })
                   
                    vehicle_obj.create(cr, uid,{
                                        'activo':True,
                                        'name':placa,
                                        'anio':anio,
                                        'number':0,
                                        'vehicle_type':'planta_mod',
                                        'marca_id':this.marca_id.id,
                                        'model_id':this.model_id.id,
                                        'color_id':this.color_id.id,
                                        'engine':motor,
                                        'chasis':chasis,
                                        'create_opc':'t',
                                        'km':0,
                                        #'location_id': location_id,                              
                                        'estado':'borrador',
                                        'cadena':"Institucional-"+str(placa)+"/"+str(this.marca_id.name)+"/"+str(this.model_id.name)+"/"+str(this.color_id.name)+"/"+str(anio)
                                        }, context={'vehicle_type':'planta'})           
        return self.pool.get('account.asset.asset').validate_poliza( cr, uid, ids, context)    
                           
                           
    def set_to_low(self, cr, uid, ids, context={}):
        # coloca el activo en estado abierto, y genera el código       
        this=self.browse(cr, uid, ids)
        configuration_obj = self.pool.get('vehicle.configuration')
        configuration = configuration_obj.search(cr, uid, [('name','=',this[0].tipo_id.id)])
        if configuration:
            vehicle_obj = self.pool.get('vehicle.vehicle')
            #location_obj = self.pool.get('stock.location')      
            for this in self.browse(cr, uid, ids):
                    for line in this.asset_property_ids:
                        if line.name.name.upper()=='PLACA':
                            placa_id=line.value                      
            vehicle_id=vehicle_obj.search(cr,uid,[('name','=',placa_id)])
            #location_id=location_obj.search(cr,uid,[('name','=','Vehículo-'+str(placa_id))])
            #location_obj.write(cr, uid,location_id ,{
             #           'active':False,                   
              #          })
            vehicle_obj.write(cr, uid,vehicle_id,{                                                               
                                        'estado':'low',                                   
                                        }, context={'vehicle_type':'planta','estado':'low'})   
        return self.pool.get('account.asset.asset').set_to_low_activo( cr, uid, ids, context) 
