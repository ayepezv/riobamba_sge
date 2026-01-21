# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Gnuthink Software Cia. Ltda.
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
from operator import itemgetter

from report import report_sxw
from osv import osv
import pooler

class voucher(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(voucher, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00   
        self.sum_acurred = 0.00
        self.sum_paid = 0.00     
        self.localcontext.update({
            'time': time,
            'get_analytic_lines': self.get_analytic_lines,
            'get_user': self.get_user,
            'get_lines': self.get_lines,
            'get_budget': self.get_budget,
            'suma_debit': self.suma_debit,
            'suma_credit': self.suma_credit,
            'get_move_lines': self.get_move_lines,
            'suma_acurred': self.suma_acurred,
            'suma_paid': self.suma_paid,
        })

    def suma_debit(self):
        return self.sum_debit or 0.00

    def suma_credit(self):
        return self.sum_credit or 0.00
    
    def suma_acurred(self):
        return self.sum_acurred or 0.00
    
    def suma_paid(self):
        return self.sum_paid or 0.00
    
    def set_context(self, objects, data, ids, report_type=None):             
        objects=[self.pool.get('account.voucher').browse(self.cr,self.uid,data['form']['voucher_id'][0])]         
        date_voucher=objects[0].date
        date_invoice=objects[0].line_ids[0].date_original
        if date_voucher==date_invoice:            
            return super(voucher, self).set_context(objects, data, ids, report_type=report_type)
        else:           
            raise osv.except_osv('Error', 'Debe imprimir los comprobantes desde asientos contables')
            
    def get_budget(self, advance):
        lines = []
        self.sum_acurred=self.sum_paid=self.credit=self.sum_debit=0.0
        data = { }
        '''
        Para obtener la aplicacion presupuestaria de la factura o del doc por pagar
        * Se compara cuando que tenga los check de devengado y recaudado para agrupar en una sola linea
        * se deve validar si el pago se hace en la misma fecha se integra el comprobante 
          si es realizado en otra fecha debe imprimir separado
        '''       
        #obtiene la partida de los movimientos del voucher
        for line in advance.move_ids:
            #condicion cuando solo esta el devengado
            if line.budget_id and line.budget_accrued==True and line.budget_paid==False:                                
                budget = line.budget_id.budget_line_id.general_budget_id
                code_project=line.budget_id.project_id.code
                if line.credit!=0:
                    acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                    planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                    planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                    if planed[0].task_id.id:
                        task=str(planed[0].task_id.id)
                    else: 
                        task='--'
                    if data.has_key(budget.code+code_project)==False:
                        data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': line.credit,'amount_paid': 0,'code_completo':code_project+"."+task+"."+budget.code}
                        self.sum_acurred += line.credit
                    else:
                        data[budget.code+code_project]['code']=budget.code+code_project
                        data[budget.code+code_project]['name']=budget.name
                        data[budget.code+code_project]['amount_acurred']+=line.credit
                        data[budget.code+code_project]['amount_paid']+=0
                        data[budget.code+code_project]['code_completo']=code_project+"."+task+"."+budget.code
                        self.sum_acurred += line.credit
                if line.debit!=0:
                    acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                    planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                    planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                    if planed[0].task_id.id:
                        task=str(planed[0].task_id.id)
                    else: 
                        task='--'
                    if data.has_key(budget.code+code_project)==False:
                        data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': line.debit,'amount_paid': 0,'code_completo':code_project+"."+task+"."+budget.code}
                        self.sum_acurred += line.debit
                    else:
                        data[budget.code+code_project]['code']=budget.code+code_project
                        data[budget.code+code_project]['name']=budget.name
                        data[budget.code+code_project]['amount_acurred']+=line.debit
                        data[budget.code+code_project]['amount_paid']+=0
                        data[budget.code+code_project]['code_completo']=code_project+"."+task+"."+budget.code
                        self.sum_acurred += line.debit
            #condicion cuando solo esta el recaudado
            if line.budget_id and line.budget_accrued==False and line.budget_paid==True:        
                budget = line.budget_id.budget_line_id.general_budget_id
                code_project=line.budget_id.project_id.code      
                print "codigo2222",code_project                                
                if line.reconcile_id.id:      
                    move_fac = self.pool.get('account.move.line').search(self.cr,self.uid,[('reconcile_id','=',line.reconcile_id.id),('id','!=',line.id),('invoice','ilike','')])
                    if move_fac:
                        move_fac_obj=self.pool.get('account.move.line').browse(self.cr,self.uid,move_fac[0])                    
                else:                  
                    move_fac = self.pool.get('account.move.line').search(self.cr,self.uid,[('reconcile_partial_id','=',line.reconcile_partial_id.id),('invoice','ilike','')])
                    if move_fac:
                        move_fac_obj=self.pool.get('account.move.line').browse(self.cr,self.uid,move_fac[0])                
                if move_fac and move_fac_obj.invoice:
                    total_fac=move_fac_obj.invoice.amount_total
                    id_voucher=self.pool.get('account.voucher').search(self.cr,self.uid,[('id','=',advance.id)])
                    total_voucher=self.pool.get('account.voucher').browse(self.cr,self.uid,id_voucher)[0].amount                   
                    for line_inv in move_fac_obj.invoice.invoice_line:
                        print line_inv
                        amount_tax=0
                        budget=line_inv.budget_id.budget_line_id.general_budget_id
                        code_project=line_inv.budget_id.project_id.code 
                        acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                        planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                        planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)                        
                        if planed[0].task_id.id:
                            task=str(planed[0].task_id.id)
                        else:
                            task='--'         
                        if line_inv.price_total!=0:
                            if total_fac==total_voucher:
                                paid=line_inv.price_total
                            else: 
                                for tax_id in line_inv.invoice_line_tax_id:
                                    if str(tax_id.tax_group).find('ret')!=-1:
                                        amount_tax+=tax_id.amount    
                                if total_fac==total_voucher:                                
                                    paid=line_inv.price_total
                                else:
                                    print "no es ighghgual"                                
                                    porcentaje=((total_voucher*100)/(total_fac))/100  
                                    paid=(line_inv.price_total+(line_inv.price_subtotal*amount_tax))*porcentaje
                        else:
                            for tax_id in line_inv.invoice_line_tax_id:
                                if str(tax_id.tax_group).find('ret')!=-1:
                                    amount_tax+=tax_id.amount    
                            if total_fac==total_voucher:                                
                                paid=line_inv.price_subtotal+(line_inv.price_subtotal*amount_tax)
                            else:
                                print "no es ighghgual"
                                porcentaje=((total_voucher*100)/(total_fac))/100  
                                paid=(line_inv.price_subtotal+(line_inv.price_subtotal*amount_tax))*porcentaje
                                                                                
                        if data.has_key(budget.code+code_project)==False:
                            data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': 0,'amount_paid': paid,'code_completo':code_project+"."+task+"."+budget.code}
                            self.sum_paid += paid
                        else:
                            data[budget.code+code_project]['code']=budget.code+code_project
                            data[budget.code+code_project]['name']=budget.name
                            data[budget.code+code_project]['amount_acurred']+=0
                            data[budget.code+code_project]['amount_paid']+=paid
                            data[budget.code+code_project]['code_completo']=code_project+"."+task+"."+budget.code
                            self.sum_paid += paid
                    break
                else:                                                                                            
                    if line.credit!=0:
                        acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                        planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                        planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                        if planed[0].task_id.id:
                            task=str(planed[0].task_id.id)
                        else:
                            task='--'                  
                        if data.has_key(budget.code+code_project)==False:
                            data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': 0,'amount_paid': line.credit,'code_completo':code_project+"."+task+"."+budget.code}
                            self.sum_paid += line.credit
                        else:
                            data[budget.code+code_project]['code']=budget.code+code_project
                            data[budget.code+code_project]['name']=budget.name
                            data[budget.code+code_project]['amount_acurred']+=0
                            data[budget.code+code_project]['amount_paid']+=line.credit
                            data[budget.code+code_project]['code_completo']=code_project+"."+task+"."+budget.code
                            self.sum_paid += line.credit
                    if line.debit!=0:
                        acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                        planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                        planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                        if planed[0].task_id.id:
                            task=str(planed[0].task_id.id)
                        else:
                            task='--'
                        if data.has_key(budget.code+code_project)==False:
                            data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': 0,'amount_paid': line.debit,'code_completo':code_project+"."+task+"."+budget.code}
                            self.sum_paid += line.debit
                        else:
                            data[budget.code+code_project]['code']=budget.code+code_project
                            data[budget.code+code_project]['name']=budget.name
                            data[budget.code+code_project]['amount_acurred']+=0
                            data[budget.code+code_project]['amount_paid']+=line.debit
                            data[budget.code+code_project]['code_completo']=code_project+"."+task+"."+budget.code
                            self.sum_paid += line.debit
            #cuando esta el devengado y el recaudado
            if line.budget_id and line.budget_accrued==True and line.budget_paid==True:        
                budget = line.budget_id.budget_line_id.general_budget_id
                code_project=line.budget_id.project_id.code
                if line.credit!=0:
                    acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                    planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                    planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                    if planed[0].task_id.id:
                        task=str(planed[0].task_id.id)
                    else: 
                        task='--'
                    if data.has_key(budget.code+code_project)==False:
                        data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': line.credit,'amount_paid': line.credit,'code_completo':code_project+"."+task+"."+budget.code}
                        self.sum_paid += line.credit
                        self.sum_acurred += line.credit
                if line.debit!=0:
                    acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                    planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                    planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                    if planed[0].task_id.id:
                        task=str(planed[0].task_id.id)
                    else: 
                        task='--'
                    if data.has_key(budget.code+code_project)==False:
                        data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': line.debit,'amount_paid': line.debit,'code_completo':code_project+"."+task+"."+budget.code}
                        self.sum_paid += line.debit
                        self.sum_acurred += line.debit
        #revisar si iterar en line_cr_ids, esta realcionado con una factura y obtiene la partidas del resgistro de la factura      
        line_vocher={}
        line_vocher1=[]              
        if advance.line_cr_ids:
            for line_cr in advance.line_cr_ids:
                if line_vocher.has_key(line_cr.move_line_id.move_id.id)==False:
                        line_vocher[line_cr.move_line_id.move_id.id]={'code':line_cr}
                        line_vocher1.append(line_cr)        
        lista=list(set(line_vocher1))                
        if lista:
            for line_cr in lista:
                if line_cr.move_line_id.move_id:
                    if line_cr.move_line_id.move_id.journal_id.type=='sale':
                        if line_cr.move_line_id.move_id.line_id:
                            for line in line_cr.move_line_id.move_id.line_id:
                                if line.budget_id and line.budget_accrued==True and line.budget_paid==False:    
                                    print "sssssssssssssssssssssssssssssssssssssssssssss"             
                                    budget = line.budget_id.budget_line_id.general_budget_id
                                    code_project=line.budget_id.project_id.code
                                    if line.credit!=0:
                                        acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                                        planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                                        planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                                        if planed[0].task_id.id:
                                            task=str(planed[0].task_id.id)
                                        else: 
                                            task='--'
                                        if data.has_key(budget.code+code_project)==False:
                                            data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': line.credit,'amount_paid': 0,'code_completo':code_project+"."+task+"."+budget.code}
                                            self.sum_acurred += line.credit
                                        else:
                                            data[budget.code+code_project]['code']=budget.code+code_project
                                            data[budget.code+code_project]['name']=budget.name
                                            data[budget.code+code_project]['amount_acurred']+=line.credit
                                            data[budget.code+code_project]['amount_paid']+=0
                                            data[budget.code+code_project]['code_completo']=code_project+"."+task+"."+budget.code
                                            self.sum_acurred += line.credit
                                    if line.debit!=0:
                                        acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                                        planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                                        planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                                        if planed[0].task_id.id:
                                            task=str(planed[0].task_id.id)
                                        else: 
                                            task='--'
                                        if data.has_key(budget.code+code_project)==False:
                                            data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': line.debit,'amount_paid': 0,'code_completo':code_project+"."+task+"."+budget.code}
                                            self.sum_acurred += line.debit
                                        else:
                                            data[budget.code+code_project]['code']=budget.code+code_project
                                            data[budget.code+code_project]['name']=budget.name
                                            data[budget.code+code_project]['amount_acurred']+=line.debit
                                            data[budget.code+code_project]['amount_paid']+=0
                                            data[budget.code+code_project]['code_completo']=code_project+"."+task+"."+budget.code
                                            self.sum_acurred += line.debit
                                if line.budget_id and line.budget_accrued==False and line.budget_paid==True:      
                                    print "sssssssssssssssssssssssssssssssssssssssssssss"  
                                    budget = line.budget_id.budget_line_id.general_budget_id
                                    code_project=line.budget_id.project_id.code
                                    if line.credit!=0:
                                        acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                                        planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                                        planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                                        if planed[0].task_id.id:
                                            task=str(planed[0].task_id.id)
                                        else: 
                                            task='--'
                                        if data.has_key(budget.code+code_project)==False:
                                            data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': 0,'amount_paid': line.credit,'code_completo':code_project+"."+task+"."+budget.code}
                                            self.sum_paid += line.credit
                                        else:
                                            data[budget.code+code_project]['code']=budget.code+code_project
                                            data[budget.code+code_project]['name']=budget.name
                                            data[budget.code+code_project]['amount_acurred']+=0
                                            data[budget.code+code_project]['amount_paid']+=line.credit
                                            data[budget.code+code_project]['code_completo']=code_project+"."+task+"."+budget.code
                                            self.sum_paid += line.credit
                                    if line.debit!=0:
                                        acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                                        planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                                        planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                                        if planed[0].task_id.id:
                                            task=str(planed[0].task_id.id)
                                        else: 
                                            task='--'
                                        if data.has_key(budget.code+code_project)==False:
                                            data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': 0,'amount_paid': line.debit,'code_completo':code_project+"."+task+"."+budget.code}
                                            self.sum_paid += line.debit
                                        else:
                                            data[budget.code+code_project]['code']=budget.code+code_project
                                            data[budget.code+code_project]['name']=budget.name
                                            data[budget.code+code_project]['amount_acurred']+=0
                                            data[budget.code+code_project]['amount_paid']+=line.debit
                                            data[budget.code+code_project]['code_completo']=code_project+"."+task+"."+budget.code
                                            self.sum_paid += line.debit
                                if line.budget_id and line.budget_accrued==True and line.budget_paid==True:        
                                    budget = line.budget_id.budget_line_id.general_budget_id
                                    code_project=line.budget_id.project_id.code
                                    if line.credit!=0:
                                        acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                                        planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                                        planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                                        if planed[0].task_id.id:
                                            task=str(planed[0].task_id.id)
                                        else: 
                                            task='--'
                                        if data.has_key(budget.code+code_project)==False:
                                            data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': line.credit,'amount_paid': line.credit,'code_completo':code_project+"."+task+"."+budget.code}
                                            self.sum_paid += line.credit
                                            self.sum_acurred += line.credit
                                    if line.debit!=0:
                                        acc_obj_id = self.pool.get('account.analytic.account').search(self.cr,self.uid,[('code','=',budget.code)])
                                        planed_cod=self.pool.get('project.budget.plan').search(self.cr,self.uid,[('acc_budget_id','in',acc_obj_id)])
                                        planed=self.pool.get('project.budget.plan').browse(self.cr,self.uid,planed_cod)
                                        if planed[0].task_id.id:
                                            task=str(planed[0].task_id.id)
                                        else: 
                                            task='--'
                                        if data.has_key(budget.code+code_project)==False:
                                            data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': line.debit,'amount_paid': line.debit,'code_completo':code_project+"."+task+"."+budget.code}
                                            self.sum_paid += line.debit
                                            self.sum_acurred += line.debit                                    
        values=data.itervalues()
        for line in values:
            lines.append(line)   
        lines = sorted(lines, key=itemgetter('amount_acurred','amount_paid','code'))
        
        if not lines:
            lines.append({'code':'*', 'name': 'SIN APLICACION'})
            return lines        
        return lines

    def get_move_lines(self, advance):
        lines = []
        for line in advance.move_ids:
            data = {'code': line.account_id.code, 'name': line.account_id.name, 'debit': line.debit, 'credit': line.credit}
            self.sum_debit += line.debit
            self.sum_credit += line.credit
            lines.append(data)        
        newlist = sorted(lines, key=itemgetter('credit','code'))
        return newlist        

    def get_lines(self, advance):   
        lines_data = []
        data_lines={}
        index=2
            
        for line in advance.move_ids:    
            if line.debit!=0 and line.credit==0:                        
                if data_lines.has_key(line.account_id.code)==False:                    
                    data_lines[line.account_id.code] = {'code': line.account_id.code, 'name': line.account_id.name, 'debit': line.debit, 'credit': 0}
                else:
                    data_lines[line.account_id.code]['code']=line.account_id.code
                    data_lines[line.account_id.code]['name']=line.account_id.name
                    data_lines[line.account_id.code]['debit']+=line.debit                   
            if line.credit!=0 and line.debit==0:
                if data_lines.has_key(line.account_id.code+'c')==False:
                    
                    data_lines[line.account_id.code+'c'] = {'code': line.account_id.code, 'name': line.account_id.name, 'debit': 0, 'credit': line.credit}
                else:
                    data_lines[line.account_id.code+'c']['code']=line.account_id.code
                    data_lines[line.account_id.code+'c']['name']=line.account_id.name
                    data_lines[line.account_id.code+'c']['credit']+=line.credit
           # data = {'code': line.account_id.code, 'name': line.account_id.name, 'debit': line.debit, 'credit': line.credit}
            self.sum_debit += line.debit
            self.sum_credit += line.credit
            #lines.append(data)
        #if advance.type == 'receipt':
         #   newlist = sorted(lines, key=itemgetter('credit','code'))
        #para obtener las lineas de la factura o del doc por cobrar        
        line_vocher={}
        line_vocher1=[]        
        if advance.line_cr_ids:
            for line_cr in advance.line_cr_ids:
                if line_vocher.has_key(line_cr.move_line_id.move_id.id)==False:
                        line_vocher[line_cr.move_line_id.move_id.id]={'code':line_cr}
                        line_vocher1.append(line_cr)        
        lista=list(set(line_vocher1))        
        if lista:
            for line_cr in lista:   
                if line_cr.move_line_id.move_id:
                    if line_cr.move_line_id.move_id.journal_id.type=='sale':
                        if line_cr.move_line_id.move_id.line_id:
                            for line in line_cr.move_line_id.move_id.line_id:    
                                if line.debit!=0 and line.credit==0:                        
                                    if data_lines.has_key(line.account_id.code)==False:
                                        
                                        data_lines[line.account_id.code] = {'code': line.account_id.code, 'name': line.account_id.name, 'debit': line.debit, 'credit': 0}
                                    else:
                                        data_lines[line.account_id.code]['code']=line.account_id.code
                                        data_lines[line.account_id.code]['name']=line.account_id.name
                                        data_lines[line.account_id.code]['debit']+=line.debit                    
                                if line.credit!=0 and line.debit==0:
                                    if data_lines.has_key(line.account_id.code+'c')==False:
                                        
                                        data_lines[line.account_id.code+'c'] = {'code': line.account_id.code, 'name': line.account_id.name, 'debit': 0, 'credit': line.credit}
                                    else:
                                        data_lines[line.account_id.code+'c']['code']=line.account_id.code
                                        data_lines[line.account_id.code+'c']['name']=line.account_id.name
                                        data_lines[line.account_id.code+'c']['credit']+=line.credit            
          #                      data = {'code': line.account_id.code, 'name': line.account_id.name, 'debit': line.debit, 'credit': line.credit}
                                self.sum_debit += line.debit
                                self.sum_credit += line.credit
           #                     lines.append(data)              

        values=data_lines.itervalues()
        for line in values:
            lines_data.append(line)            
        newlist = sorted(lines_data, key=itemgetter('credit','code'))
        return newlist

    def get_analytic_lines(self, advance, data, use):
        line_data = {}
        lines = []
        amount=total=0        
        #obtiene la partida de los movimientos del voucher
        for line in advance.move_ids:     
            for al in line.analytic_lines:
                if al.amount == 0:
                    continue
                if not al.account_id.usage == use:
                    continue                
                line_data = {'acc_name': al.account_id.complete_name,
                             'code': use=='budget' and al.account_id.code or al.general_account_id.code,
                             'amount': abs(al.amount),
                             'name': al.name}                            
                lines.append(line_data)
        if advance.line_cr_ids:
            for line_cr in advance.line_cr_ids:                
                if line_cr.move_line_id.move_id:
                    for line_ana in line_cr.move_line_id.move_id.line_id:
                        for al in line_ana.analytic_lines:
                            if al.amount == 0:
                                continue
                            if not al.account_id.usage == use:
                                continue                            
                            total+=amount
                            line_data = {'acc_name': al.account_id.complete_name,
                                         'code': use=='budget' and al.account_id.code or al.general_account_id.code,
                                         'amount': abs(al.amount),
                                         'name': al.name,
                                         'total': total}                            
                            lines.append(line_data)
                
        if not lines:
            lines.append({'code':'*', 'acc_name': 'SIN APLICACION'})
            return lines   
        return lines
    

    def get_user(self, move):
        user_name = '*'
        user_pool = pooler.get_pool(self.cr.dbname).get('res.users')
        self.cr.execute("select create_uid from account_voucher where id=%s" % move.id)
        data = self.cr.fetchone()
        user = user_pool.browse(self.cr, self.uid, data[0])
        user_name = user.name
        return user_name    
   
report_sxw.report_sxw('report.account.advances','account.voucher',
                      'addons/account_advances/report/report_advances.rml',
                      parser=voucher, header=True)
