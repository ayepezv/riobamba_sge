# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

import netsvc

from osv import fields, osv

class divideCuentaLine(osv.TransientModel):
    _name = 'divide.cuenta.line'
    _columns = dict(
        d_id = fields.many2one('divide.cuenta','Detalle'),
        account_id = fields.many2one('account.account','Cuenta'),
        monto = fields.float('Monto'),
    )
divideCuentaLine()
class divideCuenta(osv.TransientModel):
    _name = 'divide.cuenta'
    _columns = dict(
        move_id = fields.many2one('account.move','Comprobante Contable'),
        move_line_id = fields.many2one('account.move.line','Linea a dividir',required=True),
        line_ids = fields.one2many('divide.cuenta.line','d_id','Detalle cuentas y monto'),
    )
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = {}
        record_id = context and context.get('active_id', False) or False
        res.update({
                'move_id':record_id,
            })
        return res

    def divideCuenta(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        for this in self.browse(cr, uid, ids):
            move_line_id = this.move_line_id
            if move_line_id.credit!=0:
                aux_total = 0
                for line in this.line_ids:
                    aux_total += line.monto
                    if move_line_id.budget_id:
                        move_line_obj.create(cr, uid, {
                            'move_id':this.move_id.id,
                            'budget_id_cert':move_line_id.budget_id_cert.id,
                            'budget_accrued':move_line_id.budget_accrued,
                            'budget_paid':move_line_id.budget_paid,
                            'debit':0,
                            'credit':line.monto,
                            'name':move_line_id.name,
                            'account_id':line.account_id.id,
                        })
                    else:
                        move_line_obj.create(cr, uid, {
                            'move_id':this.move_id.id,
                            'debit':0,
                            'credit':line.monto,
                            'name':move_line_id.name,
                            'account_id':line.account_id.id,
                    })
                if not aux_total==move_line_id.credit:
                    raise osv.except_osv(('Error de usuario!'), ('El total credito no es igual a la suma de detalle'))
            else:
                aux_total = 0
                for line in this.line_ids:
                    aux_total += line.monto
                    if move_line_id.budget_id:
                        move_line_obj.create(cr, uid, {
                            'move_id':this.move_id.id,
                            'budget_id_cert':move_line_id.budget_id_cert.id,
                            'budget_accrued':move_line_id.budget_accrued,
                            'budget_paid':move_line_id.budget_paid,
                            'debit':line.monto,
                            'credit':0,
                            'name':move_line_id.name,
                            'account_id':line.account_id.id,
                        })
                    else:
                        move_line_obj.create(cr, uid, {
                            'move_id':this.move_id.id,
                            'debit':line.monto,
                            'credit':0,
                            'name':move_line_id.name,
                            'account_id':line.account_id.id,
                    })
                if not aux_total==move_line_id.credit:
                    raise osv.except_osv(('Error de usuario!'), ('El total debito no es igual a la suma de detalle'))
            move_line_obj.unlink(cr, uid, [move_line_id.id])
        return {'type':'ir.actions.act_window_close' }
    
divideCuenta()    

class loadGestion(osv.TransientModel):
    _name = 'load.gestion'
    
    def loadGestion(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        record_id = context and context.get('active_id', False) or False
        move = self.pool.get('account.move').browse(cr, uid, record_id, context=context)
        for this in self.browse(cr, uid, ids):
            if this.amount>0:
                p_id = move.partner_id.id
                move_line_obj.create(cr, uid, {
                        'account_id':this.acc_g1.id,
                        'debit':this.amount,
                        'move_id':move.id,
                        'partner_id':p_id,
                    })
                move_line_obj.create(cr, uid, {
                    'account_id':this.acc_g2.id,
                    'credit':this.amount,
                    'move_id':move.id,
                    'partner_id':p_id,
                })
        return {'type':'ir.actions.act_window_close' }
                
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        account_obj = self.pool.get('account.account')
        parameter_obj = self.pool.get('ir.config_parameter')
        res = {}
        record_id = context and context.get('active_id', False) or False
        move = self.pool.get('account.move').browse(cr, uid, record_id, context=context)
        aux_gestion = 0
        if move.state=='posted':
            raise osv.except_osv(('Error de usuario!'), ('No puede ejecutar esta accion en asientos contabilizados'))
        #el monto es el total del devengado
        #recorrer el CP y si es inversion suma
        if move.certificate_id:
            for c_line in move.certificate_id.line_ids:
                if c_line.budget_post.code[0:1]=='7':
                    aux_gestion += c_line.amount_commited
        acc_g1_ids = parameter_obj.search(cr, uid, [('key','=','acc_g1')],limit=1)
        acc_g2_ids = parameter_obj.search(cr, uid, [('key','=','acc_g2')],limit=1)
        if acc_g1_ids and acc_g2_ids:
            aux_code_g1 = parameter_obj.browse(cr, uid, acc_g1_ids[0]).value
            account_g1_ids = account_obj.search(cr, uid, [('code','=',aux_code_g1)],limit=1)
            aux_code_g2 = parameter_obj.browse(cr, uid, acc_g2_ids[0]).value
            account_g2_ids = account_obj.search(cr, uid, [('code','=',aux_code_g2)],limit=1)
            res.update({
                'acc_g1':account_g1_ids[0],
                'acc_g2':account_g2_ids[0],
                'amount':aux_gestion,
            })
        return res

    _columns = dict(
        acc_g1 = fields.many2one('account.account','Cta. Gastos Gestion'),
        acc_g2 = fields.many2one('account.account','Contra Cta. Gastos Gestion'),
        amount = fields.float('Monto'),
    )
loadGestion()


class otrosIngresos(osv.TransientModel):
    _name = 'otros.ingresos'
    _columns = dict(
        bank_id = fields.many2one('account.journal', 'Banco', required=True),
        budget_id = fields.many2one('budget.post','Partida'),
        monto = fields.float('Monto'),
    )

    def loadOingresos(self, cr, uid, ids, context=None):
        certificate_line_obj = self.pool.get('budget.certificate.line')
        account_obj = self.pool.get('account.account')
        item_obj = self.pool.get('budget.item')
        project_obj = self.pool.get('project.project')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        post_obj = self.pool.get('budget.post')
        parameter_obj = self.pool.get('ir.config_parameter')
        for this in self.browse(cr, uid, ids):
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            name_aux = 'Cobro'
            move_id = context and context.get('active_id', False) or False
            move = move_obj.browse(cr, uid, move_id)
            date_aux = move.date
            if move.state=='posted' and not this.other:
                raise osv.except_osv(('Error de usuario!'), 
                                     ('El asiento esta contabilizado'))
            project_ids = project_obj.search(cr, uid, [('type_budget','=','ingreso')],limit=1)
            project = project_obj.browse(cr, uid, project_ids[0])
            item_ids = item_obj.search(cr, uid, [('budget_post_id','=',this.budget_id.id),('date_start','<=',move.date),('date_end','>=',move.date)],limit=1)
            if not item_ids:
                raise osv.except_osv(('Error Configuracion !'),
                                     ("No existe la partida '%s'") % (this.budget_id.code)) 
            certificate_id = certificate_line_obj.create(cr, uid, {
                'project_id':project.id,
                'task_id':project.tasks[0].id,
                'budget_id':item_ids[0],
            })
            certificate = certificate_line_obj.browse(cr, uid, certificate_id)
            b_id = certificate.budget_id.id
            p_id = certificate.budget_post.id
            account_ids = account_obj.search(cr, uid, [('budget_id','=',this.budget_id.id)])
            if not account_ids:
                raise osv.except_osv(('Error de configuracion !'),
                                     ("No existe cuenta contable asociada a la partida '%s'")%(this.budget_id.code))
            for account_id in account_ids:
                account = account_obj.browse(cr, uid, account_id)
                if account.account_rec_id:
                    break
            aux_mseg_nocxp = account.code + ' - ' + account.name
            if not account.account_rec_id:
                raise osv.except_osv(('Error de configuracion !'),
                                     ("No existe cuenta por cobrar asociada a la cuenta '%s'")%(aux_mseg_nocxp))
            cxp = account.account_rec_id.id
            monto = this.monto
            
            #aqui considerar parametro riobamba 1131708, 91123010017008, 92123010017008
            descuento_ids = parameter_obj.search(cr, uid, [('key','=',this.budget_id.code)],limit=1)
            if descuento_ids:
                descuento_code = parameter_obj.browse(cr, uid, descuento_ids[0]).value
                aux_acc_1 = '91123010017008'
                aux_acc_2 = '92123010017008'
                account_ids1 = account_obj.search(cr, uid, [('code','=',aux_acc_1)],limit=1)
                account_ids2 = account_obj.search(cr, uid, [('code','=',aux_acc_2)],limit=1)
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,budget_id_cert,budget_id,budget_post,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,True,certificate_id,b_id,p_id,move.partner_id.id))
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s,%s,%s,%s, %s,%s,%s,%s,%s,%s)''',(move_id,account_ids1[0],monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,False,move.partner_id.id))
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_accrued,budget_paid,name,migrado,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_ids2[0],monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,False,False,name_aux,False,move.partner_id.id))
            else:
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_accrued,budget_id_cert,budget_id,budget_post,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,True,certificate_id,b_id,p_id,move.partner_id.id))
                #linea  entrada cxc haber
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,budget_id_cert,budget_id,budget_post,partner_id) VALUES (%s,%s, %s, %s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,True,certificate_id,b_id,p_id,move.partner_id.id))
                #linea  entrada cta patrimonial 621
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_accrued,budget_paid,name,migrado,budget_id_cert,budget_id,budget_post,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.id,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,False,False,name_aux,False,certificate_id,b_id,p_id,move.partner_id.id))
            #restar en banco el monto del ingreso
            if not this.bank_id.default_debit_account_id:
                raise osv.except_osv(('Error de configuracion!'), ('El banco no tiene asociada cuentas contables'))
            line_bank_ids = move_line_obj.search(cr,uid, [('move_id','=',move_id),('account_id','=',this.bank_id.default_debit_account_id.id)])
            nuevo_valor = 0 
            if line_bank_ids:
                move_line = move_line_obj.browse(cr, uid, line_bank_ids[0])
                if move_line.debit>0:
                    nuevo_valor = move_line.debit - this.monto   #estaba mas
                    move_line_obj.write(cr,uid, line_bank_ids,{
                        'debit':nuevo_valor,
                    })  
                else:
                    nuevo_valor = move_line.credit - this.monto   #estaba mas
                    move_line_obj.write(cr,uid, line_bank_ids,{
                        'credit':nuevo_valor,
                    })
        return {'type':'ir.actions.act_window_close' }

otrosIngresos()

class makePayLine(osv.TransientModel):
    _name = 'make.pay.line'
    _columns = dict(
        pay_id = fields.many2one('make.pay','Pago'),
        account_id = fields.many2one('account.account','Cuenta por pagar'),
        account_id2 = fields.many2one('account.account','Cuenta por pagar tercero'),
        monto = fields.float('Monto'),
        to_pay = fields.boolean('Pagar'),
        desc = fields.char('Detalle',size=32),
        cert_id = fields.many2one('budget.certificate.line','Linea certificado'),
    )

    _defaults = dict(
        to_pay = True,
    )
makePayLine()

#class make_pay(osv.TransientModel):
class make_pay(osv.Model):
    _name = 'make.pay'
    
    _columns = {
        'total_pagar':fields.float('TOTAL A PAGAR'),
        'bank_id': fields.many2one('account.journal', 'Banco', required=True),
        'other':fields.boolean('Comprobante Separado',help="Marque el campo para generar el pago en un comprobante separado"),
#        'line_ids':fields.one2many('make.pay.line','pay_id','Cuentas por pagar'),
        'line_ids':fields.one2many('account.move.line','pay_id','Cuentas por pagar'),
        'move_id':fields.many2one('account.move','Move'),
    }

    def verificar_monto(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            aux = 0
            for line in this.line_ids:
                if line.to_pay and not line.account_id2:
                    aux += line.monto
            self.write(cr,uid, this.id,{'total_pagar':aux})
        return True

    def make_pay(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        pago_obj = self.pool.get('move.line.pago')
        for this in self.browse(cr, uid, ids):
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            move_id = context and context.get('active_id', False) or False
            move = move_obj.browse(cr, uid, move_id)
            if move.state=='posted' and not this.other:
                raise osv.except_osv(('Error de usuario!'), 
                                     ('El asiento esta contabilizado y solo se puede hacer pago si usted marca que se genere otro comprobante'))
            aux_narration = ""
            if this.other:
                aux_narration = "PAGO - " + move.narration
                move_id = move_obj.create(cr, uid,{
                    'journal_id':move.journal_id.id,
                    'period_id':move.period_id.id,
                    'date':move.date,
                    'partner_id':move.partner_id.id,
                    'certificate_id':move.certificate_id.id,
                    'afectacion':True,
                    'narration':aux_narration,
                    'ref':aux_narration,
                })
                move = move_obj.browse(cr, uid, move_id)
            date_aux = move.date
            monto_banco = 0
            if not this.line_ids:
                raise osv.except_osv(('Error de usuario!'), 
                                     ('NO a cargado las cuentas por pagar, por favor dar click en el boton CARGAR CUENTAS POR PAGAR de este formulario'))
            for line in this.line_ids:
                partner_id = move.partner_id.id
                if line.to_pay:
                    b_id = line.budget_id_cert.budget_id.id
                    p_id = line.budget_id_cert.budget_post.id
                    if line.monto>0:
                        if line.partner_id:
                            partner_id = line.partner_id.id
                        if not line.account_id2:
                            monto_banco += line.monto
                            #SQL
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id,move_line_cxp) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,line.account_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.budget_id_cert.id,b_id,p_id,'Sueldo',False,True,partner_id,line.id))
                        else:
                            if line.account_id2:
                                cr.execute('''
                                INSERT INTO account_move_line (
                                move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id,move_line_cxp) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,line.account_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.budget_id_cert.id,b_id,p_id,'',False,False,partner_id,line.id))
                                cr.execute('''
                                INSERT INTO account_move_line (
                                move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,partner_id,move_line_cxp) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,line.account_id2.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'',False,False,partner_id,line.id))
            #banco
            if not this.bank_id.default_debit_account_id:
                raise osv.except_osv(('Error de configuracion!'), ('El banco no tiene asociada cuentas contables'))
            move_line_obj.create(cr, uid, {
                'account_id':this.bank_id.default_debit_account_id.id,
                'credit':monto_banco,
                'move_id':move_id,
                'partner_id':move.partner_id.id,
            })
        return {'type':'ir.actions.act_window_close' }

    def onchange_bank_make(self, cr, uid, ids, bank_id,move_id ,context={}):
        vals = {}
        line_ids = []
        if context is None:
            context = {}
        self.load_cxp_make

    def onchange_bank_make_1(self, cr, uid, ids, bank_id,move_id ,context={}):
        vals = {}
        line_ids = []
        if context is None:
            context = {}
        sri_obj = self.pool.get('pay.fondo.sri')
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        for this in self.browse(cr, uid, ids):
            for line in move.line_id:
                if line.account_id.type=='payable':
                    if line.credit>0 and line.budget_paid==False:
                        account_sri = ''
                        if not line.budget_id_cert:
                            raise osv.except_osv(('Error de usuario!'), ('Las cuentas por pagar deben tener la partida'))
                        acc_aux = ''
                        sri_ids = sri_obj.search(cr, uid,[('account_id','=',line.account_id.code)])
                        if sri_ids:
                            sri = sri_obj.browse(cr, uid, sri_ids[0])
                            account_ids = account_obj.search(cr, uid, [('code','=',sri.account_id2)],limit=1)
                            if account_ids:
                                account_sri = account_ids[0]
                        aux_desc = line.name
                        if line.budget_id_cert.tipo_invoice:
                            aux_desc = 'Pago ' + line.budget_id_cert.tipo_invoice
                        if account_sri:
                            move_line_obj.write(cr, uid, line.id,{
                                'pay_id':this.id,
                                'account_id2':account_sri,
                                'to_pay':True,
                                'monto':line.credit,
                            })
                        else:
                            move_line_obj.write(cr, uid, line.id,{
                                'pay_id':this.id,
                                'to_pay':True,
                                'monto':line.credit,
                            })
        return True#{'value':{'line_ids':line_ids}}

    def load_cxp_make(self, cr, uid, ids, context):
        if context is None:
            context = {}
        tax_map = self.pool.get('account.tax.map')
        sri_obj = self.pool.get('pay.fondo.sri')
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        record_id = context and context.get('active_id', False) or False
        company_obj = self.pool.get('res.company')
        company = company_obj.browse(cr, uid, 1)
        move = self.pool.get('account.move').browse(cr, uid, record_id, context=context)
        for this in self.browse(cr, uid, ids):
            if move.state=='posted' and not this.other:
                raise osv.except_osv(('Error de usuario!'), ('No puede ejecutar esta accion en asientos contabilizados, solo puede hacerlo si marca la opcion de comprbante separado'))
            if move.type=='Nomina':
                for line in move.line_id:
                    if line.account_id.type=='payable' and line.credit>0:
                        if not line.is_anticipo:
                            if not line.budget_id_cert:
                                raise osv.except_osv(('Error de usuario!'), ('Las cuentas por pagar deben tener la partida'))
                            acc_aux = ''
                            aux_desc = line.name
                            cr.execute('''update account_move_line set pay_id=%s,to_pay=True,monto=%s where id=%s'''%(this.id,str(line.credit),line.id))
                    elif line.debit>0 and line.is_ingreso_anticipo:
                        cr.execute('''update account_move_line set pay_id=%s,to_pay=True,monto=%s where id=%s'''%(this.id,str(line.debit),line.id))
                    else:
                        continue
            else:
                for line in move.line_id:
                    if not line.is_anticipo:
                        if line.account_id.type=='payable':
                            account_sri = []
                            if line.credit>0 and line.budget_paid==False:
                                if not line.budget_id_cert:
                                    raise osv.except_osv(('Error de usuario!'), ('Las cuentas por pagar deben tener la partida'))
                                acc_aux = ''
                                sri_ids = sri_obj.search(cr, uid,[('account_id','=',line.account_id.code)])
                                if sri_ids:
                                    sri = sri_obj.browse(cr, uid, sri_ids[0])
                                    account_ids = account_obj.search(cr, uid, [('code','=',sri.account_id2)],limit=1)
                                    if account_ids and not line.account_id2:
                                        account_sri = account_ids[0]
                                else:
                                    if line.partner_id.id!=line.move_id.partner_id.id:
                                        if line.partner_id.id==company.tax_company_id.id:
                                            map_ids = tax_map.search(cr, uid, [('account_id','=',line.account_id.id)])
                                            #considerar pero el porcentaje por que puede difiere la 212 esto cuando es bienes y srv al mismo tiempo
                                            if map_ids:
                                                map = tax_map.browse(cr, uid, map_ids[0])
                                                if map.tax_id.account_id:
                                                    account_sri = map.tax_id.account_id.id
                                aux_desc = line.name
                                if line.budget_id_cert.tipo_invoice:
                                    aux_desc = 'Pago ' + line.budget_id_cert.tipo_invoice
                                aux_valor = line.credit
                                if line.is_ingreso_anticipo:
                                    aux_valor = line.debit
                                if line.account_id2:
                                    #sql
    #                                cr.execute('''update account_move_line set pay_id=%s,to_pay=True,monto=%s'''%(this.id,str(line.credit)))
                                    move_line_obj.write(cr, uid, line.id,{
                                        'pay_id':this.id,
                                        'to_pay':True,
                                        'monto':aux_valor,
                                    })
                                else:
                                    if account_sri:
    #                                    cr.execute('''update account_move_line set pay_id=%s,account_id2=%s,to_pay=True,monto=%s'''%(this.id,account_sri,str(line.credit)))
                                        move_line_obj.write(cr, uid, line.id,{
                                            'pay_id':this.id,
                                            'account_id2':account_sri,
                                            'to_pay':True,
                                            'monto':aux_valor,
                                        })
                                    else:
    #                                    cr.execute('''update account_move_line set pay_id=%s,account_id2=%s,to_pay=True,monto=%s'''%(str(this.id),'Null',str(line.credit)))
                                        move_line_obj.write(cr, uid, line.id,{
                                            'account_id2':False,
                                            'pay_id':this.id,
                                            'to_pay':True,
                                            'monto':aux_valor,
                                        })
        return True        

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res={}
        record_id = context and context.get('active_id', False) or False
        move = self.pool.get('account.move').browse(cr, uid, record_id, context=context)
        if move.state=='posted':
            raise osv.except_osv(('Error de usuario!'), ('No puede ejecutar esta accion en asientos contabilizados'))
        res.update({'move_id':record_id})
        return res

make_pay()


