# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import fields, osv
import time

class activoTotalDep(osv.TransientModel):
   _name = 'activo.total.dep'
   _columns = dict(
      name = fields.char('Nombre',size=32),
      date_start = fields.date('Desde'),
      date_stop = fields.date('Hasta'),
   )

   def default_get(self, cr, uid, fields, context=None):
      if context is None:
         context = {}
      res = {}
      res.update({'date_stop':time.strftime('%Y-%m-%d'),'date_start':'1900-01-01'})
      return res

   def printActivoTotalDep(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'activo.total.dep'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'activo_total_dep',
            'model': 'activo.total.dep',
            'datas': datas,
            'nodestroy': True,                        
            }

   defaults = dict(
      date_stop= time.strftime('%Y-%m-%d'),
   )

activoTotalDep()

class activoTotal(osv.TransientModel):
   _name = 'activo.total'
   _columns = dict(
      name = fields.char('Nombre',size=32),
      opcion = fields.selection([('Operativos','Operativos'),('No Operativos','No Operativos')],'Opcion'),
      opc = fields.boolean('Entre fechas'),
      date_start = fields.date('Desde'),
      date_stop = fields.date('Hasta'),
   )

   def default_get(self, cr, uid, fields, context=None):
      if context is None:
         context = {}
      res = {}
      res.update({'opcion':'Operativos','date_stop':time.strftime('%Y-%m-%d'),'date_start':'1900-01-01'})
      return res

   def printActivoTotal(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'activo.total'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'activo_total',
            'model': 'activo.total',
            'datas': datas,
            'nodestroy': True,                        
            }

   defaults = dict(
      opcion = 'Operativos',
      date_stop= time.strftime('%Y-%m-%d'),
   )

activoTotal()
class custodioValorado(osv.TransientModel):
   _name = 'custodio.valorado'
   _columns = dict(
      tipo = fields.selection([('Larga Duracion','Larga Duracion'),('Sujeto a Control','Sujeto a Control'),('Todos','Todos')],'Tipo Bien'),
      employee_id = fields.many2one('hr.employee','Funcionario'),
      estado = fields.selection([('Operativos','Operativos'),('Bajas','Bajas')],'Tipo'),
      opc = fields.boolean('Entre fechas'),
      categ_id = fields.many2one('account.asset.category','Categoria'),
      date_start = fields.date('Fecha Desde'),
      date_stop = fields.date('Fecha Hasta'),
   )

   def default_get(self, cr, uid, fields, context=None):
      if context is None:
         context = {}
      res = {}
      res.update({'date_stop':time.strftime('%Y-%m-%d'),'date_start':'1900-01-01','tipo':'Todos'})
      return res

   def printCustodioValorado(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'custodio.valorado'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'custodio_valorado',
            'model': 'custodio.valorado',
            'datas': datas,
            'nodestroy': True,                        
            }

   defaults = dict(
      estado = 'Operativos',
      date_stop= time.strftime('%Y-%m-%d'),
   )

custodioValorado()

class departamentoValor(osv.TransientModel):
   _name = 'departamento.valor'
   _columns = dict(
      dept_ids = fields.many2many('hr.department','d_v_id','d_id','v_id','Departamentos'),
      categ_ids = fields.many2many('account.asset.category','d_c_id','d_id','c_id','Categorias'),
      tipo = fields.selection([('Todos','Todos'),('Seleccionar','Seleccionar')],'Opcion'),
      valor = fields.selection([('Adquisicion','Adquisicion'),('Actual','Actual')],'Valor'),
      opc = fields.boolean('Entre fechas'),
      opc2 = fields.selection([('Operativos','Operativos'),('Todo','Todo')],'Estado'),
      date_start = fields.date('Fecha Desde'),
      date_stop = fields.date('Fecha Hasta'),
   )

   def default_get(self, cr, uid, fields, context=None):
      if context is None:
         context = {}
      res = {}
      res.update({'date_stop':time.strftime('%Y-%m-%d'),'date_start':'1900-01-01'})
      return res

   def printActivoValorado(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'departamento.valor'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'activo_valorado',
            'model': 'departamento.valor',
            'datas': datas,
            'nodestroy': True,                        
            }

   _defaults = dict(
      tipo = 'Todos',
      valor = 'Adquisicion',
      date_stop= time.strftime('%Y-%m-%d'),
      opc2 = 'Operativos',
   )

departamentoValor()
