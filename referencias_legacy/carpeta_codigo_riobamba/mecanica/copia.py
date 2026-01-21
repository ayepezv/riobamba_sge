# -*- coding: utf-8 -*-
##############################################################################
#
# GADMLI
#
##############################################################################

from osv import osv, fields
import time
import netsvc
from gt_tool import tool
import datetime
from time import strftime, strptime


		

class reporte_mantenimiento(osv.TransientModel):
   _name = 'reporte.mantenimiento'
   _columns = dict(
      name = fields.char('Nombre',size=32),

      vehiculor_id = fields.many2one('vehiculo','Vehiculo/Maquinaria'),
      opcion = fields.selection([('Vehiculo','Vehiculo'),('Maquinaria','Maquinaria')],'Tipo'),
      opc = fields.boolean('Entre fechas'),
      date_start = fields.date('Desde'),
      date_stop = fields.date('Hasta'),
      #create_user_id = fields.many2one('res.users','Creado por'),
   )

   #def _get_user(self, cr, uid, ids, context=None):
    #   return uid

   def pulsar_opcion(self,cr,ids,context=None):
       return {'value':{'vehiculor_id':''}}

   def default_get(self, cr, uid, fields, context=None):
      if context is None:
         context = {}
      res = {}
      res.update({'date_stop':time.strftime('%Y-%m-%d'),'date_start':'2010-01-01','opcion':'Todos'})
     
      return res

   def print_mantenimiento_vehiculo(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'reporte.mantenimiento'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'reporte_mantenimiento',
            'model': 'reporte.mantenimiento',
            'datas': datas,
            'nodestroy': True,                        
            }

   defaults = dict(
      date_stop= time.strftime('%Y-%m-%d'),
     # create_user_id = _get_user,
   )
reporte_mantenimiento()

class reporte_combustible(osv.TransientModel):
   _name = 'reporte.combustible'
   _columns = dict(
      name = fields.char('Nombre',size=32),

      vehiculorc_id = fields.many2one('vehiculo','Vehiculo/Maquinaria'),
      opcion = fields.selection([('Vehiculo','Vehiculo'),('Maquinaria','Maquinaria')],'Tipo'),
      opc = fields.boolean('Entre fechas'),
      date_start = fields.date('Desde'),
      date_stop = fields.date('Hasta'),
      #create_user_id = fields.many2one('res.users','Creado por'),
   )

   #def _get_user(self, cr, uid, ids, context=None):
    #   return uid

   def pulsar_opcion(self,cr,ids,context=None):
       return {'value':{'vehiculorc_id':''}}

   def default_get(self, cr, uid, fields, context=None):
      if context is None:
         context = {}
      res = {}
      res.update({'date_stop':time.strftime('%Y-%m-%d'),'date_start':'2010-01-01','opcion':'Todos'})
     
      return res

   def print_combustible_vehiculo(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'reporte.combustible'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'reporte_combustible',
            'model': 'reporte.combustible',
            'datas': datas,
            'nodestroy': True,                        
            }

   defaults = dict(
      date_stop= time.strftime('%Y-%m-%d'),
     # create_user_id = _get_user,
   )
reporte_combustible()


class vehiculo_alias(osv.Model):
    _name = 'vehiculo.alias'
    _description = 'alias del vehiculo'
    _order = 'name'

    _columns = dict(
       name = fields.char('descripcion',size=128),
       codigo = fields.char('Codigo',size=10), 
    )        
vehiculo_alias()

class quitar_rqm_requerimiento(osv.TransientModel):
    _name = 'quitar.rqm.mantenimiento'
    _columns = {
        'rqm_id_quitar': fields.many2one('stock.requisition', 'Quitar Requerimiento', required=True),
    }
    def quitar_rqm(self, cr, uid, ids, context=None):
        vehiculo_obj = self.pool.get('vehiculo')# objeto vehiculo paso a la variabble vehiculo_obj
        mantenimiento_line_obj = self.pool.get('vehiculo.mantenimiento')
        lubricante_line_obj = self.pool.get('vehiculo.lubricante')
        requerimiento_obj = self.pool.get('stock.requisition')
        for this in self.browse(cr, uid, ids):# cargo todo el formulario de este mismo objeto osea los campos en este form 
            move_lines = context and context.get('active_id', False) or False#exactamente que hace eso 
            requerimientom = requerimiento_obj.browse(cr, uid, move_lines)#  que hace     
            requerimiento_obj.write(cr, uid, this.rqm_id_quitar.id,{'flag':False,})#PONE EL REQUERIMIENTO EL CAMPO FLAG EN FALSO
            lubri_ids_antes = lubricante_line_obj.search(cr, uid, [('requerimiento_quitar_lubri','=',this.rqm_id_quitar.name)])
            manten_ids_antes = mantenimiento_line_obj.search(cr, uid, [('requerimiento_cajachica','=',this.rqm_id_quitar.name)])
            lubricante_line_obj.unlink(cr, uid, lubri_ids_antes)
            mantenimiento_line_obj.unlink(cr, uid, manten_ids_antes)
        return {'type':'ir.actions.act_window_close' }
quitar_rqm_requerimiento()

class import_rqm_mantenimiento(osv.TransientModel):
    _name = 'import.rqm.mantenimiento'
    
    _columns = {
        'rqm_id_mant': fields.many2one('stock.requisition', 'Requerimiento', required=True),
    }

    def import_rqm_mantenimiento_vehiculo(self, cr, uid, ids, context=None):
        vehiculo_obj = self.pool.get('vehiculo')# objeto vehiculo paso a la variabble vehiculo_obj
        mantenimiento_line_obj = self.pool.get('vehiculo.mantenimiento')
        lubricante_line_obj = self.pool.get('vehiculo.lubricante')#NUEVO
        requerimiento_obj = self.pool.get('stock.requisition')
        for this in self.browse(cr, uid, ids):# cargo todo el formulario de este mismo objeto osea los campos en este form
            vehiculom_id = context and context.get('active_id', False) or False#exactamente que hace eso
            move_lines = context and context.get('active_id', False) or False#exactamente que hace eso
            vehiculom = vehiculo_obj.browse(cr, uid, vehiculom_id)#  es un select como funciona
            requerimientom = requerimiento_obj.browse(cr, uid, move_lines)#  que hace
            requerimiento_obj.write(cr, uid, this.rqm_id_mant.id,{'flag':'True',})
            for line in this.rqm_id_mant.move_lines:# aqui cojo el rqm_id.movelines foreinkey osea los campos detalle del requerimiento
                nombre_pro = line.product_id.name
                #requerimiento_obj.write(cr, uid, this.rqm_id_mant.id,{'flag':'True',})#pone la en verdadero el requerimiento escogido
                if nombre_pro.startswith("ACEITE"):#si el item de requerimiento empieza con aceite ingresa a lubricantes
                    move2_id = lubricante_line_obj.create(cr, uid, { 
                        'descripcion_lubricante':line.product_id.name,
		                'cantidad':line.qty,
                        'vehiculol_id':vehiculom.id,
                        'fecha':this.rqm_id_mant.date,
                        'requerimiento_quitar_lubri':this.rqm_id_mant.name,
                        'unidad_id':line.uom_id.id,
                    })
                else: #si el item de requerimiento no empieza con aceite ingresa a mantenimiento
                    move_id = mantenimiento_line_obj.create(cr, uid, { 
                        'name':line.product_id.name,#paso nombre del product q pertenece ala tabla stock.requisition.line y esta a producto
		                'cantidad':line.qty,
                        'vehiculom_id':vehiculom.id,
                        'date':this.rqm_id_mant.date,
                        'requerimiento_cajachica':this.rqm_id_mant.name,
                        'unidad_id':line.uom_id.id,
                    })

        return {'type':'ir.actions.act_window_close' }

import_rqm_mantenimiento()

class import_caja_mantenimiento(osv.TransientModel):
    _name = 'import.caja.mantenimiento'
    
    _columns = {
        'caja_id_mant': fields.many2one('caja.chica.solicitud', 'Caja Chica', required=True),
    }

    def import_caja_mantenimiento_vehiculo(self, cr, uid, ids, context=None):
        vehiculo_obj = self.pool.get('vehiculo')# objeto vehiculo paso a la variabble vehiculo_obj
        mantenimiento_line_obj = self.pool.get('vehiculo.mantenimiento')
        caja_obj = self.pool.get('caja.chica.solicitud')
        for this in self.browse(cr, uid, ids):# cargo todo el formulario de este mismo objeto
            vehiculom_id = context and context.get('active_id', False) or False#exactamente que hace eso
            filas = context and context.get('active_id', False) or False#exactamente que hace eso
            vehiculom = vehiculo_obj.browse(cr, uid, vehiculom_id)#  es un select como funciona
            caja_id = caja_obj.browse(cr, uid, filas)#  es un select como funciona
            for line in this.caja_id_mant.line_ids:# 
                move_id = mantenimiento_line_obj.create(cr, uid, { 
                    'name':line.name,#paso el nombre de la descripcion del detalle de la caja chica
		            'cantidad':line.qty,
                    'vehiculol_id':vehiculom.id,#que hace
                    'date':this.caja_id_mant.date,
                    'requerimiento_cajachica':this.caja_id_mant.name,
                    'unidad_id':line.unidad.id,

                })
        return {'type':'ir.actions.act_window_close' }


import_caja_mantenimiento() 


class vehiculo_combustible(osv.Model):
    _name = 'vehiculo.combustible'
    _description = 'Combustible de Vehiculos'
    _order = 'name'

    _columns = dict(
        vehiculoc_id = fields.many2one('vehiculo','Vehiculo'),
        date=fields.date('Fecha'),
        cantidad=fields.integer('Cantidad',size=20),
        name = fields.float('Kilometraje'),
        consumo_mensual = fields.float('Consumo Mensual'),
        state = fields.selection([('Borrador','Borrador'),('Ejecutado','Ejecutado')],'Estado'),
)
    _defaults = dict(
        date = time.strftime('%Y-%m-%d'),
        state = 'Borrador',
        )      
        
vehiculo_combustible()

class vehiculoChofer(osv.Model):
   _name = 'vehiculo.chofer'

   def carga_puesto(self, cr, uid, ids, chofer_id, context={}):
       item_obj = self.pool.get('hr.employee')
       res = {}
       item = item_obj.browse(cr, uid, chofer_id,context=context)
       return {'value':{'name':item.job_id.name}}


   _columns = dict(
      c_id = fields.many2one('vehiculo','Vehiculo'),
      chofer_id=fields.many2one('hr.employee','Chofer'),
      name = fields.char('Puesto de Trabajo',size=256),
   )
vehiculoChofer()

class vehiculo_mantenimiento(osv.Model):
    _name = 'vehiculo.mantenimiento'
    _description = 'Mantenimiento de Vehiculos'
    _order = 'date'

    _columns = dict(
        vehiculom_id = fields.many2one('vehiculo','Vehiculo'),
        date=fields.date('Fecha'),
 	    name=fields.char('Descripcion del Repuesto',size=128),
        cantidad=fields.float('Cantidad'),
        unidad_id = fields.many2one('product.uom','Unidad'),
        kilometraje = fields.float('Kilometraje'),
        requerimiento_cajachica = fields.char('Requerimiento/Caja Chica',size=10),
        observaciones = fields.char('Observaciones',size=64),
	    requerimiento_id = fields.many2one('stock.requisition','Requerimiento'), 
        caja_id = fields.many2one('caja.chica.solicitud','Caja Chica'),   
              
) 
    _defaults = dict(
        date = time.strftime('%Y-%m-%d'),
        )
 
       
vehiculo_mantenimiento()


class tipo_lubricante(osv.Model):
    _name = 'tipo_lubricante'
    _description = 'Tipo de lubricantes'
    _order = 'name'

    _columns = dict(
 	name=fields.char('descripcion',size=128),
)        
tipo_lubricante()

class tipo_cambio_lubricante(osv.Model):
    _name = 'tipo_cambio_lubricante'
    _description = 'cambio lubricante'
    _order = 'name'

    _columns = dict(
 	name=fields.char('descripcion',size=128),
)        
tipo_cambio_lubricante()

class vehiculo_lubricante(osv.Model):
    _name = 'vehiculo.lubricante'
    _order = 'fecha'

    _columns = dict(
        vehiculol_id = fields.many2one('vehiculo','Vehiculo'),
        tipo_lubricante_id=fields.many2one('tipo_lubricante','Lubricante'),  #la lubricacion puede tener varios lubricanes
        descripcion_lubricante=fields.char('descripcion del lubricante',size=128),
        tipo_cambio_id=fields.many2one('tipo_cambio_lubricante','Observaciones'),#untipo de lubricacion esta en varias lubs.ej: cambio motor
	cantidad=fields.integer('Cantidad',size=20),
        unidad_id = fields.many2one('product.uom','Unidad'),
        name = fields.float('Kilometraje'),
	proximo_cambio_kilometraje = fields.float('Proximo Kilometraje'),
	fecha=fields.date('Fecha'),
        requerimiento1_id = fields.many2one('stock.requisition','Requerimiento'),
        requerimiento_quitar_lubri = fields.char('Requerimiento / cajachica',size=10),
        cajachica_quitar_lubti = fields.char('Caja Chica',size=10),
)

    _defaults = dict(
        fecha = time.strftime('%Y-%m-%d'),
        )
 
vehiculo_lubricante()

class vehiculo(osv.Model):
    _name = 'vehiculo'
    _description = 'vehiculos'
    _order = 'name'

    def _get_user(self, cr, uid, ids, context=None):
        return uid    


    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
                name = record.name.name
                res.append((record.id, name))
        return res

    def _check_vehiculo_unico(self, cr, uid, ids):
        vehiculo_obj = self.pool.get('vehiculo')
        for vehi in self.browse(cr, uid, ids):
            vehiculo_ids = vehiculo_obj.search(cr, uid, [('activo_vehiculo_id','=',vehi.activo_vehiculo_id.name),('id','!=',vehi.id)]) 
            if vehiculo_ids:
                return False
        return True

    def disponible_reparacion(self, cr, uid, ids, context=None):
       vehiculo_obj = self.pool.get('vehiculo')
       #req_obj = self.pool.get('stock.requisition')
       for this in vehiculo_obj.browse(cr, uid, ids):
          vehiculo_obj.write(cr, uid, this.id,{
             'state':'Reparacion',
          })
          #creamos un req a bodega
          #req_obj.create(cr, uid, {
           #  'solicitant_id':this.activo_vehiculo_id.employee_id.id,
            # 'note':'CREADO DE EJEMPLO',
          #})
       return True

    def reparacion_disponible(self, cr, uid, ids, context=None):
       vehiculo_obj = self.pool.get('vehiculo')
       for this in vehiculo_obj.browse(cr, uid, ids):
          vehiculo_obj.write(cr, uid, this.id,{
             'state':'Disponible',
          })
       return True

    _columns = dict(
       state = fields.selection([('Reparacion','Reparacion'),('Disponible','Disponible')],'Estado'),
       chofer_ids = fields.one2many('vehiculo.chofer','c_id','Choferes'),
        
 	#placa = fields.char('PLACA',size=7),
        type = fields.selection([('Vehiculo','Vehiculo'),('Maquinaria','Maquinaria')],'type'),#para tener 2 formularios por tipo de vehiculo
        create_user_id = fields.many2one('res.users','Creado por'), #un usuario puede crear varias lubricaciones
        activo_vehiculo_id = fields.many2one('account.asset.asset','Vehiculo'), #un activo de vehiculo puede estar en varias clases de vehiculo
        lubricante_ids = fields.one2many('vehiculo.lubricante','vehiculol_id','Lubricaciones'),# varias lubricaciones estan en un vehiculo
        mantenimiento_ids = fields.one2many('vehiculo.mantenimiento','vehiculom_id','Mantenimientos'),# varios mantenimientos stan en un vehiculo
        combustible_ids = fields.one2many('vehiculo.combustible','vehiculoc_id','Combustibles'),# varios combustibles stan en un vehiculo
        name = fields.many2one('vehiculo.alias','Descripcion') #varios vehiculos pueden tener un alias.
)

    _constraints = [
        (_check_vehiculo_unico,'El vehiculo yase encuentra registrado, ingrese otro',['activo_vehiculo_id'])
        ]

    _defaults = dict(
       create_user_id = _get_user,
       state = 'Disponible',
        )
vehiculo()



