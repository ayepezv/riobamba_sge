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


class activos_empleado_line(osv.TransientModel):
    _name = 'activos.empleado.line'
    _columns = dict(
        activos_id = fields.many2one('activos.empleado','Saldo'),
        code = fields.char('Codigo', size=64),
        condicion = fields.char('Estado', size=64),
        name = fields.char('Descripcion',size=256),
        activo_id = fields.many2one('account.asset.asset','Activo'),
        valor_actual = fields.float('Valor Actual'),
        valor_compra = fields.float('Valor de Compra'),
        employee_is = fields.char('Empleado',size=256),
        cantidad = fields.integer('cantidad'),
        fecha_actual1=fields.date('Fecha Actual'),
        otros=fields.text('Otros Accesorios'),
        
    )
    _defaults = dict(
        fecha_actual1 = lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
      
   )


activos_empleado_line()

class activos_empleado(osv.TransientModel):
   _name = 'activos.empleado'
   _columns = dict(
      name = fields.char('Nombre',size=32),
      line_ids = fields.one2many('activos.empleado.line','activos_id','Detalle'),
      empleado_id = fields.many2one('hr.employee','Empleado'),
      tipo = fields.selection([('Larga Duracion','Larga Duracion'),('Sujeto a Control','Sujeto a Control'),('Todos','Todos')],'Tipo Bien'),
      estado = fields.selection([('Operativos','Operativos'),('Bajas','Bajas'),('Todos','Todos')],'Estado')
   )

   def mostrar_activos(self, cr, uid, ids, context=None):
       payslip_obj = self.pool.get('hr.payslip')
       line_activo_obj = self.pool.get('activos.empleado.line')
       empleado_obj = self.pool.get('hr.employee')
       activo_obj = self.pool.get('account.asset.asset')
       res = {}
       count=0
       for this in self.browse(cr, uid, ids):
           #this.id es el id de este formulario(clase)y compara si es que ya hay uno guardado en la base de datos
           line_ids_antes = line_activo_obj.search(cr, uid, [('activos_id','=',this.id)]) 
           if line_ids_antes:# si es verdadera la sentencia anterior ingresa.
               line_activo_obj.unlink(cr, uid, line_ids_antes)#entonces unlink borra los registros en la grilla
           
           if this.estado == 'Operativos':
               if this.tipo == 'Todos':
                   activos_ids = activo_obj.search(cr,uid,[('employee_id','=',this.empleado_id.id),('state','=','open')])
                   
               elif this.tipo == 'Larga Duracion':
                   activos_ids = activo_obj.search(cr,uid,[('employee_id','=',this.empleado_id.id),('state','=','open'),
                   ('type','=','Larga Duracion')])
               else:
                   activos_ids = activo_obj.search(cr,uid,[('employee_id','=',this.empleado_id.id),('state','=','open'),
                   ('type','=','Sujeto a Control')])
           elif this.estado == 'Bajas':
               if this.tipo == 'Todos':
                   activos_ids = activo_obj.search(cr,uid,[('employee_id','=',this.empleado_id.id),('state','=','close')])
               elif this.tipo == 'Larga Duracion':
                   activos_ids = activo_obj.search(cr,uid,[('employee_id','=',this.empleado_id.id),('state','=','close'),
                   ('type','=','Larga Duracion')])
               else:
                   if this.tipo == 'Sujeto a Control':
                       activos_ids = activo_obj.search(cr,uid,[('employee_id','=',this.empleado_id.id),('state','=','close'),
                       ('type','=','Sujeto a Control')])
           else:
               if this.tipo == 'Todos':
                   activos_ids = activo_obj.search(cr,uid,[('employee_id','=',this.empleado_id.id)])
               elif this.tipo == 'Larga Duracion':
                   activos_ids = activo_obj.search(cr,uid,[('employee_id','=',this.empleado_id.id),('type','=','Larga Duracion')])
               else:
                   if this.tipo == 'Sujeto a Control':    
                       activos_ids = activo_obj.search(cr,uid,[('employee_id','=',this.empleado_id.id),('type','=','Sujeto a Control')])

           if activos_ids:
               for line_id in activos_ids:
                   count=count + 1
                   activitos = activo_obj.browse(cr, uid, line_id)
                   line_activo_obj.create(cr, uid, {
                       'activos_id':this.id,#se pasa el id actual que se crea en el form al line.id
                       'code':activitos.code,
                       'activo_id':line_id,
                       'name':activitos.name,
                       'valor_actual':activitos.valor_actual,
                       'valor_compra':activitos.purchase_value,
                       'employee_is':activitos.employee_id.name,
                       'condicion':activitos.condicion,
                       'cantidad':count,
                       'otros':activitos.otros_accesorios,
                   })
           else:

               #line_activo_obj.unlink(cr, uid, line_ids_antes)         
               
               raise osv.except_osv(('Aviso'), ('El funcionario no tiene activos'))
               
               
       return True

   def default_get(self, cr, uid, fields, context=None):
      user_obj = self.pool.get('res.users')
      if context is None:
         context = {}
      res = {}
      user = user_obj.browse(cr, uid, uid)
      if user.employee_id:
          res.update({'empleado_id':user.employee_id.id,'tipo':'Todos','estado':'Todos'})
      else:
          raise osv.except_osv(('Error de configuración'), ('El usuario no tiene funcionario relacionado'))
      return res

   def printCustodioValorado(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'activos.empleado'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'activos_empleado',
            'model': 'activos.empleado',
            'datas': datas,
            'nodestroy': True,                        
            }

activos_empleado()




