# -*- coding: utf-8 -*-
##############################################################################
#    
# mariofchogllo@gmail.com
#
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler
import itertools
import operator
from operator import itemgetter
from gt_tool import amount_to_text_ec


class move(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(move, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.sum_acurred = 0.00
        self.sum_paid = 0.00
        self.amount_costos = 0.00     
        self.localcontext.update({
            'time': time,
            'get_analytic_lines': self.get_analytic_lines,
            'get_lines': self.get_lines,
            'get_budget': self.get_budget,
            'get_budget_lines': self.get_budget_lines,
            'get_user': self.get_user,
            'get_invoice_data': self.get_invoice_data,
            'get_amount_pay': self.get_amount_pay,
            'get_pay_title':self.get_pay_title,
            'suma_debit': self.suma_debit,
            'suma_credit': self.suma_credit,
            'suma_acurred': self.suma_acurred,
            'suma_paid': self.suma_paid,
            'sum_costos': self.sum_costos,
            'get_budget_title': self.get_budget_title,
            'get_letras_move': self.get_letras_move,
            'get_firma':self.get_firma,
        })

    def get_firma(self, move):
        parameter_obj = self.pool.get('ir.config_parameter')
        monto_ids = parameter_obj.search(self.cr, self.uid, [('key','=','montoInfima')],limit=1)
        monto = 0
        if monto_ids:
            monto = parameter_obj.browse(self.cr, self.uid, monto_ids[0]).value
        aux = "DIR. ADMINISTRATIVO"
        if move.total_banco>=float(monto):
            aux="ALCALDE"
        return aux

    def get_letras_move(self, valor):
        letra = amount_to_text_ec.amount_to_text_ec(valor)
        return letra

    def get_budget_title(self, move):
        """
        Decide entre PAGADO - RECAUDADO
        """
        title = "PAGADO"
        if move.journal_id.type in ['bank', 'cash']:
            def_acc = move.journal_id.default_debit_account_id
            for line in move.line_id:
                if line.account_id.id == def_acc.id:
                    if line.debit > 0:
                        title = "RECAUDADO"
                        break
        elif move.journal_id.type == 'sale':
            title = "RECAUDADO"                    
        return title

    def get_pay_title(self, move):
        journal_obj = self.pool.get('account.journal')
        res = ''
        aux_total_banco = 0
        for line in move.line_id:
            if line.credit>0:
                aux_account_id = line.account_id
                journal_ids = journal_obj.search(self.cr, self.uid, [('type','=','bank'),('default_credit_account_id','=',line.account_id.id)])
                if journal_ids and line.account_id.code[0:5]!='11115':
                    aux_total_banco += line.credit
            letras = self.get_letras_move(aux_total_banco)
            aux = aux_total_banco
            a = str(aux_total_banco)
            res = 'MONTO PAGAR: ' + str(aux) + '    SON: ' + letras 
        return res

    def get_amount_pay(self, move):
        journal_obj = self.pool.get('account.journal')
        aux = move.amount
        for line in move.line_id:
            if line.credit>0:
                aux_account_id = line.account_id
                journal_ids = journal_obj.search(self.cr, self.uid, [('type','=','bank'),('default_credit_account_id','=',line.account_id.id)])
                if journal_ids:
                    aux = line.credit
                    break
        return aux

    def sum_costos(self):
        return self.amount_costos
        
    def suma_debit(self):
        return self.sum_debit or 0.00

    def suma_credit(self):
        return self.sum_credit or 0.00
    
    def suma_acurred(self):
        return self.sum_acurred or 0.00
    
    def suma_paid(self):
        return self.sum_paid or 0.00
    
    def set_context(self, objects, data, ids, report_type=None):
        #Your code goes here
        return super(move, self).set_context(objects, data, ids, report_type=report_type)

    def get_invoice_data(self, move):
        """
        Informacion de documentos de pago en asiento contable
        Factura
        Retencion
        """
        data = []
        invoice = move.line_id[0] and move.line_id[0].invoice and move.line_id[0].invoice
        if not invoice:
            return data
        if invoice.reference_type == 'invoice_partner':
            texto = ' '.join([invoice.auth_inv_id.type_id.name, invoice.supplier_number, 'AUTORIZACION', invoice.auth_inv_id.name])
            data.append({'date': invoice.date_invoice, 'name': texto, 'amount': invoice.amount_pay})
        data_doc = {}
        if invoice.reference_type == 'multi_invoice':
            for line in invoice.invoice_line:
                number = ''.join([line.auth_id.serie_entidad,line.auth_id.serie_emision,line.invoice_number.zfill(9)])
                texto = ' '.join([line.auth_id.type_id.name, number, 'AUTORIZACION', line.auth_id.name])
                data.append({'date': line.date_invoice, 'name': texto, 'amount': line.price_total})
        #ordena facturas por numero
        data = sorted(data, key=lambda k: k['name'])    
        if invoice.retention_id:
            ret = invoice.retention_id
            data.append({'date': ret.date, 'name': 'RETENCION %s' % ret.number, 'amount': ret.amount_total})
        return data

    def get_analytic_lines(self, move, data, use):
        """
        Informacion de centros de costos en asiento contable
        cada linea del asiento tiene lineas analiticas
        """
        line_data = {}
        lines = []
        self.amount_costos = 0
        for line in move.line_id:
            for al in line.analytic_lines:
                if al.amount == 0:
                    continue
                if not al.account_id.usage == use:
                    continue
                if not line_data.get(al.account_id.code):
                    line_data[al.account_id.code] = {'acc_name': al.account_id.complete_name,
                                                    'code': use=='budget' and al.account_id.code or al.general_account_id.code,
                                                    'amount': 0,'name': al.name}
                line_data[al.account_id.code]['amount'] += abs(al.amount)
        for k, v in line_data.items():
            lines.append(v)
            self.amount_costos += v['amount']
        return lines

    def get_budget_lines(self, move, data, use):
        """
        Informacion de presupuestos aplicados a los detalles
        budget_id: relacion contra linea de compromiso presupuestario
        return: [{'code_completo': 'ABCD', 'name': 'PARTIDA', 'amount_acurred': 0, 'amount_paid': 0}]
        """
        datas = []
        data_budget = {}
        self.sum_acurred = 0
        self.sum_paid = 0
        for line in move.line_id:
            if not line.budget_id:
                continue
#            budget = line.budget_id.budget_line_id
            budget = line.budget_id
            if not data_budget.get(budget.id):
                #data_budget = {budget.id: {'code': budget.code, 'name': budget.name, 'amount_acurred': 0, 'amount_paid': 0}}
                data_budget[budget.id] = {'code': budget.code, 'name': budget.name, 'amount_acurred': 0, 'amount_paid': 0}
            accurred = line.budget_accrued and line.debit+line.credit or 0.00
            paid = line.budget_paid and line.debit+line.credit or 0.00
            data_budget[budget.id]['amount_acurred'] += accurred
            data_budget[budget.id]['amount_paid'] += paid
            self.sum_acurred += accurred
            self.sum_paid += paid
        datas = [val for k, val in data_budget.items()]
        datas1 = sorted(datas, key=itemgetter('code'))
        return datas1
    
    def get_budget(self, move, data, use):
        lines = []
        data = { }    
        amount_tax=0   
        project_obj = self.pool.get('project.project')
        self.sum_acurred=self.sum_paid=self.credit=self.sum_debit=0.0
        pos=0
        for line in move.line_id:
            if line.budget_id and line.budget_accrued==True and line.budget_paid==False:               
                budget = line.budget_id.budget_line_id.general_budget_id
                project = project_obj.browse(self.cr, 1, line.budget_id.project_id.id)
                #code_project='sdf'#line.budget_id.project_id.code
                code_project = project.code
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
                budget = line.budget_id.budget_line_id.general_budget_id
                code_project=line.budget_id.project_id.code      
                if line.reconcile_id.id:      
                    move_fac = self.pool.get('account.move.line').search(self.cr,self.uid,[('reconcile_id','=',line.reconcile_id.id),('id','!=',line.id),('invoice','ilike','')])
                    if move_fac:
                        move_fac_obj=self.pool.get('account.move.line').browse(self.cr,self.uid,move_fac[0])                    
                else:                  
                    move_fac = self.pool.get('account.move.line').search(self.cr,self.uid,[('reconcile_partial_id','=',line.reconcile_partial_id.id),('invoice','ilike','')])
                    if move_fac:
                        move_fac_obj=self.pool.get('account.move.line').browse(self.cr,self.uid,move_fac[0])                                                        
                if move_fac and move_fac_obj.invoice:
                    if pos==0:                        
                        pass
                    else:                                
                        if move_fac and move_fac_obj.invoice:
                            if id_fac==move_fac_obj.invoice.id:
                                break                                                   
                    total_voucher=0                    
                    for move_fac in move_fac_obj.invoice.move_id.line_id:                               
                        id_voucher=self.pool.get('account.voucher').search(self.cr,self.uid,[('move_id','=',move.id)])[0]                                    
                        id_voucher_line=self.pool.get('account.voucher.line').search(self.cr,self.uid,[('move_line_id','=',move_fac.id),('reconcile','=',False),('voucher_id','=',id_voucher)])                        
                        if id_voucher_line:                            
                            id_voucher=self.pool.get('account.voucher.line').browse(self.cr,self.uid,id_voucher_line)[0]
                            total_voucher+=id_voucher.amount  
                        else:                           
                            id_voucher_line=self.pool.get('account.voucher.line').search(self.cr,self.uid,[('move_line_id','=',move_fac.id),('reconcile','=',True),('voucher_id','=',id_voucher)])
                            if id_voucher_line:                                
                                id_voucher=self.pool.get('account.voucher.line').browse(self.cr,self.uid,id_voucher_line)[0]
                                total_voucher+=id_voucher.amount                                                                                                              
                    total_fac=move_fac_obj.invoice.amount_total                                                    
                    for line_inv in move_fac_obj.invoice.invoice_line:                        
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
                                    porcentaje=((total_voucher*100)/(total_fac))/100  
                                    paid=(line_inv.price_total+(line_inv.price_subtotal*amount_tax))*porcentaje
                        else:
                            for tax_id in line_inv.invoice_line_tax_id:
                                if str(tax_id.tax_group).find('ret')!=-1:
                                    amount_tax+=tax_id.amount    
                            if total_fac==total_voucher:                                
                                paid=line_inv.price_subtotal+(line_inv.price_subtotal*amount_tax)
                            else:                                
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
                    pos+=1 
                    if move_fac and move_fac_obj.invoice:
                        id_fac=move_fac_obj.invoice.id  
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
                        self.sum_acurred += line.credit
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
                        data[budget.code+code_project] = {'code': budget.code+code_project, 'name': budget.name, 'amount_acurred': line.debit,'amount_paid': line.debit,'code_completo':code_project+"."+task+"."+budget.code}
                        self.sum_acurred += line.debit
                        self.sum_paid += line.debit                
        values=data.itervalues()
        for line in values:
            lines.append(line)
        lines = sorted(lines, key=itemgetter('amount_acurred','amount_paid','code'))
        if not lines:
            lines.append({'code':'*', 'name': 'SIN APLICACION'})
            return lines        
        return lines

    def get_lines(self, advance):
        """
        Detalle contable
        """
        lines_data = []
        lines_data_c = []
        data_lines = {}
        data_lines_c = {}
        self.sum_acurred = self.sum_paid = self.credit = self.sum_debit = 0.0
        for line in advance.line_id:    
            if line.debit != 0 and line.credit == 0:                        
                if not data_lines.get(line.account_id.code):
                    data_lines[line.account_id.code] = {'code': line.account_id.code,
                                                        'name': line.account_id.name,
                                                        'debit': 0,
                                                        'credit': 0,
            }
                data_lines[line.account_id.code]['debit'] += line.debit                   
            if line.credit != 0 and line.debit == 0:
                if not data_lines_c.get(line.account_id.code):
                    data_lines_c[line.account_id.code] = {'code': line.account_id.code,
                                                        'name': line.account_id.name,
                                                        'debit': 0,
                                                        'credit': 0}
                data_lines_c[line.account_id.code]['credit'] += line.credit
            self.sum_debit += line.debit
            self.sum_credit += line.credit
        #debit
        values = data_lines.itervalues()
        for line in values:
            lines_data.append(line)
        newlist = sorted(lines_data, key=itemgetter('credit','code'))
        #credit
        values = data_lines_c.itervalues()
        for line in values:
            lines_data_c.append(line)
        newlist_c = sorted(lines_data_c, key=itemgetter('debit','code'))
        return newlist+newlist_c

    def get_user(self, move):
        user_name = '*'
        user_pool = pooler.get_pool(self.cr.dbname).get('res.users')
        if move.line_id and move.line_id[0] and move.line_id[0].invoice:
            user_name = move.line_id[0].invoice.user_id.name
        else:
            self.cr.execute("select create_uid from account_move where id=%s" % move.id)
            data = self.cr.fetchone()
            user = user_pool.browse(self.cr, self.uid, data[0])
            user_name = user.name
        return user_name
   
report_sxw.report_sxw('report.account.move','account.move','addons/retention/report/report_move.rml',parser=move)

