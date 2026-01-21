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
import netsvc

class projectEjectNew(osv.TransientModel):
   _name = 'project.eject.new'

   def project_eject_new(self, cr, uid, ids, context):
      project_obj = self.pool.get('project.project')
      wf_service = netsvc.LocalService("workflow")
      data = self.read(cr, uid, ids[0])
      project_ids = project_obj.search(cr, uid, [('fy_id','=',data['year_id'][0])])
      if project_ids:
         for project_id in project_ids:
            wf_service.trg_validate(uid, 'project.project', project_id, 'signal_planning', cr)
            wf_service.trg_validate(uid, 'project.project', project_id, 'signal_planning', cr)
            wf_service.trg_validate(uid, 'project.project', project_id, 'signal_execution', cr)
      return True

   _columns = dict(
      year_id = fields.many2one('account.fiscalyear','Anio Fiscal'),
   )
projectEjectNew()

class budgetCierreLine(osv.TransientModel):
   _name = 'budget.cierre.line'
   _columns = dict(
      c_id = fields.many2one('budget.cierre','Cierre Presupuestos'),
      project_id = fields.many2one('project.project','Proyecto'),
      opcion = fields.selection([('valor','Con Valores Anteriores'),('codificado','Codificado'),('cero','En cero')],'Pasar valores'),
   )
budgetCierreLine()

class budgetCierre(osv.TransientModel):
   _description = 'Cierre Presupuestario'
   _name ='budget.cierre'

   def budget_cargar(self, cr, uid, ids, context):
      line_obj = self.pool.get('budget.cierre.line')
      project_obj = self.pool.get('project.project')
      this = self.browse(cr, uid, ids[0])
      project_ids = project_obj.search(cr, uid, [('poa_id','=',this.poa_ant_id.id)])
      if project_ids:
         for project_id in project_ids:
            line_obj.create(cr, uid, {
               'project_id':project_id,
               'c_id':this.id,
               'opcion':this.valor,
            })
      return True

   def budget_cerrar(self, cr, uid, ids, context):
      # solo crea proyecto tarea los items con otro wizard el mismo que importa de excel
      wf_service = netsvc.LocalService("workflow")
      project_obj = self.pool.get('project.project')
      project_task = self.pool.get('project.task')
      item_obj = self.pool.get('budget.item')
      budget_obj = self.pool.get('budget.budget')
      parameter_obj = self.pool.get('ir.config_parameter')
      this = self.browse(cr, uid, ids[0])
      is_codif = False
      if this.line_ids:
         codif_ids = parameter_obj.search(cr, uid, [('key','=','loadcodif')],limit=1)
         if codif_ids:
            is_codif = True
         context = {'by_date':True,'date_start': this.year_ant_id.date_start, 'date_end': this.year_ant_id.date_stop,'poa_id':this.poa_ant_id.id}
         for line_id in this.line_ids:
            project_ant = project_obj.browse(cr, uid, line_id.project_id.id)
            id_new = project_obj.create(cr, uid, {
               'fy_id':this.year_id.id,
               'code':project_ant.code,
               'name':project_ant.name,
               'poa_id':this.poa_id.id,
               #'members':project_ant.members,
               'date_start':this.poa_id.date_start,
               'date':this.poa_id.date_end,
               'department_id':project_ant.department_id.id,
               'user_id':project_ant.user_id.id,
               'axis_id':project_ant.axis_id.id,
               'estrategy_id':project_ant.estrategy_id.id,
               'program_id':project_ant.program_id.id,
               'type_id':project_ant.type_id.id,
               'type_budget':project_ant.type_budget,
               'canton_id':project_ant.canton_id.id,
               'parish_id':project_ant.parish_id.id,
               'background':project_ant.background,
               'justification':project_ant.justification,
               'general_objective':project_ant.general_objective,
               'specific_objectives':project_ant.specific_objectives,
            })
            #pasa los miembros
            miembro_ids = []
            for miembro in project_ant.members:
               miembro_ids.append(miembro.id)
            project_obj.write(cr, uid, id_new,{
               'members':[(6,0,miembro_ids)],
            })
            for activity in project_ant.tasks:
               activity_id = project_task.create(cr, uid, {
                  'name':activity.name,
                  'weight':activity.weight,
                  'date_start':this.poa_id.date_start,
                  'date_end':this.poa_id.date_end,
                  'project_id':id_new,
                  'task_ant':activity.id,
               })
               #crea budget items
               for item_line in activity.budget_planned_ids:
                  planificado = 0 
                  if line_id.opcion=='valor':
                     planificado = item_line.planned_amount
                  elif line_id.opcion=='codificado':
                     planificado = 0
                     if is_codif:
                        item_line2 = item_obj.browse(cr, uid, item_line.id,context=context)
                        planificado = item_line2.codif_amount
                  item_id = item_obj.create(cr, uid, {
                     'budget_post_id':item_line.budget_post_id.id,
                     'planned_amount':planificado,
                     'task_id':activity_id,
                     'project_id':id_new,
                     'suplemento':0,
                     'reduccion':0,
                     'traspaso_aumento':0,
                     'traspaso_disminucion':0,
                     'reform_amount':0,
                     'request_amount':0,
                     'codif_amount':0,
                     'commited_amount':0,
                     'reserved_amount':0,
                     'devengado_amount':0,
                     'paid_amount':0,
                     'commited_balance':0,
                     'commited_sobregiro':0,
                     'devengado_sobregiro':0,
                     'devengado_balance':0,
                     'avai_amount':0,
                  })
      else:
         project_ids = project_obj.search(cr, uid, [('poa_id','=',this.poa_ant_id.id)])
         if project_ids:
            for project_id in project_ids:
               project_ant = project_obj.browse(cr, uid, project_id)
               id_new = project_obj.create(cr, uid, {
                  'fy_id':this.year_id.id,
                  'code':project_ant.code,
                  'name':project_ant.name,
                  'poa_id':this.poa_id.id,
                  #'members':project_ant.members,
                  'date_start':this.poa_id.date_start,
                  'date':this.poa_id.date_end,
                  'department_id':project_ant.department_id.id,
                  'user_id':project_ant.user_id.id,
                  'axis_id':project_ant.axis_id.id,
                  'estrategy_id':project_ant.estrategy_id.id,
                  'program_id':project_ant.program_id.id,
                  'type_id':project_ant.type_id.id,
                  'type_budget':project_ant.type_budget,
                  'canton_id':project_ant.canton_id.id,
                  'parish_id':project_ant.parish_id.id,
                  'background':project_ant.background,
                  'justification':project_ant.justification,
                  'general_objective':project_ant.general_objective,
                  'specific_objectives':project_ant.specific_objectives,
               })
               #pasa los miembros
               miembro_ids = []
               for miembro in project_ant.members:
                  miembro_ids.append(miembro.id)
               project_obj.write(cr, uid, id_new,{
                  'members':[(6,0,miembro_ids)],
               })
               for activity in project_ant.tasks:
                  activity_id = project_task.create(cr, uid, {
                     'name':activity.name,
                     'weight':activity.weight,
                     'date_start':this.poa_id.date_start,
                     'date_end':this.poa_id.date_end,
                     'project_id':id_new,
                     'task_ant':activity.id,
                  })
                  #crea budget items
                  for item_line in activity.budget_planned_ids:
                     planificado = 0 
                     if this.valor=='valor':
                        planificado = item_line.planned_amount
                     item_id = item_obj.create(cr, uid, {
                        'budget_post_id':item_line.budget_post_id.id,
                        'planned_amount':planificado,
                        'project_id':id_new,
                        'task_id':activity_id,
                        'suplemento':0,
                        'reduccion':0,
                        'traspaso_aumento':0,
                        'traspaso_disminucion':0,
                        'reform_amount':0,
                        'request_amount':0,
                        'codif_amount':0,
                        'commited_amount':0,
                        'reserved_amount':0,
                        'devengado_amount':0,
                        'paid_amount':0,
                        'commited_balance':0,
                        'commited_sobregiro':0,
                        'devengado_sobregiro':0,
                        'devengado_balance':0,
                        'avai_amount':0,
                     })
      return True

   _columns = dict(
      line_ids = fields.one2many('budget.cierre.line','c_id','Detalle Apertura'),
      valor = fields.selection([('valor','Con Valores Anteriores'),('codificado','Codificado'),('cero','En cero')],'Pasar valores'),
      year_ant_id = fields.many2one('account.fiscalyear','Periodo Cerrar'),
      year_id = fields.many2one('account.fiscalyear','Periodo Planificacion'),
      poa_ant_id = fields.many2one('budget.poa','Presupuesto Cerrar'),
      poa_id = fields.many2one('budget.poa','Presupuesto'),
   )
budgetCierre()


