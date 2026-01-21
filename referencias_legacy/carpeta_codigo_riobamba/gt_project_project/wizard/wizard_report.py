# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from lxml import etree

from osv import osv, fields
from datetime import date
import operator
import csv
import base64
import StringIO
import datetime
from gt_tool import XLSWriter

class nivelBudget(osv.Model):
   _name = 'nivel.budget'
   _columns = dict(
      name = fields.integer('Nivel'),
   )
nivelBudget()

class reportBudgetCard(osv.Model):
   _name = 'report.budget.card'
   _description = "Cédula Presupuestaria"
   
#   _MONTHS = [('1','Enero'),('2','Febrero'),
#              ('3','Marzo'),('4','Abril'),
#              ('5','Mayo'),('6','Junio'),
#              ('7','Julio'),('8','Agosto'),
#              ('9','Septiembre'),('10','Octubre'),
#              ('11','Noviembre'),('12','Diciembre')]

   _columns = dict(
      nivel_aux = fields.many2one('nivel.budget','Nivel'),
      poa_id = fields.many2one('budget.poa','Presupuesto'),
      tipo_nivel = fields.selection([('p','Padre'),('h','Hijas')],'Tipo Nivel'),
      proy = fields.boolean('Por Proyecto'),
      project = fields.boolean('Por programa?'),
      asig_inicial = fields.boolean('Solo asignacion inicial?'),
      project_id = fields.many2one('project.project' ,'Proyecto', domain=[('state','=','exec')]),
      program_ids = fields.many2many('project.program', 'rbc_program_rel', 'report_id', 'program_id', 'Programas'),
      fiscalyear = fields.many2one('account.fiscalyear', 'Fiscal year', ),
      date_from = fields.date('Fecha incicial'),
      date_to = fields.date('Fecha final'),
      nivel = fields.integer('Nivel'),
      data = fields.binary('Archivo de Texto', filters="*.txt",readonly=True),
      filename = fields.char('Nombre', size=128, invisible=True),
      tipo = fields.char('Tipo', size=10),
      mensajes = fields.text('Mensajes'),
      datas = fields.binary('Archivo'),
      datas_fname = fields.char('Nombre archivo', size=128),
   )

   def _get_tipo(self, cr, uid, context=None):
        """Return default tipo value"""
        if context.get('report_name',False):
           if context['report_name'] == 'BudgetCardExpense':
              return 'gasto'
           else:
              return 'ingreso'

   def onchange_project(self, cr, uid, ids, project,date_from,date_to, context=None):
      poa_obj = self.pool.get('budget.poa')
      if project:
         c_b_lines_obj = self.pool.get('budget.item')
         prog = []
         if context.get('active_id',False):
            poa_id = context['active_id']
         else:
            poa_ids = poa_obj.search(cr, uid, [('date_start','<=',date_from),('date_end','>=',date_to)])
            poa_id = poa_ids[0]
         tipo = self._get_tipo(cr, uid, context)
         ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=',tipo)])
         sql_programs = "select id,sequence from project_program where id in (select program_id from budget_item where id in %s group by program_id) order by sequence"%(str(tuple(ids_lines)))
         cr.execute(sql_programs)
         programas = cr.fetchall()
         for program in programas:
            prog.append(program[0])
         if len(prog)>=1:
            domain = {'program_ids':[('id','in',prog)]}
         else:
            domain = {}
         res = {'domain': domain}
      else:
         value = {'program_ids': False}
         res = {'value': value}      
      return res

   def onchange_proyecto(self, cr, uid, ids, project,date_from,date_to, context=None):
      poa_obj = self.pool.get('budget.poa')
      if project:
         c_b_lines_obj = self.pool.get('budget.item')
         proy = []
         if context.get('active_id',False):
            poa_id = context['active_id']
         else:
            poa_ids = poa_obj.search(cr, uid, [('date_start','<=',date_from),('date_end','>=',date_to)])
            poa_id = poa_ids[0] 
         tipo = self._get_tipo(cr, uid, context)
         ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',poa_id),('type_budget','=',tipo)])
         sql_proyectos = "select id from project_project where id in (select project_id from budget_item where id in %s group by project_id) order by id"%(str(tuple(ids_lines)))
         cr.execute(sql_proyectos)
         proyectos = cr.fetchall()
         for proyecto in proyectos:
            proy.append(proyecto[0])
         if len(proy)>=1:
            domain = {'project_id':[('id','in',proy)]}
         else:
            domain = {}
         res = {'domain': domain}
      else:
         value = {'project_id': False}
         res = {'value': value}      
      return res
           
   def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False, context=None):
        res = {}
        if fiscalyear_id:
            start_date = end_date = False
            cr.execute('''
                SELECT date_start,date_stop FROM account_fiscalyear
                               WHERE id=%s''', (fiscalyear_id,))
            data =  cr.fetchall()
            for fy in data:
               res['value'] = {'date_from': fy[0], 'date_to': fy[1]}
        return res     
     
   def _get_fiscalyear(self, cr, uid, context=None):
        """Return default Fiscalyear value"""
        return self.pool.get('account.fiscalyear').find(cr, uid, context=context)

     

   def _get_budget(self, cr, uid, context):     
       if 'active_ids' in context:
               return context['active_ids']

   def gen_excel_totales_budget(self, cr, uid, ids, context):
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        c_b_lines_obj = self.pool.get('budget.item')
        if program:
            ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('program_id','=',program),('type_budget','=','gasto')])
        else:
            ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','gasto')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + '.' + line.program_id.sequence
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'program': line.program_id.id,
                    'padre': True,#False, 
                    'code':code_aux,
                    'code_aux':code_aux,#line.code
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'commited_amount':line.commited_amount,
                    'devengado_amount':line.devengado_amount,
                    'paid_amount':line.paid_amount,
                    'devengado_balance':line.devengado_balance,
                    'commited_balance':line.commited_balance,
                    'codif_amount':line.codif_amount,
                    'reform_amount':line.reform_amount,
                    'final': True,#False,
                    'nivel': line.budget_post_id.nivel,
                }
#                if res_line.has_key(line.budget_post_id.code)==False:
#                    code_aux = line.budget_post_id.code + '.' +line.program_id.sequence
#                    res_line[line.budget_post_id.code]={
#                        'post': line.budget_post_id,
#                        'program': line.program_id.id,
#                        'padre': False, 
#                        'code': line.budget_post_id.code,
#                        'code_aux':line.budget_post_id.code,
#                        'general_budget_name':line.budget_post_id.name,
#                        'planned_amount':line.planned_amount,
#                        'commited_amount':line.commited_amount,
#                        'devengado_amount':line.devengado_amount,
#                        'paid_amount':line.paid_amount,
#                        'devengado_balance':line.devengado_balance,
#                        'commited_balance':line.commited_balance,
#                        'codif_amount':line.codif_amount,
#                        'reform_amount':line.reform_amount,
#                        'final': True,
#                        'nivel': line.budget_post_id.nivel-1,
#                    }
#                else:
#                    res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
#                    res_line[line.budget_post_id.code]['reform_amount']+=line.reform_amount
#                    res_line[line.budget_post_id.code]['codif_amount']+=line.codif_amount
#                    res_line[line.budget_post_id.code]['commited_amount']+=line.commited_amount
#                    res_line[line.budget_post_id.code]['devengado_amount']+=line.devengado_amount
#                    res_line[line.budget_post_id.code]['paid_amount']+=line.paid_amount
#                    res_line[line.budget_post_id.code]['commited_balance']+=line.commited_balance
#                    res_line[line.budget_post_id.code]['devengado_balance']+=line.devengado_balance
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:
                res_line[line.code]['planned_amount']+=line.planned_amount
                res_line[line.code]['reform_amount']+=line.reform_amount
                res_line[line.code]['codif_amount']+=line.codif_amount
                res_line[line.code]['commited_amount']+=line.commited_amount
                res_line[line.code]['devengado_amount']+=line.devengado_amount
                res_line[line.code]['paid_amount']+=line.paid_amount
                res_line[line.code]['commited_balance']+=line.commited_balance
                res_line[line.code]['devengado_balance']+=line.devengado_balance
                #res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
                #res_line[line.budget_post_id.id+line.program_id.id]['reform_amount']+=line.reform_amount
                #res_line[line.budget_post_id.id+line.program_id.id]['codif_amount']+=line.codif_amount
                #res_line[line.budget_post_id.id+line.program_id.id]['commited_amount']+=line.commited_amount
                #res_line[line.budget_post_id.id+line.program_id.id]['devengado_amount']+=line.devengado_amount
                #res_line[line.budget_post_id.id+line.program_id.id]['paid_amount']+=line.paid_amount
                #res_line[line.budget_post_id.id+line.program_id.id]['commited_balance']+=line.commited_balance
                #res_line[line.budget_post_id.id+line.program_id.id]['devengado_balance']+=line.devengado_balance

        res_line['total']={'reform_amount': 0.00,
                           'devengado_amount': 0.00,
                           'paid_amount': 0.00,
                           'commited_amount': 0.00,
                           'recaudado_amount': 0.00,
                           'planned_amount': 0.00,
                           'devengado_balance': 0.00,
                           'commited_balance': 0.00,
                           'codif_amount': 0.00,
                           'level':0,
                           'code':0,
                           'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if (line_totales['devengado_amount'] - line_totales['commited_amount'])>=0.01:
                print line_totales['code'], " mas devengado que comprometido"
            if (line_totales['paid_amount'] - line_totales['devengado_amount'])>=0.01:
                print line_totales['code'], " mas pagado que devengado"
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['commited_amount']+=line_totales['commited_amount']
                res_line['total']['devengado_amount']+=line_totales['devengado_amount']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['devengado_balance']+=line_totales['devengado_balance']
                res_line['total']['commited_balance']+=line_totales['commited_balance']
        return res_line

   def crear_padre_excel(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['devengado_amount'] += data_suma['devengado_amount']
                res[data['post'].parent_id.code]['devengado_balance'] += data_suma['devengado_balance']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reserved_amount'] += data_suma['reserved_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['commited_amount'] += data_suma['commited_amount']
                res[data['post'].parent_id.code]['commited_balance'] += data_suma['commited_balance']
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                   'code_ex':data['post'].parent_id.code,
#                    'program':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                   'reserved_amount':data['reserved_amount'],
                    'devengado_amount':data['devengado_amount'],
                    'devengado_balance':data['devengado_balance'],
                    'paid_amount':data['paid_amount'],     
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                   'avai_amount':data['avai_amount'],
                    'commited_amount':data['commited_amount'],
                    'commited_balance':data['commited_balance'],
                   'reserved_balance':data['reserved_balance'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                    'level': data['post'].parent_id.nivel-1,
                }
            self.crear_padre_excel(res[data['post'].parent_id.code], data_suma,res)

   def gen_excel_budget(self, cr, uid, ids, context):
        res = { }
        res_line = { }
        #context = { }
        result = []
        poa_obj = self.pool.get('budget.poa')
#        date_from = context['date_start']
#        date_to = context['date_end']

        c_b_lines_obj = self.pool.get('budget.item')
        program_obj = self.pool.get('project.program')
        program_ids = []
        for this in self.browse(cr, uid, ids):
           if context.has_key('active_id'):
              presupuesto = poa_obj.browse(cr, uid, context['active_id'])
           else:
              poa_ids = poa_obj.search(cr, uid, [('date_start','<=',this.date_from),('date_end','>=',this.date_to)])
              presupuesto = poa_obj.browse(cr, uid, poa_ids[0])
           date_from = this.date_from
           date_to = this.date_to
           if context['report_name']=='BudgetCard':
              ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',presupuesto.id)])
              context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':presupuesto.id}            
              planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
              #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
              for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
                  if res_line.has_key(line.code)==False:
                      res_line[line.code]={
                          'post': line.budget_post_id,
                          'program': line.program_id.id,
                          'padre': False, 
                          'code':line.code,
                          'general_budget_name':line.budget_post_id.name,
                          'planned_amount':line.planned_amount,
                          'commited_amount':line.commited_amount,
                          'devengado_amount':line.devengado_amount,
                          'paid_amount':line.paid_amount,
                          'devengado_balance':line.devengado_balance,
                          'commited_balance':line.commited_balance,
                          'codif_amount':line.codif_amount,
                          'reform_amount':line.reform_amount,
                         'avai_amount':line.avai_amount,
                         #'reserved_amount':line.reserved_amount,
                          'final': False,
                      }
                      if res_line.has_key(line.budget_post_id.code)==False:
                          res_line[line.budget_post_id.code]={
                              'post': line.budget_post_id,
                              'program': line.program_id.id,
                              'padre': False, 
                              'code': line.budget_post_id.code,
                              'general_budget_name':line.budget_post_id.name,
                              'planned_amount':line.planned_amount,
                              'commited_amount':line.commited_amount,
                              'devengado_amount':line.devengado_amount,
                              'paid_amount':line.paid_amount,
                              'devengado_balance':line.devengado_balance,
                              'commited_balance':line.commited_balance,
                              'codif_amount':line.codif_amount,
                              'reform_amount':line.reform_amount,
                          #   'reserved_amount':line.reserved_amount,
                             'avai_amount':line.avai_amount,
                              'final': True,
                          }
                      else:
                          res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
                          res_line[line.budget_post_id.code]['reform_amount']+=line.reform_amount
                          res_line[line.budget_post_id.code]['codif_amount']+=line.codif_amount
                          res_line[line.budget_post_id.code]['commited_amount']+=line.commited_amount
                          res_line[line.budget_post_id.code]['devengado_amount']+=line.devengado_amount
                          res_line[line.budget_post_id.code]['paid_amount']+=line.paid_amount
                          #res_line[line.budget_post_id.code]['reserved_amount']+=line.reserved_amount
                          res_line[line.budget_post_id.code]['avai_amount']+=line.avai_amount
                          res_line[line.budget_post_id.code]['commited_balance']+=line.commited_balance
                          res_line[line.budget_post_id.code]['devengado_balance']+=line.devengado_balance
                      self.crear_padre_excel(res_line[line.code], res_line[line.code],res_line)
                  else:              
                      res_line[line.code]['planned_amount']+=line.planned_amount
                      res_line[line.code]['reform_amount']+=line.reform_amount
                      res_line[line.code]['codif_amount']+=line.codif_amount
                      res_line[line.code]['commited_amount']+=line.commited_amount
                      res_line[line.code]['devengado_amount']+=line.devengado_amount
                      res_line[line.code]['paid_amount']+=line.paid_amount
                      res_line[line.code]['commited_balance']+=line.commited_balance
                      res_line[line.code]['devengado_balance']+=line.devengado_balance
                      #res_line[line.budget_post_id.code]['reserved_amount']+=line.reserved_amount
                      res_line[line.budget_post_id.code]['avai_amount']+=line.avai_amount

              res_line['total']={'reform_amount': 0.00,
                                 'devengado_amount': 0.00,
                                 'paid_amount': 0.00,
                                 'commited_amount': 0.00,
                                 'recaudado_amount': 0.00,
                                 'planned_amount': 0.00,
                                 'devengado_balance': 0.00,
                                 'commited_balance': 0.00,
                                 'codif_amount': 0.00,
                                 'nivel':0,
                                 'code':0
              }
              values=res_line.itervalues()
              for line_totales in values:
                  if not 'nivel' in line_totales and line_totales['final']==True:
                      res_line['total']['planned_amount']+=line_totales['planned_amount']            
                      res_line['total']['reform_amount']+=line_totales['reform_amount']
                      res_line['total']['codif_amount']+=line_totales['codif_amount']
                      res_line['total']['commited_amount']+=line_totales['commited_amount']
                      res_line['total']['devengado_amount']+=line_totales['devengado_amount']
                      res_line['total']['paid_amount']+=line_totales['paid_amount']
                      res_line['total']['devengado_balance']+=line_totales['devengado_balance']
                      res_line['total']['commited_balance']+=line_totales['commited_balance']              
               ##
              data = res_line
              result_dic=data.values()
              dic_ord=sorted(result_dic, key=operator.itemgetter('code'))
              ingresos_corrientes = []
              ingresos_corrientes_sum = {'code': "" ,
                                         'general_budget_name': 'INGRESOS CORRIENTES',
                                         'planned_amount': 0,
                                         'reform_amount': 0,
                                         'codif_amount': 0,
                                         'devengado_amount': 0,
                                         'devengado_balance': 0
              }
              gastos_corrientes = []
              gastos_corrientes_sum = {'code': "" ,
                                         'general_budget_name': 'GASTOS CORRIENTES',
                                         'planned_amount': 0,
                                         'reform_amount': 0,
                                         'codif_amount': 0,
                                         'devengado_amount': 0,
                                         'devengado_balance': 0
              }        
              sd_corriente = {'code': "." ,
                              'general_budget_name': 'SUPERAVIT/DEFICIT CORRIENTE',
                              'planned_amount': 0,
                              'reform_amount': 0,
                              'codif_amount': 0,
                              'devengado_amount': 0,
                              'devengado_balance': 0
              }
              ingresos_capital = []
              ingresos_capital_sum = {'code': "" ,
                                         'general_budget_name': 'INGRESOS CAPITAL',
                                         'planned_amount': 0,
                                         'reform_amount': 0,
                                         'codif_amount': 0,
                                         'devengado_amount': 0,
                                         'devengado_balance': 0
              }
              gastos_inversion = []
              gastos_inversion_sum = {'code': "" ,
                                         'general_budget_name': 'GASTOS INVERSION',
                                         'planned_amount': 0,
                                         'reform_amount': 0,
                                         'codif_amount': 0,
                                         'devengado_amount': 0,
                                         'devengado_balance': 0
              }        
              gastos_capital = []
              gastos_capital_sum = {'code': "" ,
                                         'general_budget_name': 'GASTOS CAPITAL',
                                         'planned_amount': 0,
                                         'reform_amount': 0,
                                         'codif_amount': 0,
                                         'devengado_amount': 0,
                                         'devengado_balance': 0
              }        
              sd_inversion = {'code': "." ,
                              'general_budget_name': 'SUPERAVIT/DEFICIT DE INVERSION',
                              'planned_amount': 0,
                              'reform_amount': 0,
                              'codif_amount': 0,
                              'devengado_amount': 0,
                              'devengado_balance': 0
              }
              ingresos_financiamiento = []
              ingresos_financiamiento_sum = {'code': "" ,
                                         'general_budget_name': 'INGRESOS FINANCIAMIENTO',
                                         'planned_amount': 0,
                                         'reform_amount': 0,
                                         'codif_amount': 0,
                                         'devengado_amount': 0,
                                         'devengado_balance': 0
              }        
              aplicacion_financiamiento = []
              aplicacion_financiamiento_sum = {'code': "" ,
                                         'general_budget_name': 'APLICACION FINANCIAMIENTO',
                                         'planned_amount': 0,
                                         'reform_amount': 0,
                                         'codif_amount': 0,
                                         'devengado_amount': 0,
                                         'devengado_balance': 0
              }        
              sd_financiamiento = {'code': "." ,
                                   'general_budget_name': 'SUPERAVIT/DEFICIT DE FINANCIAMIENTO',
                                   'planned_amount': 0,
                                   'reform_amount': 0,
                                   'codif_amount': 0,
                                   'devengado_amount': 0,
                                   'devengado_balance': 0
              }
              sd_presupuestario = {'code': "." ,
                                   'general_budget_name': 'SUPERAVIT/DEFICIT PRESUPUESTARIO',
                                   'planned_amount': 0,
                                   'reform_amount': 0,
                                   'codif_amount': 0,
                                   'devengado_amount': 0,
                                   'devengado_balance': 0
              }
              for line in dic_ord:
                  if line.get('post',False):
                      nivel = this.nivel
                      if nivel!=0:
                          nivel = this.nivel
                      else:
                          nivel=4
                      if line['post'].nivel == nivel:
                          if line['code'].startswith('1'):
                              ingresos_corrientes.append(line)
                              ingresos_corrientes_sum['planned_amount'] = ingresos_corrientes_sum['planned_amount'] + line['planned_amount']
                              ingresos_corrientes_sum['reform_amount'] = ingresos_corrientes_sum['reform_amount'] + line['reform_amount']
                              ingresos_corrientes_sum['codif_amount'] = ingresos_corrientes_sum['codif_amount'] + line['codif_amount']
                              ingresos_corrientes_sum['devengado_amount'] = ingresos_corrientes_sum['devengado_amount'] + line['devengado_amount']
                              ingresos_corrientes_sum['devengado_balance'] = ingresos_corrientes_sum['devengado_balance'] + line['devengado_balance']
                          elif line['code'].startswith('5'):
                              gastos_corrientes.append(line)
                              gastos_corrientes_sum['planned_amount'] = gastos_corrientes_sum['planned_amount'] + line['planned_amount']
                              gastos_corrientes_sum['reform_amount'] = gastos_corrientes_sum['reform_amount'] + line['reform_amount']
                              gastos_corrientes_sum['codif_amount'] = gastos_corrientes_sum['codif_amount'] + line['codif_amount']
                              gastos_corrientes_sum['devengado_amount'] = gastos_corrientes_sum['devengado_amount'] + line['devengado_amount']
                              gastos_corrientes_sum['devengado_balance'] = gastos_corrientes_sum['devengado_balance'] + line['devengado_balance']                        
                          elif line['code'].startswith('2'):
                              ingresos_capital.append(line)
                              ingresos_capital_sum['planned_amount'] = ingresos_capital_sum['planned_amount'] + line['planned_amount']
                              ingresos_capital_sum['reform_amount'] = ingresos_capital_sum['reform_amount'] + line['reform_amount']
                              ingresos_capital_sum['codif_amount'] = ingresos_capital_sum['codif_amount'] + line['codif_amount']
                              ingresos_capital_sum['devengado_amount'] = ingresos_capital_sum['devengado_amount'] + line['devengado_amount']
                              ingresos_capital_sum['devengado_balance'] = ingresos_capital_sum['devengado_balance'] + line['devengado_balance']                        
                          elif line['code'].startswith('7'):
                              gastos_inversion.append(line)
                              gastos_inversion_sum['planned_amount'] = gastos_inversion_sum['planned_amount'] + line['planned_amount']
                              gastos_inversion_sum['reform_amount'] = gastos_inversion_sum['reform_amount'] + line['reform_amount']
                              gastos_inversion_sum['codif_amount'] = gastos_inversion_sum['codif_amount'] + line['codif_amount']
                              gastos_inversion_sum['devengado_amount'] = gastos_inversion_sum['devengado_amount'] + line['devengado_amount']
                              gastos_inversion_sum['devengado_balance'] = gastos_inversion_sum['devengado_balance'] + line['devengado_balance']                        
                          elif line['code'].startswith('8'):
                              gastos_capital.append(line)
                              gastos_capital_sum['planned_amount'] = gastos_capital_sum['planned_amount'] + line['planned_amount']
                              gastos_capital_sum['reform_amount'] = gastos_capital_sum['reform_amount'] + line['reform_amount']
                              gastos_capital_sum['codif_amount'] = gastos_capital_sum['codif_amount'] + line['codif_amount']
                              gastos_capital_sum['devengado_amount'] = gastos_capital_sum['devengado_amount'] + line['devengado_amount']
                              gastos_capital_sum['devengado_balance'] = gastos_capital_sum['devengado_balance'] + line['devengado_balance']                        
                          elif line['code'].startswith('3'):
                              ingresos_financiamiento.append(line)
                              ingresos_financiamiento_sum['planned_amount'] = ingresos_financiamiento_sum['planned_amount'] + line['planned_amount']
                              ingresos_financiamiento_sum['reform_amount'] = ingresos_financiamiento_sum['reform_amount'] + line['reform_amount']
                              ingresos_financiamiento_sum['codif_amount'] = ingresos_financiamiento_sum['codif_amount'] + line['codif_amount']
                              ingresos_financiamiento_sum['devengado_amount'] = ingresos_financiamiento_sum['devengado_amount'] + line['devengado_amount']
                              ingresos_financiamiento_sum['devengado_balance'] = ingresos_financiamiento_sum['devengado_balance'] + line['devengado_balance']                       
                          elif line['code'].startswith('9'):
                              aplicacion_financiamiento.append(line)
                              aplicacion_financiamiento_sum['planned_amount'] = aplicacion_financiamiento_sum['planned_amount'] + line['planned_amount']
                              aplicacion_financiamiento_sum['reform_amount'] = aplicacion_financiamiento_sum['reform_amount'] + line['reform_amount']
                              aplicacion_financiamiento_sum['codif_amount'] = aplicacion_financiamiento_sum['codif_amount'] + line['codif_amount']
                              aplicacion_financiamiento_sum['devengado_amount'] = aplicacion_financiamiento_sum['devengado_amount'] + line['devengado_amount']
                              aplicacion_financiamiento_sum['devengado_balance'] = aplicacion_financiamiento_sum['devengado_balance'] + line['devengado_balance']

              sd_corriente['planned_amount'] = ingresos_corrientes_sum['planned_amount'] - gastos_corrientes_sum['planned_amount']
              sd_corriente['reform_amount'] = ingresos_corrientes_sum['reform_amount'] - gastos_corrientes_sum['reform_amount']
              sd_corriente['codif_amount'] = ingresos_corrientes_sum['codif_amount'] - gastos_corrientes_sum['codif_amount'] 
              sd_corriente['devengado_amount'] = ingresos_corrientes_sum['devengado_amount'] - gastos_corrientes_sum['devengado_amount']
              sd_corriente['devengado_balance'] = ingresos_corrientes_sum['devengado_balance'] - gastos_corrientes_sum['devengado_balance']

              sd_inversion['planned_amount'] = ingresos_capital_sum['planned_amount'] - gastos_inversion_sum['planned_amount'] -  gastos_capital_sum['planned_amount']
              sd_inversion['reform_amount'] = ingresos_capital_sum['reform_amount'] - gastos_inversion_sum['reform_amount'] - gastos_capital_sum['reform_amount']
              sd_inversion['codif_amount'] = ingresos_capital_sum['codif_amount'] - gastos_inversion_sum['codif_amount'] - gastos_capital_sum['codif_amount']
              sd_inversion['devengado_amount'] = ingresos_capital_sum['devengado_amount'] - gastos_inversion_sum['devengado_amount'] - gastos_capital_sum['devengado_amount']
              sd_inversion['devengado_balance'] = ingresos_capital_sum['devengado_balance'] - gastos_inversion_sum['devengado_balance'] - gastos_capital_sum['devengado_balance']

              sd_financiamiento['planned_amount'] = ingresos_financiamiento_sum['planned_amount'] - aplicacion_financiamiento_sum['planned_amount']
              sd_financiamiento['reform_amount'] = ingresos_financiamiento_sum['reform_amount'] - aplicacion_financiamiento_sum['reform_amount']
              sd_financiamiento['codif_amount'] = ingresos_financiamiento_sum['codif_amount'] - aplicacion_financiamiento_sum['codif_amount'] 
              sd_financiamiento['devengado_amount'] = ingresos_financiamiento_sum['devengado_amount'] - aplicacion_financiamiento_sum['devengado_amount']
              sd_financiamiento['devengado_balance'] = ingresos_financiamiento_sum['devengado_balance'] - aplicacion_financiamiento_sum['devengado_balance']

              sd_presupuestario['planned_amount'] = ingresos_financiamiento_sum['planned_amount'] - aplicacion_financiamiento_sum['planned_amount'] 
              sd_presupuestario['reform_amount'] = ingresos_financiamiento_sum['reform_amount'] - aplicacion_financiamiento_sum['reform_amount']
              sd_presupuestario['codif_amount'] = ingresos_financiamiento_sum['codif_amount'] - aplicacion_financiamiento_sum['codif_amount'] - sd_financiamiento['codif_amount']
              sd_presupuestario['paid_amount'] = ingresos_financiamiento_sum['devengado_amount'] - aplicacion_financiamiento_sum['devengado_amount']
              #sumas algebraicas
      #        sd_presupuestario['devengado_balance'] = ingresos_financiamiento_sum['devengado_balance'] - aplicacion_financiamiento_sum['devengado_balance']
              sd_presupuestario['devengado_balance'] = sd_corriente['devengado_amount'] + sd_inversion['devengado_amount'] + sd_financiamiento['devengado_amount']
              sd_presupuestario['devengado_amount'] = sd_corriente['devengado_amount'] + sd_inversion['devengado_amount'] + sd_financiamiento['devengado_amount']


              result =  [ingresos_corrientes_sum] + ingresos_corrientes + [gastos_corrientes_sum]+ gastos_corrientes + [sd_corriente]+ [ingresos_capital_sum] + ingresos_capital + [gastos_inversion_sum] + gastos_inversion + [gastos_capital_sum] + gastos_capital + [sd_inversion] + [ingresos_financiamiento_sum] + ingresos_financiamiento + [aplicacion_financiamiento_sum] + aplicacion_financiamiento + [sd_financiamiento] + [sd_presupuestario]                
              #mandar al excel
              #import pdb
              #pdb.set_trace()
              writer_excel = XLSWriter.XLSWriter()
              cabecera_titulo = ["EJECUCION PRESUPUESTARIA " " del " + date_from + ' al ' + date_to]
              writer_excel.append(cabecera_titulo)
              cabecera_all = ['CODIGO','PARTIDA','CODIFICADO','DEVENGADO','DIFERENCIA %']
              writer_excel.append(cabecera_all)
              for values in result:
                 writer_excel.append([values['code'],values['general_budget_name'],values['codif_amount'],values['devengado_amount'],values['codif_amount']-values['devengado_amount']])
              writer_excel.save("EJECUCION PRESUPUESTARIA " + " del "  + date_from + ' al ' + date_to + '.xls')
              out1 = open("EJECUCION PRESUPUESTARIA " + " del " + date_from + ' al ' + date_to + '.xls',"rb").read().encode("base64")
              filename = "EJECUCION PRESUPUESTARIA " + " del " + date_from + ' al ' + date_to + '.txt' 
              self.write(cr, uid, ids, {
                                        'datas':out1,
                                        'datas_fname':"EJECUCION PRESUPUESTARIA " + " del " + date_from + ' al ' + date_to + '.xls',
                                     })
           elif context['report_name']=='BudgetCardIncome':
              aux_tipo = 'INGRESOS'
              ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',presupuesto.id),('type_budget','=','ingreso')])
              context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':presupuesto.id}            
              planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
              for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
                  if res_line.has_key(line.code)==False:
                      code_aux = line.budget_post_id.code + '.' + line.program_id.sequence
                      res_line[line.code]={
                          'post': line.budget_post_id,
                          'program': line.program_id.id,
                          'padre': True,#False,
                         'code_ex':line.code,
                          'code':code_aux,
                          'code_aux':code_aux,#line.code
                          'general_budget_name':line.budget_post_id.name,
                          'planned_amount':line.planned_amount,
                          'commited_amount':line.commited_amount,
                          'devengado_amount':line.devengado_amount,
                          'paid_amount':line.paid_amount,
                          'devengado_balance':line.devengado_balance,
                          'commited_balance':line.commited_balance,
                          'codif_amount':line.codif_amount,
                          'avai_amount':line.avai_amount,
                          'reform_amount':line.reform_amount,
                          'final': True,#False,
                          'nivel': line.budget_post_id.nivel,
                         'level': line.budget_post_id.nivel,
                      }
                      self.crear_padre_excel(res_line[line.code], res_line[line.code],res_line)
                  else:
                     res_line[line.code]['planned_amount']+=line.planned_amount
                     res_line[line.code]['reform_amount']+=line.reform_amount
                     res_line[line.code]['codif_amount']+=line.codif_amount
                     res_line[line.code]['commited_amount']+=line.commited_amount
                     res_line[line.code]['devengado_amount']+=line.devengado_amount
                     res_line[line.code]['paid_amount']+=line.paid_amount
                     res_line[line.code]['commited_balance']+=line.commited_balance
                     res_line[line.code]['devengado_balance']+=line.devengado_balance
                     res_line[line.code]['avai_amount']+=line.avai_amount
                      #res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
                      #res_line[line.budget_post_id.id+line.program_id.id]['reform_amount']+=line.reform_amount
                      #res_line[line.budget_post_id.id+line.program_id.id]['codif_amount']+=line.codif_amount
                      #res_line[line.budget_post_id.id+line.program_id.id]['commited_amount']+=line.commited_amount
                      #res_line[line.budget_post_id.id+line.program_id.id]['devengado_amount']+=line.devengado_amount
                      #res_line[line.budget_post_id.id+line.program_id.id]['paid_amount']+=line.paid_amount
                      #res_line[line.budget_post_id.id+line.program_id.id]['commited_balance']+=line.commited_balance
                      #res_line[line.budget_post_id.id+line.program_id.id]['devengado_balance']+=line.devengado_balance
                      #res_line[line.budget_post_id.id+line.program_id.id]['avai_amount']+=line.avai_amount

              res_line['total']={'reform_amount': 0.00,
                                 'devengado_amount': 0.00,
                                 'paid_amount': 0.00,
                                 'commited_amount': 0.00,
                                 'recaudado_amount': 0.00,
                                 'planned_amount': 0.00,
                                 'devengado_balance': 0.00,
                                 'commited_balance': 0.00,
                                 'codif_amount': 0.00,
                                 'avai_amount': 0.00,
                                 'nivel':0,
                                 'level':0,
                                 'general_budget_name':0,
                                 'code':0,
                                 'code_ex':0,
                                 'code_aux':0,
              }
              values=res_line.itervalues()
              for line_totales in values:
                  if (line_totales['devengado_amount'] - line_totales['commited_amount'])>=0.01:
                      print line_totales['code'], " mas devengado que comprometido"
                  if (line_totales['paid_amount'] - line_totales['devengado_amount'])>=0.01:
                      print line_totales['code'], " mas pagado que devengado"
                  if not 'level' in line_totales and line_totales['final']==True:
                      res_line['total']['planned_amount']+=line_totales['planned_amount']            
                      res_line['total']['reform_amount']+=line_totales['reform_amount']
                      res_line['total']['codif_amount']+=line_totales['codif_amount']
                      res_line['total']['commited_amount']+=line_totales['commited_amount']
                      res_line['total']['devengado_amount']+=line_totales['devengado_amount']
                      res_line['total']['paid_amount']+=line_totales['paid_amount']
                      res_line['total']['devengado_balance']+=line_totales['devengado_balance']
                      res_line['total']['commited_balance']+=line_totales['commited_balance']
                      res_line['total']['avai_amount']+=line_totales['avai_amount']
              writer_excel = XLSWriter.XLSWriter()
              cabecera_titulo = ["CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to]
              writer_excel.append(cabecera_titulo)
              cabecera_all = ['Codigo Partida','Denominacion','Asignacion Inicial','Reforma','Codificado','Comprometido','Devengado','Recaudado','Saldo por devengar','Saldo por recaudar']
              writer_excel.append(cabecera_all)
              result_dict = res_line.values()
              dic_ord = sorted(result_dict, key=operator.itemgetter('code_aux'))
              j = 0
              for line in dic_ord:
                 if j==1:
                    line_total = line
                    aux_pagar_total = line['devengado_balance'] - line['paid_amount']
                    j = 2
                 j+=1
                 #no la partida 0
                 if str(line['code_ex'])[0]!='0':
                    aux_saldo_recaudar = line['codif_amount'] - line['paid_amount']
                    if this.nivel:
                       if this.tipo_nivel:
                          if this.tipo_nivel=='p':
                             if line['level']<=this.nivel:
                                writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['devengado_balance'],aux_saldo_recaudar])
                          elif this.tipo_nivel=='h':
                             if line['level']>=this.nivel:
                                writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['devengado_balance'],aux_saldo_recaudar])
                       else:
                          if line['level']==this.nivel:
                             writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['devengado_balance'],aux_saldo_recaudar])                       
                    else:
                       writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['devengado_balance'],aux_saldo_recaudar])
              writer_excel.append(['','TOTALES',line_total['planned_amount'],line_total['reform_amount'],line_total['codif_amount'],line_total['commited_amount'],line_total['devengado_amount'],line_total['paid_amount'],line_total['devengado_balance'],aux_pagar_total])
              writer_excel.save("CEDULA " + aux_tipo + " del "  + date_from + ' al ' + date_to + '.xls')
              out1 = open("CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to + '.xls',"rb").read().encode("base64")
              filename = "CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to + '.txt' 
              self.write(cr, uid, ids, {
                                        'datas':out1,
                                        'datas_fname':"CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to + '.xls',
                                     })
           else:
              aux_tipo = 'GASTOS'
              if this.project:
                 writer_excel = XLSWriter.XLSWriter()
                 cabecera_titulo = ["CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to]
                 writer_excel.append(cabecera_titulo)
                 total_general = {
                    'planned_amount':0,
                    'reform_amount':0,
                    'codif_amount':0,
                    'reserved_amount':0,
                    'commited_amount':0,
                    'devengado_amount':0,
                    'paid_amount':0,
                    'reserved_balance':0,
                    'commited_balance':0,
                    'devengado_balance':0,
                    'aux_pagar_total':0,
                    }
                 #ordenar por codigo de programa
                 programas = {}
                 program_ids_ord = []
                 for program_id in this.program_ids:
                    if programas.has_key(program_id.sequence)==False:
                       programas[program_id.id]={'code':program_id.sequence,
                                                 'id':program_id.id,
                       }
                 result_programas = programas.values()
                 programa_ids_ordenado = sorted(result_programas, key=operator.itemgetter('code'))
                 for prog in programa_ids_ordenado:
                    program_ids_ord.append(prog['id'])
                 for program_id_id in program_ids_ord:
                    program_id = program_obj.browse(cr, uid, program_id_id)
                    context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':presupuesto.id}            
                    planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
                    aux_program = program_id.sequence+" - "+program_id.name
                    writer_excel.append(['PROGRAMA',aux_program])
                    ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',presupuesto.id),('code','!=','0'),('program_id','=',program_id.id),('type_budget','=','gasto')])
                    res_line = {}
                    for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
                        if res_line.has_key(line.code)==False:
                            code_aux = line.budget_post_id.code + '.' + line.program_id.sequence
                            res_line[line.code]={
                                'post': line.budget_post_id,
                                'program': line.program_id.id,
                                'padre': True,#False, 
                               'code_ex':line.code,
                               'code':code_aux,
                                'code_aux':code_aux,#line.code
                                'general_budget_name':line.budget_post_id.name,
                                'planned_amount':line.planned_amount,
                               'reserved_amount':line.reserved_amount,
                                'commited_amount':line.commited_amount,
                                'devengado_amount':line.devengado_amount,
                                'paid_amount':line.paid_amount,
                                'devengado_balance':line.devengado_balance,
                                'commited_balance':line.commited_balance,
                               'reserved_balance':line.reserved_balance,
                                'codif_amount':line.codif_amount,
                                'avai_amount':line.avai_amount,
                                'reform_amount':line.reform_amount,
                                'final': True,#False,
                                'nivel': line.budget_post_id.nivel,
                               'level': line.budget_post_id.nivel,
                            }
                            self.crear_padre_excel(res_line[line.code], res_line[line.code],res_line)
                        else:
                            res_line[line.code]['planned_amount']+=line.planned_amount
                            res_line[line.code]['reform_amount']+=line.reform_amount
                            res_line[line.code]['codif_amount']+=line.codif_amount
                            res_line[line.code]['commited_amount']+=line.commited_amount
                            res_line[line.code]['reserved_amount']+=line.reserved_amount
                            res_line[line.code]['devengado_amount']+=line.devengado_amount
                            res_line[line.code]['paid_amount']+=line.paid_amount
                            res_line[line.code]['commited_balance']+=line.commited_balance
                            res_line[line.code]['reserved_balance']+=line.commited_balance
                            res_line[line.code]['devengado_balance']+=line.devengado_balance
                            res_line[line.code]['avai_amount']+=line.avai_amount
                    res_line['total']={'reform_amount': 0.00,
                                       'devengado_amount': 0.00,
                                       'paid_amount': 0.00,
                                       'commited_amount': 0.00,
                                       'reserved_amount': 0.00,
                                       'recaudado_amount': 0.00,
                                       'planned_amount': 0.00,
                                       'devengado_balance': 0.00,
                                       'commited_balance': 0.00,
                                       'reserved_balance': 0.00,
                                       'codif_amount': 0.00,
                                       'level':0,
                                       'code':0,
                                       'code_ex':0,
                                       'avai_amount':0,
                                       'general_budget_name':0,
                                       'code_aux':0,
                    }
                    values=res_line.itervalues()
                    for line_totales in values:
                        if (line_totales['devengado_amount'] - line_totales['commited_amount'])>=0.01:
                            print line_totales['code'], " mas devengado que comprometido"
                        if (line_totales['paid_amount'] - line_totales['devengado_amount'])>=0.01:
                            print line_totales['code'], " mas pagado que devengado"
                        if not 'level' in line_totales and line_totales['final']==True:
                            res_line['total']['planned_amount']+=line_totales['planned_amount']            
                            res_line['total']['reform_amount']+=line_totales['reform_amount']
                            res_line['total']['codif_amount']+=line_totales['codif_amount']
                            res_line['total']['reserved_amount']+=line_totales['reserved_amount']
                            res_line['total']['commited_amount']+=line_totales['commited_amount']
                            res_line['total']['devengado_amount']+=line_totales['devengado_amount']
                            res_line['total']['paid_amount']+=line_totales['paid_amount']
                            res_line['total']['devengado_balance']+=line_totales['devengado_balance']
                            res_line['total']['commited_balance']+=line_totales['commited_balance']
                            res_line['total']['reserved_balance']+=line_totales['reserved_balance']
                            res_line['total']['avai_amount']+=line_totales['avai_amount']
                    cabecera_all = ['Codigo Partida','Denominacion','Asignacion Inicial','Reforma','Codificado','Certificado','Comprometido','Devengado','Pagado','Saldo por certificar','Saldo por comprometer','Saldo por devengar','Saldo por  pagar']
                    writer_excel.append(cabecera_all)
                    result_dict = res_line.values()
                    dic_ord = sorted(result_dict, key=operator.itemgetter('code_aux'))
                    j = aux_p_t = 0
                    aux_p_t = dic_ord[1]['devengado_balance'] - dic_ord[1]['paid_amount']
                    writer_excel.append(['','TOTAL PROGRAMA',dic_ord[1]['planned_amount'],dic_ord[1]['reform_amount'],dic_ord[1]['codif_amount'],dic_ord[1]['reserved_amount'],dic_ord[1]['commited_amount'],dic_ord[1]['devengado_amount'],dic_ord[1]['paid_amount'],dic_ord[1]['reserved_balance'],dic_ord[1]['commited_balance'],dic_ord[1]['devengado_balance'],aux_p_t])
                    for line in dic_ord:
                       if j==1:
                          line_total = line
                          total_general['planned_amount']+=line_total['planned_amount']
                          total_general['reform_amount']+=line_total['reform_amount']
                          total_general['codif_amount']+=line_total['codif_amount']
                          total_general['commited_amount']+=line_total['commited_amount']
                          total_general['reserved_amount']+=line_total['reserved_amount']
                          total_general['devengado_amount']+=line_total['devengado_amount']
                          total_general['paid_amount']+=line_total['paid_amount']
                          total_general['commited_balance']+=line_total['commited_balance']
                          total_general['reserved_balance']+=line_total['reserved_balance']
                          total_general['devengado_balance']+=line_total['devengado_balance']
                          total_general['aux_pagar_total']+=(line_total['codif_amount'] - line_total['paid_amount'] )
                          aux_pagar_total = line['devengado_balance'] - line['paid_amount']
                          j = 2
                       j+=1
                       aux_por_pagar = line['codif_amount'] - line['paid_amount']
                       if str(line['code_ex'])[0]!='0':
                          if this.nivel:
                             if this.tipo_nivel:
                                if this.tipo_nivel=='p':
                                   if line['level']<=this.nivel:
                                      writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['reserved_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['reserved_balance'],line['commited_balance'],line['devengado_balance'],aux_por_pagar])
                                elif this.tipo_nivel=='h':
                                   if line['level']>=this.nivel:
                                      writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['reserved_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['reserved_balance'],line['commited_balance'],line['devengado_balance'],aux_por_pagar])
                             else:
                                if line['level']==this.nivel:
                                   writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['reserved_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['reserved_balance'],line['commited_balance'],line['devengado_balance'],aux_por_pagar])
                          else:
                             writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['reserved_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['reserved_balance'],line['commited_balance'],line['devengado_balance'],aux_por_pagar])
                    writer_excel.append(['','TOTAL PROGRAMA',line_total['planned_amount'],line_total['reform_amount'],line_total['codif_amount'],line_total['reserved_amount'],line_total['commited_amount'],line_total['devengado_amount'],line_total['paid_amount'],line_total['reserved_balance'],line_total['commited_balance'],line_total['devengado_balance'],aux_pagar_total])
                 writer_excel.append(['','TOTALES GENERAL',total_general['planned_amount'],total_general['reform_amount'],total_general['codif_amount'],total_general['reserved_amount'],total_general['commited_amount'],total_general['devengado_amount'],total_general['paid_amount'],total_general['reserved_balance'],total_general['commited_balance'],total_general['devengado_balance'],total_general['aux_pagar_total']])     
                 writer_excel.save("CEDULA " + aux_tipo + " del "  + date_from + ' al ' + date_to + '.xls')
                 out1 = open("CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to + '.xls',"rb").read().encode("base64")
                 filename = "CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to + '.txt' 
                 self.write(cr, uid, ids, {
                    'datas':out1,
                    'datas_fname':"CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to + '.xls',
                 })
              else:
                  program_ids = program_obj.search(cr, uid, [])
                  aux_tipo = 'GASTOS'
                  ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',presupuesto.id),('program_id','in',program_ids),('type_budget','=','gasto')])
                  #ids_lines = [26826]
                  context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':presupuesto.id}            
                  planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
                  for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
                     #import pdb
                     #pdb.set_trace()
                     if res_line.has_key(line.code)==False:
                        code_aux = line.budget_post_id.code + '.' + line.program_id.sequence
                        res_line[line.code]={
                           'post': line.budget_post_id,
                           'program': line.program_id.id,
                           'padre': True,#False, 
                           'code':code_aux,
                           'code_ex':line.code,
                           'code_aux':code_aux,#line.code
                           'general_budget_name':line.budget_post_id.name,
                           'planned_amount':line.planned_amount,
                           'commited_amount':line.commited_amount,
                           'reserved_amount':line.reserved_amount,
                           'devengado_amount':line.devengado_amount,
                           'paid_amount':line.paid_amount,
                           'devengado_balance':line.devengado_balance,
                           'commited_balance':line.commited_balance,
                           'reserved_balance':line.reserved_balance,
                           'avai_amount':line.avai_amount,
                           'codif_amount':line.codif_amount,
                           'reform_amount':line.reform_amount,
                           'final': True,#False,
                           'nivel': line.budget_post_id.nivel,
                           'level': line.budget_post_id.nivel,
                        }
                        if res_line.has_key(line.budget_post_id.code)==False:
                           code_aux = line.budget_post_id.code + '.' +line.program_id.sequence
                           res_line[line.budget_post_id.code]={
                              'post': line.budget_post_id,
                              'program': line.program_id.id,
                              'padre': False, 
                              'code':line.budget_post_id.code,
                              'code_ex':line.budget_post_id.code,
                              'code_aux':line.budget_post_id.code,
                              'general_budget_name':line.budget_post_id.name,
                              'planned_amount':line.planned_amount,
                              'commited_amount':line.commited_amount,
                              'reserved_amount':line.reserved_amount,
                              'devengado_amount':line.devengado_amount,
                              'paid_amount':line.paid_amount,
                              'devengado_balance':line.devengado_balance,
                              'commited_balance':line.commited_balance,
                              'reserved_balance':line.reserved_balance,
                              'avai_amount':line.avai_amount,
                              'codif_amount':line.codif_amount,
                              'reform_amount':line.reform_amount,
                              'final': True,#False,
                              'nivel': line.budget_post_id.nivel-1,
                              'level': line.budget_post_id.nivel-1,
                           }
                        else:
                           res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
                           res_line[line.budget_post_id.code]['reform_amount']+=line.reform_amount
                           res_line[line.budget_post_id.code]['codif_amount']+=line.codif_amount
                           res_line[line.budget_post_id.code]['commited_amount']+=line.commited_amount
                           res_line[line.budget_post_id.code]['reserved_amount']+=line.reserved_amount
                           res_line[line.budget_post_id.code]['devengado_amount']+=line.devengado_amount
                           res_line[line.budget_post_id.code]['paid_amount']+=line.paid_amount
                           res_line[line.budget_post_id.code]['commited_balance']+=line.commited_balance
                           res_line[line.budget_post_id.code]['reserved_balance']+=line.reserved_balance
                           res_line[line.budget_post_id.code]['devengado_balance']+=line.devengado_balance
                           res_line[line.budget_post_id.code]['avai_amount']+=line.avai_amount
                        self.crear_padre_excel(res_line[line.code], res_line[line.code],res_line)
                     else:
                        res_line[line.code]['planned_amount']+=line.planned_amount
                        res_line[line.code]['reform_amount']+=line.reform_amount
                        res_line[line.code]['codif_amount']+=line.codif_amount
                        res_line[line.code]['commited_amount']+=line.commited_amount
                        res_line[line.code]['reserved_amount']+=line.reserved_amount
                        res_line[line.code]['devengado_amount']+=line.devengado_amount
                        res_line[line.code]['paid_amount']+=line.paid_amount
                        res_line[line.code]['commited_balance']+=line.commited_balance
                        res_line[line.code]['reserved_balance']+=line.reserved_balance
                        res_line[line.code]['devengado_balance']+=line.devengado_balance
                        res_line[line.code]['avai_amount']+=line.avai_amount
                  res_line['total']={'reform_amount': 0.00,
                                     'devengado_amount': 0.00,
                                     'paid_amount': 0.00,
                                     'commited_amount': 0.00,
                                     'reserved_amount': 0.00,
                                     'recaudado_amount': 0.00,
                                     'planned_amount': 0.00,
                                     'devengado_balance': 0.00,
                                     'commited_balance': 0.00,
                                     'reserved_balance': 0.00,
                                     'codif_amount': 0.00,
                                     'level':0,
                                     'general_budget_name':0,
                                     'code':0,
                                     'avai_amount':0,
                                     'code_ex':0,
                                     'code_aux':0,
                              }
                  values=res_line.itervalues()
                  for line_totales in values:
                     if (line_totales['devengado_amount'] - line_totales['commited_amount'])>=0.01:
                        print line_totales['code'], " mas devengado que comprometido"
                     if (line_totales['paid_amount'] - line_totales['devengado_amount'])>=0.01:
                        print line_totales['code'], " mas pagado que devengado"
                     if not 'level' in line_totales and line_totales['final']==True:
                        res_line['total']['planned_amount']+=line_totales['planned_amount']            
                        res_line['total']['reform_amount']+=line_totales['reform_amount']
                        res_line['total']['codif_amount']+=line_totales['codif_amount']
                        res_line['total']['commited_amount']+=line_totales['commited_amount']
                        res_line['total']['reserved_amount']+=line_totales['reserved_amount']
                        res_line['total']['devengado_amount']+=line_totales['devengado_amount']
                        res_line['total']['paid_amount']+=line_totales['paid_amount']
                        res_line['total']['devengado_balance']+=line_totales['devengado_balance']
                        res_line['total']['commited_balance']+=line_totales['commited_balance']
                        res_line['total']['reserved_balance']+=line_totales['reserved_balance']
                        res_line['total']['avai_amount']+=line_totales['avai_amount']
                  writer_excel = XLSWriter.XLSWriter()
                  cabecera_titulo = ["CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to]
                  writer_excel.append(cabecera_titulo)
                  cabecera_all = ['Codigo Partida','Denominacion','Asignacion Inicial','Reforma','Codificado','Certificado','Comprometido','Devengado','Pagado','Saldo por certificar','Saldo por comprometer','Saldo por devengar','Saldo por  pagar']
                  writer_excel.append(cabecera_all)
                  result_dict = res_line.values()
                  dic_ord = sorted(result_dict, key=operator.itemgetter('code_aux'))
                  j = 0
                  for line in dic_ord:
                     if j==1:
                          line_total = line
                          aux_pagar_total = line['commited_amount'] - line['paid_amount']
                          j = 2
                     j+=1
                     aux_por_pagar = line['commited_amount'] - line['paid_amount']
                     #considerar los niveles
                     if str(line['code_ex'])[0]!='0':
                        if this.nivel:
                           if this.tipo_nivel:
                              if this.tipo_nivel=='p':
                                 if line['level']<=this.nivel:
                                    writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['reserved_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['reserved_balance'],line['commited_balance'],line['devengado_balance'],aux_por_pagar])
                              elif this.tipo_nivel=='h':
                                 if line['level']>=this.nivel:
                                    writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['reserved_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['reserved_balance'],line['commited_balance'],line['devengado_balance'],aux_por_pagar])
                           else:
                              if line['level']==this.nivel:
                                 writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['reserved_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['reserved_balance'],line['commited_balance'],line['devengado_balance'],aux_por_pagar])
                        else:
                           writer_excel.append([line['code_ex'],line['general_budget_name'],line['planned_amount'],line['reform_amount'],line['codif_amount'],line['reserved_amount'],line['commited_amount'],line['devengado_amount'],line['paid_amount'],line['reserved_balance'],line['commited_balance'],line['devengado_balance'],aux_por_pagar])
                  writer_excel.append(['','TOTALES',line_total['planned_amount'],line_total['reform_amount'],line_total['codif_amount'],line_total['reserved_amount'],line_total['commited_amount'],line_total['devengado_amount'],line_total['paid_amount'],line_total['reserved_balance'],line_total['commited_balance'],line_total['devengado_balance'],aux_pagar_total])
                  writer_excel.save("CEDULA " + aux_tipo + " del "  + date_from + ' al ' + date_to + '.xls')
                  out1 = open("CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to + '.xls',"rb").read().encode("base64")
                  filename = "CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to + '.txt' 
                  self.write(cr, uid, ids, {
                     'datas':out1,
                     'datas_fname':"CEDULA " + aux_tipo + " del " + date_from + ' al ' + date_to + '.xls',
                  })
        return True

   def gen_esigef_pdf(self, cr, uid, ids, context):
      if not context:
         context = {}
      solicitud = self.browse(cr, uid, ids, context)[0]
      datas = {'ids': [solicitud.id], 'model': 'report.budget.card'}
      return {
         'type': 'ir.actions.report.xml',
         'report_name': 'esigef4',
         'model': 'report.budget.card',
         'datas': datas,
         'nodestroy': True,                        
      }

   def gen_esigef_file(self, cr, uid, ids, context):
      user_obj = self.pool.get('res.users')
      if context is None:
         context = {}     
      if 'report_name' in context:               
         report_name = context['report_name']
         #aqui debe mandar el reporte correcto siempre manda el mismo
         print context['report_name']
      data = self.read(cr, uid, ids, [], context=context)[0]
      mensajes = ""
      data['budget_id'] = context['active_id']
      data['type_report'] = 'gasto'
      certificate = self.browse(cr, uid, ids, context)[0]
      data['date_from'] = certificate.date_from
      data['date_to'] = certificate.date_to
      datas = {'ids': [certificate.id], 'model': 'report.budget.card',
               'form': data, 'type_report': 'gasto',
               'budget_id': context.get('active_id'),
               'project': False}
      budget_items_obj = self.pool.get('budget.item')
      datas = self.read(cr, uid, ids, [], context=context)[0]
      date_from = datas['date_from']
      date_to = datas['date_to']
      resumen_id = context['active_id']
      
      lineas_ing = self._get_totales_ing(cr, uid, ids, context)
      result_dic = lineas_ing.values()
      dic_ord=sorted(result_dic, key=operator.itemgetter('code'))
      datas_ing = []
      total_reform = 0
      mes = str(datetime.datetime.strptime(date_to, '%Y-%m-%d').month)
      writer_excel = XLSWriter.XLSWriter()
      usuario = user_obj.browse(cr, uid, uid)
      cabecera_empresa = [usuario.company_id.name]
      writer_excel.append(cabecera_empresa)
      cabecera_titulo = ["CEDULA INGRESOS-GASTOS del " + date_from + ' al ' + date_to]
      writer_excel.append(cabecera_titulo)
      cabecera_all = ['Codigo Partida','Asignacion Inicial','Reforma','Codificado','Comprometido','Devengado','Pagado']
      writer_excel.append(cabecera_all)
      for line in dic_ord:
         if line['final']:
            total_reform += line['reform_amount']
            if line['planned_amount']!=0 or line['reform_amount'] != 0 or line['codif_amount']!=0 or line['devengado_amount']!=0 or line['paid_amount']!=0 or line['devengado_balance']!=0:
               if (line['paid_amount'] - line['devengado_amount'])>=0.01:
                  mensajes+="El valor de recaudado no puede ser mayor al valor de devengado en la partida %s, la diferencia es %s\n"%(line['code'],line['paid_amount']-line['devengado_amount'])
               datas_ing.append([mes,'I',line['code'][0:2],line['code'][2:4],line['code'][4:6],'%.2f'%line['planned_amount'],'%.2f'%line['reform_amount'],'%.2f'%line['codif_amount'],'%.2f'%line['devengado_amount'],'%.2f'%line['paid_amount'],'%.2f'%line['devengado_balance']])
               aux_excel = [line['code'][0:6],'%.2f'%line['planned_amount'],'%.2f'%line['reform_amount'],'%.2f'%line['codif_amount'],'%.2f'%line['commited_amount'],'%.2f'%line['devengado_amount'],'%.2f'%line['paid_amount']]
               writer_excel.append(aux_excel)
#      if total_reform != 0:
#         raise osv.except_osv('Error', "El total de la columna REFORMAS INGRESOS debe ser igual a cero")
      budget_buf = StringIO.StringIO() 
      writer = csv.writer(budget_buf, delimiter='|')
      writer.writerows(datas_ing)
      lineas_gas = self._get_totales_gas(cr, uid, ids, context)
      result_dic = lineas_gas.values()
      dic_ord=sorted(result_dic, key=operator.itemgetter('code'))
      datas_gas = []
      mes = str(datetime.datetime.strptime(date_to, '%Y-%m-%d').month)
      for line in dic_ord:
         if line['final']:
            total_reform += line['reform_amount']
            if line['planned_amount']!=0 or line['reform_amount'] !=0 or line['codif_amount']!=0 or line['commited_amount']!=0 or line['devengado_amount']!=0 or line['paid_amount']!=0 or line['commited_balance']!=0 or line['devengado_balance']:
               if (line['paid_amount'] - line['devengado_amount'])>=0.01:
                  mensajes+="El valor de pagado no puede ser mayor al valor de devengado en la partida %s, la diferencia es %s\n"%(line['code'],line['paid_amount']-line['devengado_amount'])
               if (line['devengado_amount'] - line['commited_amount'])>=0.01:
                  mensajes+="El valor de devengado no puede ser mayor al valor de comprometido en la partida %s, la diferencia es %s\n"%(line['code'], line['devengado_amount']-line['commited_amount'])
               if line['devengado_balance'] < 0:
                  mensajes+="La partida %s se encuentra sobregirada el total de sobregiro es %s\n"%(line['code'], line['devengado_balance'])
               datas_gas.append([mes,'G',line['code'][0:2],line['code'][2:4],line['code'][4:6],'000','%.2f'%line['planned_amount'],'%.2f'%line['reform_amount'],'%.2f'%line['codif_amount'],'%.2f'%line['commited_amount'],'%.2f'%line['devengado_amount'],'%.2f'%line['paid_amount'],'%.2f'%line['commited_balance'],'%.2f'%line['devengado_balance']])
               aux_excel = [line['code'][0:6],'%.2f'%line['planned_amount'],'%.2f'%line['reform_amount'],'%.2f'%line['codif_amount'],'%.2f'%line['commited_amount'],'%.2f'%line['devengado_amount'],'%.2f'%line['paid_amount']]
               writer_excel.append(aux_excel)
      writer.writerows(datas_gas)
      out = base64.encodestring(budget_buf.getvalue())
      budget_buf.close()
      writer_excel.save("CEDULA INGRESOS-GASTOS del " + date_from + ' al ' + date_to + '.xls')
      out1 = open("CEDULA INGRESOS-GASTOS del " + date_from + ' al ' + date_to + '.xls',"rb").read().encode("base64")
      filename = "ESIGEF CEDULAS INGRESOS-GASTOS del " + date_from + ' al ' + date_to + '.txt' 
      self.write(cr, uid, ids, {'data': out, 
                                'filename': filename, 
                                'mensajes': mensajes,
                                'datas':out1,
                                'datas_fname':"CEDULA INGRESOS-GASTOS del " + date_from + ' al ' + date_to + '.xls',
                             })
#      if total_reform != 0:
#         raise osv.except_osv('Error', "El total de la columna REFORMAS GASTO debe ser igual a cero")
      return True

   def crear_padre_ing(self, data, data_suma, res):
      if data['post'].parent_id:
         data['padre'] = data['post'].parent_id
         if res.get(data['post'].parent_id.code,False):
            res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
            res[data['post'].parent_id.code]['devengado_amount'] += data_suma['devengado_amount']
            res[data['post'].parent_id.code]['devengado_balance'] += data_suma['devengado_balance']
            res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
            res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
            res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
         else:
            res[data['post'].parent_id.code] = {
               'post': data['post'].parent_id,
               'padre': False, 
               'code':data['post'].parent_id.code,
               'general_budget_name':data['post'].parent_id.name,
               'planned_amount':data['planned_amount'],
               'devengado_amount':data['devengado_amount'],
               'devengado_balance':data['devengado_balance'],
               'paid_amount':data['paid_amount'], #pagado - recaudado
               'codif_amount':data['codif_amount'],
               'reform_amount':data['reform_amount'],
               'final': False,
            }
         self.crear_padre_ing(res[data['post'].parent_id.code], data_suma,res)
            
   def _get_totales_ing(self, cr, uid, ids,context):
      res = { }
      res_line = { }
      result = []
      datas = self.read(cr, uid, ids, [], context=context)[0]
      date_from = datas['date_from']
      date_to = datas['date_to']
      c_b_lines_obj = self.pool.get('budget.item')
      resumen_id = context['active_id']
      ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',resumen_id),('type_budget','=','ingreso')])
      context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen_id}            
      planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
      #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
      for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
         if res_line.has_key(line.code)==False:
            res_line[line.code]={
               'post': line.budget_post_id,
               'padre': False, 
               'code':line.code,
               'general_budget_name':line.budget_post_id.name,
               'planned_amount':line.planned_amount,
               'devengado_amount':line.devengado_amount,
               'devengado_balance':line.devengado_balance,
               'paid_amount':line.paid_amount,     
               'codif_amount':line.codif_amount,
               'reform_amount':line.reform_amount,
               'commited_amount':line.commited_amount,
               'final': True,
            }
            self.crear_padre_ing(res_line[line.code], res_line[line.code],res_line)
         else:                                
            res_line[line.budget_post_id.id]['planned_amount']+=line.planned_amount
            res_line[line.budget_post_id.id]['devengado_amount']+=line.devengado_amount
            res_line[line.budget_post_id.id]['devengado_balance']+=line.devengado_balance
            res_line[line.budget_post_id.id]['commited_amount']+=line.commited_amount
            res_line[line.budget_post_id.id]['paid_amount']+=line.paid_amount
            res_line[line.budget_post_id.id]['codif_amount']+=line.codif_amount
            res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount
      return res_line

   def crear_padre_gas(self, data, data_suma, res):
      if data['post'].parent_id:
         data['padre'] = data['post'].parent_id
         if res.get(data['post'].parent_id.code,False):
            res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
            res[data['post'].parent_id.code]['devengado_amount'] += data_suma['devengado_amount']
            res[data['post'].parent_id.code]['devengado_balance'] += data_suma['devengado_balance']
            res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
            res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
            res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
            res[data['post'].parent_id.code]['commited_amount'] += data_suma['commited_amount']
            res[data['post'].parent_id.code]['commited_balance'] += data_suma['commited_balance']
         else:
            res[data['post'].parent_id.code] = {
               'post': data['post'].parent_id,
               'padre': False, 
               'code':data['post'].parent_id.code,
               'general_budget_name':data['post'].parent_id.name,
               'planned_amount':data['planned_amount'],
               'devengado_amount':data['devengado_amount'],
               'devengado_balance':data['devengado_balance'],
               'paid_amount':data['paid_amount'],     
               'codif_amount':data['codif_amount'],
               'reform_amount':data['reform_amount'],
               'commited_amount':data['commited_amount'],
               'commited_balance':data['commited_balance'],
               'final': False,
            }
         self.crear_padre_gas(res[data['post'].parent_id.code], data_suma,res)


   def _get_totales_gas(self, cr, uid, ids,context):
      res = { }
      res_line = { }
      result = []
      datas = self.read(cr, uid, ids, [], context=context)[0]
      date_from = datas['date_from']
      date_to = datas['date_to']
      c_b_lines_obj = self.pool.get('budget.item')
      resumen_id = context['active_id']
      ids_lines=c_b_lines_obj.search(cr,uid,[('poa_id','=',resumen_id),('type_budget','=','gasto')])
      context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen_id}            
      planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
      #        totales = c_b_lines_obj._compute_budget_all(cr, uid, ids_lines,[],[], context)
      for line in c_b_lines_obj.browse(cr,uid,ids_lines, context=context):
         if res_line.has_key(line.code)==False:
            res_line[line.code]={
               'post': line.budget_post_id,
               'program': line.program_id.id,
               'padre': False, 
               'code':line.code,
               'general_budget_name':line.budget_post_id.name,
               'planned_amount':line.planned_amount,
               'commited_amount':line.commited_amount,
               'devengado_amount':line.devengado_amount,
               'paid_amount':line.paid_amount,
               'devengado_balance':line.devengado_balance,
               'commited_balance':line.commited_balance,
               'codif_amount':line.codif_amount,
               'reform_amount':line.reform_amount,
               'final': False,
            }
            if res_line.has_key(line.budget_post_id.code)==False:
               res_line[line.budget_post_id.code]={
                  'post': line.budget_post_id,
                  'program': line.program_id.id,
                  'padre': False, 
                  'code': line.budget_post_id.code,
                  'general_budget_name':line.budget_post_id.name,
                  'planned_amount':line.planned_amount,
                  'commited_amount':line.commited_amount,
                  'devengado_amount':line.devengado_amount,
                  'paid_amount':line.paid_amount,
                  'devengado_balance':line.devengado_balance,
                  'commited_balance':line.commited_balance,
                  'codif_amount':line.codif_amount,
                  'reform_amount':line.reform_amount,
                  'final': True,
               }
            else:
               res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
               res_line[line.budget_post_id.code]['reform_amount']+=line.reform_amount
               res_line[line.budget_post_id.code]['codif_amount']+=line.codif_amount
               res_line[line.budget_post_id.code]['commited_amount']+=line.commited_amount
               res_line[line.budget_post_id.code]['devengado_amount']+=line.devengado_amount
               res_line[line.budget_post_id.code]['paid_amount']+=line.paid_amount
               res_line[line.budget_post_id.code]['commited_balance']+=line.commited_balance
               res_line[line.budget_post_id.code]['devengado_balance']+=line.devengado_balance
            self.crear_padre_gas(res_line[line.code], res_line[line.code],res_line)
         else:              
            res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
            res_line[line.budget_post_id.id+line.program_id.id]['reform_amount']+=line.reform_amount
            res_line[line.budget_post_id.id+line.program_id.id]['codif_amount']+=line.codif_amount
            res_line[line.budget_post_id.id+line.program_id.id]['commited_amount']+=line.commited_amount
            res_line[line.budget_post_id.id+line.program_id.id]['devengado_amount']+=line.devengado_amount
            res_line[line.budget_post_id.id+line.program_id.id]['paid_amount']+=line.paid_amount
            res_line[line.budget_post_id.id+line.program_id.id]['commited_balance']+=line.commited_balance
            res_line[line.budget_post_id.id+line.program_id.id]['devengado_balance']+=line.devengado_balance
      return res_line

   
   def print_report(self, cr, uid, ids, context):
        if context is None:
            context = {}     
        poa_obj = self.pool.get('budget.poa')
        certificate = self.browse(cr, uid, ids, context)[0]
        if 'report_name' in context:               
            report_name = context['report_name']
            #aqui debe mandar el reporte correcto siempre manda el mismo
            print context['report_name']
        data = self.read(cr, uid, ids, [], context=context)[0]
        band_asig_inicial = data['asig_inicial']
        if band_asig_inicial:
           report_name = report_name + 'R'
        if context.has_key('active_id'):
           data['budget_id'] = context['active_id']
        else:
           poa_ids = poa_obj.search(cr, uid, [('date_start','<=',certificate.date_from),('date_end','>=',certificate.date_to)])
           data['budget_id'] = poa_ids[0]
        data['type_report'] = 'gasto'
        data['date_from'] = certificate.date_from
        data['date_to'] = certificate.date_to
        data['sobregiro'] = False
        datas = {'ids': [certificate.id], 'model': 'report.budget.card',
                 'form': data, 'type_report': 'gasto',
                 'budget_id': context.get('active_id'),
                 'project': False}
        if certificate.project:
            datas.update({'project_id': certificate.project_id.id,
                          'project': True,
                          'project_name': '%s %s'% (certificate.project_id.code, certificate.project_id.name)})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'model': 'report.budget.card',
            'datas': datas,
            'nodestroy': True,                              
            }

   def print_report_sobregiradas(self, cr, uid, ids, context):
        print "llamada al reporte"
        if context is None:
            context = {}     
        if 'report_name' in context:               
            report_name = context['report_name']
            #aqui debe mandar el reporte correcto siempre manda el mismo
            print context['report_name']
        data = self.read(cr, uid, ids, [], context=context)[0]
        data['budget_id'] = context['active_id']
        data['type_report'] = 'gasto'
        certificate = self.browse(cr, uid, ids, context)[0]
        data['date_from'] = certificate.date_from
        data['date_to'] = certificate.date_to
        data['sobregiro'] = True
        datas = {'ids': [certificate.id], 'model': 'report.budget.card',
                 'form': data, 'type_report': 'gasto',
                 'budget_id': context.get('active_id'),
                 'project': False}
        if certificate.project:
            datas.update({'project_id': certificate.project_id.id,
                          'project': True,
                          'project_name': '%s %s'% (certificate.project_id.code, certificate.project_id.name)})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'model': 'report.budget.card',
            'datas': datas,
            'nodestroy': True,                              
            }

     
   
   _defaults = dict(       
        project = False,
        fiscalyear= _get_fiscalyear,
        tipo = _get_tipo
        )

reportBudgetCard()


class reportReformWizard(osv.Model):
   _name = 'report.reform.wizard'
   _description = "Reporte de reforma"

   def onchange_container(self, cr, uid, ids, container=False, context=None):
        res = {}
        if container:
           date = self.read(cr, uid, ids, ['date'])
        return res     
   
   _columns = dict(
        fiscalyear = fields.many2one('account.fiscalyear', 'Fiscal year', ),
        massive_in = fields.many2one('mass.reform.ingreso', 'Reforma Masiva de ingreso', ),
        massive_out = fields.many2one('mass.reform', 'Reforma Masiva de gastos', ),
        poa = fields.many2one('budget.poa', 'POA', ),
        nivel = fields.integer('Nivel'),
        )

   def _get_massive_in(self, cr, uid, context):
      if context.get('active_model',False) and context['active_model'] == 'mass.reform.ingreso':
         if 'active_ids' in context:
            return context['active_ids'][0]

   def _get_massive_out(self, cr, uid, context):
      if context.get('active_model',False) and context['active_model'] == 'mass.reform':
         if 'active_ids' in context:
            return context['active_ids'][0]
   
   def print_report(self, cr, uid, ids, context):
        print "llamada al reporte"
        if context is None:
            context = {}     
        if 'report_name' in context:               
            report_name = context['report_name']
            #aqui debe mandar el reporte correcto siempre manda el mismo
            print context['report_name']
        data = self.read(cr, uid, ids, [], context=context)[0]
        data['budget_id'] = context['active_id']
        data['type_report'] = 'gasto'
        certificate = self.browse(cr, uid, ids, context)[0]
        data['date_from'] = certificate.date_from
        data['date_to'] = certificate.date_to
        data['sobregiro'] = False
        datas = {'ids': [certificate.id], 'model': 'report.budget.card',
                 'form': data, 'type_report': 'gasto',
                 'budget_id': context.get('active_id'),
                 'project': False}
        if certificate.project:
            datas.update({'project_id': certificate.project_id.id,
                          'project': True,
                          'project_name': '%s %s'% (certificate.project_id.code, certificate.project_id.name)})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'model': 'report.budget.card',
            'datas': datas,
            'nodestroy': True,                              
            }     
   
   _defaults = dict(
        massive_in = _get_massive_in,
        massive_out = _get_massive_out,
        )

reportReformWizard()

