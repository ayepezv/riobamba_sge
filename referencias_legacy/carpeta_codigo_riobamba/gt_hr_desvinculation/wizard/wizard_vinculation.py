# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from time import strftime
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class hr_vinculation(osv.osv_memory):
   _name='hr.vinculation'

   def onchange_job(self, cr, uid, ids, job_id, contract_id,context=None):
       res={}
       sectorial_obj=self.pool.get('hr.sectorial.table')
       sectorial_line_obj = self.pool.get('hr.sectorial.table.line')
       emp_aca_obj = self.pool.get('hr.employee.title')
       job_obj = self.pool.get('hr.job')
       contract_obj = self.pool.get('hr.contract')
       contract = contract_obj.browse(cr, uid, contract_id)
       linea_academica_ids = emp_aca_obj.search(cr, uid, [('employee_id','=',contract.employee_id.id),('titulo','=',True)],limit=1)
       if not linea_academica_ids:
           res.update({
                   'w_sugested':0,
                   'wage':0,
                   })
       else:
           linea_academica = emp_aca_obj.browse(cr, uid, linea_academica_ids[0])
           sectorial_ids=sectorial_obj.search(cr, uid, [('vigente','=',True)])
           if sectorial_ids:
               job = job_obj.browse(cr, uid, job_id)
               line_ids = sectorial_line_obj.search(cr, uid, [('job_id','=',job.name.id),('nivel','=',linea_academica.nivel),
                                                              ('vigente','=',True)],limit=1)
               if line_ids:
                   line = sectorial_line_obj.browse(cr, uid, line_ids[0])
                   res.update({
                           'w_sugested':line.valor,
                           'wage':line.valor,
                           })
           else:
               raise osv.except_osv(('Error de configuración !'), 'No existe tabla sectorial activa, Notifique al personal de sistemas de esta configuración')
       return {
           'value':res
           }
   
   def vinculate(self, cr, uid, ids, context):
       if context is None:
           context = {}
       job_obj = self.pool.get('hr.job')           
       contract_obj = self.pool.get('hr.contract')
       emp_obj = self.pool.get('hr.employee')
       vinculate_obj = self.pool.get('vinculation')
       contract_type_obj = self.pool.get('hr.contract.type')
       data = self.read(cr, uid, ids)[0]
       contract_id = data['contract_id']
       tipo_c = contract_type_obj.browse(cr, uid, data['type_id'])
       contrato=contract_obj.browse(cr, uid, contract_id[0])
       contract_obj.write(cr, uid,contract_id[0],{
               'name':contract_obj.pool.get('ir.sequence').get(cr, uid, 'hr.contract'),
               'active':True,
               #'institute_id':data['institute_id'],
               'job_id':data['job_id'][0],
               'type_id':data['type_id'][0],
               'wage_sugested':data['w_sugested'],
               'wage':data['wage'],
               #'return':data['reingreso'],
               #'meses_ant':data['meses'],
               'date_start':data['date'],
               'date_end':(datetime.strptime(data['date'],'%Y-%m-%d')+timedelta(days=365)).strftime('%Y-%m-%d'),
               'trial_date_start':data['date'],
               'trial_date_end':(datetime.strptime(data['date'],'%Y-%m-%d')+timedelta(days=89)).strftime('%Y-%m-%d'),
               'state':'prueba',
               })
       vinculate_id = vinculate_obj.create(cr, uid, {
               'name':'Vinculacion de empleado',
               'contract_id':contract_id[0],
               'date':strftime('%Y-%m-%d'),
               #'institute_id':data['institute_id'],
               'job_id':data['job_id'][0],
               'wage_sugested':data['w_sugested'],
               'wage':data['wage'],
               })
       #job_obj.job_open(cr, uid, [data['job_id'][0]])
       #job_obj.log_incidence(cr, uid, data['job_id'][0], contrato.employee_id.id, 'vinculation', vinculate_id, context)
       value = {
           'name':'Vinculacion',
           'view_type': 'form',
           'view_mode': 'tree,form',
           'res_model': 'vinculation',
           'res_id': vinculate_id,
           'type': 'ir.actions.act_window',
           }
       return value
   
   def onchange_c(self, cr, uid, ids, contract_id, context=None):
       res={}
       if not contract_id:
           return res
       contract_obj=self.pool.get('hr.contract')
       contrato=contract_obj.browse(cr, uid, contract_id)
       res.update({
               'type_id': contrato.type_id.id,
               'date':contrato.date_start,
               'wage':contrato.wage,
               'job_id':contrato.job_id.id,
               })
       return {
           'value': res
           }

   _columns={
      'date':fields.date('Fecha Inicio'),
      'date_end':fields.date('Fecha Fin'),
#      'struct_id':fields.many2one('hr.payroll.structure','Estructura Salarial'),
#      'wage_type_id':fields.many2one('hr.contract.wage.type','Tipo Salario'),
#      'tipo_id':fields.selection([('subcontratado','Subcontratado'),('admin','Ocacional'),
#                                  ('pfijo','Plazo Fijo'),('parcial','Parcial'),('pfiscal','Prof. Fiscal')],
#                                 'Tipo de contrato'),
      'employee_id':fields.many2one('hr.employee','Empleado',required=True),
      'type_id':fields.many2one('hr.contract.type','Tipo Contrato'),
      'contract_id': fields.many2one('hr.contract', 'Contrato Empleado',required=True),
      'job_id': fields.many2one('hr.job', 'Puesto Trabajo',required=True),
      'w_sugested':fields.float('Sueldo sugerido'),
      'wage':fields.float('Sueldo',required=True),
      'reingreso':fields.boolean('Reingreso???', help="Seleccione esta opción si es un reingreso"),
      'meses':fields.integer('Numero meses',help="Es el número de meses que el empleado trabajo con el contrato anterior"),
      }
   
   _defaults = {
       'date':lambda *a: time.strftime("%Y-%m-%d"),
    }

hr_vinculation()


class hr_desvinculation(osv.osv_memory):
   _name ='hr.desvinculation'
   
   _OUT_TYPE = [('contrato','Por las causas legalmente previstas en el contrato'),
                ('acuerdo','Por acuerdo de las partes'),
                ('conclusion','Por la conclusión de la obra, período de labor o servicios objeto del contrato'),
                ('muerte_empleador','Por muerte o incapacidad del empleador o extinción de la persona jurídicamente contratante'),
                ('muerte_trabajador','Por muerte del trabajador o incapacidad permanente y total del trabajador'),
                ('fuerza_mayor','Por caso fortuito o fuerza mayor que imposibiliten el trabajo y los contratantes no pudieron preveer o evitar'),
                ('vbueno_empleador','Por voluntad del empleador previo visto bueno'),
                ('vbueno_trabajador','Por voluntad del trabajador previo visto bueno'),
                ('desahucio','Por desahucio'),
                ('despido','Por despido intempestivo'),]
   
   _columns = dict(
        contract_id = fields.many2one('hr.contract', 'Contrato',required=True),
        out_type = fields.selection(_OUT_TYPE,'Tipo de Salida'),
        date = fields.date('Fecha'),
        memo = fields.text('Motivo Salida'),
       )
   
   def desvinculate(self, cr, uid, ids, context):
       if context is None:
           context = {}
       #sacar todas las provisiones de los roles del pana en ese periodo fiscal
       data = self.read(cr, uid, ids)[0]
       wage_period_obj=self.pool.get('hr.work.period')
       period_obj=self.pool.get('hr.work.period.line')
       contract_id = data['contract_id']
       job_obj = self.pool.get('hr.job')
       desvinculation_obj=self.pool.get('desvinculation')
       desvinc_line_obj=self.pool.get('desvinculation.line')
       contract_obj = self.pool.get('hr.contract')
#       date_configuration_obj=self.pool.get('hr.fechas.mintrab')
#       after_obj=self.pool.get('employee.after')
#       provision_obj=self.pool.get('hr.provision.line')
#       teacher_obj=self.pool.get('academic.teacher')
       fecha=data['date']
       contract_id=data['contract_id']
       contract_id=contract_id[0]
       ###########
       wage_period_ids=wage_period_obj.search(cr, uid, [('date_start','<=',fecha),('date_stop','>=',fecha)],limit=1)
#       if wage_period_ids:
#           date_configuration_ids=date_configuration_obj.search(cr, uid, [('fy_id','=',wage_period_ids[0])])
#           if date_configuration_ids:
#               date_configuration=date_configuration_obj.browse(cr, uid, date_configuration_ids)
       contrato=contract_obj.browse(cr, uid, contract_id)
#               regimen=contrato.employee_id.regimen
#               periodo_inicio_d3=date_configuration.date_start13
#               periodo_fin_d3=date_configuration.date_stop13
#               if regimen=='costa':
#                   periodo_inicio_d4=date_configuration.date_start14
#                   periodo_fin_d4=date_configuration.date_stop14
#               else:
#                   periodo_inicio_d4=date_configuration.date_start14s
#                   periodo_fin_d4=date_configuration.date_stop14s
#       provisiones_dec3=provision_obj.search(cr, uid, [('state','=','pendiente'),('name','=','DECIMO TERCERO'),
#                                                       ('employee_id','=',contrato.employee_id.id)])
#       provisiones_dec4=provision_obj.search(cr, uid, [('state','=','pendiente'),('name','=','DECIMO CUARTO'),
#                                                       ('employee_id','=',contrato.employee_id.id)])
#       decimos=provisiones_dec3+provisiones_dec4
##########
       d_id = desvinculation_obj.create(cr, uid, {
               'contract_id':contract_id,
               'date':fecha,
               'name':data['memo'],
               'out_type':data['out_type'],
               'state':'confirmed',
               })
       decimos = []
       if decimos:
           for dec_id in decimos:
               provision=provision_obj.browse(cr, uid, dec_id)
               desvinc_line_obj.create(cr, uid, {
                       'name':provision.name+provision.period_id.name,
                       'concepto':provision.name+provision.period_id.name,
                       'valor':provision.valor,
                       'desvinculation_id':d_id,
                   })
##       dias=(datetime.today()-datetime.strptime(contrato.date_end,'%Y-%m-%d')).days
       contract_obj.write(cr, uid, contract_id,{
               'active':False,
               'state':'terminado',
               'out_type':data['out_type'],
 #              'plazo_contrato':dias,
               })
#       after_obj.create(cr, uid, {
#               'employee_id':contrato.employee_id.id,
#               'f_inicio':contrato.date_start,
#               'f_fin':time.strftime("%Y-%m-%d"),
#               'state':'desvinculado',
#               'dias':dias,
#               })
       value = {
           'name':'Desvinculacion',
           'view_type': 'form',
           'view_mode': 'tree,form',
           'res_model': 'desvinculation',
           'res_id': d_id,
           'type': 'ir.actions.act_window',
           }
       return value

   _defaults = dict(
       out_type = 'despido',
       date = time.strftime("%Y-%m-%d"),
    )

hr_desvinculation()
