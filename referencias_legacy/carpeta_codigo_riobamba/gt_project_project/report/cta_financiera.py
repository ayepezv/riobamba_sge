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

class cta_financiera(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cta_financiera, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            '_get_totales':self._get_totales,
            '_get_code':self._get_code,
            '_get_financia':self._get_financia,
        })

    def _get_financia(self, opc,campo):
        certificate_line_obj = self.pool.get('budget.certificate.line')
        financia_obj = self.pool.get('partida.financia')
        financiera_obj = self.pool.get('budget.financiamiento')
        c_b_lines_obj = self.pool.get('budget.item')
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        poa_id = self.datas['form']['poa_id']
        if opc=='SC':
            financiera_ids = financiera_obj.search(self.cr, self.uid, [('sc','=','SC')])
        else:
            financiera_ids = financiera_obj.search(self.cr, self.uid, [('sc','!=','SC')])
        partidas_sc = [] #post
        financia_sc_ids = financia_obj.search(self.cr, self.uid, [('financiera_id','in',financiera_ids)])
        if financia_sc_ids:
            for financia_sc_id in financia_sc_ids:
                financia_sc = financia_obj.browse(self.cr, self.uid, financia_sc_id)
                if not financia_sc.budget_id.id in partidas_sc:
                    partidas_sc.append(financia_sc.budget_id.id)
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}            
        ids_lines_sc=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',poa_id),('budget_post_id','in',partidas_sc)])
        recaudado_sc = gastado_sc = saldo_sc = 0
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines_sc, context=context):
            recaudado_sc += line.paid_amount
        #Gastado de los compromisos
        certificate_line_ids = certificate_line_obj.search(self.cr, self.uid, [('financia_id','in',financiera_ids),
                                                                     ('date_commited','>=',date_from),('date_commited','<=',date_to)])
        if certificate_line_ids:
            for certificate_line_id in certificate_line_ids:
                certificate_line = certificate_line_obj.browse(self.cr, self.uid, certificate_line_id)
                gastado_sc += certificate_line.amount_commited
        saldo_sc = recaudado_sc - gastado_sc
        if campo=='recaudado':
            return recaudado_sc
        else:
            return gastado_sc

    def set_context(self, objects, data, ids, report_type=None):
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['poa_id']),
                                                         ('type_budget','in',('ingreso','gasto'))])
        if ids_lines:
            objects=self.pool.get('budget.poa').browse(self.cr,self.uid,data['form']['poa_id'])         
            return super(cta_financiera, self).set_context([objects], data, ids, report_type=report_type)
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
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['end']=end.upper()
        return res 
        
    def _get_code(self,resumen):
        result = []
        financia_obj = self.pool.get('budget.financiamiento')
        lista_subtotal = []
        financia_ids = financia_obj.search(self.cr, self.uid, [],order='name')
        if financia_ids:
            for financia_id in financia_ids:
                financiera = financia_obj.browse(self.cr, self.uid, financia_id)
                if not financiera.name[0:2] in lista_subtotal:
                    lista_subtotal.append(financiera.name[0:2])
        return lista_subtotal
            
    def _get_totales(self,resumen,code):
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        poa_id = self.datas['form']['poa_id']
        c_b_lines_obj = self.pool.get('budget.item')
        financia_obj = self.pool.get('budget.financiamiento')
        partida_fin_obj = self.pool.get('partida.financia')
        #itera por cuenta financiera catalogo
        lista_subtotal = []
#        financia_ids = financia_obj.search(self.cr, self.uid, [('code','=',code)])
        financia_ids = financia_obj.search(self.cr, self.uid, [])
        ids_lines_ingreso = []
        if financia_ids:
            for financia_id in financia_ids:
                financiera = financia_obj.browse(self.cr, self.uid, financia_id)
                #busco partidas de ingreso que financia la cuenta
                if not financiera.name[0:2]==code:
                    continue
                partida_fin_ids = partida_fin_obj.search(self.cr, self.uid, [('financiera_id','=',financia_id)])
                res_line[financia_id] = {
                    'code':financiera.name,
                    'name': financiera.desc,
                    'planned_amount':0,
                    'reform':0,
                    'codificado':0,
                    'ingresos':0,
                    'gastos':0,
                    'saldo':0,
                    'descripcion':financiera.desc_report,
                }
                ids_lines_ingreso = []
                aux_sc = 0
                for record in partida_fin_obj.read(self.cr, self.uid, partida_fin_ids, ['budget_id','monto','reforma','recaudado'], context):
                    #aqui en la lista hay q pasar ids de budget item no de post
                    res_line[financia_id]['planned_amount'] += record['monto']
                    aux_sc += record['monto']
                    res_line[financia_id]['reform'] += record['reforma']
                    res_line[financia_id]['codificado'] += (record['monto']+record['reforma'])
                    if not record['budget_id']:
                        continue
                    item_ids = c_b_lines_obj.search(self.cr, self.uid, [('budget_post_id','=',record['budget_id'][0]),('poa_id','=',poa_id)])
                    if item_ids:
                        ids_lines_ingreso.append(item_ids[0]) #tengo las de ingreso que financian esa cuenta no si va solo la cero o todo
                    context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}           
                    planed = 0
                aux_ingreso = 0
                #preguntar si es SC pone lo mismo del inicial
                if financiera.desc:
                    if financiera.desc[0:2]=='SC':
                        aux_ingreso = aux_sc
                        res_line[financia_id]['ingresos']=aux_sc
                    else:
                        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines_ingreso, context=context):
                            res_line[financia_id]['ingresos']+=line.paid_amount
                            aux_ingreso += line.paid_amount
                else:
                    for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines_ingreso, context=context):
                        res_line[financia_id]['ingresos']+=line.paid_amount
                        aux_ingreso += line.paid_amount
                #gastos tomo los certificate_line o los move_line de esa cuenta financiera
                sql = "SELECT budget_certificate_line.id,budget_certificate_line.amount,budget_certificate_line.amount_certified,budget_certificate_line.amount_commited,budget_id FROM budget_certificate_line,budget_certificate \
                WHERE budget_certificate.state='commited' and budget_certificate_line.certificate_id=budget_certificate.id and financia_id = %s \
                AND budget_certificate.date_commited is not Null and budget_certificate.date_commited>='%s' and budget_certificate.date_commited<='%s'" % (financia_id,date_from, date_to)
                self.cr.execute(sql)
                data = self.cr.fetchall()
                pagado_aux = 0
                for moveline in data:
                    pagado_aux += moveline[3]
                res_line[financia_id]['gastos'] = pagado_aux
                res_line[financia_id]['saldo'] = aux_ingreso - pagado_aux
        values=res_line.itervalues()
        return res_line

report_sxw.report_sxw('report.cta_financiera',
                       'cta.financiera', 
                       'gt_project_project/report/cta_financiera.mako',
                       parser=cta_financiera,
                       header=True)


class cta_financierac(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cta_financierac, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.cta_financierac',
                       'cta.financiera', 
                       'gt_project_project/report/cta_financierac.mako',
                       parser=cta_financierac,
                       header=True)


class cta_financierac_gastado(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cta_financierac_gastado, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.cta_financierac_gastado',
                       'cta.financiera.gastado', 
                       'gt_project_project/report/cta_financierac_gastado.mako',
                       parser=cta_financierac_gastado,
                       header=True)


class cta_financiera_gastado(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cta_financiera_gastado, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_vars': self._vars,
            '_get_totales':self._get_totales,
            '_get_code':self._get_code,
            '_get_financia':self._get_financia,
        })

    def _get_financia(self, opc,campo):
        certificate_line_obj = self.pool.get('budget.certificate.line')
        financia_obj = self.pool.get('partida.financia')
        financiera_obj = self.pool.get('budget.financiamiento')
        c_b_lines_obj = self.pool.get('budget.item')
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        poa_id = self.datas['form']['poa_id']
        if opc=='SC':
            financiera_ids = financiera_obj.search(self.cr, self.uid, [('sc','=','SC')])
        else:
            financiera_ids = financiera_obj.search(self.cr, self.uid, [('sc','!=','SC')])
        partidas_sc = [] #post
        financia_sc_ids = financia_obj.search(self.cr, self.uid, [('financiera_id','in',financiera_ids)])
        if financia_sc_ids:
            for financia_sc_id in financia_sc_ids:
                financia_sc = financia_obj.browse(self.cr, self.uid, financia_sc_id)
                if not financia_sc.budget_id.id in partidas_sc:
                    partidas_sc.append(financia_sc.budget_id.id)
        context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}            
        ids_lines_sc=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',poa_id),('budget_post_id','in',partidas_sc)])
        recaudado_sc = gastado_sc = saldo_sc = 0
        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines_sc, context=context):
            recaudado_sc += line.paid_amount
        #Gastado de los compromisos
        sql = "SELECT debit,credit from account_move_line where financia_id in %s and budget_accrued=True and state='valid' and date>='%s' and date<='%s'" % (tuple(financiera_ids),date_from, date_to)
        self.cr.execute(sql)
        data = self.cr.fetchall()
        pagado_aux = 0
        for moveline in data:
            aux_pago = 0
            if moveline[0]:
                aux_pago = moveline[0]
            elif moveline[1]:
                aux_pago = moveline[1]
            gastado_sc += aux_pago
        saldo_sc = recaudado_sc - gastado_sc
        if campo=='recaudado':
            return recaudado_sc
        else:
            return gastado_sc

    def set_context(self, objects, data, ids, report_type=None):
        c_b_lines_obj = self.pool.get('budget.item')
        ids_lines=c_b_lines_obj.search(self.cr,self.uid,[('poa_id','=',data['form']['poa_id']),
                                                         ('type_budget','in',('ingreso','gasto'))])
        if ids_lines:
            objects=self.pool.get('budget.poa').browse(self.cr,self.uid,data['form']['poa_id'])         
            return super(cta_financiera_gastado, self).set_context([objects], data, ids, report_type=report_type)
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
        today=time.strftime('%Y-%m-%d %H:%M:%S')        
        res['date']=today                                            
        res['begin']=begin.upper()
        end = self.datas['form']['date_to']
        res['end']=end.upper()
        return res 
        
    def _get_code(self,resumen):
        result = []
        financia_obj = self.pool.get('budget.financiamiento')
        lista_subtotal = []
        financia_ids = financia_obj.search(self.cr, self.uid, [],order='name')
        if financia_ids:
            for financia_id in financia_ids:
                financiera = financia_obj.browse(self.cr, self.uid, financia_id)
                if not financiera.name[0:2] in lista_subtotal:
                    lista_subtotal.append(financiera.name[0:2])
        return lista_subtotal
            
    def _get_totales(self,resumen,code):
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        poa_id = self.datas['form']['poa_id']
        c_b_lines_obj = self.pool.get('budget.item')
        financia_obj = self.pool.get('budget.financiamiento')
        partida_fin_obj = self.pool.get('partida.financia')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        move_obj = self.pool.get('account.move')
        #itera por cuenta financiera catalogo
        lista_subtotal = []
#        financia_ids = financia_obj.search(self.cr, self.uid, [('code','=',code)])
        financia_ids = financia_obj.search(self.cr, self.uid, [])
        ids_lines_ingreso = []
        if financia_ids:
            for financia_id in financia_ids:
                financiera = financia_obj.browse(self.cr, self.uid, financia_id)
                #busco partidas de ingreso que financia la cuenta
                if not financiera.name[0:2]==code:
                    continue
                partida_fin_ids = partida_fin_obj.search(self.cr, self.uid, [('financiera_id','=',financia_id)])
                res_line[financia_id] = {
                    'code':financiera.name,
                    'name': financiera.desc,
                    'planned_amount':0,
                    'reform':0,
                    'codificado':0,
                    'ingresos':0,
                    'gastos':0,
                    'saldo':0,
                    'descripcion':financiera.desc_report,
                }
                ids_lines_ingreso = []
                aux_sc = 0
                for record in partida_fin_obj.read(self.cr, self.uid, partida_fin_ids, ['budget_id','monto','reforma','recaudado','porcentaje'], context):
                    #aqui en la lista hay q pasar ids de budget item no de post
                    res_line[financia_id]['planned_amount'] += record['monto']
                    aux_sc += record['monto']
                    res_line[financia_id]['reform'] += record['reforma']
                    res_line[financia_id]['codificado'] += (record['monto']+record['reforma'])
                    item_ids = c_b_lines_obj.search(self.cr, self.uid, [('budget_post_id','=',record['budget_id'][0]),('poa_id','=',poa_id)])
                    if item_ids:
                        ids_lines_ingreso.append(item_ids[0]) #tengo las de ingreso que financian esa cuenta no si va solo la cero o todo
                    context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}           
                    planed = 0
                aux_ingreso = 0
                #preguntar si es SC pone lo mismo del inicial
                if financiera.desc:
                    if financiera.desc[0:2]=='SC':
                        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines_ingreso, context=context):
                            partida_ids_porcen = partida_fin_obj.search(self.cr, self.uid, [('financiera_id','=',financiera.id),
                                                                                            ('budget_id','=',line.budget_post_id.id)])
                            if partida_ids_porcen:
                                partida_fin = partida_fin_obj.browse(self.cr, self.uid, partida_ids_porcen[0])
                                porcentaje = partida_fin.porcentaje
                                res_line[financia_id]['ingresos']+=partida_fin.monto
                                aux_ingreso += partida_fin.monto
                    else:
                        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines_ingreso, context=context):
                            #solo el porcentaje
                            partida_ids_porcen = partida_fin_obj.search(self.cr, self.uid, [('financiera_id','=',financiera.id),
                                                                                            ('budget_id','=',line.budget_post_id.id)])
                            if partida_ids_porcen:
                                partida_fin = partida_fin_obj.browse(self.cr, self.uid, partida_ids_porcen[0])
                                porcentaje = partida_fin.porcentaje
                                if porcentaje!=0:
                                    aux_porcentaje = (line.paid_amount*porcentaje)/100.00
                                    res_line[financia_id]['ingresos']+=aux_porcentaje
                                    aux_ingreso += aux_porcentaje
                                else:
                                    res_line[financia_id]['ingresos']+=line.paid_amount
                                    aux_ingreso += line.paid_amount
                else:
                    for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines_ingreso, context=context):
                        res_line[financia_id]['ingresos']+=line.paid_amount
                        aux_ingreso += line.paid_amount
                #gastos tomo los certificate_line o los move_line de esa cuenta financiera
                #sql = "SELECT debit,credit from account_move_line where financia_id= %s and budget_accrued=True and state='valid' and date>='%s' and date<='%s'" % (financia_id,date_from, date_to)
                sql = "SELECT debit,credit from account_move_line where budget_id_cert in (select id from budget_certificate_line where financia_id=%s) and budget_accrued=True and state='valid' and date>='%s' and date<='%s'" % (financia_id,date_from, date_to)
                self.cr.execute(sql)
                data = self.cr.fetchall()
                pagado_aux = 0
                for moveline in data:
                    aux_pago = 0
                    if moveline[0]:
                        aux_pago = moveline[0]
                    elif moveline[1]:
                        aux_pago = moveline[1]
                    pagado_aux += aux_pago
                    #pronto pagos
                sql_pronto = "SELECT commited_amount,move_id from budget_item_migrated where financia_id= %s and date>='%s' and date<='%s' and is_pronto=True" % (financia_id,date_from, date_to)
                self.cr.execute(sql_pronto)
                data_pronto = self.cr.fetchall()
                pagado_aux_pronto = 0
                for movepronto in data_pronto:
                    pagado_aux_pronto += movepronto[0]
                res_line[financia_id]['gastos'] = pagado_aux + pagado_aux_pronto
                res_line[financia_id]['saldo'] = aux_ingreso - pagado_aux - pagado_aux_pronto
        values=res_line.itervalues()
        return res_line

    def _get_totales2(self,resumen,code):
        res = { }
        res_line = { }
        context = { }
        result = []
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']
        poa_id = self.datas['form']['poa_id']
        c_b_lines_obj = self.pool.get('budget.item')
        financia_obj = self.pool.get('budget.financiamiento')
        partida_fin_obj = self.pool.get('partida.financia')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        #itera por cuenta financiera catalogo
        lista_subtotal = []
#        financia_ids = financia_obj.search(self.cr, self.uid, [('code','=',code)])
        financia_ids = financia_obj.search(self.cr, self.uid, [])
        ids_lines_ingreso = []
        if financia_ids:
            for financia_id in financia_ids:
                financiera = financia_obj.browse(self.cr, self.uid, financia_id)
                #busco partidas de ingreso que financia la cuenta
                if not financiera.name[0:2]==code:
                    continue
                partida_fin_ids = partida_fin_obj.search(self.cr, self.uid, [('financiera_id','=',financia_id)])
                res_line[financia_id] = {
                    'code':financiera.name,
                    'name': financiera.desc,
                    'planned_amount':0,
                    'reform':0,
                    'codificado':0,
                    'ingresos':0,
                    'gastos':0,
                    'saldo':0,
                    'descripcion':financiera.desc_report,
                }
                ids_lines_ingreso = []
                aux_sc = 0
                for record in partida_fin_obj.read(self.cr, self.uid, partida_fin_ids, ['budget_id','monto','reforma','recaudado'], context):
                    #aqui en la lista hay q pasar ids de budget item no de post
                    res_line[financia_id]['planned_amount'] += record['monto']
                    aux_sc += record['monto']
                    res_line[financia_id]['reform'] += record['reforma']
                    res_line[financia_id]['codificado'] += (record['monto']+record['reforma'])
                    item_ids = c_b_lines_obj.search(self.cr, self.uid, [('budget_post_id','=',record['budget_id'][0]),('poa_id','=',poa_id)])
                    if item_ids:
                        ids_lines_ingreso.append(item_ids[0]) #tengo las de ingreso que financian esa cuenta no si va solo la cero o todo
                    context = {'by_date':True,'date_start': date_from, 'date_end': date_to,'poa_id':poa_id}           
                    planed = 0
                aux_ingreso = 0
                #preguntar si es SC pone lo mismo del inicial
                if financiera.desc:
                    if financiera.desc[0:2]=='SC':
                        aux_ingreso = aux_sc
                        res_line[financia_id]['ingresos']=aux_sc
                    else:
                        for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines_ingreso, context=context):
                            res_line[financia_id]['ingresos']+=line.paid_amount
                            aux_ingreso += line.paid_amount
                else:
                    for line in c_b_lines_obj.browse(self.cr,self.uid,ids_lines_ingreso, context=context):
                        res_line[financia_id]['ingresos']+=line.paid_amount
                        aux_ingreso += line.paid_amount
                #gastos tomo los certificate_line o los move_line de esa cuenta financiera
#                sql = "SELECT budget_certificate_line.id,budget_certificate_line.amount,budget_certificate_line.amount_certified,budget_certificate_line.amount_commited,budget_id FROM budget_certificate_line,budget_certificate \
#                WHERE budget_certificate.state='commited' and budget_certificate_line.certificate_id=budget_certificate.id and financia_id = %s \
#                AND budget_certificate.date_commited is not Null and budget_certificate.date_commited>='%s' and budget_certificate.date_commited<='%s'" % (financia_id,date_from, date_to)
                sql = "SELECT budget_certificate_line.id FROM budget_certificate_line,budget_certificate \
                WHERE budget_certificate.state='commited' and budget_certificate_line.certificate_id=budget_certificate.id and financia_id = %s \
                AND budget_certificate.date_commited is not Null and budget_certificate.date_commited>='%s' and budget_certificate.date_commited<='%s'" % (financia_id,date_from, date_to)
                self.cr.execute(sql)
                data = self.cr.fetchall()
                pagado_aux = 0
                for moveline in data:
                    certificate_line = certificate_line_obj.browse(self.cr, self.uid, moveline[0])
                    pagado_aux += certificate_line.budget_accrued
                res_line[financia_id]['gastos'] = pagado_aux
                res_line[financia_id]['saldo'] = aux_ingreso - pagado_aux
        values=res_line.itervalues()
        return res_line

report_sxw.report_sxw('report.cta_financiera_gastado',
                       'cta.financiera.gastado', 
                       'gt_project_project/report/cta_financiera_gastado.mako',
                       parser=cta_financiera_gastado,
                       header=True)

