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

class rf_programa(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(rf_programa, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            '_get_totales':self._get_totales,
            '_get_funcion':self._get_funcion,
            '_get_general':self._get_general,
        })
        
    def _get_funcion(self,reforma,texto):
        program_obj = self.pool.get('project.program')
        line_gasto_obj = self.pool.get('mass.reform.line')
        aux = 0
        aux_funcion = reforma.program_id.sequence[0:1]
        program_ids = program_obj.search(self.cr,self.uid,[('funcion','=',aux_funcion)])
        if program_ids:
            aux_planned = aux_final = aux_traspaso_aumento = aux_aumento = aux_traspaso_disminucion = aux_disminucion = 0
            line_origen_ids = line_gasto_obj.search(self.cr, self.uid, [('program_id','in',program_ids),('mass_id','=',reforma.rfg_id.id)])
            line_destino_ids = line_gasto_obj.search(self.cr, self.uid, [('program_id','in',program_ids),('mass_id2','=',reforma.rfg_id.id)])
            line_completo_ids = line_origen_ids + line_destino_ids
            if line_completo_ids:
                for line in line_gasto_obj.browse(self.cr,self.uid,line_completo_ids):
                    aux_planned += line.inicial
                    aux_final += line.final
                    if line.mass_id:
                        if line.traspaso:
                            aux_traspaso_disminucion += line.monto
                        else:
                            aux_disminucion += line.monto
                    else:
                        if line.traspaso:
                            aux_traspaso_aumento += line.monto
                        else:
                            aux_aumento += line.monto
            if texto=='planned':
                return aux_planned
            elif texto=='aumento':
                return aux_aumento
            elif texto=='disminucion':
                return aux_disminucion
            elif texto=='suplemento':
                return aux_traspaso_aumento
            elif texto=='reduccion':
                return aux_traspaso_disminucion
            elif texto=='final':
                return aux_final

    def _get_general(self,reforma,texto):
        aux = 0
        program_obj = self.pool.get('project.program')
        line_gasto_obj = self.pool.get('mass.reform.line')
        item_obj = self.pool.get('budget.item')
        poa_obj = self.pool.get('budget.poa')
        aux = 0
        program_ids = program_obj.search(self.cr,self.uid,[])
        if reforma.rfg_id.line_ids:
            poa_id = reforma.rfg_id.line_ids[0].budget_id.poa_id.id
        else:
            poa_id = reforma.rfg_id.line_ids2[0].budget_id.poa_id.id
        id_lines=item_obj.search(self.cr,self.uid,[('poa_id','=',poa_id),('type_budget','=','gasto')])
        aux_planned_general = aux_final_general = 0
        if id_lines:
            for id_line in id_lines:
                line = item_obj.browse(self.cr, self.uid, id_line) 
                aux_planned_general += line.planned_amount
        if program_ids:
            aux_planned = aux_final = aux_traspaso_aumento = aux_aumento = aux_traspaso_disminucion = aux_disminucion = 0
            line_origen_ids = line_gasto_obj.search(self.cr, self.uid, [('program_id','in',program_ids),('mass_id','=',reforma.rfg_id.id)])
            line_destino_ids = line_gasto_obj.search(self.cr, self.uid, [('program_id','in',program_ids),('mass_id2','=',reforma.rfg_id.id)])
            line_completo_ids = line_origen_ids + line_destino_ids
            if line_completo_ids:
                for line in line_gasto_obj.browse(self.cr,self.uid,line_completo_ids):
                    aux_planned += line.inicial
                    #aux_final += line.final
                    if line.mass_id:
                        if line.traspaso:
                            aux_traspaso_disminucion += line.monto
                        else:
                            aux_disminucion += line.monto
                    else:
                        if line.traspaso:
                            aux_traspaso_aumento += line.monto
                        else:
                            aux_aumento += line.monto
            #aux_final_general = aux_planned_general + aux_traspaso_aumento + aux_aumento - aux_traspaso_disminucion - aux_disminucion
            if reforma.tipo=='GASTO':
                aux_planned_general = reforma.rfg_id.inicial
            else:
                aux_planned_general = reforma.rfi_id.inicial
            aux_final_general = aux_planned_general + aux_traspaso_aumento + aux_aumento - aux_traspaso_disminucion - aux_disminucion
            if texto=='planned':
                return aux_planned_general
            elif texto=='aumento':
                return aux_aumento
            elif texto=='disminucion':
                return aux_disminucion
            elif texto=='suplemento':
                return aux_traspaso_aumento
            elif texto=='reduccion':
                return aux_traspaso_disminucion
            elif texto=='final':
                return aux_final_general

    def _vars(self,resumen):  
        res = { }          
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        return res 
        
    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['suplemento'] += data_suma['suplemento']
                res[data['post'].parent_id.code]['disminucion'] += data_suma['disminucion']
                res[data['post'].parent_id.code]['traspaso_aumento'] += data_suma['traspaso_aumento']
                res[data['post'].parent_id.code]['traspaso_disminucion'] += data_suma['traspaso_disminucion']
                res[data['post'].parent_id.code]['total'] += data_suma['total']
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
                    'code_aux':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'suplemento':data['suplemento'],
                    'disminucion':data['disminucion'],
                    'traspaso_aumento':data['traspaso_aumento'],
                    'traspaso_disminucion':data['traspaso_disminucion'],
                    'total':data['total'],
                    'final': False,
                    'nivel': data['post'].parent_id.nivel-1,
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
            
    def _get_totales(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        poa_obj = self.pool.get('budget.poa')
        reform_obj = self.pool.get('mass.reform')
        line_ingreso_obj = self.pool.get('mass.reform.line.ingreso')
        line_gasto_obj = self.pool.get('mass.reform.line')
        item_obj = self.pool.get('budget.item')
        program_id = self.datas['form']['program_id']
        tipo = self.datas['form']['tipo']
        if tipo == 'INGRESO':
            reforma = self.datas['form']['rfi_id']
        else:
            reforma_id = self.datas['form']['rfg_id']
            reforma = reform_obj.browse(self.cr, self.uid,self.datas['form']['rfg_id'])
            line_origen_ids = line_gasto_obj.search(self.cr, self.uid, [('program_id','=',program_id),('mass_id','=',reforma_id)])
            line_destino_ids = line_gasto_obj.search(self.cr, self.uid, [('program_id','=',program_id),('mass_id2','=',reforma_id)])
            line_completo_ids = line_origen_ids + line_destino_ids
            items_base = []
            items_all = []
            poa_ids = poa_obj.search(self.cr, self.uid, [('date_start','=',reforma.fy_id.date_start),('date_end','=',reforma.fy_id.date_stop)])
            if not poa_ids:
                raise osv.except_osv('Error de usuario','No hay presupuesto definido para la fecha o periodo contable seleccionado.')
            for line_reforma in line_completo_ids:
                linea_reforma = line_gasto_obj.browse(self.cr, self.uid, line_reforma)
                if not linea_reforma.budget_id.id in items_base:
                    items_base.append(linea_reforma.budget_id.id)
            for item_id in items_base:
                item = item_obj.browse(self.cr, self.uid, item_id)
                aux_code_budget = item.code_aux[0:6]
                items_2 = item_obj.search(self.cr, self.uid, [('program_id','=',program_id),('poa_id','=',poa_ids[0]),('code','like',aux_code_budget+"%")])
                items_all += items_2
            final_aux = datetime.datetime.strptime(reforma.date, '%Y-%m-%d').date()
            final_aux = final_aux - timedelta(days=1)
            date_final_reporte = final_aux.strftime('%Y-%m-%d')
            context = {'by_date':True,'date_start': reforma.fy_id.date_start, 'date_end': date_final_reporte,'poa_id':poa_ids[0]}            
            for line in item_obj.browse(self.cr,self.uid,items_all, context=context):
                if res_line.has_key(line.code)==False:
#                    partida = item_obj.browse(self.cr,self.uid,line.budget_id.id, context=context)
                    code_aux = line.budget_post_id.code + line.program_id.sequence
                    aux_traspaso_aumento = aux_aumento = aux_traspaso_disminucion = aux_disminucion = aux_final = 0
                    aux_final = line.codif_amount
#                    line_reformas_ids = line_gasto_obj.search(self.cr, self.uid, [('budget_id','=',line.id)])
                    line_reformas_ids = line_gasto_obj.search(self.cr, self.uid, [('mass_id','=',reforma_id),('budget_id','=',line.id)])
                    line_reformas_ids2 = line_gasto_obj.search(self.cr, self.uid, [('mass_id2','=',reforma_id),('budget_id','=',line.id)])
                    line_reformas_ids3 = line_reformas_ids + line_reformas_ids2
                    if line_reformas_ids3:
                        for line_reforma_id in line_reformas_ids3:
                            line_r = line_gasto_obj.browse(self.cr, self.uid, line_reforma_id)
                            if line_r.mass_id:
                                if line_r.traspaso:
                                    aux_traspaso_disminucion = line_r.monto
                                else:
                                    aux_disminucion = line_r.monto
                            else:
                                if line_r.traspaso:
                                    aux_traspaso_aumento = line_r.monto
                                else:
                                    aux_aumento = line_r.monto
                        aux_final = aux_final + line_r.final
                    res_line[line.code]={
                        'post': line.budget_post_id,
                        'padre': False, 
                        'code':code_aux,
                        'code_aux':code_aux,
                        'general_budget_name':line.budget_post_id.name,
                        'planned_amount':line.codif_amount,#planned_amount,
                        'suplemento':aux_aumento,
                        'disminucion':aux_disminucion,
                        'nivel': line.budget_post_id.nivel-1,
                        'traspaso_aumento':aux_traspaso_aumento,
                        'traspaso_disminucion':aux_traspaso_disminucion,
                        'total':aux_final,
                        'final': True,
                    }
                    self.crear_padre(res_line[line.code], res_line[line.code],res_line)
                else:         
                    res_line[line.code]['planned_amount']+=line.codif_amount
                    #res_line[line.budget_post_id.id]['planned_amount']+=partida.planned_amount                       
            res_line['total']={
                'planned_amount': 0.00,
                'suplemento':0.00,
                'disminucion':0.00,
                'traspaso_aumento':0.00,
                'traspaso_disminucion':0.00,
                'code':0,
                'code_aux':0,
                'final':0,
                'total':0.00,
            }
            values=res_line.itervalues()
            for line_totales in values:
                if not 'level' in line_totales and line_totales['final']==True:
                    res_line['total']['planned_amount']+=line_totales['planned_amount']            
                    res_line['total']['suplemento']+=line_totales['suplemento']
                    res_line['total']['disminucion']+=line_totales['disminucion']
                    res_line['total']['traspaso_aumento']+=line_totales['traspaso_aumento']
                    res_line['total']['traspaso_disminucion']+=line_totales['traspaso_disminucion']
                    res_line['total']['total']+=line_totales['total']                                                            
            return res_line

    def _get_totales2(self,resumen):
        res = { }
        res_line = { }
        context = { }
        result = []
        poa_obj = self.pool.get('budget.poa')
        reform_obj = self.pool.get('mass.reform')
        line_ingreso_obj = self.pool.get('mass.reform.line.ingreso')
        line_gasto_obj = self.pool.get('mass.reform.line')
        item_obj = self.pool.get('budget.item')
        program_id = self.datas['form']['program_id']
        tipo = self.datas['form']['tipo']
        if tipo == 'INGRESO':
            reforma = self.datas['form']['rfi_id']
        else:
            reforma = self.datas['form']['rfg_id']
            line_origen_ids = line_gasto_obj.search(self.cr, self.uid, [('program_id','=',program_id),('mass_id','=',reforma)])
            line_destino_ids = line_gasto_obj.search(self.cr, self.uid, [('program_id','=',program_id),('mass_id2','=',reforma)])
            line_completo_ids = line_origen_ids + line_destino_ids
            reforma = reform_obj.browse(self.cr, self.uid,self.datas['form']['rfg_id'])
            poa_ids = poa_obj.search(self.cr, self.uid, [('date_start','=',reforma.fy_id.date_start),('date_end','=',reforma.fy_id.date_stop)])
            if not poa_ids:
                raise osv.except_osv('Error de usuario','No hay presupuesto definido para la fecha o periodo contable seleccionado.')
            final_aux = datetime.datetime.strptime(reforma.date, '%Y-%m-%d').date()
            final_aux = final_aux - timedelta(days=1)
            date_final_reporte = final_aux.strftime('%Y-%m-%d')
            context = {'by_date':True,'date_start': reforma.fy_id.date_start, 'date_end': date_final_reporte,'poa_id':poa_ids[0]}            
            for line in line_gasto_obj.browse(self.cr,self.uid,line_completo_ids, context=context):
                if res_line.has_key(line.code)==False:
                    partida = item_obj.browse(self.cr,self.uid,line.budget_id.id, context=context)
                    code_aux = line.budget_id.budget_post_id.code + line.program_id.sequence
                    aux_traspaso_aumento = aux_aumento = aux_traspaso_disminucion = aux_disminucion = 0
                    if line.mass_id:
                        if line.traspaso:
                            aux_traspaso_disminucion = line.monto
                        else:
                            aux_disminucion = line.monto
                    else:
                        if line.traspaso:
                            aux_traspaso_aumento = line.monto
                        else:
                            aux_aumento = line.monto
                    res_line[line.code]={
                        'post': line.budget_id.budget_post_id,
                        'padre': False, 
                        'code':code_aux,
                        'code_aux':code_aux,
                        'general_budget_name':line.budget_id.budget_post_id.name,
                        'planned_amount':partida.codif_amount,#planned_amount,
                        'suplemento':aux_aumento,
                        'disminucion':aux_disminucion,
                        'nivel': line.budget_id.budget_post_id.nivel-1,
                        'traspaso_aumento':aux_traspaso_aumento,
                        'traspaso_disminucion':aux_traspaso_disminucion,
                        'total':line.final,
                        'final': True,
                    }
                    self.crear_padre(res_line[line.code], res_line[line.code],res_line)
                else:         
                    res_line[line.budget_post_id.id]['planned_amount']+=partida.planned_amount                       
            res_line['total']={
                'planned_amount': 0.00,
                'suplemento':0.00,
                'disminucion':0.00,
                'traspaso_aumento':0.00,
                'traspaso_disminucion':0.00,
                'code':0,
                'code_aux':0,
                'final':0,
                'total':0.00,
            }
            values=res_line.itervalues()
            for line_totales in values:
                if not 'level' in line_totales and line_totales['final']==True:
                    res_line['total']['planned_amount']+=line_totales['planned_amount']            
                    res_line['total']['suplemento']+=line_totales['suplemento']
                    res_line['total']['disminucion']+=line_totales['disminucion']
                    res_line['total']['traspaso_aumento']+=line_totales['traspaso_aumento']
                    res_line['total']['traspaso_disminucion']+=line_totales['traspaso_disminucion']
                    res_line['total']['total']+=line_totales['total']                                                            
            return res_line

report_sxw.report_sxw('report.rf.programa','rf.programa',
                      'gt_project_project/report/rf_programa.mako',
                      parser=rf_programa)

