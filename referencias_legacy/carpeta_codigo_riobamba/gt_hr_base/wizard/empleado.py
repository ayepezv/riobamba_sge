# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

import time
from osv import fields, osv
from time import strftime

class importDeductionLine(osv.TransientModel):
   _name = 'import.deduction.line'
   _columns = dict(
      i_id = fields.many2one('import.deduction','Deducciones'),
      employee_id = fields.many2one('hr.employee','Funcionario'),
      monto = fields.float('Valor'),
   )
importDeductionLine()

class importDeduction(osv.TransientModel):
   _name = 'import.deduction'
   _columns = dict(
      period_id = fields.many2one('hr.work.period','Anio'),
      deduction_id = fields.many2one('hr.deduction','Deduccion'),
      line_ids = fields.one2many('import.deduction.line','i_id','Detalle'),
      archivo = fields.binary('Archivo', required=True),
      log = fields.text('Log Importacion'),
   )

   def confirmDeduction(self, cr, uid, ids, context=None):
      proy_obj = self.pool.get('hr.anual.projection')
      proy_line_obj = self.pool.get('hr.projection.line')
      for this in self.browse(cr, uid, ids):
         aux_projection_id = this.deduction_id.id
         for line in this.line_ids:
            proy_ids = proy_obj.search(cr, uid, [('employee_id','=',line.employee_id.id),('fy_id','=',this.period_id.id)])
            if proy_ids:
               proy_line_ids = proy_line_obj.search(cr, uid, [('pl_id','=',proy_ids[0]),('projection_id','=',aux_projection_id)])
               if proy_line_ids:
                  proy_line_obj.write(cr, uid, {
                     'value':line.monto,
                  })
               else:
                  proy_line_obj.create(cr, uid, {
                     'pl_id':proy_ids[0],
                     'projection_id':aux_projection_id,
                     'value':line.monto,
                  })
            else:
               proy_id = proy_obj.create(cr, uid, {
                  'employee_id':line.employee_id.id,
                  'fy_id':this.period_id.id,
               })
               proy_line_obj.create(cr, uid, {
                  'pl_id':proy_id,
                  'projection_id':aux_projection_id,
                  'value':line.monto,
               })
      return True   

   def importDeduction(self, cr, uid, ids, context=None):
      ded_obj = self.pool.get('import.deduction')
      emp_obj = self.pool.get('hr.employee')
      line_obj = self.pool.get('import.deduction.line')
      for this in self.browse(cr, uid, ids):
         if this.archivo:
            j = cargados = no = 0 
            aux_log = ''
            for r in range(sh.nrows)[1:]:
               j += 1
               aux_cedula = sh.cell(r,0).value
               emp_ids = emp_obj.search(cr, uid, [('name','=',aux_cedula)])
               if emp_ids:
                  cargados += 1
                  line_obj.create(cr, uid, {
                     'employee_id':emp_ids[0],
                     'monto':sh.cell(r,1).value,
                  })
               else:
                  aux_no += 'aux_cedula' + '/t'
                  no += 1
            aux_log = 'Total Archivo = ' + str(j) + '/t' + 'Cargados = ' + str(cargador) + '/t' + 'No encontrados = ' + str(no) + aux_no 
            ded_obj.write(cr, uid, ids[0],{
               log:aux_log,
            })
      return True

importDeduction()

class imprimeContrato(osv.TransientModel):
   _name = 'imprime.contrato'
   _columns = dict(
      contract_id = fields.many2one('hr.contract','Empleado'),
      type_id = fields.many2one('hr.contract.type.type','Tipo'),
   )

   def default_get(self, cr, uid, fields, context=None):
      if context is None:
         context = {}
      res = {}
      contrato_obj = self.pool.get('hr.contract')
      contrato = contrato_obj.browse(cr, uid, context['active_id'])
      res.update({'contract_id':contrato.id,
                  'type_id':contrato.subtype_id.id})
      return res
   
   def imprimeContrato(self, cr, uid, ids, context=None):
      for this in self.browse(cr, uid, ids):
         #datas = this
         if this.type_id.name=='CONTRATO INDEFINIDO':
            return {
               'type': 'ir.actions.report.xml',
               'report_name': 'indefinidow',
               'model': 'imprime.contrato',
               #'datas': datas,
               'nodestroy': True,                        
            }
         elif this.type_id.name=='CONTRATO':
            return {
               'type': 'ir.actions.report.xml',
               'report_name': 'ocacionalesw',
               'model': 'imprime.contrato',
               #'datas': datas,
               'nodestroy': True,                        
            }
         elif this.type_id.name=='OBREROS':
            return {
               'type': 'ir.actions.report.xml',
               'report_name': 'codtrabajow',
               'model': 'imprime.contrato',
               #'datas': datas,
               'nodestroy': True,                        
            }
         else:
            print "no"
      return True

imprimeContrato()
class empleadoListaLine(osv.TransientModel):
   _name = 'empleado.lista.line'
   _order = 'employee_name asc'
   _columns = dict(
      l_id = fields.many2one('empleado.lista','Lista'),
      contract_id = fields.many2one('hr.contract','Contrato'),
      employee_id = fields.many2one('hr.employee','Empleado'),
      employee_name = fields.char('Nombre',size=256),
   )
empleadoListaLine()

class empleadoLista(osv.TransientModel):
   _name ='empleado.lista'
   _columns = dict(
      line_ids = fields.one2many('empleado.lista.line','l_id','Detalle'),
   )
   
   def printListaEmpleado(self, cr, uid, ids, context):
      if context is None:
         context = {}
      contract_obj = self.pool.get('hr.contract')
      line_obj = self.pool.get('empleado.lista.line')
      for this in self.browse(cr, uid, ids):
         contract_ids=contract_obj.search(cr, uid, [('activo','=',True)])
         if contract_ids:
            for contract_id in contract_ids:
               contrato = contract_obj.browse(cr, uid, contract_id)
               line_obj.create(cr, uid, {
                  'employee_id':contrato.employee_id.id,
                  'contract_id':contract_id,
                  'l_id':this.id,
                  'employee_name':contrato.employee_id.complete_name,
               })
      data = self.read(cr, uid, ids, [], context=context)[0]
      report = self.browse(cr, uid, ids, context)[0]
      return {
         'type': 'ir.actions.report.xml',
         'report_name': 'lista_empleado',
         'model': 'empleado.lista',
         'datas': data,
         'nodestroy': True,                        
      }
      return True

empleadoLista()

