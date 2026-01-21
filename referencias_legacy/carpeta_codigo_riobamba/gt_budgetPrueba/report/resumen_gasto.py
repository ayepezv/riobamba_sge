# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
import time
from report import report_sxw
from osv import fields, osv
from gt_tool import XLSWriter
import re
from tools import ustr
import operator

class resumen_gasto(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(resumen_gasto, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_budget_gp': self.get_budget_gp,
            'get_programa_name':self.get_programa_name,
            'get_programa_gp': self.get_programa_gp,
            '_vars': self._vars,
        })

    def _vars(self,resumen):  
        res = { }          
#        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
#        res['date']=today
#        res['date_from'] = self.datas['form']['date_from']
#        res['date_to'] = self.datas['form']['date_to']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
#        end = self.datas['form']['date_to']
#        res['end']=end.upper()
        return res 

    def get_programa_name(self, p_id):
        program_obj = self.pool.get('project.program')
        aux = ''
        programa = program_obj.browse(self.cr, self.uid, p_id)
        aux = programa.sequence + ' - ' + programa.name
        return aux


    def get_programa_gp(self, poa):
        programa_list = []
        sql = '''select id from project_program where id in (select program_id from project_project where type_budget='gasto') order by sequence'''
        self.cr.execute(sql)
        result = self.cr.fetchall()
        for id_p in result:
            programa_list.append(id_p[0])
        return programa_list

    def get_budget_gp(self, program_id,text,text1):
        budget_item_obj = self.pool.get('budget.item')
        poa_id = self.datas['form']['poa_id']
        budget_ids_1 = budget_item_obj.search(self.cr, self.uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text+"%")])
        budget_ids_2 = []
        if text1!='0':
            budget_ids_2 = budget_item_obj.search(self.cr, self.uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text1+"%")])
        context = {}
        total = 0 
        budget_ids = budget_ids_1 + budget_ids_2
        for budget_id in budget_ids:
            budget = budget_item_obj.browse(self.cr, self.uid, budget_id,context)
            total += budget.planned_amount
        return total

report_sxw.report_sxw('report.resumen_gasto',
                       'resumen.gasto.wizard', 
                       'addons/gt_budget/report/resumen_gasto.mako',
                       parser=resumen_gasto,
                       header=True)

class resumen_gasto_final(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(resumen_gasto_final, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_budget_gp_final': self.get_budget_gp_final,
            'get_programa_name_final':self.get_programa_name_final,
            'get_programa_gp_final': self.get_programa_gp_final,
            '_vars': self._vars,
        })

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_to'] = self.datas['form']['date_to']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['end']=end.upper()
        return res 

    def get_programa_name_final(self, p_id):
        program_obj = self.pool.get('project.program')
        aux = ''
        programa = program_obj.browse(self.cr, self.uid, p_id)
        aux = programa.sequence + ' - ' + programa.name
        return aux


    def get_programa_gp_final(self, poa):
        programa_list = []
        sql = '''select id from project_program where id in (select program_id from project_project where type_budget='gasto') order by sequence'''
        self.cr.execute(sql)
        result = self.cr.fetchall()
        for id_p in result:
            programa_list.append(id_p[0])
        return programa_list

    def get_budget_gp_final(self, program_id,text,text1):
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        poa_id = self.datas['form']['poa_id']
        budget_item_obj = self.pool.get('budget.item')
        budget_ids_1 = budget_item_obj.search(self.cr, self.uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text+"%")])
        budget_ids_2 = []
        if text1!='0':
            budget_ids_2 = budget_item_obj.search(self.cr, self.uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text1+"%")])
        context = {}
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}
        total = 0 
        budget_ids = budget_ids_1 + budget_ids_2
        for line in budget_item_obj.browse(self.cr,self.uid,budget_ids, context=context):
            total += line.codif_amount
        return total

report_sxw.report_sxw('report.resumen_gasto_final',
                       'resumen.gasto.final.wizard', 
                       'addons/gt_budget/report/resumen_gasto_final.mako',
                       parser=resumen_gasto_final,
                       header=True)

class resumen_gasto_comprometido(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(resumen_gasto_comprometido, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_budget_gp_comprometido': self.get_budget_gp_comprometido,
            'get_budget_gp_comprometido_field': self.get_budget_gp_comprometido_field,
            'get_programa_name_comprometido':self.get_programa_name_comprometido,
            'get_programa_gp_comprometido': self.get_programa_gp_comprometido,
            '_vars': self._vars,
        })

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_to'] = self.datas['form']['date_to']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['end']=end.upper()
        return res 

    def get_programa_name_comprometido(self, p_id):
        program_obj = self.pool.get('project.program')
        aux = ''
        programa = program_obj.browse(self.cr, self.uid, p_id)
        aux = programa.sequence + ' - ' + programa.name
        return aux


    def get_programa_gp_comprometido(self, poa):
        programa_list = []
        sql = '''select id from project_program where id in (select program_id from project_project where type_budget='gasto') order by sequence'''
        self.cr.execute(sql)
        result = self.cr.fetchall()
        for id_p in result:
            programa_list.append(id_p[0])
        return programa_list

    def get_budget_gp_comprometido_field(self, text,text1,campo):
        poa_id = self.datas['form']['poa_id']
        budget_item_obj = self.pool.get('budget.item')
        budget_ids_1 = budget_item_obj.search(self.cr, self.uid, [('code_aux','=like',text+"%"),('poa_id','=',poa_id)])
        budget_ids_2 = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        if text1!='0':
            budget_ids_2 = budget_item_obj.search(self.cr, self.uid, [('code_aux','=like',text1+"%"),('poa_id','=',poa_id)])
        context = {}
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}
        total = 0 
        budget_ids = budget_ids_1 + budget_ids_2
        for line in budget_item_obj.browse(self.cr,self.uid,budget_ids, context=context):
            if campo=='planned_amount':
                total += line.planned_amount
            elif campo=='codif_amount':
                total += line.codif_amount
            elif campo=='commited_amount':
                total += line.commited_amount
            elif campo=='paid_amount':
                total += line.paid_amount
            elif campo=='commited_balance':
                total += line.commited_balance
        return total

    def get_budget_gp_comprometido(self, program_id,text,text1):
        budget_item_obj = self.pool.get('budget.item')
        poa_id = self.datas['form']['poa_id']
        budget_ids_1 = budget_item_obj.search(self.cr, self.uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text+"%")])
        budget_ids_2 = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        poa_id = self.datas['form']['poa_id']
        if text1!='0':
            budget_ids_2 = budget_item_obj.search(self.cr, self.uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text1+"%")])
        context = {}
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}
        total = 0 
        budget_ids = budget_ids_1 + budget_ids_2
        for line in budget_item_obj.browse(self.cr,self.uid,budget_ids, context=context):
            total += line.commited_amount
        return total

report_sxw.report_sxw('report.resumen_gasto_comprometido',
                       'resumen.gasto.comprometido.wizard', 
                       'addons/gt_budget/report/resumen_gasto_comprometido.mako',
                       parser=resumen_gasto_comprometido,
                       header=True)


class resumen_gasto_pagado(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(resumen_gasto_pagado, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_budget_gp_pagado': self.get_budget_gp_pagado,
            'get_budget_gp_pagado_field': self.get_budget_gp_pagado_field,
            'get_programa_name_pagado':self.get_programa_name_pagado,
            'get_programa_gp_pagado': self.get_programa_gp_pagado,
            '_vars': self._vars,
        })

    def _vars(self,resumen):  
        res = { }          
        begin = self.datas['form']['date_from']
        user=ustr(self.pool.get('res.users').browse(self.cr,self.uid,self.uid).name.upper())
        res['user']=user
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today
        res['date_from'] = self.datas['form']['date_from']
        res['date_to'] = self.datas['form']['date_to']
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['end']=end.upper()
        return res

    def get_programa_name_pagado(self, p_id):
        program_obj = self.pool.get('project.program')
        aux = ''
        programa = program_obj.browse(self.cr, self.uid, p_id)
        aux = programa.sequence + ' - ' + programa.name
        return aux


    def get_programa_gp_pagado(self, poa):
        programa_list = []
        sql = '''select id from project_program where id in (select program_id from project_project where type_budget='gasto') order by sequence'''
        self.cr.execute(sql)
        result = self.cr.fetchall()
        for id_p in result:
            programa_list.append(id_p[0])
        return programa_list

    def get_budget_gp_pagado_field(self, text,text1,campo):
        poa_id = self.datas['form']['poa_id']
        budget_item_obj = self.pool.get('budget.item')
        budget_ids_1 = budget_item_obj.search(self.cr, self.uid, [('code_aux','=like',text+"%"),('poa_id','=',poa_id)])
        budget_ids_2 = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        if text1!='0':
            budget_ids_2 = budget_item_obj.search(self.cr, self.uid, [('code_aux','=like',text1+"%"),('poa_id','=',poa_id)])
        context = {}
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}
        total = 0 
        budget_ids = budget_ids_1 + budget_ids_2
        for line in budget_item_obj.browse(self.cr,self.uid,budget_ids, context=context):
            if campo=='planned_amount':
                total += line.planned_amount
            elif campo=='commited_amount':
                total += line.commited_amount
            elif campo=='codif_amount':
                total += line.codif_amount
            elif campo=='paid_amount':
                total += line.paid_amount
            elif campo=='commited_balance':
                total += line.commited_balance
            elif campo=='avai_amount':
                total += line.avai_amount
        return total

    def get_budget_gp_pagado(self, program_id,text,text1):
        budget_item_obj = self.pool.get('budget.item')
        poa_id = self.datas['form']['poa_id']
        budget_ids_1 = budget_item_obj.search(self.cr, self.uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text+"%")])
        budget_ids_2 = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        poa_id = self.datas['form']['poa_id']
        if text1!='0':
            budget_ids_2 = budget_item_obj.search(self.cr, self.uid, [('poa_id','=',poa_id),('program_id','=',program_id),('code_aux','=like',text1+"%")])
        context = {}
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}
        total = 0 
        budget_ids = budget_ids_1 + budget_ids_2
        for line in budget_item_obj.browse(self.cr,self.uid,budget_ids, context=context):
            total += line.paid_amount
        return total

report_sxw.report_sxw('report.resumen_gasto_pagado',
                       'resumen.gasto.pagado.wizard', 
                       'addons/gt_budget/report/resumen_gasto_pagado.mako',
                       parser=resumen_gasto_pagado,
                       header=True)

