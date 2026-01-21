# -*- coding: utf-8 -*-
##############################################################################
#    
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################


from report import report_sxw
from osv import osv
import operator
import time
import datetime
from datetime import date, timedelta
from tools import ustr
import operator

## proforma presupuestaria gastos

class proformaPresupuestariaGasto(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(proformaPresupuestariaGasto, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_get_totales':self._get_totales,
            '_vars': self._vars,
            '_get_total_funcion':self._get_total_funcion,
        })

    def _get_total_presupuesto(self,poa,programa):
        aux = False
        if programa.sequence[0]=='1':
            aux = poa.total_presupuesto
        return aux

    def _get_total_funcion(self,programa,poa):
        line_obj = self.pool.get('budget.poa.funcion')
        line_ids = line_obj.search(self.cr,self.uid,[('funcion','=',programa.sequence[0]),('p_id','=',poa.id)])
        aux = 0
        if line_ids:
            line = line_obj.browse(self.cr, self.uid, line_ids[0])
            aux = line.total
        return aux

    def _vars(self,resumen):  
        res = { }          
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date_from'] = resumen.poa_id.date_start
        res['date_to'] = resumen.poa_id.date_end
        return res 

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = resumen.poa_id.date_start
        date_to = resumen.poa_id.date_end
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('program_id','=',resumen.program_id.id),('poa_id','=',resumen.poa_id.id),('type_budget','=','gasto')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + '.' + line.program_id.sequence
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                   # 'code':line.code,
                    'code':code_aux,#line.code_report,#line.code
                    'code_aux':code_aux,#line.code_report,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                if res_line.has_key(line.budget_post_id.code)==False:
                    code_aux = line.budget_post_id.code + '.' +line.program_id.sequence
                    res_line[line.budget_post_id.code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': False, 
                        'code': line.budget_post_id.code,
                        'code_aux':line.budget_post_id.code,
                        'general_budget_name':line.budget_post_id.name,
                        'planned_amount':line.planned_amount,
                        'final': True,
                        'nivel': line.budget_post_id.nivel-1,
                        'level': line.budget_post_id.nivel-1,
                    }
 #               else:
 #                   res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                res_line[line.code]['planned_amount']+=line.planned_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
        res_line['total']={'planned_amount': 0.00,
                           'level':0,
                           'nivel':0,
                           'code':0,
                           'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']        
        return res_line

report_sxw.report_sxw('report.proforma_presupuestaria_gasto','proforma.presupuestaria.gasto',
                      'gt_project_project/report/report_proforma_gasto.mako',
                      parser=proformaPresupuestariaGasto)

## proforma presupuestaria ingreso

class proformaPresupuestariaIngreso(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(proformaPresupuestariaIngreso, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_get_totales':self._get_totales,
            '_vars': self._vars,
        })

    def _vars(self,resumen):  
        res = { }          
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date_from'] = resumen.poa_id.date_start
        res['date_to'] = resumen.poa_id.date_end
        return res 

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = resumen.poa_id.date_start
        date_to = resumen.poa_id.date_end
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.poa_id.id),('type_budget','=','ingreso')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + '.' + line.program_id.sequence
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                   # 'code':line.code,
                    'code':code_aux,#line.code_report,#line.code
                    'code_aux':code_aux,#line.code_report,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                if res_line.has_key(line.budget_post_id.code)==False:
                    code_aux = line.budget_post_id.code + '.' +line.program_id.sequence
                    res_line[line.budget_post_id.code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': False, 
                        'code': line.budget_post_id.code,
                        'code_aux':line.budget_post_id.code,
                        'general_budget_name':line.budget_post_id.name,
                        'planned_amount':line.planned_amount,
                        'final': True,
                        'nivel': line.budget_post_id.nivel-1,
                        'level': line.budget_post_id.nivel-1,
                    }
 #               else:
 #                   res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
        res_line['total']={'planned_amount': 0.00,
                           'level':0,
                           'nivel':0,
                           'code':0,
                           'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']        
        return res_line

report_sxw.report_sxw('report.proforma_presupuestaria_ingreso','proforma.presupuestaria.ingreso',
                      'gt_project_project/report/report_proforma_ingreso.mako',
                      parser=proformaPresupuestariaIngreso)


## proforma presupuestaria gastos resumen

class proformaPresupuestariaGastoResumen(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(proformaPresupuestariaGastoResumen, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_get_totales':self._get_totales,
            '_vars': self._vars,
            '_get_total_funcion':self._get_total_funcion,
        })

    def _get_total_presupuesto(self,poa,programa):
        aux = False
        if programa.sequence[0]=='1':
            aux = poa.total_presupuesto
        return aux

    def _get_total_funcion(self,programa,poa):
        line_obj = self.pool.get('budget.poa.funcion')
        line_ids = line_obj.search(self.cr,self.uid,[('funcion','=',programa.sequence[0]),('p_id','=',poa.id)])
        aux = 0
        if line_ids:
            line = line_obj.browse(self.cr, self.uid, line_ids[0])
            aux = line.total
        return aux

    def _vars(self,resumen):  
        res = { }          
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date_from'] = resumen.poa_id.date_start
        res['date_to'] = resumen.poa_id.date_end
        return res 

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = resumen.poa_id.date_start
        date_to = resumen.poa_id.date_end
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('program_id','=',resumen.program_id.id),('poa_id','=',resumen.poa_id.id),('type_budget','=','gasto')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + '.' + line.program_id.sequence
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                   # 'code':line.code,
                    'code':code_aux,#line.code_report,#line.code
                    'code_aux':code_aux,#line.code_report,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                if res_line.has_key(line.budget_post_id.code)==False:
                    code_aux = line.budget_post_id.code + '.' +line.program_id.sequence
                    res_line[line.budget_post_id.code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': False, 
                        'code': line.budget_post_id.code,
                        'code_aux':line.budget_post_id.code,
                        'general_budget_name':line.budget_post_id.name,
                        'planned_amount':line.planned_amount,
                        'final': True,
                        'nivel': line.budget_post_id.nivel-1,
                        'level': line.budget_post_id.nivel-1,
                    }
 #               else:
 #                   res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                res_line[line.code]['planned_amount']+=line.planned_amount
        res_line['total']={'planned_amount': 0.00,
                           'level':0,
                           'nivel':0,
                           'code':0,
                           'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']        
        return res_line

report_sxw.report_sxw('report.proforma_presupuestaria_gasto_resumen','proforma.presupuestaria.gasto.resumen',
                      'gt_project_project/report/report_proforma_gasto_resumen.mako',
                      parser=proformaPresupuestariaGastoResumen)

## proforma presupuestaria ingreso resumen

class proformaPresupuestariaIngresoResumen(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(proformaPresupuestariaIngresoResumen, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_get_totales':self._get_totales,
            '_vars': self._vars,
        })

    def _vars(self,resumen):  
        res = { }          
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date_from'] = resumen.poa_id.date_start
        res['date_to'] = resumen.poa_id.date_end
        return res 

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = resumen.poa_id.date_start
        date_to = resumen.poa_id.date_end
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.poa_id.id),('type_budget','=','ingreso')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + '.' + line.program_id.sequence
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                   # 'code':line.code,
                    'code':code_aux,#line.code_report,#line.code
                    'code_aux':code_aux,#line.code_report,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                if res_line.has_key(line.budget_post_id.code)==False:
                    code_aux = line.budget_post_id.code + '.' +line.program_id.sequence
                    res_line[line.budget_post_id.code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': False, 
                        'code': line.budget_post_id.code,
                        'code_aux':line.budget_post_id.code,
                        'general_budget_name':line.budget_post_id.name,
                        'planned_amount':line.planned_amount,
                        'final': True,
                        'nivel': line.budget_post_id.nivel-1,
                        'level': line.budget_post_id.nivel-1,
                    }
 #               else:
 #                   res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
        res_line['total']={'planned_amount': 0.00,
                           'level':0,
                           'nivel':0,
                           'code':0,
                           'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']        
        return res_line

report_sxw.report_sxw('report.proforma_presupuestaria_ingreso_resumen','proforma.presupuestaria.ingreso.resumen',
                      'gt_project_project/report/report_proforma_ingreso_resumen.mako',
                      parser=proformaPresupuestariaIngresoResumen)


##nivel 4 esigef
class esigef4Expense(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(esigef4Expense, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
#            '_months':self._months,
            '_get_totales':self._get_totales,
            '_vars': self._vars,
            '_get_programs': self._get_programs,
            'get_cargo': self.get_cargo,
        })

    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        aux = 'ALCALDE'
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux        

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_to'] = self.datas['form']['date_to']
        res['nivel'] = self.datas['form']['nivel']
        res['tipo_nivel'] = self.datas['form']['tipo_nivel']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['sobregiro'] = self.datas['form']['sobregiro']
        res['end']=end.upper()
        return res 
        
    def set_context(self, objects, data, ids, report_type=None):
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['budget_id']),
                                                         ('type_budget','=','gasto')])
        if ids_lines:
            objects=self.pool.get('budget.poa').browse(self.cr,self.uid,data['form']['budget_id'])         
            return super(esigef4Expense, self).set_context([objects], data, ids, report_type=report_type)
        else:
            raise osv.except_osv('Error!!', 'No existen partidas tipo egreso del presupuesto')
        
    def _months(self,resumen):  
        res = { }                       
        user=str(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                        
        begin = self.datas['form']['period_from'][1]
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        if len(begin)>7:
            res['begin']=begin.upper()
        else:
            res['begin']=datetime.datetime.strptime(str(self.datas['form']['period_from'][1]), "%m/%Y").strftime("%B").upper()
        end = self.datas['form']['period_to'][1]
        if len(end)>7:
            res['end']=end.upper()
        else:
            res['end']=datetime.datetime.strptime(str(self.datas['form']['period_to'][1]), "%m/%Y").strftime("%B").upper()   
        project=self.datas['form']['project_id'][1]
        proyecto=self.pool.get('project.project').browse(self.cr,self.uid,[self.datas['form']['project_id'][0]])[0]              
        res['project']=project.upper()
        res['program']=proyecto.program_id.name
        return res 

    def crear_padre(self, data, data_suma, res):
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
                    'code_aux':data['post'].parent_id.code,
                    'code_report':data['post'].parent_id.code,
#                    'program':data['post'].parent_id.code,
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
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)

    def _get_programs(self,resumen):
        res = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        c_b_lines_obj = self.pool.get('budget.item')
        program_obj = self.pool.get('project.program')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','ingreso')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to}
        project = self.datas['form']['project']
        if project:
            program_ids = self.datas['form']['program_ids']
            if program_ids:
                programas = self.datas['form']['program_ids']
                if len(programas)==1:
                    programas.append(programas[0])
                sql_programs = "select id,name,sequence from project_program where id in %s order by sequence"%(str(tuple(programas)))
            else:
                ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','ingreso')])
                sql_programs = "select id,name,sequence from project_program where id in (select program_id from budget_item where id in %s group by program_id) order by sequence"%(str(tuple(ids_lines)))
            self.cr.execute(sql_programs)
            programas = self.cr.fetchall()
            for program in programas:
                res.append({'id': program[0], 'name': program[1], 'sequence': program[2]})
            return res
        else:
            return [{'id': False, 'name': '', 'sequence': ''}]

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

    def _get_totales(self, resumen, program=False):
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
      lineas_gas = self._get_totales_gas(cr, uid, ids, context)
      result_dic = lineas_gas.values()
      dic_ord=sorted(result_dic, key=operator.itemgetter('code'))
      datas_gas = []
      mes = str(datetime.datetime.strptime(date_to, '%Y-%m-%d').month)
      for line in dic_ord:
          print "vele"
      return dic_ord

report_sxw.report_sxw('report.esigef4','budget.poa',
                      'gt_budget/report/esigef4.mako',
                      parser=esigef4Expense)

##

class ReportCertificate(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportCertificate, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_manager': self._get_manager,
            'get_cargo': self.get_cargo,
        })

    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        aux = 'ALCALDE'
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux

    def _get_manager(self, manager_id):
        employee_name = self.pool.get('hr.employee').name_get(self.cr, self.uid, [manager_id])
        return employee_name[0][1]

report_sxw.report_sxw('report.crossovered.request','budget.certificate',
                      'addons/gt_budget/report/report_certificate.mako',
                      parser=ReportCertificate)


class ReportCompromise(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportCompromise, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.CompromisoPresupuestario.pdf','budget.certificate',
                      'addons/gt_budget/report/report_compromise.mako',
                      parser=ReportCompromise)


class BudgetCard(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(BudgetCard, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_months':self._months,
            '_get_totales':self._get_totales,
            '_vars': self._vars,
            '_get_extra_data': self._get_extra_data,
            'get_cargo': self.get_cargo,
            'get_firmas':self.get_firmas,
        })

    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux
    

    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        aux = 'ALCALDE'
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_to'] = self.datas['form']['date_to']
        res['tipo_nivel'] = self.datas['form']['tipo_nivel']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['sobregiro'] = self.datas['form']['sobregiro']
        res['end']=end.upper()
        res['nivel'] = self.datas['form']['nivel']
        return res 
        
    def set_context(self, objects, data, ids, report_type=None):
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['budget_id']),
                                                         ('type_budget','=','gasto')])
        if ids_lines:
            objects=self.pool.get('budget.poa').browse(self.cr,self.uid,data['form']['budget_id'])         
            return super(BudgetCard, self).set_context([objects], data, ids, report_type=report_type)
        else:
            raise osv.except_osv('Error!!', 'No existen partidas tipo egreso del presupuesto')
        
    def _months(self,resumen):  
        res = { }                       
        user=str(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                        
        begin = self.datas['form']['period_from'][1]
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        if len(begin)>7:
            res['begin']=begin.upper()
        else:
            res['begin']=datetime.datetime.strptime(str(self.datas['form']['period_from'][1]), "%m/%Y").strftime("%B").upper()
        end = self.datas['form']['period_to'][1]
        if len(end)>7:
            res['end']=end.upper()
        else:
            res['end']=datetime.datetime.strptime(str(self.datas['form']['period_to'][1]), "%m/%Y").strftime("%B").upper()   
        project=self.datas['form']['project_id'][1]
        proyecto=self.pool.get('project.project').browse(self.cr,self.uid,[self.datas['form']['project_id'][0]])[0]              
        res['project']=project.upper()
        res['program']=proyecto.program_id.name
        return res 

    def crear_padre(self, data, data_suma, res):
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
#                    'program':data['post'].parent_id.code,
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
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)

    def _get_extra_data(self,resumen):
        data = self._get_totales(resumen)
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
                nivel = date_to = self.datas['form']['nivel']
                if nivel!=0:
                    nivel = date_to = self.datas['form']['nivel']
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
        return result
                        
    def _get_totales(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
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
        return res_line


report_sxw.report_sxw('report.BudgetCard','budget.poa',
                      'gt_budget/report/report_budget_card.mako',
                      parser=BudgetCard)

class BudgetCardIncome(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(BudgetCardIncome, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            #            '_months':self._months,
            '_vars': self._vars,
            '_get_totales':self._get_totales,
            'get_cargo': self.get_cargo,
            'get_firmas':self.get_firmas,
        })

    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux

    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        aux = 'ALCALDE'
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux
        
    def set_context(self, objects, data, ids, report_type=None):
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['budget_id']),
                                                         ('type_budget','=','ingreso')])
        if ids_lines:
            objects=self.pool.get('budget.poa').browse(self.cr,self.uid,data['form']['budget_id'])         
            return super(BudgetCardIncome, self).set_context([objects], data, ids, report_type=report_type)
        else:
            raise osv.except_osv('Error!!', 'No existen partidas tipo ingreso del presupuesto')

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_to'] = self.datas['form']['date_to']
        res['nivel'] = self.datas['form']['nivel']
        res['tipo_nivel'] = self.datas['form']['tipo_nivel']
        res['sobregiro'] = self.datas['form']['sobregiro']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['end']=end.upper()
        return res 
        
    def _months(self,resumen):  
        res = { }          
        begin = self.datas['form']['period_from'][1]
        user=str(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        if len(begin)>7:
            res['begin']=begin.upper()
        else:
            res['begin']=datetime.datetime.strptime(str(self.datas['form']['period_from'][1]), "%m/%Y").strftime("%B").upper()
        end = self.datas['form']['period_to'][1]
        if len(end)>7:
            res['end']=end.upper()
        else:
            res['end']=datetime.datetime.strptime(str(self.datas['form']['period_to'][1]), "%m/%Y").strftime("%B").upper()   
        return res

    def crear_padre(self, data, data_suma, res):
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
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'devengado_amount':data['devengado_amount'],
                    'devengado_balance':data['devengado_balance'],
                    'paid_amount':data['paid_amount'], #pagado - recaudado
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','ingreso')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + '.' + line.program_id.sequence
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'program': line.program_id.id,
                    'padre': True,#False, 
                    'code':code_aux,
                    'code_aux':code_aux,#line.code
                    'code_report':line.code_report,
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
                if res_line.has_key(line.budget_post_id.code)==False:
                    code_aux = line.budget_post_id.code + '.' +line.program_id.sequence
                    res_line[line.budget_post_id.code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': False, 
                        'code': line.budget_post_id.code,
                        'code_aux':line.budget_post_id.code,
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
                        'nivel': line.budget_post_id.nivel-1,
                        'level': line.budget_post_id.nivel-1,
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

                #res_line[line.program_id.sequence+'.'+line.budget_post_id.code]['planned_amount']+=line.planned_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.sequence]['reform_amount']+=line.reform_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.sequence]['codif_amount']+=line.codif_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.id]['commited_amount']+=line.commited_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.id]['devengado_amount']+=line.devengado_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.id]['paid_amount']+=line.paid_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.id]['commited_balance']+=line.commited_balance
                #res_line[line.budget_post_id.code+'.'+line.program_id.id]['devengado_balance']+=line.devengado_balance
                
#                res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['reform_amount']+=line.reform_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['codif_amount']+=line.codif_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['commited_amount']+=line.commited_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['devengado_amount']+=line.devengado_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['paid_amount']+=line.paid_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['commited_balance']+=line.commited_balance
#                res_line[line.budget_post_id.id+line.program_id.id]['devengado_balance']+=line.devengado_balance

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
                           'nivel':0,
                           'code_aux':0,
                           'code_report':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['devengado_amount']+=line_totales['devengado_amount']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['commited_amount']+=line_totales['commited_amount']
                res_line['total']['devengado_balance']+=line_totales['devengado_balance']
        return res_line

report_sxw.report_sxw('report.BudgetCardIncome','budget.poa',
                      'gt_budget/report/report_budget_card_income.mako',
                      parser=BudgetCardIncome)

class BudgetCardExpense(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(BudgetCardExpense, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
#            '_months':self._months,
            '_get_totales':self._get_totales,
            '_vars': self._vars,
            '_get_programs': self._get_programs,
            'get_cargo': self.get_cargo,
            'get_firmas':self.get_firmas,
        })
        
    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux

    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        aux = 'ALCALDE'
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_to'] = self.datas['form']['date_to']
        res['nivel'] = self.datas['form']['nivel']
        res['tipo_nivel'] = self.datas['form']['tipo_nivel']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['sobregiro'] = self.datas['form']['sobregiro']
        res['end']=end.upper()
        return res 
        
    def set_context(self, objects, data, ids, report_type=None):
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['budget_id']),
                                                         ('type_budget','=','gasto')])
        if ids_lines:
            objects=self.pool.get('budget.poa').browse(self.cr,self.uid,data['form']['budget_id'])         
            return super(BudgetCardExpense, self).set_context([objects], data, ids, report_type=report_type)
        else:
            raise osv.except_osv('Error!!', 'No existen partidas tipo egreso del presupuesto')
        
    def _months(self,resumen):  
        res = { }                       
        user=str(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                        
        begin = self.datas['form']['period_from'][1]
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        if len(begin)>7:
            res['begin']=begin.upper()
        else:
            res['begin']=datetime.datetime.strptime(str(self.datas['form']['period_from'][1]), "%m/%Y").strftime("%B").upper()
        end = self.datas['form']['period_to'][1]
        if len(end)>7:
            res['end']=end.upper()
        else:
            res['end']=datetime.datetime.strptime(str(self.datas['form']['period_to'][1]), "%m/%Y").strftime("%B").upper()   
        project=self.datas['form']['project_id'][1]
        proyecto=self.pool.get('project.project').browse(self.cr,self.uid,[self.datas['form']['project_id'][0]])[0]              
        res['project']=project.upper()
        res['program']=proyecto.program_id.name
        return res 

    def crear_padre(self, data, data_suma, res):
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
                    'code_aux':data['post'].parent_id.code,
                    'code_report':data['post'].parent_id.code,
#                    'program':data['post'].parent_id.code,
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
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)

    def _get_programs(self,resumen):
        res = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        c_b_lines_obj = self.pool.get('budget.item')
        program_obj = self.pool.get('project.program')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','ingreso')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to}
        project = self.datas['form']['project']
        if project:
            program_ids = self.datas['form']['program_ids']
            if program_ids:
                programas = self.datas['form']['program_ids']
                if len(programas)==1:
                    programas.append(programas[0])
                sql_programs = "select id,name,sequence from project_program where id in %s order by sequence"%(str(tuple(programas)))
            else:
                ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','ingreso')])
                sql_programs = "select id,name,sequence from project_program where id in (select program_id from budget_item where id in %s group by program_id) order by sequence"%(str(tuple(ids_lines)))
            self.cr.execute(sql_programs)
            programas = self.cr.fetchall()
            for program in programas:
                res.append({'id': program[0], 'name': program[1], 'sequence': program[2]})
            return res
        else:
            return [{'id': False, 'name': '', 'sequence': ''}]
            
    def _get_totales(self, resumen, program=False):
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
                    'code_report':line.code_report,
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
                if res_line.has_key(line.budget_post_id.code)==False:
                    code_aux = line.budget_post_id.code + '.' +line.program_id.sequence
                    res_line[line.budget_post_id.code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': False, 
                        'code': line.budget_post_id.code,
                        'code_aux':line.budget_post_id.code,
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
                        'nivel': line.budget_post_id.nivel-1,
                        'level': line.budget_post_id.nivel-1,
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

                #res_line[line.program_id.sequence+'.'+line.budget_post_id.code]['planned_amount']+=line.planned_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.sequence]['reform_amount']+=line.reform_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.sequence]['codif_amount']+=line.codif_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.id]['commited_amount']+=line.commited_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.id]['devengado_amount']+=line.devengado_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.id]['paid_amount']+=line.paid_amount
                #res_line[line.budget_post_id.code+'.'+line.program_id.id]['commited_balance']+=line.commited_balance
                #res_line[line.budget_post_id.code+'.'+line.program_id.id]['devengado_balance']+=line.devengado_balance
                
#                res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['reform_amount']+=line.reform_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['codif_amount']+=line.codif_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['commited_amount']+=line.commited_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['devengado_amount']+=line.devengado_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['paid_amount']+=line.paid_amount
#                res_line[line.budget_post_id.id+line.program_id.id]['commited_balance']+=line.commited_balance
#                res_line[line.budget_post_id.id+line.program_id.id]['devengado_balance']+=line.devengado_balance

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
                           'nivel':0,
                           'code_aux':0,
                           'code_report':0,
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

report_sxw.report_sxw('report.BudgetCardExpense','budget.poa',
                      'gt_budget/report/report_budget_card_expense.mako',
                      parser=BudgetCardExpense)

class BudgetCardExpenseGroup(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(BudgetCardExpenseGroup, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
 #           '_months':self._months,
            '_get_totales':self._get_totales,
            'get_cargo': self.get_cargo,
           
        })
        
    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        aux = 'ALCALDE'
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux

    def set_context(self, objects, data, ids, report_type=None):
        if data['form']['project']==True: #and data['form']['project_id']:
            if data['form']['project_id']:
                objects=self.pool.get('crossovered.budget').browse(self.cr,self.uid,data['form']['budget_id'])         
                return super(BudgetCardExpenseGroup, self).set_context(objects, data, ids, report_type=report_type)
            else:
                raise osv.except_osv('Error!!', 'Debe seleccionar un Proyecto')
        objects=self.pool.get('crossovered.budget').browse(self.cr,self.uid,data['form']['budget_id'])         
        return super(BudgetCardExpenseGroup, self).set_context(objects, data, ids, report_type=report_type)
        
    def _months(self,resumen):  
        res = { }                       
        user=str(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                        
        begin = self.datas['form']['period_from'][1]
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        if len(begin)>7:
            res['begin']=begin.upper()
        else:
            res['begin']=datetime.datetime.strptime(str(self.datas['form']['period_from'][1]), "%m/%Y").strftime("%B").upper()
        end = self.datas['form']['period_to'][1]
        if len(end)>7:
            res['end']=end.upper()
        else:
            res['end']=datetime.datetime.strptime(str(self.datas['form']['period_to'][1]), "%m/%Y").strftime("%B").upper()
        if self.datas['form']['project_id']:
            project=self.datas['form']['project_id'][1]
            proyecto=self.pool.get('project.project').browse(self.cr,self.uid,[self.datas['form']['project_id'][0]])[0]              
            res['project']=project.upper()
            res['program']=proyecto.program_id.name
        else:
            res['project']=''
            res['program']=''
        return res 
    
    def _get_totales(self,resumen):  
        res = { }
        res_line = {}
        context = { }
        result_dic = {}
        pos =0
        if self.datas['form']['project']==True and self.datas['form']['project_id']:
            project_id=self.datas['form']['project_id']
            period_from = int(self.datas['form']['period_from'][0])
            period_to = int(self.datas['form']['period_to'][0])
            c_b_lines_obj = self.pool.get('crossovered.budget.lines')
            ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('crossovered_budget_id.id','=',resumen.id),('type_budget','=','gasto'),('task_id.project_id.id','=',project_id[0])])
            context = {'period_from': period_from, 'period_to': period_to}            
            planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
            totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)                                                    
            for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines):                    
                if res_line.has_key(line.budget_id.id)==False:
                    res_line[line.budget_id.id]={'code':str(project_id[0])+"."+line.budget_id.code,
                                                         'general_budget_name':line.budget_id.name,
                                                         'planned_amount':line.planned_amount,                                                         
                                                         'balance_acurred_amount':line.balance_accured,
                                                         'paid_amount':totales[line.id]['paid_amount'],
                                                         'commited_amount':totales[line.id]['commited_amount'],
                                                         'nivel':1                                                
                                                         }
                    
                    if res_line.has_key(line.budget_id.id*(line.id+1))==False:
                        res_line[line.budget_id.id*(line.id+1)]={'code':str(project_id[0])+"."+line.budget_id.code+".1",
                                                         'general_budget_name':line.full_name,
                                                         'planned_amount':line.planned_amount,                                                         
                                                         'balance_acurred_amount':line.balance_accured,
                                                         'paid_amount':totales[line.id]['paid_amount'],
                                                         'commited_amount':totales[line.id]['commited_amount'],
                                                         'nivel':2}
                        
                else:
                    if res_line.has_key(line.budget_id.id*(line.id+1))==False:
                        res_line[line.budget_id.id*(line.id+1)]={'code':str(project_id[0])+"."+line.budget_id.code+".1",
                                                         'general_budget_name':line.full_name,
                                                         'planned_amount':line.planned_amount,
                                                         'balance_acurred_amount':line.balance_accured,
                                                         'paid_amount':totales[line.id]['paid_amount'],
                                                         'commited_amount':totales[line.id]['commited_amount'],
                                                         'nivel':2}
                        
                    res_line[line.budget_id.id]['planned_amount']+=line.planned_amount         
                    res_line[line.budget_id.id]['balance_acurred_amount']+=line.balance_accured                               
                    res_line[line.budget_id.id]['paid_amount']+=totales[line.id]['paid_amount']
                    res_line[line.budget_id.id]['commited_amount']+=totales[line.id]['commited_amount']
            res_line['total']={                                                           
                              'planned_amount': 0.00,
                              'balance_acurred_amount': 0.00,
                              'commited_amount': 0.00,
                              'paid_amount': 0.00,
                              'general_budget_name': "TOTAL",
                              'code': 0,
                                  'code_aux': 0,
                              'nivel': 0,                                                                                  
                              }
            values=res_line.itervalues()
            for line_totales in values:
                if 'nivel' in line_totales:
                    if line_totales['nivel']==1:
                        res_line['total']['planned_amount']+=line_totales['planned_amount']            
                        res_line['total']['commited_amount']+=line_totales['commited_amount']
                        res_line['total']['paid_amount']+=line_totales['paid_amount']                        
                        res_line['total']['balance_acurred_amount']+=line_totales['balance_acurred_amount']
            res_dic=res_line.values()             
            result_dic=sorted(res_dic, key=operator.itemgetter('code_aux'))            
            return result_dic 
        else:
            return False

report_sxw.report_sxw('report.BudgetCardExpenseGroup','budget.poa',
                      'gt_budget/report/report_budget_card_expense_group.mako',
                      parser=BudgetCardExpenseGroup)


class ReformReportin(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReformReportin, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_get_totales':self._get_totales,
            '_vars': self._vars,
            'get_cargo': self.get_cargo,
        })

    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        aux = 'ALCALDE'
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux
        
    def _vars(self,resumen):  
        res = { }          
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')
        res['date']=today
        res['nivel'] = self.datas['form']['nivel']
        return res 

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['suplemento'] += data_suma['suplemento']
                res[data['post'].parent_id.code]['reduccion'] += data_suma['reduccion']
                res[data['post'].parent_id.code]['traspaso_aumento'] += data_suma['traspaso_aumento']
                res[data['post'].parent_id.code]['traspaso_disminucion'] += data_suma['traspaso_disminucion']                
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'suplemento': data['suplemento'],
                    'reduccion': data['reduccion'],
                    'traspaso_aumento': data['traspaso_aumento'],
                    'traspaso_disminucion': data['traspaso_dismunucion'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales(self, massreform, program=False):
        reform_obj = self.pool.get('budget.reform')
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = massreform.date
        date_to = massreform.date
        items = [] 
        reform1 = []
        reform2 = []
        for line in massreform.line_ids:
            #busco reforma con iguales valores
            items.append(line.budget_id.id)
            r_ids = reform_obj.search(cr, uid, [('budget_id','=',line.budget_id.id),('date','=',massreform.date),('amount','=',line.monto)])
            r_ids2 = reform_obj.search(cr, uid, [('budget2_id','=',line.budget_id.id),('date','=',massreform.date),('amount','=',line.monto)])
            for r in r_ids:
                reform11.append(r)
            for r in r_ids2:
                reform12.append(r)                
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[(id,'in',items)])
            
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to, 'reforms1':reform1, 'reforms2': reform2}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
            if res_line.has_key(line.code)==False:
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'program': line.program_id.id,
                    'padre': False, 
                    'code':line.code,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'codif_amount':line.codif_amount,
                    'reform_amount':line.reform_amount,
                    'suplemento':line.suplemento,
                    'reduccion':line.reduccion,
                    'traspaso_aumento': line.traspaso_aumento,
                    'traspaso_disminucion': line.traspaso_disminucion,
                    'final': False,
                    'nivel': line.budget_post_id.nivel,
                }
                if res_line.has_key(line.budget_post_id.code)==False:
                    res_line[line.budget_post_id.code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': False, 
                        'code': line.budget_post_id.code,
                        'general_budget_name':line.budget_post_id.name,
                        'planned_amount':line.planned_amount,
                        'codif_amount':line.codif_amount,
                        'reform_amount':line.reform_amount,
                        'suplemento':line.suplemento,
                        'reduccion':line.reduccion,
                        'traspaso_aumento': line.traspaso_aumento,
                        'traspaso_disminucion': line.traspaso_disminucion,                        
                        'final': True,
                        'nivel': line.budget_post_id.nivel-1,
                    }
                else:
                    res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
                    res_line[line.budget_post_id.code]['reform_amount']+=line.reform_amount
                    res_line[line.budget_post_id.code]['codif_amount']+=line.codif_amount
                    res_line[line.budget_post_id.code]['suplemento']+=line.suplemento
                    res_line[line.budget_post_id.code]['reduccion']+=line.reduccion
                    res_line[line.budget_post_id.code]['traspaso_aumento']+=line.traspaso_aumento
                    res_line[line.budget_post_id.code]['traspaso_disminucion']+=line.traspaso_disminucion
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:              
                res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
                res_line[line.budget_post_id.id+line.program_id.id]['reform_amount']+=line.reform_amount
                res_line[line.budget_post_id.id+line.program_id.id]['codif_amount']+=line.codif_amount
                res_line[line.budget_post_id.id+line.program_id.id]['suplemento']+=line.suplemento
                res_line[line.budget_post_id.id+line.program_id.id]['reduccion']+=line.reduccion
                res_line[line.budget_post_id.id+line.program_id.id]['traspaso_aumento']+=line.traspaso_aumento
                res_line[line.budget_post_id.id+line.program_id.id]['traspaso_disminucion']+=line.traspaso_disminucion                
                
        res_line['total']={'reform_amount': 0.00,
                           'planned_amount': 0.00,
                           'codif_amount': 0.00,
                           'suplemento': 0.00,
                           'reduccion': 0.00,
                           'traspaso_aumento': 0.00,
                           'traspaso_disminucion': 0.00,
                           'level':0,
                           'code':0
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['suplemento']+=line_totales['suplemento']
                res_line['total']['reduccion']+=line_totales['reduccion']
                res_line['total']['traspaso_aumento']+=line_totales['traspaso_aumento']
                res_line['total']['traspaso_disminucion']+=line_totales['traspaso_disminucion']

        return res_line

report_sxw.report_sxw('report.ReformReportin','mass.reform.ingreso',
                      'gt_budget/report/report_reform.mako',
                      parser=ReformReportin)


class BudgetCardIncomeR(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(BudgetCardIncomeR, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            '_get_totales':self._get_totales,
            'get_cargo': self.get_cargo,
            'get_firmas':self.get_firmas,
        })

    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux

    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        aux = 'ALCALDE'
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux
        
    def set_context(self, objects, data, ids, report_type=None):
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['budget_id']),
                                                         ('budget_post_id.internal_type','=','ingreso')])
#        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['budget_id']),
#                                                         ('type_budget','=','ingreso')])
        if ids_lines:
            objects=self.pool.get('budget.poa').browse(self.cr,self.uid,data['form']['budget_id'])         
            return super(BudgetCardIncomeR, self).set_context([objects], data, ids, report_type=report_type)
        else:
            raise osv.except_osv('Error!!', 'No existen partidas tipo ingreso del presupuesto')

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_to'] = self.datas['form']['date_to']
        res['nivel'] = self.datas['form']['nivel']
        res['tipo_nivel'] = self.datas['form']['tipo_nivel']
        res['sobregiro'] = self.datas['form']['sobregiro']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['end']=end.upper()
        return res 
        
    def _months(self,resumen):  
        res = { }          
        begin = self.datas['form']['period_from'][1]
        user=str(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        if len(begin)>7:
            res['begin']=begin.upper()
        else:
            res['begin']=datetime.datetime.strptime(str(self.datas['form']['period_from'][1]), "%m/%Y").strftime("%B").upper()
        end = self.datas['form']['period_to'][1]
        if len(end)>7:
            res['end']=end.upper()
        else:
            res['end']=datetime.datetime.strptime(str(self.datas['form']['period_to'][1]), "%m/%Y").strftime("%B").upper()   
        return res

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','ingreso')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + '.' + line.program_id.sequence
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                   # 'code':line.code,
                    'code':code_aux,#line.code_report,#line.code
                    'code_aux':code_aux,#line.code_report,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                if res_line.has_key(line.budget_post_id.code)==False:
                    code_aux = line.budget_post_id.code + '.' +line.program_id.sequence
                    res_line[line.budget_post_id.code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': False, 
                        'code': line.budget_post_id.code,
                        'code_aux':line.budget_post_id.code,
                        'general_budget_name':line.budget_post_id.name,
                        'planned_amount':line.planned_amount,
                        'final': True,
                        'nivel': line.budget_post_id.nivel-1,
                        'level': line.budget_post_id.nivel-1,
                    }
 #               else:
 #                   res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
        res_line['total']={'planned_amount': 0.00,
                           'level':0,
                           'nivel':0,
                           'code':0,
                           'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
        return res_line

report_sxw.report_sxw('report.BudgetCardIncomeR','budget.poa',
                      'gt_budget/report/report_budget_card_income_r.mako',
                      parser=BudgetCardIncomeR)

class BudgetCardExpenseR(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(BudgetCardExpenseR, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_get_totales':self._get_totales,
            '_vars': self._vars,
            '_get_programs': self._get_programs,
            'get_cargo': self.get_cargo,
            'get_firmas':self.get_firmas,
        })

    def get_firmas(self, cargo):
        aux = ""
        parameter_obj = self.pool.get('ir.config_parameter')
        cargo_ids = parameter_obj.search(self.cr, self.uid, [('key','=',cargo)],limit=1)
        if cargo_ids:
            aux = parameter_obj.browse(self.cr, self.uid,cargo_ids[0]).value
        return aux
        
    def get_cargo(self, texto):
        job_obj = self.pool.get('hr.job')
        employee_obj = self.pool.get('hr.employee')
        job_ids = job_obj.search(self.cr, self.uid, [('name','=',texto)])
        aux = 'ALCALDE'
        if job_ids:
            job = job_obj.browse(self.cr, self.uid, job_ids[0])
            employee_ids = employee_obj.search(self.cr, self.uid, [('job_id','=',job_ids[0])])
            if employee_ids:
                employee = employee_obj.browse(self.cr, self.uid, employee_ids[0])
                aux = employee.complete_name
        return aux

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_to'] = self.datas['form']['date_to']
        res['nivel'] = self.datas['form']['nivel']
        res['tipo_nivel'] = self.datas['form']['tipo_nivel']
        today=time.strftime('%Y-%m-%d %H:%M:%S')    
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['sobregiro'] = self.datas['form']['sobregiro']
        res['end']=end.upper()
        return res 
        
    def set_context(self, objects, data, ids, report_type=None):
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['budget_id']),
                                                         ('budget_post_id.internal_type','=','gasto')])
#        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['budget_id']),
#                                                         ('type_budget','=','gasto')])
        if ids_lines:
            objects=self.pool.get('budget.poa').browse(self.cr,self.uid,data['form']['budget_id'])         
            return super(BudgetCardExpenseR, self).set_context([objects], data, ids, report_type=report_type)
        else:
            raise osv.except_osv('Error!!', 'No existen partidas tipo egreso del presupuesto')
        
    def _months(self,resumen):  
        res = { }                       
        user=str(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                        
        begin = self.datas['form']['period_from'][1]
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        if len(begin)>7:
            res['begin']=begin.upper()
        else:
            res['begin']=datetime.datetime.strptime(str(self.datas['form']['period_from'][1]), "%m/%Y").strftime("%B").upper()
        end = self.datas['form']['period_to'][1]
        if len(end)>7:
            res['end']=end.upper()
        else:
            res['end']=datetime.datetime.strptime(str(self.datas['form']['period_to'][1]), "%m/%Y").strftime("%B").upper()   
        project=self.datas['form']['project_id'][1]
        proyecto=self.pool.get('project.project').browse(self.cr,self.uid,[self.datas['form']['project_id'][0]])[0]              
        res['project']=project.upper()
        res['program']=proyecto.program_id.name
        return res 

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'code_report':data['post'].parent_id.code,
#                    'program':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)

    def _get_programs(self,resumen):
        res = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        c_b_lines_obj = self.pool.get('budget.item')
        program_obj = self.pool.get('project.program')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','ingreso')])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to}
        project = self.datas['form']['project']
        if project:
            program_ids = self.datas['form']['program_ids']
            if program_ids:
                programas = self.datas['form']['program_ids']
                if len(programas)==1:
                    programas.append(programas[0])
                sql_programs = "select id,name,sequence from project_program where id in %s order by sequence"%(str(tuple(programas)))
            else:
                ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','ingreso')])
                sql_programs = "select id,name,sequence from project_program where id in (select program_id from budget_item where id in %s group by program_id) order by sequence"%(str(tuple(ids_lines)))
            self.cr.execute(sql_programs)
            programas = self.cr.fetchall()
            for program in programas:
                res.append({'id': program[0], 'name': program[1], 'sequence': program[2]})
            return res
        else:
            return [{'id': False, 'name': '', 'sequence': ''}]
            
    def _get_totales(self, resumen, program=False):
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
            
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
            if res_line.has_key(line.code)==False:
                aux_code_report = line.program_id.sequence + '.' + line.budget_post_id.code
                code_aux = line.budget_post_id.code + '.' + line.program_id.sequence
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'program': line.program_id.id,
                    'padre': True,#False, 
                    'code':code_aux,#line.code_report,#line.code
                    'code_aux':code_aux,#line.code_report,
                    'code_report':aux_code_report,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'final': True,#False,
                    'nivel': line.budget_post_id.nivel,
                }
                if res_line.has_key(line.budget_post_id.code)==False:
                    code_aux = line.budget_post_id.code + '.' +line.program_id.sequence
                    res_line[line.budget_post_id.code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': False, 
                        'code': line.budget_post_id.code,
                        'code_aux':line.budget_post_id.code,
                        'code_report':line.budget_post_id.code,#aux_code_report,#line.code_report,
                        'general_budget_name':line.budget_post_id.name,
                        'planned_amount':line.planned_amount,
                        'final': True,
                        'nivel': line.budget_post_id.nivel-1,
                        'level': line.budget_post_id.nivel-1,
                    }
                #else:
                #    res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:
                #if not res_line.has_key(line.budget_post_id.id+line.program_id.id):
                #    MSG = 'Verifique los proyectos del programa %s de la partida %s no esta codificada, recuerde que para generar los reportes los proyectos deben estar en ejecucion' % (line.program_id.name,line.budget_post_id.name)
                #    raise osv.except_osv('Error', MSG)
                #res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
                if not res_line.has_key(line.code):
                    MSG = 'Verifique los proyectos del programa %s de la partida %s no esta codificada, recuerde que para generar los reportes los proyectos deben estar en ejecucion' % (line.program_id.name,line.budget_post_id.name)
                    raise osv.except_osv('Error', MSG)
                res_line[line.code]['planned_amount']+=line.planned_amount
        res_line['total']={'planned_amount': 0.00,
                           'level':0,
                           'nivel':0,#add mc
                           'code':0,
                           'code_aux':0,
                           'code_report':0,
        }
        values=res_line.itervalues()
        #import pdb
        #pdb.set_trace()
        #result_dic=sorted(res_dic, key=operator.itemgetter('code'))            
        for line_totales in values:
#            if not 'nivel' in line_totales and line_totales['final']==True:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']   
       # res_dic=res_line.values()             
       # res_line=sorted(res_line, key=operator.itemgetter('code_aux'))            
        return res_line 

report_sxw.report_sxw('report.BudgetCardExpenseR','budget.poa',
                      'gt_budget/report/report_budget_card_expense_r.mako',
                      parser=BudgetCardExpenseR)
