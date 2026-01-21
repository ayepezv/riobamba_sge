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

class evaluacion_programa_comprometido(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(evaluacion_programa_comprometido, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            '_get_totales':self._get_totales,
           '_get_totales_funcion':self._get_totales_funcion,
           '_get_totales_egreso':self._get_totales_egreso,
        })
        
    def set_context(self, objects, data, ids, report_type=None):
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['poa_id'][0]),
                                                         ('type_budget','=','gasto'),('program_id','=',data['form']['program_id'][0])])
        if ids_lines:
            objects=self.pool.get('budget.poa').browse(self.cr,self.uid,data['form']['poa_id'][0])         
            return super(evaluacion_programa_comprometido, self).set_context([objects], data, ids, report_type=report_type)
        else:
            raise osv.except_osv('Error!!', 'No existen partidas tipo gasto del presupuesto')

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
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['end']=end.upper()
        res['program_name']=self.datas['form']['program_id'][1]
        return res 
        
    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            aux_percent = aux_percent_mes = 0 
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['commited_amount'] += data_suma['commited_amount']
                res[data['post'].parent_id.code]['commited_amount_mes'] += data_suma['commited_amount_mes']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['commited_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                    aux_percent_mes = (res[data['post'].parent_id.code]['commited_amount_mes']*100)/res[data['post'].parent_id.code]['codif_amount']
                    res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
                else:
                    res[data['post'].parent_id.code]['percent_sal'] = 0
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_rec_mes'] = aux_percent_mes
#                res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['code'][0:4]+data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'paid_amount':data['paid_amount'], #pagado - recaudado
                    'codif_amount':data['codif_amount'],
                    'commited_amount':data['commited_amount'],
                    'commited_amount_mes':data['commited_amount_mes'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_rec_mes':data['percent_rec_mes'],
                    'percent_sal':data['percent_sal'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales_egreso(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        program_obj = self.pool.get('project.program')
        date_from = resumen.date_start#self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        program_id = self.datas['form']['program_id'][0]
        c_b_lines_obj = self.pool.get('budget.item')
        program_code = self.datas['form']['program_id'][1][0:1]
        if self.datas['form']['program_id'][1][0:3]!='1.1':
            return False
        program_ids = program_obj.search(self.cr, self.uid, [])
        pr_ids = []
        if program_ids:
            for program_id in program_ids:
                pr_ids.append(program_id)
                #programa = program_obj.browse(self.cr, self.uid, program_id)
                #if programa.sequence[0:1]==program_code:
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(self.cr, self.uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(self.cr, self.uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':resumen.id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(self.cr,self.uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.commited_amount
            comp_corte += line.commited_amount
        saldo = final_funcion - comp_corte  #comp_corte
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result


    def _get_totales_funcion(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        program_obj = self.pool.get('project.program')
        date_from = resumen.date_start#self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        program_id = self.datas['form']['program_id'][0]
        c_b_lines_obj = self.pool.get('budget.item')
        program_code = self.datas['form']['program_id'][1][0:1]
        program_ids = program_obj.search(self.cr, self.uid, [])
        pr_ids = []
        if self.datas['form']['program_id'][1][2]!='1':
            return False
        if program_ids:
            for program_id in program_ids:
                programa = program_obj.browse(self.cr, self.uid, program_id)
                if programa.sequence[0:1]==program_code:
                    pr_ids.append(programa.id)
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(self.cr, self.uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(self.cr, self.uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':resumen.id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(self.cr,self.uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.commited_amount
            comp_corte += line.commited_amount
        saldo = final_funcion - comp_corte#mes
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result
        

    def _get_totales(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        date_from = resumen.date_start#self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        program_id = self.datas['form']['program_id'][0]
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','gasto'),('program_id','=',program_id)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(self.cr, self.uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(self.cr, self.uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':resumen.id}                      
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
            line2 = c_b_lines_obj.browse(self.cr,self.uid,line.id, context=context2)
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.commited_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                aux_superavit = line.codif_amount - line.commited_amount #en gasto
                if line.codif_amount>0:
                    aux_percent_rec = ((line.commited_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.commited_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                    aux_percent_sal = 100 - aux_percent_rec
                else:
                    aux_percent_sal = 0
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':line.code,
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'paid_amount':line.paid_amount,   
                    'commited_amount':line.commited_amount,  
                    'commited_amount_mes':line2.commited_amount,
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_rec_mes':aux_percent_rec_mes,
                    'percent_sal':aux_percent_sal,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = line.paid_amount - line.codif_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.commited_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.code]['planned_amount']+=line.planned_amount
                res_line[line.code]['reform_amount']+=line.reform_amount#res_line[line.budget_post_id.id]['reform_amount']+=line.reform_amount
                res_line[line.code]['codif_amount']+=line.codif_amount#res_line[line.budget_post_id.id]['codif_amount']
                res_line[line.code]['paid_amount']+=line.paid_amount
                res_line[line.code]['commited_amount']+=line.commited_amount
                res_line[line.code]['commited_amount_mes']+=line2.commited_amount
                res_line[line.code]['to_rec']+=aux_to_pay
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'commited_amount': 0.00,
            'commited_amount_mes': 0.00,
            'paid_amount': 0.00,
            'to_rec': 0.00,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'percent_super': 0.00,
            'superavit': 0.00,
            'level':0,
            'code':0,
            'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['commited_amount']+=line_totales['commited_amount']
                res_line['total']['commited_amount_mes']+=line_totales['commited_amount_mes']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['to_rec']+=line_totales['to_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
        return res_line

report_sxw.report_sxw('report.evaluacion_programa_comprometido','evaluacion.programa.comprometido',
                      'gt_project_project/report/evaluacion_programa_comprometido.mako',
                      parser=evaluacion_programa_comprometido)

class evaluacion_programa_comprometido_cons(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(evaluacion_programa_comprometido_cons, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
        
report_sxw.report_sxw('report.evaluacion_programa_comprometido_cons','evaluacion.programa.comprometido.cons',
                      'gt_project_project/report/evaluacion_programa_comprometido_cons.mako',
                      parser=evaluacion_programa_comprometido_cons)

class evaluacion_programa_cons(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(evaluacion_programa_cons, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
        
report_sxw.report_sxw('report.evaluacion_programa_cons','evaluacion.programa.cons',
                      'gt_project_project/report/evaluacion_programa_cons.mako',
                      parser=evaluacion_programa_cons)

class evaluacion_programa(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(evaluacion_programa, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            '_get_totales':self._get_totales,
            '_get_totales_funcion':self._get_totales_funcion,
            '_get_totales_egreso':self._get_totales_egreso,
        })
        
    def set_context(self, objects, data, ids, report_type=None):
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['poa_id'][0]),
                                                         ('type_budget','=','gasto'),('program_id','=',data['form']['program_id'][0])])
        if ids_lines:
            objects=self.pool.get('budget.poa').browse(self.cr,self.uid,data['form']['poa_id'][0])         
            return super(evaluacion_programa, self).set_context([objects], data, ids, report_type=report_type)
        else:
            raise osv.except_osv('Error!!', 'No existen partidas tipo gasto del presupuesto')

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
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['end']=end.upper()
        res['program_name']=self.datas['form']['program_id'][1]
        return res 
        
    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['to_rec'] += data_suma['to_rec']
                aux_percent = aux_percent_mes = 0
                if res[data['post'].parent_id.code]['codif_amount']>0:
                    aux_percent = (res[data['post'].parent_id.code]['paid_amount']*100)/res[data['post'].parent_id.code]['codif_amount']
                    aux_percent_mes = (res[data['post'].parent_id.code]['paid_amount_mes']*100)/res[data['post'].parent_id.code]['codif_amount']
                    res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
                else:
                    res[data['post'].parent_id.code]['percent_sal'] = 0
                res[data['post'].parent_id.code]['percent_rec'] = aux_percent
                res[data['post'].parent_id.code]['percent_rec_mes'] = aux_percent_mes
#                res[data['post'].parent_id.code]['percent_sal'] = 100 - aux_percent
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['code'][0:4]+data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'paid_amount':data['paid_amount'], #pagado - recaudado
                    'paid_amount_mes':data['paid_amount_mes'],
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'to_rec':data['to_rec'],
                    'percent_rec':data['percent_rec'],
                    'percent_rec_mes':data['percent_rec_mes'],
                    'percent_sal':data['percent_sal'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales_funcion(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        program_obj = self.pool.get('project.program')
        date_from = resumen.date_start#self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        program_id = self.datas['form']['program_id'][0]
        c_b_lines_obj = self.pool.get('budget.item')
        program_code = self.datas['form']['program_id'][1][0:1]
        program_ids = program_obj.search(self.cr, self.uid, [])
        pr_ids = []
        if self.datas['form']['program_id'][1][2]!='1':
            return False
        if program_ids:
            for program_id in program_ids:
                programa = program_obj.browse(self.cr, self.uid, program_id)
                if programa.sequence[0:1]==program_code:
                    pr_ids.append(programa.id)
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(self.cr, self.uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(self.cr, self.uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':resumen.id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(self.cr,self.uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.paid_amount
            comp_corte += line.paid_amount
        saldo = final_funcion - comp_corte
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result

    def _get_totales_egreso(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        program_obj = self.pool.get('project.program')
        date_from = resumen.date_start#self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        program_id = self.datas['form']['program_id'][0]
        c_b_lines_obj = self.pool.get('budget.item')
        program_code = self.datas['form']['program_id'][1][0:1]
        program_ids = program_obj.search(self.cr, self.uid, [])
        pr_ids = []
        if self.datas['form']['program_id'][1][0:3]!='1.1':
            return False
        if program_ids:
            for program_id in program_ids:
                pr_ids.append(program_id)
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','gasto'),('program_id','in',pr_ids)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}  
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(self.cr, self.uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(self.cr, self.uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':resumen.id}                      
        porcentaje_mes = porcentaje_acumula = planned_funcion = reforma_funcion = final_funcion = comp_mes = comp_corte = 0
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
#            if line.program_id!=program_id:
                #es de la funcion pero no del programa
            line2 = c_b_lines_obj.browse(self.cr,self.uid,line.id, context=context2)
            planned_funcion += line.planned_amount
            reforma_funcion += line.reform_amount
            final_funcion += line.codif_amount
            comp_mes += line2.paid_amount
            comp_corte += line.paid_amount
        saldo = final_funcion - comp_corte
        porcentaje_mes = (comp_mes*100.00)/final_funcion
        porcentaje_acumula = (comp_corte*100.00)/final_funcion
        porcentaje_saldo = (saldo*100.00)/final_funcion
        result.append(planned_funcion)
        result.append(reforma_funcion)
        result.append(final_funcion)
        result.append(comp_mes)
        result.append(porcentaje_mes)
        result.append(comp_corte)
        result.append(porcentaje_acumula)
        result.append(saldo)
        result.append(porcentaje_saldo)
        return result

    def _get_totales(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        period_obj = self.pool.get('account.period')
        date_from = resumen.date_start#self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        program_id = self.datas['form']['program_id'][0]
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',resumen.id),('type_budget','=','gasto'),('program_id','=',program_id)])
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':resumen.id}            
        ##sacar el contexto dos para saber el mensual
        period_ids = period_obj.search(self.cr, self.uid, [('date_start','<=',date_to),('date_stop','>=',date_to)])
        periodo = period_obj.browse(self.cr, self.uid, period_ids[0])
        context2 = {'by_date':True,'date_start': periodo.date_start, 'date_end': periodo.date_stop,'poa_id':resumen.id}            
        planned_total=coded_total=reforma_total=balance_accured_total=practical_total=recaudado_total=0
        #        totales = c_b_lines_obj._compute_budget_all(self.cr, self.uid, ids_lines,[],[], context)
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines, context=context):
            line2 = c_b_lines_obj.browse(self.cr,self.uid,line.id, context=context2)
            if res_line.has_key(line.code)==False:
                code_aux = line.budget_post_id.code + line.program_id.sequence
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                aux_superavit = line.codif_amount - line.paid_amount #en gasto
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                    aux_percent_sal = 100 - aux_percent_rec
                else:
                    aux_percent_sal = 0
                res_line[line.code]={
                    'post': line.budget_post_id,
                    'padre': False, 
                    'code':line.code,#code_aux,#line.code
                    'code_aux':code_aux,
                    'general_budget_name':line.budget_post_id.name,
                    'planned_amount':line.planned_amount,
                    'reform_amount':line.reform_amount,
                    'codif_amount':line.codif_amount,
                    'paid_amount':line.paid_amount,   
                    'paid_amount_mes':line2.paid_amount,  
                    'to_rec':aux_to_pay,
                    'percent_rec':aux_percent_rec,
                    'percent_rec_mes':aux_percent_rec_mes,
                    'percent_sal':aux_percent_sal,
                    'nivel': line.budget_post_id.nivel-1,
                    'final': True,
                }
                self.crear_padre(res_line[line.code], res_line[line.code],res_line)
            else:                                
                aux_to_pay = line.codif_amount - line.paid_amount
                aux_percent_sal = 100 - aux_percent_rec
                aux_superavit = line.paid_amount - line.codif_amount
                aux_percent_rec = aux_percent_rec_mes = aux_percent_super = 0
                if line.codif_amount>0:
                    aux_percent_rec = ((line.paid_amount)*(100))/line.codif_amount
                    aux_percent_rec_mes = ((line2.paid_amount)*(100))/line.codif_amount
                    aux_percent_super = ((aux_superavit)*(100))/line.codif_amount
                res_line[line.code]['planned_amount']+=line.planned_amount
                res_line[line.code]['reform_amount']+=line.reform_amount#totales[line.id]['reforma_amount']
                res_line[line.code]['codif_amount']+=line.codif_amount#totales[line.id]['coded_amount']
                res_line[line.code]['paid_amount']+=line.paid_amount
                res_line[line.code]['paid_amount_mes']+=line2.paid_amount
                res_line[line.code]['to_rec']+=aux_to_pay
        res_line['total']={
            'planned_amount': 0.00,
            'reform_amount': 0.00,
            'codif_amount': 0.00,
            'paid_amount': 0.00,
            'paid_amount_mes': 0.00,
            'to_rec': 0.00,
            'percent_rec': 0.00,
            'percent_sal': 0.00,
            'percent_super': 0.00,
            'superavit': 0.00,
            'level':0,
            'code':0,
            'code_aux':0,
        }
        values=res_line.itervalues()
        for line_totales in values:
            if not 'level' in line_totales and line_totales['final']==True:
                res_line['total']['planned_amount']+=line_totales['planned_amount']            
                res_line['total']['reform_amount']+=line_totales['reform_amount']
                res_line['total']['codif_amount']+=line_totales['codif_amount']
                res_line['total']['paid_amount']+=line_totales['paid_amount']
                res_line['total']['paid_amount_mes']+=line_totales['paid_amount_mes']
                res_line['total']['to_rec']+=line_totales['to_rec']
                res_line['total']['percent_rec']+=line_totales['percent_rec']
                res_line['total']['percent_sal']+=line_totales['percent_sal']
        return res_line

report_sxw.report_sxw('report.evaluacion_programa','evaluacion.programa',
                      'gt_project_project/report/evaluacion_programa.mako',
                      parser=evaluacion_programa)

