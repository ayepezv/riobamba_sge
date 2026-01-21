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


#este reporte se esta haciendo falta por terminar
class reporte_varios_combustible(osv.TransientModel):
   _name = 'reporte.varios.combustible'
   _columns = dict(
      name = fields.char('Nombre',size=32),

      variosr_id = fields.many2one('mecanica.varios','Descripcion'),
      opc = fields.boolean('Entre fechas'),
      date_start = fields.date('Desde'),
      date_stop = fields.date('Hasta'),
   )


   def pulsar_opcion(self,cr,ids,context=None):
       return {'value':{'varios_id':''}}

   def default_get(self, cr, uid, fields, context=None):
      if context is None:
         context = {}
      res = {}
      res.update({'date_stop':time.strftime('%Y-%m-%d'),'date_start':'2010-01-01','opcion':'Todos'})
     
      return res

   def print_mecanica_varios_combustible(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'reporte.varios.combustible'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'reporte_varios_combustible',
            'model': 'reporte.varios.combustible',
            'datas': datas,
            'nodestroy': True,                        
            }

   defaults = dict(
      date_stop= time.strftime('%Y-%m-%d'),
     # create_user_id = _get_user,
   )
reporte_varios_combustible()



class mecanica_varios_alias(osv.Model):
    _name = 'mecanica.varios.alias'
    _description = 'alias o nombre del bien'
    _order = 'name'

    _columns = dict(
       name = fields.char('descripcion',size=128),
       codigo = fields.char('Codigo',size=10), 
    )        
mecanica_varios_alias()


class mecanica_varios_tipo_combustible(osv.Model):
    _name = 'mecanica.varios.tipo.combustible'
    _description = 'tipo de combustible'
    _order = 'name'

    _columns = dict(
 	name=fields.char('descripcion',size=128),
)        
mecanica_varios_tipo_combustible()


class mecanica_varios_combustible(osv.Model):
    _name = 'mecanica.varios.combustible'
    _description = 'varios combustilbe'
    _order = 'date'

    _columns = dict(
        varios_id = fields.many2one('mecanica.varios','Varios'),
        date=fields.date('Fecha'),
        cantidad=fields.integer('Cantidad',size=20),
        name = fields.char('Descripcion',255), #no se usa
        tipo_combustible_id=fields.many2one('mecanica.varios.tipo.combustible','Actividad Asignada/Destino'),
        unidad_id = fields.many2one('product.uom','Unidad'),
        responsable_id=fields.many2one('hr.employee','Responsable'),
)   
    _defaults = dict(
        date = time.strftime('%Y-%m-%d'),
        
        )      
        
mecanica_varios_combustible()



class mecanica_varios(osv.Model):
    _name = 'mecanica.varios'
    _description = 'mecanica varios'
    _order = 'name'

#con esta funcion me idica el usuarioque esta actualmente
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

#validacion que el bien de varios sea unico que no se repita 
    def _check_varios_unico(self, cr, uid, ids):
        varios_obj = self.pool.get('mecanica.varios')
        for var in self.browse(cr, uid, ids):
            varios_ids = varios_obj.search(cr, uid, [('name','=',var.name.name),('id','!=',var.id)]) 
            if varios_ids:
                return False
        return True

    _columns = dict(
       
        create_user_id = fields.many2one('res.users','Creado por', help='Usuario que crea este registro'), 
        combustible_ids = fields.one2many('mecanica.varios.combustible','varios_id','Combustibles'),#varios combustibles stan 1 vehiculo
        name = fields.many2one('mecanica.varios.alias','Descripcion', help='Descripcion del bien' ) 
)

    _constraints = [
        (_check_varios_unico,'El bien ya esta registrado, ingrese otro con un nuevo nombre',['name'])
        ]

    _defaults = dict(
       create_user_id = _get_user,
        )
mecanica_varios()



