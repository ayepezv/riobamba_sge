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
from tools import ustr

class ejecutaIe(osv.TransientModel):

   _name ='ejecuta.ie'
   _columns = {
        'period_id': fields.many2one('hr.work.period.line', 'Periodo'),
       }

   def ejecuta_ie(self, cr, uid, ids, context):
      slip_obj = self.pool.get('hr.payslip')
      ie_obj = self.pool.get('hr.ie.head')
      line_obj = self.pool.get('hr.ie.line')
      contract_obj = self.pool.get('hr.contract')
      if context is None:
         context = {}
      data = self.read(cr, uid, ids)[0]
      period_id = data['period_id'][0]
      head_all_ids = ie_obj.search(cr, uid, [('period_id','=',period_id)])
      if head_all_ids:
         cr.execute("update hr_ie_head set state='%s' where id in %s"%('draft',str(tuple(head_all_ids))))
         sql_aux = "update hr_ie_line set state='%s' where head_id in %s"%('draft',str(tuple(head_all_ids)))
        #  sql_aux = "update hr_ie_line set valor=valor_original,state='%s' where head_id in %s"%('draft',str(tuple(head_all_ids)))
         cr.execute(sql_aux)
      head_ids = ie_obj.search(cr, uid, [('period_id','=',period_id),('name.is_replanifica','=',False),('state','=','draft')])
      if head_ids:
         cr.execute("update hr_ie_head set state='%s' where id in %s"%('pendiente',str(tuple(head_ids))))
         cr.execute("update hr_ie_line set state='%s' where head_id in %s"%('pendiente',str(tuple(head_ids))))
      for this in self.browse(cr, uid, ids, context):
         lista_rubros = []
         cr.execute("select id from hr_salary_rule where is_replanifica=True order by sequence")
         for rubro in cr.fetchall():
            lista_rubros.append(rubro[0])
         head_ids2 = ie_obj.search(cr, uid, [('period_id','=',period_id),('name','in',lista_rubros),('state','=','draft')],order='sequence desc')
         contract_ids = contract_obj.search(cr, uid, [('activo','=',True),('date_start','<=',this.period_id.date_stop),'|',
                                                      ('date_end','>=',this.period_id.date_start),
                                                      ('date_end','=',False)])
         if contract_ids:
            for contract_id in contract_ids:
               context.update({'contract':True})
               contrato = contract_obj.browse(cr, uid, contract_id)
               from_date = this.period_id.date_start
               to_date = this.period_id.date_stop
               slip_data = slip_obj.onchange_employee_id(cr,uid,[],from_date,to_date,contrato.employee_id.id,contrato.id,context=context)
               department_id = contrato.employee_id.department_id.id
               job_id = contrato.employee_id.job_id.id
               res = {
                  'employee_id': contrato.employee_id.id,
                  'name': slip_data['value'].get('name', False),
                  'struct_id': contrato.struct_id.id,
                  'contract_id': contrato.id,
                  'payslip_run_id': context.get('active_id', False),
                  'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
                  'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
                  'date_from': from_date,
                  'date_to': to_date,
                  'department_id': department_id,
                  'job_id': job_id,
               }
               slip_id = slip_obj.create(cr, uid, res, context=context)
               slip_obj.compute_sheet(cr, uid, [slip_id], context=context)
               rol = slip_obj.browse(cr, uid, slip_id)
               sql_lines = "select l.id from hr_ie_line l,hr_salary_rule r where l.categ_id=r.id and employee_id=%s and head_id in %s and period_id=%s order by r.sequence desc"%(contrato.employee_id.id,str(tuple(head_ids2)),this.period_id.id)
               cr.execute(sql_lines)
               lineas = cr.fetchall()
               if lineas:
                  recibir_rol = rol.net
                  #if recibir_rol<0:
                     #raise osv.except_osv("Error !", "El funcionario %s tiene rol negativo, aun despues de replanificar descuentos"%(ustr(rol.employee_id.complete_name)))
                  total_menos = diferencia = 0
                  for line_id in lineas:
                     line = line_obj.browse(cr, uid, line_id[0])
                     line_obj.write(cr, uid, line_id,{'state':'pendiente',})
                     if diferencia != 0:
                        line_obj.write(cr,uid, line.id,{
                           'valor_original':line.valor,
                           'valor':0,
                        })
                        recibir_rol = 0
                     if recibir_rol>0:
                        if recibir_rol - line.valor_original >= 0:
                           recibir_rol = recibir_rol - line.valor_original
                        else:
                           diferencia = recibir_rol
                           line_obj.write(cr,uid, line.id,{
                              'valor_original':line.valor_original,
                              'valor':diferencia,
                           })
         cr.execute("update hr_ie_head set state='%s' where id in %s"%('pendiente',str(tuple(head_ids2))))
      return {'type':'ir.actions.act_window_close' }

ejecutaIe()


