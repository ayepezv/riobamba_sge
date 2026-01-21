# -*- coding: utf-8 -*-
##############################################################################
#
#    Gestion de Obras - GobERP
#    Copyright (C) 2013 Mario Chogllo
#    mariofchogllo@gmail.com
#    $Id$
#
##############################################################################
from tools import ustr
from osv import osv, fields
import time

class obraCxp(osv.TransientModel):
    _name = 'obra.cxp'
    _columns = dict(
        obra_id = fields.many2one('obra.obra','Obra/Contrato'),
        date = fields.date('Fecha'),
        obr_id = fields.many2one('ejec.contrato.line','Beneficiario'),
    )
obraCxp()

class ejecContratoLine(osv.TransientModel):
    _name = 'ejec.contrato.line'
    _columns = dict(
        ejec_id = fields.many2one('ejec.contrato','Beneficiario'),
        partner_id = fields.many2one('res.partner','Beneficiario'),
        num_contratos = fields.integer('Num. Contratos'),
        total_contrato = fields.float('Total Contratos'),
        total_anticipo = fields.float('Total Anticipo'),
        total_devengado = fields.float('Total Devengado'),
        saldo_por_devengar = fields.float('Saldo'),
        line_ids = fields.one2many('obra.cxp','obr_id','Obras'),
    )

ejecContratoLine()

class ejecContrato(osv.TransientModel):
    _name = 'ejec.contrato'
    _columns = dict(
        partner_id = fields.many2one('res.partner','Beneficiario'),
        contract_id = fields.many2one('obra.obra','Obra/Contrato'),
        line_ids = fields.one2many('ejec.contrato.line','ejec_id','Beneficiarios'),
    )

    def print_cxp_obra(self, cr, uid, ids, context):
        print "hace"
        return True

    def load_contratos(self, cr, uid, ids, context):
        obra_obj = self.pool.get('obra.obra')
        partner_obj = self.pool.get('res.partner')
        line_obj = self.pool.get('ejec.contrato.line')
        obra_cxp_obj = self.pool.get('obra.cxp')
        partner_ids = []
        line_detalle = []
        for this in self.browse(cr, uid, ids):
            if this.partner_id:
                obra_ids = obra_obj.search(cr, uid, [('partner_id','=',this.partner_id.id)])
                partner_ids.append(this.partner_id.id)
            else:
                obra_ids = obra_obj.search(cr, uid, [])
                for obra_id in obra_ids:
                    obra = obra_obj.browse(cr, uid, obra_id)
                    if not obra.partner_id.id in partner_ids:
                        partner_ids.append(obra.partner_id.id)
            for partner_id in partner_ids:
                line_detalle = []
                obra_ids = obra_obj.search(cr, uid, [('partner_id','=',partner_id)])
                num_contratos = total_contrato = total_anticipo = total_devengado = saldo_por_devengar = 0
                if obra_ids:
                    num_contratos = len(obra_ids)
                    for obra_id in obra_ids:
                        obra = obra_obj.browse(cr, uid, obra_id)
                        total_contrato += obra.monto
                        total_anticipo += obra.anticipo_entregado
                        if obra.certificate_id:
                            for line_compromiso in obra.certificate_id.line_ids:
                                total_devengado += line_compromiso.amount_paid
                            saldo_por_devengar += (total_contrato-total_devengado)
                            linea_detalle_id = obra_cxp_obj.create(cr, uid, {
                                'obra_id':obra_id,
                                'date':obra.date_start,
                            })
                            line_detalle.append(linea_detalle_id)
                    id_linea = line_obj.create(cr, uid, {
                        'partner_id':partner_id,
                        'num_contratos':num_contratos,
                        'ejec_id':this.id,
                        'total_contrato':total_contrato,
                        'total_anticipo':total_anticipo,
                        'total_devengado':total_devengado,
                        'saldo_por_devengar':saldo_por_devengar,
                    })
                    if line_detalle:
                        for linea_id in line_detalle:
                            obra_cxp_obj.write(cr, uid, linea_id,{
                                'obr_id':id_linea,
                            })
        return True                

ejecContrato()

class groupMove(osv.TransientModel):
    _name = 'group.move'
    _columns = dict(
        caja_chica = fields.boolean('Caja Chica/Fondo Reposicion'),
        partner_id = fields.many2one('res.partner','Proveedor/Beneficiario'),
        certificate_id = fields.many2one('budget.certificate','Comprimiso'),
        move_ids = fields.many2many('account.move','g_m_rel','g_id','m_id','Comprobantes a pagar'),
    )
    
    def agrupaMoves(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        move_obj = self.pool.get('account.move')
        account_ids = []
        move_ids = []
        for this in self.browse(cr, uid, ids):
            aux_desc = "PAGO " + this.partner_id.name
            move_aux = move_obj.browse(cr, uid, this.move_ids[0].id)
            move_id_creado = move_obj.create(cr, uid, {
                'journal_id':move_aux.journal_id.id,
                'period_id':move_aux.period_id.id,
                'date':move_aux.certificate_id.date_commited,
                'partner_id':move_aux.certificate_id.partner_id.id,
                'certificate_id':move_aux.certificate_id.id,
                'afectacion':True,
                'ref':'Resultado Agrupacion',
            })
            move= move_obj.browse(cr, uid, move_id_creado)
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            date_aux = move_aux.certificate_id.date_commited
            #unir agrupando por cuenta contable
            aux_invoice = ''
            for move_id in this.move_ids:
                #tomar campo ref y agrupar tambien
                aux_txt = 'FACTURAS: '
                aux_factura = move_id.ref + ' - '
                aux_invoice += aux_factura
                for line_id in move_id.line_id:
                    if not line_id.budget_id_cert:
                        raise osv.except_osv(('Error de usuario!'), 
                                             ('El comprobante con referencia %s no tiene partida')%(line_id.move_id.ref))
                    if not line_id.budget_id_cert.budget_id:
                        raise osv.except_osv(('Error de usuario!'), 
                                             ('El comprobante con referencia %s no tiene partida')%(line_id.move_id.ref))
                    b_id = line_id.budget_id_cert.budget_id.id
                    p_id = line_id.budget_id_cert.budget_post.id
                    if line_id.partner_id:
                        aux_partner_id = line_id.partner_id.id
                    else:
                        aux_partner_id = move_aux.certificate_id.partner_id.id
                    if line_id.debit>0:
                        #crear con sql
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id,ref) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_creado,line_id.account_id.id,line_id.debit,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id.budget_id_cert.id,b_id,p_id,line_id.name,False,True,aux_partner_id,line_id.ref))
                    elif line_id.credit>0:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,partner_id,ref) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_creado,line_id.account_id.id,line_id.credit,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id.budget_id_cert.id,b_id,p_id,line_id.name,False,aux_partner_id,line_id.ref))
                aux_narration = aux_txt + aux_invoice
            move_obj.write(cr, uid, [move_id_creado],{'narration':aux_narration})
        return {'type': 'ir.actions.act_window_close'}

groupMove()

#=====================
class voucherDevengado(osv.Model):
    _name = 'voucher.devengado'
    _columns = dict(
        is_migrado = fields.boolean('Migrado'),
        name = fields.many2one('account.move','Comprobante Contable'),
        voucher_id = fields.many2one('account.voucher','Anticipo'),
#        name = fields.char('Comprobante',size=32),
        monto = fields.float('Monto'),
        date = fields.date('Fecha'),
        partner_id = fields.related('voucher_id','partner_id',type='many2one',relation='res.partner',string='Beneficiario'),
    )
voucherDevengado()

class voucherAnticipo(osv.Model):
    _inherit = 'account.voucher'

    def _amount_all_anticipo(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for anticipo in self.browse(cr, uid, ids, context=context):
            res[anticipo.id] = {
                'devengado': 0.0,
                'saldo': 0.0,
            }
            aux = aux2 = 0
            for line in anticipo.dev_ids:
                if line.name or line.is_migrado:
                    if line.name.state=='posted' or line.is_migrado:
                        aux += line.monto
            aux2 = anticipo.amount - aux
            res[anticipo.id]['devengado']=aux
            res[anticipo.id]['saldo']=aux2
        return res

    _columns = dict(
        tipo = fields.selection([('Obra','Obra'),('Bienes y Servicios','Bienes y Servicios'),('Viaticos','Viaticos'),('Salario','Salario')],'Tipo'),
        dev_ids = fields.one2many('voucher.devengado','voucher_id','Detalle Devengado'),
#        devengado = fields.float('Devengado'),
#        saldo = fields.float('Saldo'),
        devengado = fields.function(_amount_all_anticipo, string='Devengado/Liquidado', multi="antic",store=True),
        saldo = fields.function(_amount_all_anticipo, string='Saldo', multi="antic",store=True),
    )
voucherAnticipo()

#Retencion ordenanza e incumplimiento de contrato
class makePayInc(osv.TransientModel):
    _inherit = 'make.pay'
    _columns = dict(
        anio_ant = fields.boolean('Anticipo Anio Actual'),
        anticipo_id = fields.many2one('account.account','Cuenta Anticipo'),
        monto_anticipo = fields.float('Monto Anticipo'),
        amount_ord = fields.float('Retencion Segun Ordenanza'),
        amount_inc = fields.float('Retencion Incumplimiento Contrato'),
        genera_cxc = fields.boolean('Generar cuenta cobrar iva a recuperar'),
    )

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = {}
        res.update({'genera_cxc':True})
        return res

    def make_pay(self, cr, uid, ids, context=None):
        no_rol = self.pool.get('hr.no.cobro')
        run_obj = self.pool.get('hr.payslip.run')
        payslip_obj = self.pool.get('hr.payslip')
        contract_obj = self.pool.get('hr.contract')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        cert_line = self.pool.get('budget.certificate.line')
        parameter_obj = self.pool.get('ir.config_parameter')
        item_obj = self.pool.get('budget.item')
        account_obj = self.pool.get('account.account')
        pago_obj = self.pool.get('move.line.pago')
        for this in self.browse(cr, uid, ids):
            nocobraBand=False
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            aux_total_no_cobra = 0
            move_id = context and context.get('active_id', False) or False
            move_id_2 = context and context.get('active_id', False) or False
            move = move_obj.browse(cr, uid, move_id)
            move_origen = move_obj.browse(cr, uid, move_id_2)
            if move.state=='posted' and not this.other:
                raise osv.except_osv(('Error de usuario!'), 
                                     ('El asiento esta contabilizado y solo se puede hacer pago si usted marca que se genere otro comprobante'))
            aux_narration = ""
            if this.other:
                if move.narration:
                    aux_narration = "PAGO - " +move.name + ' - '+ move.narration
                else:
                    aux_narration = "PAGO - " +move.name
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
            date_aux = move.certificate_id.date_commited            
            monto_banco = 0
            aux_iva = 0
            contratos_no = []
            nocobra_ids = []
            if move.type=='Nomina':
                run_ids = run_obj.search(cr, uid, [('move_id','=',context['active_id'])])
                if run_ids:
                    run_aux = run_obj.browse(cr, uid, run_ids[0])
                if run_ids:
                    if run_aux.normal:
                        nocobra_ids = no_rol.search(cr, uid, [])
                if nocobra_ids:
                    for nocobra_id in nocobra_ids:
                        nocobra = no_rol.browse(cr, uid, nocobra_id)
                        contratos_no.append(nocobra.contract_id.id)
                    if run_ids:
                        payslip_ids = payslip_obj.search(cr, uid, [('payslip_run_id','=',run_ids[0]),('contract_id','in',contratos_no)])
                        if payslip_ids:
                            aux_total_no_cobra = 0 
                            for payslip_id in payslip_ids:
                                payslip = payslip_obj.browse(cr, uid, payslip_id)
                                aux_total_no_cobra += payslip.net
                #agregado el verificar si no cobran el rol mandar a la 212 esta en sys param : rolnocobrado
                aux_i = 0
                for line in this.line_ids:
                    partner_id = move.partner_id.id
                    #verificar el iva que esta por pagar
                    if line.to_pay:
                        if line.budget_id_cert:
                            b_id = line.budget_id_cert.budget_id.id
                            p_id = line.budget_id_cert.budget_post.id
                            if line.monto>0:
                                if line.partner_id:
                                    partner_id = line.partner_id.id
                                if line.account_id2:
                                    if line.judicial_decimo>0:
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_2,line.account_id.id,line.judicial_decimo,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.budget_id_cert.id,b_id,p_id,line.name,False,True,partner_id))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)''',(move_id_2,line.account_id2.id,line.judicial_decimo,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.name,False,False,partner_id))
                                        #y sumo al banco la diferencia
                                        aux_diferencia = line.monto - line.judicial_decimo
                                        monto_banco += aux_diferencia
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_2,line.account_id.id,aux_diferencia,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.budget_id_cert.id,b_id,p_id,line.name,False,True,partner_id))
                                    else:
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_2,line.account_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.budget_id_cert.id,b_id,p_id,line.name,False,True,partner_id))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)''',(move_id_2,line.account_id2.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.name,False,False,partner_id))
                                else:
                                    if line.is_ingreso_gad:
                                        #debo considerar la 213 con la misma partida al debe
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_2,line.account_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.budget_id_cert.id,b_id,p_id,line.name,False,True,partner_id))
                                        #####################################
                                        ingreso_gad_ids = parameter_obj.search(cr, uid, [('key','=','ingresoGad')],limit=1)
                                        if not ingreso_gad_ids:
                                            raise osv.except_osv(('Error de configuracion!'), ('Configure el parametro de cuenta de ingreso por descuento Rol'))
                                        aux_gad = parameter_obj.browse(cr, uid, ingreso_gad_ids[0]).value
                                        account_gad_ids = account_obj.search(cr, uid, [('code','=',aux_gad)],limit=1)
                                        if not account_gad_ids:
                                            raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta contable ingreso descuento rol configurada en parametros'))
                                        account_gad = account_obj.browse(cr, uid, account_gad_ids[0])
                                        if not account_gad.account_rec_id:
                                            raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta por cobrar de la cuenta descuento rol configurada'))
                                        cxp = account_gad.account_rec_id.id
                                        if not account_gad.budget_id:
                                            raise osv.except_osv(('Error de configuracion!'), ('No existe partida asociada a la cuenta descuento rol configurada'))
                                        item_ids = item_obj.search(cr, uid, [('budget_post_id','=',account_gad.budget_id.id),('date_start','<=',move.date),
                                                                             ('date_end','>=',move.date)],limit=1)
                                        certificate_line_ids = cert_line.search(cr, uid, [('budget_post','=',account_gad.budget_id.id),('budget_id','=',item_ids[0])])
                                        if not certificate_line_ids:
                                            raise osv.except_osv(('Error de configuracion!'), ('La partida de ingreso por descuento rol no tiene certificado'))
                                        monto = line.credit
                                        cert_ingreso = cert_line.browse(cr, uid, certificate_line_ids[0])
                                        b_id = cert_ingreso.budget_id.id
                                        p_id = cert_ingreso.budget_post.id
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_2,account_gad.id,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,certificate_line_ids[0],b_id,p_id,'Ingreso Gad',False,True,partner_id))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_2,cxp,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,certificate_line_ids[0],b_id,p_id,'Ingreso Gad',False,False,partner_id))
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_2,cxp,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,certificate_line_ids[0],b_id,p_id,'Ingreso Gad',False,True,partner_id))
                                    else:
                                        nocobraBand=False
                                        param_no_ids = parameter_obj.search(cr, uid, [('key','=','rolnocobrado')],limit=1)
                                        if param_no_ids and line.name=='neto':
                                            aux_cta_nocobro = parameter_obj.browse(cr, uid, param_no_ids[0]).value
                                            cta_no_cobro_aux_ids = account_obj.search(cr, uid, [('code','=',aux_cta_nocobro)])
                                            nocobraBand = True
                                        monto_banco += line.monto
                                        cr.execute('''
                                        INSERT INTO account_move_line (
                                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,line.account_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.budget_id_cert.id,b_id,p_id,line.name,False,True,partner_id))
                        else:
                            monto_banco += line.monto
                    if not this.bank_id.default_debit_account_id:
                        raise osv.except_osv(('Error de configuracion!'), ('El banco no tiene asociada cuentas contables'))
                monto_banco = monto_banco - aux_total_no_cobra
                move_line_obj.create(cr, uid, {
                    'account_id':this.bank_id.default_debit_account_id.id,
                    'credit':monto_banco,
                    'move_id':move_id,
                    'partner_id':move.partner_id.id,
                })
                if nocobraBand and cta_no_cobro_aux_ids:
                    if aux_total_no_cobra>0:
                        #mando ala 212
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)''',(move_id,cta_no_cobro_aux_ids[0],aux_total_no_cobra,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'No Pagado Rol',False,False,partner_id))
            # es pago normal no nomina
            else:
                if not this.line_ids:
                    raise osv.except_osv(('Error de usuario!'), 
                                         ('NO a cargado las cuentas por pagar, por favor dar click en el boton CARGAR CUENTAS POR PAGAR de este formulario'))
                for line in move_origen.line_id:
                    if line.account_id.code[0:3]!='112':
                        if 'IVA' in line.account_id.name and line.credit>0:
                            aux_iva += line.credit
                        elif 'iva' in line.account_id.name and line.credit>0:
                            aux_iva += line.credit
                        elif 'Iva' in line.account_id.name and line.credit>0:
                            aux_iva += line.credit
                        elif 'I.V.A' in line.account_id.name and line.credit>0:
                            aux_iva += line.credit
                        elif 'I.V.A.' in line.account_id.name and line.credit>0:
                            aux_iva += line.credit
                        elif line.name=='Iva':
                            aux_iva += line.credit
                for line in this.line_ids:
                    partner_id = move.partner_id.id
                    #verificar el iva que esta por pagar
                    if line.to_pay:
                        if line.budget_id_cert:
                            b_id = line.budget_id_cert.budget_id.id
                            p_id = line.budget_id_cert.budget_post.id
                            if line.monto!=0:
                                if line.partner_id:
                                    partner_id = line.partner_id.id
                                if not line.account_id2:
                                    monto_banco += line.monto
                                    cr.execute('''
                                    INSERT INTO account_move_line (
                                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id,move_line_cxp) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,line.account_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.budget_id_cert.id,b_id,p_id,line.name,False,True,partner_id,line.id))
                                    pago_obj.create(cr, uid, {
                                        'line_id':line.id,
        #                                'line_move_id':line_id,
                                        'monto_pagado':line.monto,
                                    })
                                else:
                                    #aqui cambiado 4 oct pago perp
                                    if line.account_id2:
                                        if line.judicial_decimo>0:
                                            cr.execute('''
                                            INSERT INTO account_move_line (
                                            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_2,line.account_id.id,line.judicial_decimo,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.budget_id_cert.id,b_id,p_id,line.name,False,True,partner_id))
                                            cr.execute('''
                                            INSERT INTO account_move_line (
                                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)''',(move_id_2,line.account_id2.id,line.judicial_decimo,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.name,False,False,partner_id))
                                            #y sumo al banco la diferencia
                                            aux_diferencia = line.monto - line.judicial_decimo
                                            monto_banco += aux_diferencia
                                            cr.execute('''
                                            INSERT INTO account_move_line (
                                            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_2,line.account_id.id,aux_diferencia,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.budget_id_cert.id,b_id,p_id,line.name,False,True,partner_id))
                                            pago_obj.create(cr, uid, {
                                                'line_id':line.id,
                                                #                                    'line_move_id':line_id,
                                                'monto_pagado':line.monto,
                                            })
                                        else:
                                            cr.execute('''
                                            INSERT INTO account_move_line (
                                            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_paid,partner_id,move_line_cxp) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_2,line.account_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.budget_id_cert.id,b_id,p_id,line.name,False,True,partner_id,line.id))
                                            cr.execute('''
                                            INSERT INTO account_move_line (
                                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,partner_id,move_line_cxp) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)''',(move_id_2,line.account_id2.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line.name,False,False,partner_id,line.id))
                                            pago_obj.create(cr, uid, {
                                                'line_id':line.id,
            #                                    'line_move_id':line_id,
                                                'monto_pagado':line.monto,
                                            })
                        else:
                            monto_banco += line.monto
                #cuenta por cobrar a gobierno central
                if aux_iva>0 and this.genera_cxc:
                    aux_narration = "MINISTERIO DE ECONOMIA Y FINANZAS - REGISTRO DEL IVA A RECUPERAR SEGUN EL COMPROBANTE DE PAGO Nro. " + move.name + ' - ' + 'A FAVOR DE ' + move.partner_id.name
                    cxc_ids = parameter_obj.search(cr, uid, [('key','=','cxcgob')],limit=1)
                    if not cxc_ids:
                        raise osv.except_osv(('Error de configuracion!'), ('Configure el parametro de cuenta por cobrar a gobierno central'))
                    aux_cxc = parameter_obj.browse(cr, uid, cxc_ids[0]).value
                    account_cxc_ids = account_obj.search(cr, uid, [('code','=',aux_cxc)],limit=1)
                    if not account_cxc_ids:
                        raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta contable configurada en parametros para gobierno central'))
                    account_cxc = account_obj.browse(cr, uid, account_cxc_ids[0])
                    if not account_cxc.account_rec_id:
                        raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta por cobrar de la cuenta gobierno central'))
                    cxp = account_cxc.account_rec_id.id
                    if not account_cxc.budget_id:
                        raise osv.except_osv(('Error de configuracion!'), ('No existe partida asociada a la cuenta de gobierno central'))
                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',account_cxc.budget_id.id),('date_start','<=',move.date),
                                                         ('date_end','>=',move.date)],limit=1)
                    if not item_ids:
                        raise osv.except_osv(('Error de configuracion!'), ('No existe item de partida presupuestaria para %s')%(account_cxc.budget_id.code))
                    certificate_line_ids = cert_line.search(cr, uid, [('budget_post','=',account_cxc.budget_id.id),('budget_id','=',item_ids[0])])
                    if not certificate_line_ids:
                        raise osv.except_osv(('Error de configuracion!'), ('La partida de gobierno central no tiene certificado'))
                    #si cta cobrar iva en el mismo comprobante
                    devIva_ids = parameter_obj.search(cr, uid, [('key','=','devIvaComprobante')],limit=1)
                    if devIva_ids:
                        devIva = parameter_obj.browse(cr, uid, devIva_ids[0]).value
                        if devIva=='Si':
                            move_line_obj.create(cr, uid, {
                                'move_id':move_id_2,
                                'account_id':account_cxc.id,
                                'credit':aux_iva,
                                'budget_id_cert':certificate_line_ids[0],
                                'budget_accrued':True,
                                'partner_id':move.partner_id.id,
                            })
                            move_line_obj.create(cr, uid, {
                                'move_id':move_id_2,
                                'account_id':cxp,
                                'debit':aux_iva,
                                'budget_id_cert':certificate_line_ids[0],
                                'partner_id':move.partner_id.id,
                            })      
                    else:
                        move_id2 = move_obj.create(cr, uid,{
                            'journal_id':move.journal_id.id,
                            'period_id':move.period_id.id,
                            'date':move.date,
                            'partner_id':move.partner_id.id,
                            'afectacion':True,
                            'type':'Recaudacion',
                            'no_cp':True,
                            'narration':aux_narration,
                            'ref':aux_narration,
                        })
                        move_line_obj.create(cr, uid, {
                            'move_id':move_id2,
                            'account_id':account_cxc.id,
                            'credit':aux_iva,
                            'budget_id_cert':certificate_line_ids[0],
                            'budget_accrued':True,
                            'partner_id':move.partner_id.id,
                        })
                        move_line_obj.create(cr, uid, {
                            'move_id':move_id2,
                            'account_id':cxp,
                            'debit':aux_iva,
                            'budget_id_cert':certificate_line_ids[0],
                            'partner_id':move.partner_id.id,
                        })
                #banco
                #descontar si es ordenanza o incumplimiento
                if this.amount_ord>0:
                    #partida parametros ord
                    ord_ids = parameter_obj.search(cr, uid, [('key','=','ord')],limit=1)
                    if not ord_ids:
                        raise osv.except_osv(('Error de configuracion!'), ('Configure el parametro de cuenta de ingreso por ordenanza'))
                    aux_ord = parameter_obj.browse(cr, uid, ord_ids[0]).value
                    account_ord_ids = account_obj.search(cr, uid, [('code','=',aux_ord)],limit=1)
                    if not account_ord_ids:
                        raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta contable configurada en parametros'))
                    account_ord = account_obj.browse(cr, uid, account_ord_ids[0])
                    if not account_ord.account_rec_id:
                        raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta por cobrar de la cuenta ordenanza configurada'))
                    cxp = account_ord.account_rec_id.id
                    if not account_ord.budget_id:
                        raise osv.except_osv(('Error de configuracion!'), ('No existe partida asociada a la cuenta ordenanza configurada'))
                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',account_ord.budget_id.id),('date_start','<=',move.date),
                                                         ('date_end','>=',move.date)],limit=1)
                    certificate_line_ids = cert_line.search(cr, uid, [('budget_post','=',account_ord.budget_id.id),('budget_id','=',item_ids[0])])
                    if not certificate_line_ids:
                        raise osv.except_osv(('Error de configuracion!'), ('La partida de ordenanza no tiene certificado'))
                    monto = this.amount_ord
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':account_ord.id,
                        'credit':monto,
                        'budget_id_cert':certificate_line_ids[0],
                        'budget_accrued':True,
                        'partner_id':move.partner_id.id,
                    })
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':cxp,
                        'debit':monto,
                        'budget_id_cert':certificate_line_ids[0],
                        'partner_id':move.partner_id.id,
                    })
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':cxp,
                        'credit':monto,
                        'budget_id_cert':certificate_line_ids[0],
                        'budget_paid':True,
                        'partner_id':move.partner_id.id,
                    })
                    monto_banco -= this.amount_ord
                if this.amount_inc>0:
                    #partida paramentros inc
                    inc_ids = parameter_obj.search(cr, uid, [('key','=','inc')],limit=1)
                    if not inc_ids:
                        raise osv.except_osv(('Error de configuracion!'), ('Configure el parametro de cuenta de ingreso por incumplimiento'))
                    aux_inc = parameter_obj.browse(cr, uid, inc_ids[0]).value
                    account_inc_ids = account_obj.search(cr, uid, [('code','=',aux_inc)],limit=1)
                    if not account_inc_ids:
                        raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta contable configurada en parametros para incumplimiento'))
                    account_inc = account_obj.browse(cr, uid, account_inc_ids[0])
                    if not account_inc.account_rec_id:
                        raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta por cobrar de la cuenta incumplimiento configurada'))
                    cxp = account_inc.account_rec_id.id
                    if not account_inc.budget_id:
                        raise osv.except_osv(('Error de configuracion!'), ('No existe partida asociada a la cuenta incumplimiento configurada'))
                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',account_inc.budget_id.id),('date_start','<=',move.date),('date_end','>=',move.date)],limit=1)
                    certificate_line_ids = cert_line.search(cr, uid, [('budget_post','=',account_inc.budget_id.id),('budget_id','=',item_ids[0])])
                    if not certificate_line_ids:
                        raise osv.except_osv(('Error de configuracion!'), ('La partida de incumplimiento no tiene certificado'))
                    monto = this.amount_inc
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':account_inc.id,
                        'credit':monto,
                        'budget_id_cert':certificate_line_ids[0],
                        'budget_accrued':True,
                        'partner_id':move.partner_id.id,
                    })
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':cxp,
                        'debit':monto,
                        'budget_id_cert':certificate_line_ids[0],
                        'partner_id':move.partner_id.id,
                    })
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':cxp,
                        'credit':monto,
                        'budget_id_cert':certificate_line_ids[0],
                        'budget_paid':True,
                        'partner_id':move.partner_id.id,
                    })
                    monto_banco -= this.amount_inc
                #anticipo restar y crear el move
                if this.anticipo_id and this.monto_anticipo>0:
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':this.anticipo_id.id,
                        'credit':this.monto_anticipo,
                        'name':'Anticipo Devengado',
                        'partner_id':move.partner_id.id,
                    })
                    #es anio anterior tiene mas moves
                    if not this.anio_ant:
                        anticipo_ant_ids = parameter_obj.search(cr, uid, [('key','=','cuentaanticipoanterior')],limit=1)
                        if not anticipo_ant_ids:
                            raise osv.except_osv(('Error de configuracion!'), ('Configure el parametro de cuenta anticipo de anio anterior'))
                        aux_anticipo_ant = parameter_obj.browse(cr, uid, anticipo_ant_ids[0]).value
                        if aux_anticipo_ant=='Varias':
                            if not this.anticipo_id.budget_id:
                                raise osv.except_osv(('Error de configuracion!'), ('La cuenta de anticipo no tiene configurada la partida'))
                            item_antic_ant = item_obj.search(cr, uid, [('budget_post_id','=',this.anticipo_id.budget_id.id),('date_start','<=',move.date),
                                                                       ('date_end','>=',move.date)],limit=1)
                            certificate_line_ids = cert_line.search(cr, uid, [('budget_post','=',this.anticipo_id.budget_id.id),('budget_id','=',item_antic_ant[0])])
                            if not certificate_line_ids:
                                raise osv.except_osv(('Error de configuracion!'), ('La partida de anticipos anios anteriores no esta planificada'))
                            if not this.anticipo_id.account_rec_id:
                                raise osv.except_osv(('Error de configuracion!'), ('La cuenta de anticipo no tiene cuenta de cobro configurada'))
                            account_ant_anterior = this.anticipo_id.account_rec_id
                        else:
                            ## con esto toma directo la partida atada a la cuenta seleccionada 124
                            anticipo_ant_ids_2 = parameter_obj.search(cr, uid, [('key','=','cuentaanticipoanterior124')],limit=1)
                            if anticipo_ant_ids_2:
                                #considerar la 11397 que sea
                                account_11397_ids = account_obj.search(cr, uid, [('budget_id','=',this.anticipo_id.budget_id.id),('code','like','11397')])
                                if account_11397_ids:
                                    account_ant_anterior = account_obj.browse(cr, uid, account_11397_ids[0])
                            else:
                                account_anticipo_ant_ids = account_obj.search(cr, uid, [('code','=',aux_anticipo_ant)],limit=1)
                                if not account_anticipo_ant_ids:
                                    raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta contable configurada en parametros de anticipo anterior'))
                                account_ant_anterior = account_obj.browse(cr, uid, account_anticipo_ant_ids[0])
                            if not account_ant_anterior.budget_id:
                                raise osv.except_osv(('Error de configuracion!'), ('La cuenta contable de anio anterior no tiene configurada la partida'))
                            item_antic_ant = item_obj.search(cr, uid, [('budget_post_id','=',account_ant_anterior.budget_id.id),('date_start','<=',move.date),
                                                                       ('date_end','>=',move.date)],limit=1)
                            certificate_line_ids = cert_line.search(cr, uid, [('budget_post','=',account_ant_anterior.budget_id.id),('budget_id','=',item_antic_ant[0])])
                            if not certificate_line_ids:
                                raise osv.except_osv(('Error de configuracion!'), ('La partida de anticipos anios anteriores no esta planificada'))
                        move_line_obj.create(cr, uid, {
                            'move_id':move_id,
                            'account_id':account_ant_anterior.id,
                            'debit':this.monto_anticipo,
                            'budget_id_cert':certificate_line_ids[0],
                            'budget_accrued':True,
                            'partner_id':move.partner_id.id,
                        })
                        move_line_obj.create(cr, uid, {
                            'move_id':move_id,
                            'account_id':account_ant_anterior.id,
                            'credit':this.monto_anticipo,
                            'budget_id_cert':certificate_line_ids[0],
                            'budget_paid':True,
                            'partner_id':move.partner_id.id,
                        })
                    monto_banco -= this.monto_anticipo
                if not this.bank_id.default_debit_account_id:
                    raise osv.except_osv(('Error de configuracion!'), ('El banco no tiene asociada cuentas contables'))
                if monto_banco!=0:
                    move_line_obj.create(cr, uid, {
                        'account_id':this.bank_id.default_debit_account_id.id,
                        'credit':monto_banco,
                        'move_id':move_id,
                        'partner_id':move.partner_id.id,
                    })
        return {'type':'ir.actions.act_window_close' }
    
    _defaults = dict(
        genera_cxc = True,
    )

makePayInc()

#gastpos gestion
class loadGestion(osv.TransientModel):
    _inherit = 'load.gestion'
    
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
#        if move.certificate_id:
#            for c_line in move.certificate_id.line_ids:
#                if c_line.budget_post.code[0:1]=='7':
#                    aux_gestion += c_line.amount_commited
#cambiado que tome solo devengado de inversion
        for line in move.line_id:
            if line.budget_accrued:
                if line.budget_id_cert.budget_post.code[0:1]=='7':
                    aux_gestion += (line.credit+line.debit)
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
##
class loadAnticipoLine(osv.TransientModel):
    _name = 'load.anticipo.line'
    _columns = dict(
        l_id = fields.many2one('load.anticipo','Pago'),
        account_id = fields.many2one('account.account','Cuenta por pagar'),
        account_id2 = fields.many2one('account.account','Cuenta por pagar tercero'),
        monto = fields.float('Monto'),
        to_pay = fields.boolean('Pagar'),
        cert_id = fields.many2one('budget.certificate.line','Linea certificado'),
    )

    _defaults = dict(
        to_pay = True,
    )
loadAnticipoLine()

class loadAnticipo(osv.TransientModel):
    _name = 'load.anticipo'

    def devengaAnticipo(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        dev_obj = self.pool.get('voucher.devengado')
        post_obj = self.pool.get('budget.post')
        item_obj = self.pool.get('budget.item')
        account_obj = self.pool.get('account.account')
        cert_line = self.pool.get('budget.certificate.line')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        parameter_obj = self.pool.get('ir.config_parameter')
        for this in self.browse(cr, uid, ids):
            if not this.monto_devengar>0 or this.monto_devengar>this.anticipo_id.saldo:
                raise osv.except_osv(('Error de usuario!'), ('Por favor verifique el monto a devengar y el saldo que tiene disponible'))
            move_line_id = context and context.get('active_id', False) or False
            move_line = move_line_obj.browse(cr, uid, move_line_id)
            move = move_line.move_id
            move_id = move.id
            aux_iva = 0
            for line in move.line_id:
                if line.account_id.code[0:3]!='112':
                    if 'IVA' in line.account_id.name and line.credit>0:
                        aux_iva += line.credit
                    elif 'iva' in line.account_id.name and line.credit>0:
                        aux_iva += line.credit
                    elif 'Iva' in line.account_id.name and line.credit>0:
                        aux_iva += line.credit
                    elif 'I.V.A' in line.account_id.name and line.credit>0:
                        aux_iva += line.credit
                    elif 'I.V.A.' in line.account_id.name and line.credit>0:
                        aux_iva += line.credit
                    elif line.name=='Iva':
                        aux_iva += line.credit                
#                if 'IVA' or 'iva' or 'I.V.A'or 'I.V.A.' in line.account_id.name and line.credit>0:
#                    aux_iva += line.credit            
            #el monto es el total del devengado de la planilla OJO
            aux_gestion = 0 
#            if move.certificate_id:
#                for c_line in move.certificate_id.line_ids:
#                    if c_line.budget_post.code[0:1]=='7':
#                        aux_gestion += c_line.amount_commited
            for line in move.line_id:
                if line.budget_accrued:
                    if line.budget_id_cert.budget_post.code[0:1]=='7':
                        aux_gestion += (line.credit+line.debit)
            aux_narration = ""
            monto_banco = 0
            p_id = move.partner_id.id
            for line in this.line_ids:
                if line.to_pay:
                    if line.monto>0:
                        monto_banco += line.monto
                        move_line_obj.create(cr, uid, {
                            'account_id':line.account_id.id,
                            'debit':line.monto,
                            'budget_id_cert':line.cert_id.id,
                            'budget_paid':True,
                            'move_id':move_id,
                            'partner_id':p_id,
                           })
                if line.account_id2:
                    move_line_obj.create(cr, uid, {
                        'account_id':line.account_id.id,
                        'debit':line.monto,
                        'move_id':move_id,
                        'partner_id':p_id,
                    })
                    move_line_obj.create(cr, uid, {
                        'account_id':line.account_id2.id,
                        'credit':line.monto,
                        'move_id':move_id,
                        'partner_id':p_id,
                    })  
            #pasar anticipo
            #buscar partida 380101
            #if this.anio=='Anterior':
            date_inicio = move.period_id.fiscalyear_id.date_start
            if this.anticipo_id.date<date_inicio:
                parameter_obj = self.pool.get('ir.config_parameter')
                if this.tipo=='Obra':
                    pxc_ids = parameter_obj.search(cr, uid, [('key','=','pxco')],limit=1)
                else:
                    pxc_ids = parameter_obj.search(cr, uid, [('key','=','pxcb')],limit=1)
                if pxc_ids:
                    code_post = parameter_obj.browse(cr, uid, pxc_ids[0]).value
                    post_ids = post_obj.search(cr, uid, [('code','=',code_post)],limit=1)
                    if post_ids:
                        item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),
                                                             ('year_id','=',move.period_id.fiscalyear_id.id)],limit=1)
                        if item_ids:
                            cert_line_ids = certificate_line_obj.search(cr, uid, [('budget_id','=',item_ids[0])])
                move_line_obj.create(cr, uid, {
                    'account_id':this.account_id2.id,
                    'debit':this.monto_devengar,
                    'budget_id_cert':cert_line_ids[0],
                    'budget_paid':True,
                    'move_id':move_id,
                    'partner_id':p_id,
                })
                move_line_obj.create(cr, uid, {
                    'account_id':this.account_id2.id,
                    'credit':this.monto_devengar,
                    'budget_id_cert':cert_line_ids[0],
                    'budget_accrued':True,
                    'move_id':move_id,
                    'partner_id':p_id,
                })
                move_line_obj.create(cr, uid, {
                    'account_id':this.account_id.id,
                    'credit':this.monto_devengar,
                    'budget_id_cert':cert_line_ids[0],
                    'move_id':move_id,
                    'partner_id':p_id,
                })
            else:
                move_line_obj.create(cr, uid, {
                    'account_id':this.account_id.id,
                    'credit':this.monto_devengar,
                    'move_id':move_id,
                    'partner_id':p_id,
                })
            #gastos de gestion
            if this.gestion:
                if this.acc_g1 and this.acc_g2:
                    move_line_obj.create(cr, uid, {
                        'account_id':this.acc_g1.id,
                        'debit':aux_gestion,
                        'move_id':move_id,
                        'partner_id':p_id,
                    })
                    move_line_obj.create(cr, uid, {
                        'account_id':this.acc_g2.id,
                        'credit':aux_gestion,
                        'move_id':move_id,
                        'partner_id':p_id,
                    })
            #descuentos de ordenanza
            if this.amount_ord>0:
                #partida parametros ord
                ord_ids = parameter_obj.search(cr, uid, [('key','=','ord')],limit=1)
                if not ord_ids:
                    raise osv.except_osv(('Error de configuracion!'), ('Configure el parametro de cuenta de ingreso por ordenanza'))
                aux_ord = parameter_obj.browse(cr, uid, ord_ids[0]).value
                account_ord_ids = account_obj.search(cr, uid, [('code','=',aux_ord)],limit=1)
                if not account_ord_ids:
                    raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta contable configurada en parametros'))
                account_ord = account_obj.browse(cr, uid, account_ord_ids[0])
                if not account_ord.account_rec_id:
                    raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta por cobrar de la cuenta ordenanza configurada'))
                cxp = account_ord.account_rec_id.id
                if not account_ord.budget_id:
                    raise osv.except_osv(('Error de configuracion!'), ('No existe partida asociada a la cuenta ordenanza configurada'))
                item_ids = item_obj.search(cr, uid, [('budget_post_id','=',account_ord.budget_id.id),('date_start','<=',move.date),
                                                     ('date_end','>=',move.date)],limit=1)
                certificate_line_ids = cert_line.search(cr, uid, [('budget_post','=',account_ord.budget_id.id),('budget_id','=',item_ids[0])])
                if not certificate_line_ids:
                    raise osv.except_osv(('Error de configuracion!'), ('La partida de ordenanza no tiene certificado'))
                monto = this.amount_ord
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':account_ord.id,
                    'credit':monto,
                    'budget_id_cert':certificate_line_ids[0],
                    'budget_accrued':True,
                    'partner_id':p_id,
                })
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':cxp,
                    'debit':monto,
                    'partner_id':p_id,
                    'budget_id_cert':certificate_line_ids[0],
                })
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':cxp,
                    'credit':monto,
                    'partner_id':p_id,
                    'budget_id_cert':certificate_line_ids[0],
                    'budget_paid':True,
                })
                monto_banco -= this.amount_ord
            if this.amount_inc>0:
                #partida paramentros inc
                inc_ids = parameter_obj.search(cr, uid, [('key','=','inc')],limit=1)
                if not inc_ids:
                    raise osv.except_osv(('Error de configuracion!'), ('Configure el parametro de cuenta de ingreso por incumplimiento'))
                aux_inc = parameter_obj.browse(cr, uid, inc_ids[0]).value
                account_inc_ids = account_obj.search(cr, uid, [('code','=',aux_inc)],limit=1)
                if not account_inc_ids:
                    raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta contable configurada en parametros para incumplimiento'))
                account_inc = account_obj.browse(cr, uid, account_inc_ids[0])
                if not account_inc.account_rec_id:
                    raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta por cobrar de la cuenta incumplimiento configurada'))
                cxp = account_inc.account_rec_id.id
                if not account_inc.budget_id:
                    raise osv.except_osv(('Error de configuracion!'), ('No existe partida asociada a la cuenta incumplimiento configurada'))
                item_ids = item_obj.search(cr, uid, [('budget_post_id','=',account_inc.budget_id.id),('date_start','<=',move.date),('date_end','>=',move.date)],limit=1)
                certificate_line_ids = cert_line.search(cr, uid, [('budget_post','=',account_inc.budget_id.id),('budget_id','=',item_ids[0])])
                if not certificate_line_ids:
                    raise osv.except_osv(('Error de configuracion!'), ('La partida de incumplimiento no tiene certificado'))
                monto = this.amount_inc
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':account_inc.id,
                    'credit':monto,
                    'budget_id_cert':certificate_line_ids[0],
                    'budget_accrued':True,
                    'partner_id':p_id,
                })
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':cxp,
                    'debit':monto,
                    'partner_id':p_id,
                    'budget_id_cert':certificate_line_ids[0],
                })
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':cxp,
                    'partner_id':p_id,
                    'credit':monto,
                    'budget_id_cert':certificate_line_ids[0],
                    'budget_paid':True,
                })
                monto_banco -= this.amount_inc
            #iva a recuperar
            if aux_iva>0 and this.genera_cxc:
                aux_narration = "MINISTERIO DE ECONOMIA Y FINANZAS - REGISTRO DEL IVA A RECUPERAR SEGUN EL COMPROBANTE DE PAGO Nro. " + move.name + ' - ' + 'A FAVOR DE ' + move.partner_id.name
                move_id2 = move_obj.create(cr, uid,{
                    'journal_id':move.journal_id.id,
                    'period_id':move.period_id.id,
                    'date':move.date,
                    'partner_id':move.partner_id.id,
                    'afectacion':True,
                    'type':'Recaudacion',
                    'no_cp':True,
                    'narration':aux_narration,
                    'ref':aux_narration,
                })
                cxc_ids = parameter_obj.search(cr, uid, [('key','=','cxcgob')],limit=1)
                if not cxc_ids:
                    raise osv.except_osv(('Error de configuracion!'), ('Configure el parametro de cuenta por cobrar a gobierno central'))
                aux_cxc = parameter_obj.browse(cr, uid, cxc_ids[0]).value
                account_cxc_ids = account_obj.search(cr, uid, [('code','=',aux_cxc)],limit=1)
                if not account_cxc_ids:
                    raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta contable configurada en parametros para gobierno central'))
                account_cxc = account_obj.browse(cr, uid, account_cxc_ids[0])
                if not account_cxc.account_rec_id:
                    raise osv.except_osv(('Error de configuracion!'), ('No existe la cuenta por cobrar de la cuenta gobierno central'))
                cxp = account_cxc.account_rec_id.id
                if not account_cxc.budget_id:
                    raise osv.except_osv(('Error de configuracion!'), ('No existe partida asociada a la cuenta de gobierno central'))
                item_ids = item_obj.search(cr, uid, [('budget_post_id','=',account_cxc.budget_id.id),('date_start','<=',move.date),
                                                     ('date_end','>=',move.date)],limit=1)
                certificate_line_ids = cert_line.search(cr, uid, [('budget_post','=',account_cxc.budget_id.id),('budget_id','=',item_ids[0])])
                if not certificate_line_ids:
                    raise osv.except_osv(('Error de configuracion!'), ('La partida de gobierno central no tiene certificado'))
                move_line_obj.create(cr, uid, {
                    'move_id':move_id2,
                    'account_id':account_cxc.id,
                    'credit':aux_iva,
                    'budget_id_cert':certificate_line_ids[0],
                    'budget_accrued':True,
                    'partner_id':move.partner_id.id,
                })
                move_line_obj.create(cr, uid, {
                    'move_id':move_id2,
                    'account_id':cxp,
                    'partner_id':move.partner_id.id,
                    'debit':aux_iva,
                    'budget_id_cert':certificate_line_ids[0],
                })            
            #banco
            monto_banco = monto_banco - this.monto_devengar
            if not this.bank_id.default_debit_account_id:
                raise osv.except_osv(('Error de configuracion!'), ('El banco no tiene asociada cuentas contables'))
            move_line_obj.create(cr, uid, {
                'account_id':this.bank_id.default_debit_account_id.id,
                'credit':monto_banco,
                'move_id':move_id,
                'partner_id':p_id,
            })
            dev_obj.create(cr, uid, {
                'voucher_id':this.anticipo_id.id,
                'name':move_id,
                'date':move.date,
                'monto':this.monto_devengar,
            })
        return {'type':'ir.actions.act_window_close' }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        pay_line_obj = self.pool.get('load.anticipo.line')
        sri_obj = self.pool.get('pay.fondo.sri')
        account_obj = self.pool.get('account.account')
        line_ids = []
        res = {}
        record_id = context and context.get('active_id', False) or False
        move_line = self.pool.get('account.move.line').browse(cr, uid, record_id, context=context)
        move = move_line.move_id
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
                    if account_sri:
                        pay_line_id = pay_line_obj.create(cr, uid, {
                            'cert_id':line.budget_id_cert.id,
                            'account_id':line.account_id.id,
                            'account_id2':account_sri,
                            'monto':line.credit,
                        })
                    else:
                        pay_line_id = pay_line_obj.create(cr, uid, {
                            'cert_id':line.budget_id_cert.id,
                            'account_id':line.account_id.id,
                            'monto':line.credit,
                        })
                    line_ids.append(pay_line_id)
        #carga banco automatico
        parameter_obj = self.pool.get('ir.config_parameter')
        bank_ids = parameter_obj.search(cr, uid, [('key','=','anticipo')],limit=1)
        journal_pool = self.pool.get('account.journal')
        if bank_ids:
            bank_name = parameter_obj.browse(cr, uid, bank_ids[0]).value
            j_ids = journal_pool.search(cr, uid, [('name','=',bank_name)],limit=1)
        else:
            j_ids = journal_pool.search(cr, uid, [('type', '=', 'bank')], limit=1)
        ####
        acc_g1_ids = parameter_obj.search(cr, uid, [('key','=','acc_g1')],limit=1)
        acc_g2_ids = parameter_obj.search(cr, uid, [('key','=','acc_g2')],limit=1)
        if acc_g1_ids and acc_g2_ids:
            aux_code_g1 = parameter_obj.browse(cr, uid, acc_g1_ids[0]).value
            account_g1_ids = account_obj.search(cr, uid, [('code','=',aux_code_g1)],limit=1)
            aux_code_g2 = parameter_obj.browse(cr, uid, acc_g2_ids[0]).value
            account_g2_ids = account_obj.search(cr, uid, [('code','=',aux_code_g2)],limit=1)
            res.update({
                'move_id':move.id,
                'bank_id':j_ids[0],
                'line_ids':line_ids,
                'partner_id':move.partner_id.id,
                'certificate_line_id':move_line.budget_id_cert.id,
                'acc_g1':account_g1_ids[0],
                'acc_g2':account_g2_ids[0],
                'gestion':True,
                'genera_cxc':True,
            })
        else:
            res.update({
                'move_id':move.id,
                'bank_id':j_ids[0],
                'line_ids':line_ids,
                'partner_id':move.partner_id.id,
                'certificate_line_id':move_line.budget_id_cert.id,
                'genera_cxc':True,
            })
        return res

    def onchange_ma(self, cr, uid, ids, anticipo_id, context={}):
        return True
        raise osv.except_osv('Error de usuario', 'No puede modificar este valor')

    def onchange_sa(self, cr, uid, ids, anticipo_id, context={}):
        return True
        raise osv.except_osv('Error de usuario', 'No puede modificar este valor')

    def onchange_loadanticipo(self, cr, uid, ids, anticipo_id,move_id, context={}):
        move_obj = self.pool.get('account.move')
        account_obj = self.pool.get('account.account')
        ant_obj = self.pool.get('account.voucher')
        load_obj = self.pool.get('load.anticipo')
        parameter_obj = self.pool.get('ir.config_parameter')
        ant = ant_obj.browse(cr, uid, anticipo_id)
        move = move_obj.browse(cr, uid, move_id)
        vals = {}
        date_inicio = move.period_id.fiscalyear_id.date_start
        if ant.tipo:
            result = {'value':{'tipo':ant.tipo,
                         }} 
        if ant.date<date_inicio:
            ##cuentas de anticipo
            if account_id2:
                account_id2 = ant.line_dr_ids[0].account_id.id
            acc11_ids = parameter_obj.search(cr, uid, [('key','=','cc11')],limit=1)
            if acc11_ids:
                code_aux = parameter_obj.browse(cr, uid, acc11_ids[0]).value
                account_ids = account_obj.search(cr, uid, [('code','=',code_aux)],limit=1)
                if account_ids:
                    account_id2 = account_ids[0]
            account_id = ant.line_dr_ids[0].account_id.id
            acc124_ids = parameter_obj.search(cr, uid, [('key','=','cc124')],limit=1)
            if acc124_ids:
                code_aux = parameter_obj.browse(cr, uid, acc124_ids[0]).value
                account_ids = account_obj.search(cr, uid, [('code','=',code_aux)],limit=1)
                if account_ids:
                    account_id = account_ids[0]
            result = {'value':{'anio':'Anterior',
                               'monto_anticipo':ant.amount,
                               'saldo_anticipo':ant.saldo,
                               'account_id2':account_id2,
                               'account_id':account_id,
                               'genera_cxc':True,
                           }} 
        else:
            if ant.line_dr_ids:
                result = {'value':{'anio':'Actual',
                                   'monto_anticipo':ant.amount,
                                   'saldo_anticipo':ant.saldo,
                                   'account_id':ant.line_dr_ids[0].account_id.id,
                                   'account_id2':ant.line_dr_ids[0].account_id.id,
                                   'genera_cxc':True,
                               }}
            elif ant.partner_id.anticipo_id:
                result = {'value':{'anio':'Actual',
                                   'monto_anticipo':ant.amount,
                                   'saldo_anticipo':ant.saldo,
                                   'account_id':ant.partner_id.anticipo_id.id,
                                   'account_id2':ant.partner_id.anticipo_id.id,
                                   'genera_cxc':True,
                               }}
            else:
                #tomar directamente la cuenta de infraestrutura
                account_ids_2 = account_obj.search(cr, uid, [('code','=','1120301001')])
                if account_ids_2:
                    result = {'value':{'anio':'Actual',
                                       'monto_anticipo':ant.amount,
                                       'saldo_anticipo':ant.saldo,
                                       'account_id':account_ids_2[0],
                                       'account_id2':account_ids_2[0],
                                       'genera_cxc':True,
                                   }}
        return result

    _columns = dict(
        acc_g1 = fields.many2one('account.account','Cta. Gastos Gestion'),
        acc_g2 = fields.many2one('account.account','Contra Cta. Gastos Gestion'),
        gestion = fields.boolean('Aplicar Gastos Gestion'),
        tipo = fields.selection([('Obra','Obra'),('Bien o Servicio','Bien o Servicio')],'Tipo'),
        certificate_line_id = fields.many2one('budget.certificate.line','Cert.  Line'),
        account_id2 = fields.many2one('account.account','Cuenta por cobrar Anterior'),
        account_id = fields.many2one('account.account','Cuenta por cobrar Anticipo'),
        move_id = fields.many2one('account.move','Comprobante'),
        bank_id = fields.many2one('account.journal','Banco'),
        line_ids = fields.one2many('load.anticipo.line','l_id','Cuentas Por pagar'),
        partner_id = fields.many2one('res.partner','Beneficiario'),
        anticipo_id = fields.many2one('account.voucher','Anticipo'),
        anio = fields.selection([('Actual','Actual'),('Anterior','Anterior')],'Anio Anticipo'),
        monto_anticipo = fields.float('Monto Anticipo'),
        saldo_anticipo = fields.float('Saldo Anticipo'),
        monto_devengar = fields.float('Monto Devengar'),
        amount_ord = fields.float('Retencion Segun Ordenanza'),
        amount_inc = fields.float('Retencion Incumplimiento Contrato'),
        genera_cxc = fields.boolean('Generar cuenta cobrar iva a recuperar'),
    )
    
    _defaults = dict(
        tipo = 'Obra',
        gestion = True,
    )

loadAnticipo()
#====================
class ObraObraPago(osv.Model):
    _name = 'obra.obra.pago'
    _columns = dict(
        obra_id = fields.many2one('obra.obra','Obra'),
        name = fields.char('Descripcion',size=64,required=True),
        date = fields.date('Fecha Pago'),
        valor = fields.float('Monto'),
    )
ObraObraPago()

class accountMoveLineObra(osv.Model):
    _inherit = 'account.move.line'
    _columns = dict(
        
        obra_id = fields.related('move_id','obra_id',relation='obra.obra',type='many2one',store=True),
    )
accountMoveLineObra()    

class accountMoveObra(osv.Model):
    _inherit = 'account.move'
    _columns = dict(
        obra_id = fields.many2one('obra.obra','Obra Relacionada'),
#        cta_inventario = fields.many2one('account.account','Cuenta de Inventario'),
    )

accountMoveObra()

class budgetCertificateObra(osv.Model):
    _inherit = 'budget.certificate'
    _columns = dict(
        obra_id = fields.many2one('obra.obra','Obra Relacionada'),
    )
budgetCertificateObra()

class garantia(osv.Model):
    _description = 'Tipos de garantias'
    _name='garantia.garantia'
    _columns = dict(
        name = fields.char('Nombre',size=32,required=1),
        account_id = fields.many2one('account.account','Cuenta debe'),
        account_id2 = fields.many2one('account.account','Cuenta Haber'),
        porcentaje = fields.integer('Porcentaje'),
    )
garantia()

class obraGarantiaRenovacion(osv.Model):
    _name = 'obra.garantia.renovacion'
    _columns = dict(
        name = fields.char('Num. Oficio',size=128),
        g_id = fields.many2one('obra.garantia','Garantia'),
        monto = fields.float('Monto'),
        date_start = fields.date('Desde'),
        date_end = fields.date('Hasta'),
    )

    def imprimeRenovacion(self, cr, uid, ids, context):
        if not context:
            context = {}
        renovacion = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [renovacion.id],
                 'model': 'obra.garantia.renovacion'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'obra.garantia.renovacion',
            'model': 'obra.garantia.renovacion',
            'datas': datas,
            'nodestroy': True,            
                }


    def tomaSecuenciaRenovacion(self, cr, uid, ids, context):
        obj_sequence = self.pool.get('ir.sequence')
        for this in self.browse(cr, uid, ids):
            if this.name=='/':
                aux_sec = obj_sequence.get(cr, uid, 'obra.garantia.renovacion')
                self.write(cr, uid, this.id, {
                    'name':aux_sec,
                })
        return True

    _defaults = dict(
        name = '/',
    )

obraGarantiaRenovacion()

class obraGarantia(osv.Model):
    _name = 'obra.garantia'
    _columns = dict(
        carpeta = fields.integer('Num. Carpeta'),
        dias_renova = fields.integer('Dias Renovacion'),
        oficio = fields.char('Oficio',size=128),
        partner_id = fields.many2one('res.partner','Proveedor'),
        desc = fields.text('Descripcion'),
        numero = fields.char('Numero',size=32),
        renovacion_ids = fields.one2many('obra.garantia.renovacion','g_id','Renovaciones'),
        name = fields.many2one('garantia.garantia','Garantia',required=True),
        aseguradora_id = fields.many2one('res.partner','Aseguradora'),
        fecha_inicio = fields.date('Fecha Inicio'),
        fecha_fin = fields.date('Fecha Fin'),
        porcentaje = fields.integer('Porcentaje'),
        monto = fields.float('Valor Garantia'),
        obra_id = fields.many2one('obra.obra','Obra'),
        proceso_cp = fields.related('obra_id','num_proceso',type='char',size=128,string='Proceso',store=True),
        state = fields.selection([('En Tramite','En Tramite'),('Activa','Activa'),('Ejecutada','Ejecutada'),('Finalizada','Finalizada/Pasiva')],'Estado'),
    )

    def finalizaPoliza(self, cr, uid, ids, context=None):
        garantia_obj = self.pool.get('obra.garantia')
        garantia_obj.write(cr, uid, ids, {
            'state':'Finalizada',
        })

    _defaults = dict(
        state = 'En Tramite',
    )
obraGarantia()

class wizardComprobanteGarantia(osv.TransientModel):
    _name = 'wizard.comprobante.garantia'
    _columns = dict(
        date = fields.date('Fecha'),
        account_id = fields.many2one('account.account','Cuenta 1'),
        account_id2 = fields.many2one('account.account','Cuenta 2'),
        monto = fields.float('Monto'),
    )

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = {}
        record_id = context and context.get('active_id', False) or False
        obra = self.pool.get('obra.garantia').browse(cr, uid, record_id, context=context)
        monto_aux = obra.monto
        res.update({
            'monto':monto_aux,
            'account_id':obra.name.account_id.id,
            'account_id2':obra.name.account_id2.id,
        })
        return res

    def action_create_garantiaObra(self, cr, uid, ids, context):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        obra_g = self.pool.get('obra.garantia')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        garantia = obra_g.browse(cr, uid, context['active_id'])
        partner_id = garantia.partner_id.id
        journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
        if not journal_ids:
            raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
        this = self.browse(cr, uid, ids[0])
        period_ids = period_obj.find(cr, uid, garantia.fecha_inicio)
        if not period_ids:
            raise osv.except_osv('Error de configuracion', 'No existe periodo contable definido para la fecha de garantia')
        desc_aux = 'Registro Garantia: ' + ustr(garantia.desc) + 'Por: ' + str(garantia.monto)
        move_id = move_obj.create(cr, uid, {
            'journal_id':journal_ids[0],
            'period_id':period_ids[0],
            'date':garantia.fecha_inicio,
            'partner_id':partner_id,
            'type2_id':'Financiero',
            'ref':desc_aux,
            'narration':desc_aux,
        })
        move_line_obj.create(cr, uid, {
            'move_id':move_id,
            'partner_id':partner_id,
            'name':'Garantia',
            'debit':this.monto,
            'account_id':this.account_id.id,
        })
        move_line_obj.create(cr, uid, {
            'move_id':move_id,
            'partner_id':partner_id,
            'name':'Garantia',
            'credit':this.monto,
            'account_id':this.account_id2.id,
        })
        return {'type':'ir.actions.act_window_close' }

wizardComprobanteGarantia()

class obraAnticipo(osv.TransientModel):
    _name = 'wizard.create.anticipo'
    _columns = dict(
        date = fields.date('Fecha'),
        account_id = fields.many2one('account.account','Cuenta Anticipo'),
        bank_id = fields.many2one('account.journal','Banco'),
        monto = fields.float('Monto'),
        garantia = fields.boolean('Generar Movimiento Garantia?'),
        g_id = fields.many2one('garantia.garantia','Tipo Garantia'),
        monto_g = fields.float('Monto Garantia'),
    )

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = {}
        record_id = context and context.get('active_id', False) or False
        obra = self.pool.get('obra.obra').browse(cr, uid, record_id, context=context)
        monto_aux = (obra.monto * obra.porcentaje_anticipo)/100
        #cargar las cuentas de las garantias
        res.update({'partner_id':obra.partner_id.id,
                    'monto':monto_aux,
                    'monto_g':obra.monto,
                    'date':time.strftime('%Y-%m-%d'),
                })
        return res

    def action_create_anticipoObra(self, cr, uid, ids, context):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        obra_obj = self.pool.get('obra.obra')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        voucher_obj = self.pool.get('account.voucher')
        obra = obra_obj.browse(cr, uid, context['active_id'])
        partner_id = obra.partner_id.id
        journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
        if not journal_ids:
            raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
        this = self.browse(cr, uid, ids[0])
        period_ids = period_obj.search(cr, uid, [('date_start','<=',this.date),('date_stop','>=',this.date)],limit=1)
        if not period_ids:
            raise osv.except_osv('Error de configuracion', 'No existe periodo contable definido para la fecha de anticipo')
        desc_aux = 'Anticipo a ' + obra.partner_id.name + 'Por: ' + obra.name
        #tambien crea el voucher
        voucher_id = voucher_obj.create(cr, uid, {
            'partner_id':partner_id,
            'account_id':this.bank_id.default_debit_account_id.id,
            'journal_id':this.bank_id.id,
            'reference':obra.name,
            'date':this.date,
            'amount':this.monto,
            'tipo':'Obra',
            'narration':obra.name,
            'state':'posted',
            'internal_type':'AP',
        })
        move_id = move_obj.create(cr, uid, {
            'journal_id':journal_ids[0],
            'period_id':period_ids[0],
            'date':this.date,
            'partner_id':partner_id,
            'type2_id':'Financiero',
            'obra_id':obra.id,
            'ref':desc_aux,
            'narration':desc_aux,
        })
        move_line_obj.create(cr, uid, {
            'move_id':move_id,
            'partner_id':partner_id,
            'name':'Banco',
            'credit':this.monto,
            'account_id':this.bank_id.default_debit_account_id.id,
        })
        move_line_obj.create(cr, uid, {
            'move_id':move_id,
            'partner_id':partner_id,
            'name':'Anticipo',
            'debit':this.monto,
            'account_id':this.account_id.id,
        })
        obra_obj.write(cr, uid, obra.id,{'anticipo_entregado':this.monto})
        #lineas de garantia
        if this.garantia:
            move_line_obj.create(cr, uid, {
                'move_id':move_id,
                'partner_id':partner_id,
                'name':'Garantia',
                'credit':this.monto_g,
                'account_id':this.g_id.account_id2.id,
            })
            move_line_obj.create(cr, uid, {
                'move_id':move_id,
                'partner_id':partner_id,
                'name':'Garantia',
                'debit':this.monto_g,
                'account_id':this.g_id.account_id.id,
            })  
        return {'type':'ir.actions.act_window_close' }

obraAnticipo()

class relObra(osv.TransientModel):
    _name = 'wizard.rel.obra'
    _columns = dict(
        partner_id = fields.many2one('res.partner','Proveedor'),
        obra_id = fields.many2one('obra.obra','Obra'),
    )

    def action_relObra(self, cr,  uid, ids, context):
        move_obj = self.pool.get('account.move')
        invoice_obj = self.pool.get('account.invoice')
        move = invoice_obj.browse(cr, uid, context['active_id'])
        wizard = self.browse(cr, uid, ids[0])
        move_obj.write(cr, uid, [move.id],{
            'obra_id':wizard.obra_id.id,
        })
        return {'type':'ir.actions.act_window_close' }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = {}
        record_id = context and context.get('active_id', False) or False
        move = self.pool.get('account.move').browse(cr, uid, record_id, context=context)
        res.update({'partner_id':move.partner_id.id,
                })
        return res

relObra()

class projectObra(osv.Model):
    _inherit = 'project.project'
    _columns = dict(
        obra_ids = fields.one2many('obra.obra','project_id','Obras/Contratos'),
    )
projectObra()

class obraReajuste(osv.Model):
    _name = 'obra.reajuste'
    _columns = dict(
        name = fields.text('Detalle'),
        obra_id = fields.many2one('obra.obra','Obra'),
        fecha = fields.date('Fecha'),
        valor = fields.float('Valor Reajuste(Inc. IVA)'),
    )
obraReajuste()

class ObraObra(osv.Model):
    _description = 'Gestion De Obras y Contratos'
    _name = 'obra.obra'
    _order = 'date_start desc'

    def _iva(self, cr, uid, ids, a, b, c):
        this = self.browse(cr, uid, ids[0])
        res = {}
        res[this.id] = {'iva':0,'total':0,'anticipo_entregado':0,'total_reajuste':0,'total_pagado':0}
        aux_ajuste = aux_pagado = aux_saldo = aux_iva = aux_total = aux_anticipo = aux_sin_iva = p_aux = aux_total_final = 0
        if this.monto:
            if this.inc_iva:
                p_aux = 1 + (this.porcentaje_iva/100.00)
                aux_sin_iva = this.monto/p_aux
                aux_iva = this.monto - aux_sin_iva
                aux_total = this.monto
                aux_anticipo = (aux_sin_iva*this.porcentaje_anticipo)/100.00
            else:
                aux_iva = (this.monto*this.porcentaje_iva)/100.00
                aux_total = this.monto + aux_iva
                aux_anticipo = (this.monto*this.porcentaje_anticipo)/100.00
                aux_sin_iva = this.monto
            for move_line in this.pago_ids:
                if move_line.state=='posted':
                    aux_pagado = move_line.total_banco
            for reajuste_line in this.reajuste_ids:
                aux_ajuste = reajuste_line.valor
        aux_total_final = aux_total + aux_ajuste
        aux_saldo = aux_total_final - aux_pagado
        res[this.id]['monto_sin_iva'] = aux_sin_iva        
        res[this.id]['iva'] = aux_iva        
        res[this.id]['total'] = aux_total_final
        res[this.id]['anticipo_entregado'] = aux_anticipo
        res[this.id]['total_reajuste'] = aux_ajuste
        res[this.id]['total_final'] = aux_total_final
        res[this.id]['total_pagado'] = aux_pagado
        res[this.id]['saldo'] = aux_saldo
        return res

    _columns = dict(
        saldo = fields.function(_iva,string='Total Saldo',type="float",store=True,multi='total',method=True),
        total_final = fields.function(_iva,string='Total Obra',type="float",store=True,multi='total',method=True),
        total_reajuste = fields.function(_iva,string='Total Reajuste',type="float",store=True,multi='total',method=True),
        reajuste_ids = fields.one2many('obra.reajuste','obra_id','Detalle Reajustes'),
        inc_iva = fields.boolean('Monto Incluye IVA'),
        monto_sin_iva = fields.function(_iva,string='Monto sin iva',type="float",store=True,multi='total',method=True),
        secuencia = fields.integer('Secuencia'),
        fiscalizador_id = fields.many2one('res.partner','Fiscalizador',required=True),
        administrador_id = fields.many2one('res.partner','Administrador',required=True),
        garantia_ids = fields.one2many('obra.garantia','obra_id','Garantias'),
        state = fields.selection([('Borrador','Borrador'),('Ejecucion','Ejecucion'),('Finalizado','Finalizado')],'Estado',readonly=True),
        name = fields.char('Nombre Obra/Contrato',size=128,required=True),
        project_id = fields.many2one('project.project','Proyecto/Programa POA',required=True),
        partner_id = fields.many2one('res.partner','Contratista',required=True),
        porcentaje_anticipo = fields.integer('Porcentaje Anticipo'),
        monto = fields.float('Monto Obra/Contrato'),
        porcentaje_iva = fields.integer('Porcentaje IVA'),
        iva = fields.function(_iva,string='IVA',type="float",store=True,multi='total',method=True),
        total = fields.function(_iva,string='Total',type="float",store=True,multi='total',method=True),
        date_start = fields.date('Fecha Inicio'),
        date_end = fields.date('Fecha Fin'),
        date_anticipo = fields.date('Fecha Anticipo'),
        plazo = fields.integer('Plazo'),
        pay_ids = fields.one2many('obra.obra.pago','obra_id','Terminos Pago'),
        certificate_id = fields.many2one('budget.certificate','Documento Presupuestario'),
        certificate_ids = fields.one2many('budget.certificate','obra_id','Certificados Presupuestarios'),
        pago_ids = fields.one2many('account.move','obra_id','Pagos Realizados'),
        anticipo_entregado = fields.function(_iva,string='Anticipo Entregado',type="float",store=True,multi='total',method=True),
        total_pagado = fields.function(_iva,string='Total Pagado',type="float",store=True,multi='total',method=True),#fields.float('Total Pagos Planilla'),
        num_contrato = fields.char('Numero de Contrato',size=32),
        num_proceso = fields.char('Numero de Proceso',size=32),        
        observaciones = fields.text('Observaciones'),
        tipo = fields.selection([('Obra','Obra'),('Consultoria','Consultoria'),('Bien','Bien'),('Servicio','Servicio')],'Tipo'),
        tipo_fondo = fields.selection([('Propios','Propios'),('Externos','Externos')],'Tipo de fondos'),
        financiamiento = fields.many2one('budget.financiamiento','Financiamiento'),
    )

    def imprimir_obra(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        obra = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [obra.id], 'model': 'obra.obra'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'obra.obra',
            'model': 'obra.obra',
            'datas': datas,
            'nodestroy': True,                        
            }    

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        if name:
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('num_contrato', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.read(cr, uid, ids, ['id', 'num_contrato', 'name','secuencia'], context):
            if record['secuencia']:
                if record['num_contrato']:
                    res.append((record['id'], '%s - %s - %s' % (record['secuencia'],record['num_contrato'] ,record['name'])))
                else:
                    res.append((record['id'], '%s - %s' % (record['secuencia'],record['name'])))
            elif record['num_contrato']:   
                res.append((record['id'], '%s - %s' % (record['num_contrato'],record['name'])))
            else:
                res.append((record['id'], '%s' % (record['name'])))
        return res

    def iniciar_obra(self, cr, uid, ids, context=None):
        garantia_obj = self.pool.get('obra.garantia')
        self.write(cr, uid, ids[0],{'state':'Ejecucion'})
        for this in self.browse(cr, uid, ids):
            if this.garantia_ids:
                for garantia in this.garantia_ids:
                    garantia_obj.write(cr, uid, garantia.id,{
                        'state':'Activa',
                    })
        return True

    _defaults = dict(
        state = 'Borrador',
    )
ObraObra()


class cobraAnticipo(osv.TransientModel):
    _name = 'wizard.cobra.anticipo'
    
    def action_cobra_anticipo(self, cr, uid, ids, context):
        #banco al debe y 124 al habe
        dev_obj = self.pool.get('voucher.devengado')
        certificate_obj = self.pool.get('budget.certificate')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        post_obj = self.pool.get('budget.post')
        item_obj = self.pool.get('budget.item')
        account_obj = self.pool.get('account.account')
        cert_line = self.pool.get('budget.certificate.line')
        certificate_line_obj = self.pool.get('budget.certificate.line')        
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        voucher_obj = self.pool.get('account.voucher')
        parameter_obj = self.pool.get('ir.config_parameter')
        for this in self.browse(cr, uid, ids):
#            date_inicio = move.period_id.fiscalyear_id.date_start
            journal_ids = journal_obj.search(cr, uid, [('name','=','INGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv('Erro configuracion','No esta creado un diario de ingresos.')
            period_ids = period_obj.find(cr, uid, this.date)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            voucher = voucher_obj.browse(cr, uid, context['active_id'])
            p_id = voucher.partner_id.id
            journal_id = journal_ids[0]
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            name_aux = 'Cobro Anticipo ' + voucher.partner_id.name + ' - ' + voucher.narration
            date_aux = this.date
            certificate_ids = certificate_obj.search(cr, uid, [('tipo_aux','=','ingreso'),('date','<=',date_aux),('date_commited','>=',date_aux)])
            move_id = move_obj.create(cr, uid, {
                'ref': name_aux,
                'narration':name_aux,
                'journal_id': journal_id,
                'date': this.date,
                'period_id':period_ids[0],
                'state':'draft',
                'afectacion':True,
                'partner_id':p_id,
                'no_cp':True,
                'type':'Recaudacion',
                'certificate_id':certificate_ids[0],
            })
            if this.account_id2:
                parameter_obj = self.pool.get('ir.config_parameter')
                if voucher.tipo=='Obra':
                    pxc_ids = parameter_obj.search(cr, uid, [('key','=','pxco')],limit=1)
                else:
                    pxc_ids = parameter_obj.search(cr, uid, [('key','=','pxcb')],limit=1)
                if pxc_ids:
                    code_post = parameter_obj.browse(cr, uid, pxc_ids[0]).value
                    post_ids = post_obj.search(cr, uid, [('code','=',code_post)],limit=1)
                    if post_ids:
                        item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),
                                                             ('date_start','<=',date_aux),('date_end','>=',date_aux)],limit=1)
                        if item_ids:
                            cert_line_ids = certificate_line_obj.search(cr, uid, [('budget_id','=',item_ids[0]),('certificate_id','=',certificate_ids[0])])
                move_line_obj.create(cr, uid, {
                    'account_id':this.account_id2.id,
                    'credit':this.monto,
                    'budget_id_cert':cert_line_ids[0],
                    'budget_paid':True,
                    'budget_accrued':True,
                    'move_id':move_id,
                    'partner_id':p_id,
                })
                move_line_obj.create(cr, uid, {
                    'account_id':this.bank_id.default_debit_account_id.id,
                    'debit':this.monto,
                    'move_id':move_id,
                    'partner_id':p_id,
                })
                ####debe haber de la 113 recaudacion
                acc11_ids = parameter_obj.search(cr, uid, [('key','=','cc11')],limit=1)
                if acc11_ids:
                    code_aux = parameter_obj.browse(cr, uid, acc11_ids[0]).value
                    account_ids = account_obj.search(cr, uid, [('code','=',code_aux)],limit=1)
                    if account_ids:
                        move_line_obj.create(cr, uid, {
                            'account_id':account_ids[0],
                            'debit':this.monto,
                            'budget_id_cert':cert_line_ids[0],
                            'move_id':move_id,
                            'partner_id':p_id,
                        })      
                        move_line_obj.create(cr, uid, {
                            'account_id':account_ids[0],
                            'credit':this.monto,
                            'budget_id_cert':cert_line_ids[0],
                            'move_id':move_id,
                            'partner_id':p_id,
                        })      
                dev_obj.create(cr, uid, {
                    'voucher_id':voucher.id,
                    'name':move_id,
                    'date':date_aux,
                    'monto':this.monto,
                })
            else:
                raise osv.except_osv('Error de configuracion','No hay parametrizacion de cuenta 124 por defecto')
        return {'type':'ir.actions.act_window_close' }

    def action_cobra_anticipo2(self, cr, uid, ids, context):
        certificate_obj = self.pool.get('budget.certificate')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        post_obj = self.pool.get('budget.post')
        item_obj = self.pool.get('budget.item')
        account_obj = self.pool.get('account.account')
        cert_line = self.pool.get('budget.certificate.line')
        certificate_line_obj = self.pool.get('budget.certificate.line')        
        post_obj = self.pool.get('budget.post')
        item_obj = self.pool.get('budget.item')
        account_obj = self.pool.get('account.account')
        cert_line = self.pool.get('budget.certificate.line')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        voucher_obj = self.pool.get('account.voucher')
        for this in self.browse(cr, uid, ids):
#            date_inicio = move.period_id.fiscalyear_id.date_start
            journal_ids = journal_obj.search(cr, uid, [('name','=','INGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv('Erro configuracion','No esta creado un diario de ingresos.')
            period_ids = period_obj.find(cr, uid, this.date)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            voucher = voucher_obj.browse(cr, uid, context['active_id'])
            p_id = voucher.partner_id.id
            journal_id = journal_ids[0]
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            name_aux = 'Cobro Anticipo ' + voucher.partner_id.name
            date_aux = this.date
            certificate_ids = certificate_obj.search(cr, uid, [('tipo_aux','=','ingreso'),('date','<=',date_aux),('date_commited','>=',date_aux)])
            move_id = move_obj.create(cr, uid, {
                'ref': name_aux,
                'narration':name_aux,
                'journal_id': journal_id,
                'date': this.date,
                'period_id':period_ids[0],
                'state':'draft',
                'afectacion':True,
                'partner_id':p_id,
                'no_cp':True,
                'type':'Recaudacion',
                'certificate_id':certificate_ids[0],
            })
            if this.date:#<date_inicio:
                parameter_obj = self.pool.get('ir.config_parameter')
                if voucher.tipo=='Obra':
                    pxc_ids = parameter_obj.search(cr, uid, [('key','=','pxco')],limit=1)
                else:
                    pxc_ids = parameter_obj.search(cr, uid, [('key','=','pxcb')],limit=1)
                if pxc_ids:
                    code_post = parameter_obj.browse(cr, uid, pxc_ids[0]).value
                    post_ids = post_obj.search(cr, uid, [('code','=',code_post)],limit=1)
                    if post_ids:
                        item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_ids[0]),
                                                             ('year_id','=',this.certificate_line_id.budget_id.year_id.id)],limit=1)
                        if item_ids:
                            cert_line_ids = certificate_line_obj.search(cr, uid, [('budget_id','=',item_ids[0])])
                move_line_obj.create(cr, uid, {
                    'account_id':this.account_id2.id,
                    'debit':this.monto,
                    'budget_id_cert':cert_line_ids[0],
                    'budget_paid':True,
                    'move_id':move_id,
                    'partner_id':p_id,
                })
                move_line_obj.create(cr, uid, {
                    'account_id':this.bank_id.default_debit_account_id.id,
                    'debit':this.monto,
                    'move_id':move_id,
                    'partner_id':p_id,
                })
                move_line_obj.create(cr, uid, {
                    'account_id':this.account_id2.id,
                    'credit':this.monto_devengar,
                    'budget_id_cert':cert_line_ids[0],
                    'budget_accrued':True,
                    'move_id':move_id,
                    'partner_id':p_id,
                })
                move_line_obj.create(cr, uid, {
                    'account_id':this.account_id.id,
                    'credit':this.monto_devengar,
                    'budget_id_cert':cert_line_ids[0],
                    'move_id':move_id,
                    'partner_id':p_id,
                })
            else:
                move_line_obj.create(cr, uid, {
                    'account_id':this.account_id.id,
                    'credit':this.monto_devengar,
                    'move_id':move_id,
                    'partner_id':p_id,
                })
        return True

    def default_get(self, cr, uid, fields, context=None):
        ant_obj = self.pool.get('account.voucher')
        parameter_obj = self.pool.get('ir.config_parameter')
        account_obj = self.pool.get('account.account')
        period_obj = self.pool.get('account.period')
        if context is None:
            context = {}
        res = {}
        ant = ant_obj.browse(cr, uid, context['active_id'])
#        periodo_actual = period_obj.find(cr, uid, ant.)
#        if ant.date
        account_id2 = ant.line_dr_ids[0].account_id.id
        acc11_ids = parameter_obj.search(cr, uid, [('key','=','cc11')],limit=1)
        if acc11_ids:
            code_aux = parameter_obj.browse(cr, uid, acc11_ids[0]).value
            account_ids = account_obj.search(cr, uid, [('code','=',code_aux)],limit=1)
            if account_ids:
                account_id2 = account_ids[0]
        account_id = ant.line_dr_ids[0].account_id.id
        acc124_ids = parameter_obj.search(cr, uid, [('key','=','cc124')],limit=1)
        if acc124_ids:
            code_aux = parameter_obj.browse(cr, uid, acc124_ids[0]).value
            account_ids = account_obj.search(cr, uid, [('code','=',code_aux)],limit=1)
            if account_ids:
                account_id = account_ids[0]
        res.update({
            'monto':ant.amount,
            'account_id2':account_id,
 #           'account_id':account_id,
            'date':time.strftime('%Y-%m-%d'),
        })
        return res

    _columns = dict(
        bank_id = fields.many2one('account.journal','Banco'),
        monto = fields.float('Monto'),
        date = fields.date('Fecha'),
        account_id2 = fields.many2one('account.account','Cuenta por cobrar Anterior'),
        account_id = fields.many2one('account.account','Cuenta por cobrar Anticipo'),
    )

cobraAnticipo()
