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

class hr_payroll_update_wage(osv.osv_memory):

   _name ='hr.payroll.update.wage'
   _columns = {
       'contract_id': fields.many2one('hr.contract', 'Contrato',required=True),
       'wage': fields.float('Sueldo Anterior', readonly=True),
       'new_wage':fields.float('Sueldo Nuevo', required=True),
       }
   
   def onchange_contract(self, cr, uid, ids, contract_id=False, context=None):
      res = {}
      if contract_id:
         contract = self.pool.get('hr.contract').browse(cr, uid, contract_id, context=context)
         if contract.wage:
            res.update({'wage': contract.wage})
      return {
         'value':res
         }

   def update_wage(self, cr, uid, ids, context):
      if context is None:
         context = {}
      data = self.read(cr, uid, ids)[0]
      new_wage = data['new_wage']
      contract_id = data['contract_id'][0]
      contract_obj = self.pool.get('hr.contract')
      wage_hist_obj= self.pool.get('hr.hist.wage')
      contract = contract_obj.browse(cr, uid, contract_id)
      ids_ant=[]
      new_wage=data['new_wage']
      wage=contract.wage
      h_w_id = wage_hist_obj.create(cr, uid, {'name':strftime('%Y-%m-%d'),
                                              'job_id':contract.job_id.id,
                                              'wage':contract.wage,
                                              'contract_wage_id':contract_id,
                                              'new_wage':new_wage})
      contract_obj.write(cr, uid, contract.id,{'wage':new_wage})
      return {'type':'ir.actions.act_window_close' }
  
   _defaults = {

    }

hr_payroll_update_wage()


class hr_payroll_update_masive_wage(osv.osv_memory):

   _name ='hr.payroll.update.masive.wage'
   _columns = {
      'type': fields.selection([('value','Valor'), ('percent', 'Porcentaje')],'Tipo',
                               help="Si el monto a subir es fijo o un porcentaje"),
      'type_value':fields.float('Porcentaje/Valor'),
      'whos':fields.selection([('all','Todos'), ('basic', 'Basico')],'Quienes',
                              help="Si el alza afecta a todos o solo a los que perciben el basico por ley"),
      'basico': fields.float('Basico Anterior'),
      'value':fields.float('Nuevo Salario'),
      'log':fields.text('Actualizados'),
   }
   
   def update_wage(self, cr, uid, ids, context):
      if context is None:
         context = {}
      data = self.read(cr, uid, ids)[0]
      tipo = data['type']
      valor = data['type_value'] 
      valor_ant = data['basico']
      whos = data['whos']
      contract_obj = self.pool.get('hr.contract')
      wage_hist_obj= self.pool.get('hr.hist.wage')
      period_obj = self.pool.get('hr.work.period')
      if whos=='all':
         contract_ids=contract_obj.search(cr, uid, [('activo','=',True)])
      else:
         contract_ids=contract_obj.search(cr, uid, [('wage','=',valor_ant),('activo','=',True)])
      if not contract_ids:
         raise osv.except_osv(('Error de usuario!'), 
                              'No se han encontrado contratos a actualizar')
      aux_log = 'ACTUALIZADOS:'+'\r\n'
      for contract in contract_ids:
         contrato = contract_obj.browse(cr, uid, contract)
         wage=contrato.wage
         if tipo=='value':
            aux=valor
         else:
            aux=(wage)+(wage*valor/100)
         aux_empleado = contrato.employee_id.complete_name + '\t' + str(aux) +'\r\n'
         contract_obj.write(cr, uid, contract, {'wage':aux})
         aux_log += aux_empleado
         h_w_id = wage_hist_obj.create(cr, uid, {'name':strftime('%Y-%m-%d'),'wage':wage,
                                                 'new_wage':aux, 'contract_wage_id':contract})
      self.write(cr, uid, ids[0],{
         'log':aux_log,
      })
      return True#{'type':'ir.actions.act_window_close' }

   _defaults = dict(
      whos = 'basic',
   )

hr_payroll_update_masive_wage()

