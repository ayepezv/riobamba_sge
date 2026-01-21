# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

import time
from osv import fields, osv
import datetime
from datetime import date, timedelta
from tools import ustr
from gt_tool import XLSWriter

class mayorCuentaLineC(osv.TransientModel):
    _name = 'mayor.cuenta.linec'
#    _order = "date asc,seq asc"
    _order = "seq asc,date asc"
    _columns = dict(
        spi_number = fields.integer('Num. SPI'),
        seq = fields.integer('Secuencia'),
        l_id = fields.many2one('mayor.linec','Cuenta',ondelete='cascade'),
        date = fields.date('Fecha'),
        partner_id = fields.many2one('res.partner','Empresa/Beneficiario'),
        name = fields.char('Referencia',size=256),
        debit = fields.float('Debe'),
        credit = fields.float('Haber'),
        saldo = fields.float('Saldo'),
        doc = fields.char('Ref.',size=20),
        documento = fields.char('Documento',size=128),
        conciliado = fields.boolean('Conciliado'),
    )
mayorCuentaLineC()

class mayorLineC(osv.TransientModel):
    _name = 'mayor.linec'
    _columns =dict(
        saldo_anterior = fields.float('Saldo Anterior'),
        debe = fields.float('Total Debe'),
        haber = fields.float('Total Haber'),
        saldo_final = fields.float('Saldo Final'),
        m_id = fields.many2one('mayor.cuentac','Mayor'),
        account_id = fields.many2one('account.account','Cuenta Contable'),
        name = fields.char('Cuenta',size=32),
        line_line_ids = fields.one2many('mayor.cuenta.linec','l_id','Detalle Cuenta'),
    )
mayorLineC()

class mayorCuentaC(osv.TransientModel):
    _name = 'mayor.cuentac'

    def exportaExcelC(self, cr, uid, ids, name, context={}):
        for this in self.browse(cr, uid, ids):
            writer = XLSWriter.XLSWriter()
            cabecera_all = ['Codigo Cuenta','Nombre Cuenta']
            writer.append(cabecera_all)
            aux_debit = aux_credit = 0
            cabecera_cuenta = [this.bank_resumen.name.default_debit_account_id.code,this.bank_resumen.name.default_debit_account_id.name]
            writer.append(cabecera_cuenta)
            cabecera_all2 = ['','Fecha','Comp.','Referencia','Num. SPI','Beneficiario','Conciliado','Debe','Haber']
            writer.append(cabecera_all2)
            aux_debit = aux_credit = 0
            for line_a in this.line_ids:
                for line in line_a.line_line_ids:
                    aux_c = 'NO'
                    if line.conciliado:
                        aux_c = 'SI'
                    detalle_cuenta = ['',line.date,line.doc,line.name,line.spi_number,line.partner_id.name,aux_c,line.debit,line.credit]
                    writer.append(detalle_cuenta)
#            for line in this.bank_resumen.line_ids:
#                if line.state=='valid' and line.move_id.state=='posted':
#                    detalle_cuenta = ['',line.date,line.move_id.name,line.move_id.narration,line.move_id.partner_id.name,'Si',line.debit,line.credit]
#                    writer.append(detalle_cuenta)
#                    if line.debit:
#                        aux_debit += line.debit
#                    else:
#                        aux_credit += line.credit
#            if this.bank_resumen.line_antes_ids:
#                for line in this.bank_resumen.line_antes_ids:
#                    if line.concilied_ok:
#                        aux_credit += line.amount
#                        detalle_cuenta = ['',line.date,line.comprobante,line.name,line.partner_id,'Si',0,line.amount]
#                        writer.append(detalle_cuenta)
            final = ['','','','','','SUMAS',aux_debit,aux_credit]
        writer.append(final)
        writer.save("conciliacion.xls")
        out = open("conciliacion.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'conciliacion.xls'})
        return True

    def onchange_mayor_accc(self, cr, uid, ids, name, context={}):
        vals = {}
        return {'value':{'name_to':name}}    

    def onchange_conciliacion(self, cr, uid, ids, name, context={}):
        vals = {}
        bank_obj = self.pool.get('bank.conciliation.mark')
        bank = bank_obj.browse(cr, uid, name)
        aux_name = bank.name.default_credit_account_id.id
        return {'value':{'name':aux_name,'name_to':aux_name,'date_start':bank.period_id.date_start,'date_end':bank.period_id.date_stop}}    

    def loadMayorC(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        mayor_line_obj = self.pool.get('mayor.cuenta.linec') #detalle por cada movimiento
        line_obj = self.pool.get('mayor.linec') #linea de cuenta
        move_obj = self.pool.get('account.move')
        partner_obj = self.pool.get('res.partner')
        mark_line_obj = self.pool.get('mark.line')
        for this in self.browse(cr, uid, ids):
            antes_ids = line_obj.search(cr, uid, [('m_id','=',this.id)])
            line_obj.unlink(cr, uid, antes_ids)
            account_ids = account_obj.search(cr, uid, [('code','>=',this.name.code),('code','<=',this.name_to.code),('type','!=','view')])
            if account_ids:
                #vamos por cada cuenta contable
                for account_id in account_ids:
                    debe_aux = haber_aux = 0
                    #sacar con la funcion
                    aux_start = this.date_start
                    date_start = datetime.datetime.strptime(aux_start, "%Y-%m-%d")
                    dias = timedelta(days=1)
                    date_start2 = date_start - dias
                    date_start2 = date_start2.strftime("%Y-%m-%d")
                    ctx = {}
                    ctx['fiscalyear'] = this.fiscalyear_id.id
                    ctx['date_from'] = this.fiscalyear_id.date_start
                    if this.fiscalyear_id.date_start==this.date_start:
                        ctx['date_to'] =  this.date_start
                    else:
                        ctx['date_to'] =  date_start2
                    ctx['state'] = 'posted'
                    account = account_obj.read(cr, uid, account_id, ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx)
                    if this.concilied_ok=='No Conciliado':
                        saldo_inicial = 0
                    else:
                        saldo_inicial = abs(account['balance'])
                    debe_aux_f = haber_aux_f = 0
                    aux_date_rio = '2017-01-01' 
                    if this.partner_id:
                        if this.concilied_ok:
                            if this.concilied_ok=='Conciliado':
                                move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',account_id),('date','>=',this.date_start),('is_start','=',False),
                                                                               ('date','<=',this.date_end),('move_id.state','=','posted'),
                                                                               ('date','!=',this.fiscalyear_id.date_start),('concilied_ok','=',True),
                                                                               ('state','=','valid'),('partner_id','=',this.partner_id.id)],order='date asc')
                            else:
                                #this.date_start
                                move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',account_id),('date','>=',aux_date_rio),('is_start','=',False),
                                                                               ('date','<=',this.date_end),('move_id.state','=','posted'),
                                                                               ('date','!=',this.fiscalyear_id.date_start),('concilied_ok','=',False),
                                                                               ('state','=','valid'),('partner_id','=',this.partner_id.id)],order='date asc')
                        else:
                            move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',account_id),('date','>=',this.date_start),('is_start','=',False),
                                                                           ('date','<=',this.date_end),('move_id.state','=','posted'),
                                                                           ('date','!=',this.fiscalyear_id.date_start),
                                                                           ('state','=','valid'),('partner_id','=',this.partner_id.id)],order='date asc')
                    else:
                        if this.concilied_ok:
                            if this.concilied_ok=='Conciliado':
                                move_line_ids = move_line_obj.search(cr, uid, [('bank_c_id','=',this.bank_resumen.id),('concilied_ok','=',True),
                                                                               ('is_start','=',False)],order='date asc')
#                                move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',account_id),('date','>=',this.date_start),('is_start','=',False),
#                                                                               ('date','<=',this.date_end),('move_id.state','=','posted'),
#                                                                               ('date','!=',this.fiscalyear_id.date_start),('concilied_ok','=',True),
#                                                                               ('state','=','valid')],order='date asc')
                            elif this.concilied_ok=='No Conciliado':
#                                move_line_ids = move_line_obj.search(cr, uid, [('bank_c_id','=',this.bank_resumen.id),('concilied_ok','=',False)],order='date asc')
                               move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',account_id),('date','>=',aux_date_rio),
                                                                              ('is_start','=',False),
                                                                              ('date','<=',this.date_end),('move_id.state','=','posted'),
                                                                              ('date','!=',this.fiscalyear_id.date_start),('concilied_ok','=',False),
                                                                              ('state','=','valid')],order='date asc')
                            else:
                                move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',account_id),('date','>=',this.date_start),
                                                                               ('is_start','=',False),
                                                                               ('date','<=',this.date_end),('move_id.state','=','posted'),
                                                                               ('date','!=',this.fiscalyear_id.date_start),
                                                                               ('state','=','valid')],order='date asc')
                        else:
                            move_line_ids = move_line_obj.search(cr, uid, [('bank_c_id','=',this.bank_resumen.id)],order='date asc')
#                            move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',account_id),('date','>=',this.date_start),('is_start','=',False),
#                                                                           ('date','<=',this.date_end),('move_id.state','=','posted'),
#                                                                           ('date','!=',this.fiscalyear_id.date_start),
#                                                                           ('state','=','valid')],order='date asc')
                    seq = 0
                    if move_line_ids:
                        for move_line_id in move_line_ids:
                            move_line = move_line_obj.browse(cr, uid, move_line_id)
                            if move_line.debit:
                                if move_line.debit!=0:  #ojo
                                    debe_aux_f += move_line.debit
                            if move_line.credit:
                                if move_line.credit!=0:
                                    haber_aux_f += move_line.credit
                            #saldo_final = saldo_inicial + debe_aux_f - haber_aux_f
                        saldo_final = saldo_inicial + debe_aux_f - haber_aux_f
                        line_id = line_obj.create(cr, uid, {
                            'm_id':this.id,
                            'account_id':account_id,
                            'saldo_anterior':saldo_inicial,
                            'debe':debe_aux_f,
                            'haber':haber_aux_f,
                            'saldo_final':saldo_final,
                        })
                        saldo_aux = 0
                        next_saldo = saldo_inicial
                        #falta crear la linea de saldo inicial
                        for move_line_id in move_line_ids:
                            seq += 1
                            move_line = move_line_obj.browse(cr, uid, move_line_id)
                            if move_line.debit!=0 or move_line.credit!=0:
                                saldo_aux = move_line.debit - move_line.credit
                                if move_line.move_id.narration:
                                    aux_desc = move_line.move_id.name + move_line.move_id.narration
                                else:
                                    aux_desc = move_line.move_id.name
                                if move_line.debit:
#                                    if move_line.debit>0:
                                    next_saldo += move_line.debit
                                elif move_line.credit:
#                                    if move_line.credit>0:
                                    next_saldo -= move_line.credit
                                #verificar el proveedor si  no esta
                                aux_p_id = move_line.move_id.partner_id.id
                                partner_ids = partner_obj.search(cr, uid, [('id','=',aux_p_id)])
                                if partner_ids:
                                    partner_id = partner_ids[0]
                                else:
                                    partner_id = 1
                                mayor_line_id = mayor_line_obj.create(cr, uid, {
                                    'l_id':line_id,
                                    'doc':move_line.move_id.name,
                                    'name':aux_desc,
                                    'date':move_line.date,
                                    'partner_id':partner_id,
                                    'debit':move_line.debit,
                                    'credit':move_line.credit,
                                    'saldo':next_saldo,
                                    'conciliado':move_line.concilied_ok,
                                    'documento':move_line.tipo_conciliacion.name,
                                    'seq':seq,
                                    'spi_number':move_line.spi_numero,
                                })
                        #agregar los mark.line que son de anio anterior
                        if this.concilied_ok=='No Conciliado':
                            mark_line_ids = mark_line_obj.search(cr, uid, [('concilied_ok','=',False),('account_id','=',account_id)],order='date asc')
#                            mark_line_ids = mark_line_obj.search(cr, uid, [('account_id','=',account_id)])
                            if mark_line_ids:
                                for mark_line_id in mark_line_ids:
                                    seq += 1
                                    mark_line = mark_line_obj.browse(cr, uid, mark_line_id)
                                    if mark_line.name:
                                        aux_name = mark_line.name
                                    else:
                                        aux_name = 'ANIO ANTERIOR'
                                    next_saldo -= mark_line.amount
                                    mayor_line_id = mayor_line_obj.create(cr, uid, {
                                        'l_id':line_id,
                                        'doc':mark_line.comprobante,
                                        'name':aux_name,
                                        'date':mark_line.date,
                                        'partner_id':partner_id,
                                        'credit':mark_line.amount,
                                        'saldo':next_saldo,
                                        'conciliado':False,
                                        'documento':mark_line.tipo_conciliacion.name,
                                        'seq':seq,
                                    }) 
                        elif this.concilied_ok=='Conciliado':

                            mark_line_ids = mark_line_obj.search(cr, uid, [('concilied_ok','=',True),('b_id','=',this.bank_resumen.id),
                                                                           ('account_id','=',account_id)],order='date asc')
                            if mark_line_ids:
                                for mark_line_id in mark_line_ids:
                                    seq += 1
                                    mark_line = mark_line_obj.browse(cr, uid, mark_line_id)
                                    if mark_line.name:
                                        aux_name = mark_line.name
                                    else:
                                        aux_name = 'ANIO ANTERIOR'
                                    #sumar lo anterior tambien
                                    haber_aux_f += mark_line.amount
                                    mayor_line_id = mayor_line_obj.create(cr, uid, {
                                        'l_id':line_id,
                                        'doc':mark_line.comprobante,
                                        'name':aux_name,
                                        'date':mark_line.date,
                                        'partner_id':partner_id,
                                        'credit':mark_line.amount,
                                        'saldo':next_saldo,
                                        'conciliado':True,
                                        'documento':mark_line.tipo_conciliacion.name,
                                        'seq':seq,
                                    })
                                    line_obj.write(cr, uid, line_id,{'haber':haber_aux_f})
                        else:
                            mark_line_ids = mark_line_obj.search(cr, uid, [('account_id','=',account_id)],order='date asc')
                            if mark_line_ids:
                                for mark_line_id in mark_line_ids:
                                    seq += 1
                                    mark_line = mark_line_obj.browse(cr, uid, mark_line_id)
                                    if mark_line.name:
                                        aux_name = mark_line.name
                                    else:
                                        aux_name = 'ANIO ANTERIOR'
                                    #estaba comentado
                                   # mayor_line_id = mayor_line_obj.create(cr, uid, {
                                   #     'l_id':line_id,
                                   #     'doc':mark_line.comprobante,
                                   #     'name':aux_name,
                                   #     'date':mark_line.date,
                                   #     'partner_id':partner_id,
                                   #     'credit':mark_line.amount,
                                   #     'saldo':next_saldo,
                                   #     'conciliado':mark_line.concilied_ok,
                                   #     'documento':mark_line.tipo_conciliacion.name,
                                   # })
                    else:
                        line_id = line_obj.create(cr, uid, {
                            'm_id':this.id,
                            'account_id':account_id,
                            'saldo_anterior':saldo_inicial,
                            'debe':0,
                            'haber':0,
                            'saldo_final':saldo_inicial,
                        })
        return True

    def print_mayor_ctac(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'mayor.cuentac'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'mayor.cuentac',
            'model': 'mayor.cuentac',
            'datas': datas,
            'nodestroy': True,                        
            }

    _columns = dict(
        bank_resumen = fields.many2one('bank.conciliation.mark','Resumen Conciliacion'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
        line_ids = fields.one2many('mayor.linec','m_id','Cuentas'),
        name = fields.many2one('account.account','Cuenta Contable Desde'),
        name_to = fields.many2one('account.account','Cuenta Contable Hasta'),
        date_start = fields.date('Desde'),
        date_end = fields.date('Hasta'),
        fiscalyear_id = fields.many2one('account.fiscalyear', 'Año fiscal', required=True),
        partner_id = fields.many2one('res.partner','Beneficiario'),
        concilied_ok = fields.selection([('Libro Bancos','Libro Bancos'),('Conciliado','Conciliado'),('No Conciliado','No Concliado')],'Tipo Conciliado'),
    )

    def onchange_fiscalyearc(self, cr, uid, ids, fiscalyear_id):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear = fiscalyear_obj.browse(cr, uid, fiscalyear_id)
        res = {'value': {'date_start': fiscalyear.date_start, 'date_end': fiscalyear.date_stop}}
        return res

    
    def _get_activeyear(self, cr, uid, context):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('state','=','draft')])
        res = {}
        if fiscalyear_ids:
            return fiscalyear_ids[0]
        else:
            raise osv.except_osv('Error !', 'No existe un año fiscal abierto')
    
    _defaults = {
        'fiscalyear_id': _get_activeyear,
        'concilied_ok':'Libro Bancos',
    }
    
    
mayorCuentaC()

class tipoConciliacion(osv.Model):
    _name = 'tipo.conciliacion'
    _columns = dict(
        name = fields.char('Tipo Movimiento',size=64,required=True),
    )
tipoConciliacion()

class accountMoveLineBank(osv.Model):
    _inherit = 'account.move.line'
    _columns = dict(
        tipo_conciliacion = fields.many2one('tipo.conciliacion','Tipo Movimiento'),
        partner2_id = fields.related('move_id','partner_id',type='many2one',
                                    relation='res.partner',string='Beneficiario',readonly=True,store=True),
        num_comp = fields.related('move_id','name',type='char',size=32,string='Comprobante',readonly=True,store=True),
        num_concilied = fields.char('Numero Transferencia',size=64),
        concilied_ok = fields.boolean('Conciliado'),
        bank_c_id = fields.many2one('bank.conciliation.mark','Linea Asiento'),
        hoja = fields.integer('Num. Hoja Estado Cuenta'),
        date_concilied = fields.date('Fecha Conciliacion'),
        date_transfer = fields.date('Fecha Transferencia'),
        num_referencia = fields.integer('Num. Transferencia'),
        )

    def noConciliar(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'concilied_ok':False})

accountMoveLineBank()

class wizardConciliarA(osv.TransientModel):
    _name = 'wizard.conciliar.a'

    def action_conciliar_a(self, cr, uid, ids, context):
        mark_line_obj = self.pool.get('mark.line')
        for this in self.browse(cr, uid, ids):
            mark_line_obj.write(cr, uid, context['active_id'],{
                'concilied_ok':True,
                'num_concilied':this.ref,
                'hoja':this.hoja,
                'tipo_conciliacion':this.tipo_id.id,
                'date_concilied':this.date_conciliado,
            })
        return {'type':'ir.actions.act_window_close' }


    _columns = dict(
        date_conciliado = fields.date('Fecha Conciliado'),
        date_transferido = fields.date('Fecha de Transferencia'),
        ref = fields.char('Referencia BCE',size=64),
        hoja = fields.integer('Num. Hoja Estado Cuenta'),
        tipo_id = fields.many2one('tipo.conciliacion','Tipo'),
    )
wizardConciliarA()

class wizardConciliar(osv.TransientModel):
    _name = 'wizard.conciliar'

    def action_conciliar(self, cr, uid, ids, context):
        move_line_obj = self.pool.get('account.move.line')
        concilied_obj = self.pool.get('bank.conciliation.mark')
        for this in self.browse(cr, uid, ids):
            move_line_obj.write(cr, uid, context['active_id'],{
                'concilied_ok':True,
                'num_concilied':this.ref,
                'hoja':this.hoja,
                'tipo_conciliacion':this.tipo_id.id,
                'num_referencia':this.num_transferencia,
                'date_concilied':this.date_conciliado,
            })
#        return True
        return {'type':'ir.actions.act_window_close' }


    _columns = dict(
        num_transferencia = fields.integer('Num. Transferencia'),
        date_conciliado = fields.date('Fecha Conciliado'),
        date_transferido = fields.date('Fecha de Transferencia'),
        ref = fields.char('Referencia BCE',size=64),
        hoja = fields.integer('Num. Hoja Estado Cuenta'),
        tipo_id = fields.many2one('tipo.conciliacion','Tipo'),
    )
wizardConciliar()

class markLine(osv.Model):
    _name = 'mark.line'
    _columns = dict(
        account_id = fields.many2one('account.account','Cuenta'),
        name = fields.char('Referencia',size=256),
        tipo_conciliacion = fields.many2one('tipo.conciliacion','Tipo Movimiento'),
        b_id = fields.many2one('bank.conciliation.mark','Conciliacion'),
        num_concilied = fields.char('Referencia BCE',size=64),
        num_referencia = fields.integer('Num. Transferencia'),
        concilied_ok = fields.boolean('Conciliado'),
        hoja = fields.integer('Num. Hoja Estado Cuenta'),
        comprobante = fields.char('Num. Comprobante',size=16),
        date = fields.date('Fecha'),
        date_concilied = fields.date('Fecha Conciliacion'),
        date_transfer = fields.date('Fecha Transferencia'),
        partner_id = fields.char('Proveedor/Beneficiario',size=64),
        amount = fields.float('Monto'),
    )
markLine()

class noContabilizado(osv.Model):
    _name = 'no.contabilizado'
    _columns = dict(
        date = fields.date('Fecha'),
        tipo = fields.selection([('DEBITO','DEBITO'),('CREDITO','CREDITO')],'Tipo'),
        b_id = fields.many2one('bank.conciliation.mark','Conciliacion'),
        monto = fields.float('Monto'),
        descripcion = fields.char('Descripcion',size=256),
        ref = fields.char('Ref. BCE',size=10),
    )
noContabilizado()

class bank_conciliation_mark(osv.Model):
    _name = 'bank.conciliation.mark'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.period_id.name + " - " + record.name.name
            res.append((record.id, name))
        return res    


    def _amount_conciliado(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = {
                'monto_conciliado_debitos': 0.0,
                'monto_conciliado_creditos': 0.0,
                }
            aux_debit = aux_credit = 0
            for line in this.line_ids:
                if line.concilied_ok:
                    if line.debit:
                        aux_debit += line.debit
                    else:
                        aux_credit += line.credit
            if this.line_antes_ids:
                for line in this.line_antes_ids:
                    if line.concilied_ok:
                        aux_credit += line.amount
        #aqui es cambiado por q es banco
        res[this.id]['monto_conciliado_debitos']  = aux_credit
        res[this.id]['monto_conciliado_creditos']  = aux_debit
        res[this.id]['saldo_por_conciliar']  = aux_credit
        return res

    def _amount_saldo_conciliar(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        total = 0
        for this in self.browse(cr, uid, ids):
            total = this.final_estado_cuenta - this.monto_conciliado_debitos - this.monto_conciliado_creditos
            res[this.id] = total
        return res

    def cerrar_conciliar(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'Cerrado'})

    _columns = dict(
        state = fields.selection([('Abierto','Abierto'),('Cerrado','Cerrado/Conciliado')],'Estado'),
        no_ids = fields.one2many('no.contabilizado','b_id','No Contabilizados'),
        name = fields.many2one('account.journal','Banco',required=True),
        period_id = fields.many2one('account.period','Periodo',required=True),
        account_id = fields.related('name','default_debit_account_id',type='many2one',
                                    relation='account.account',string='Cuenta Contable',readonly=True,store=True),
        no_edit = fields.boolean('No Edit'),
        saldo_inicial_sistema = fields.float('Inicial Sistema $'),
        saldo_final_sistema = fields.float('Final Sistema $'),
        total_debitos = fields.float('Total Debitos(-) $'),
        total_creditos = fields.float('Total Creditos(+) $'),
        total_movimientos = fields.integer('Numero Movimientos'),
        total_conciliados = fields.integer('Conciliados'),
        total_sinconciliar = fields.integer('Sin conciliar'),
        monto_conciliado_debitos = fields.float('Total Conciliado Debitos'),
        monto_conciliado_creditos = fields.float('Total Conciliado Creditos'),
#        monto_conciliado_debitos = fields.function(_amount_conciliado, string='Total Conciliado Debitos',multi="bck", store=True),
#        monto_conciliado_creditos = fields.function(_amount_conciliado, string='Total Conciliado Creditos', multi="bck", store=True),
        final_estado_cuenta = fields.float('Saldo Final Estado Cuenta'),
        inicial_estado_cuenta = fields.float('Saldo Inicial Estado Cuenta'),
        saldo_por_conciliar = fields.function(_amount_conciliado, string='Saldo Por Conciliar',multi="bck", store=True),
        line_antes_ids = fields.one2many('mark.line','b_id','Detalle Movimientos'),
        line_ids = fields.one2many('account.move.line','bank_c_id','Detalle'),
        )
    

    def bank_all(self, cr, uid, ids, context):
        if context is None:
            context = {}
        line_obj = self.pool.get('account.move.line')
        line_ant_obj = self.pool.get('mark.line')
        account_obj = self.pool.get('account.account')
        conciliation_obj = self.pool.get('bank.conciliation.mark')
        ctx = {}
        ctx2 = {} 
        debitos = creditos = total_moves = conciliados = no_conciliados =0
        for this in self.browse(cr, uid, ids):
            #saldos de la cuenta contable
            ctx['fiscalyear'] = this.period_id.fiscalyear_id.id
            ctx['date_from'] = this.period_id.fiscalyear_id.date_start
            if this.period_id.date_start!=this.period_id.fiscalyear_id.date_start:
                aux_inicial = this.period_id.date_start
                final_aux = datetime.datetime.strptime(aux_inicial, '%Y-%m-%d').date()
                final_aux = final_aux - timedelta(days=1)
                date_final_anterior = final_aux.strftime('%Y-%m-%d')
                ctx['date_to'] =  date_final_anterior
            else:
                ctx['date_to'] =  this.period_id.date_start
            account = account_obj.read(cr, uid, [this.name.default_debit_account_id.id], 
                                       ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx)
            inicial = abs(account[0]['balance'])
            ctx2['fiscalyear'] = this.period_id.fiscalyear_id.id
            ctx2['date_from'] = this.period_id.fiscalyear_id.date_start
            ctx2['date_to'] =  this.period_id.date_stop
            account2 = account_obj.read(cr, uid, [this.name.default_debit_account_id.id], 
                                       ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx2)
            #final = abs(account2[0]['balance'])
            #sql toma los lineas de la cuenta y saca el saldo
            sql_aux = """select sum(debit),sum(credit) from account_move_line l,account_move m where l.move_id=m.id and l.account_id=%s and m.date>='%s' and m.date<='%s' and m.state='posted'"""%(this.name.default_debit_account_id.id,this.period_id.fiscalyear_id.date_start,this.period_id.date_stop)
            cr.execute(sql_aux)
            aux = cr.fetchall()
            final = abs(aux[0][0]-aux[0][1])
#            final = this.saldo_inicial_sistema + this.monto_conciliado_creditos - this.total_debitos
            line_ids_concilied = line_obj.search(cr, uid, [('account_id','=',this.name.default_debit_account_id.id),('move_id.state','=','posted'),
                                                 ('is_start','=',False),('state','=','valid'),
                                                 ('date_concilied','<=',this.period_id.date_stop),('date_concilied','>=',this.period_id.date_start)])
            line_ids = line_obj.search(cr, uid, [('account_id','=',this.name.default_debit_account_id.id),('move_id.state','=','posted'),
                                                 ('is_start','=',False),('state','=','valid'),
                                                 ('date','<=',this.period_id.date_stop),('date','>=',this.period_id.date_start)])
            if line_ids_concilied:
                if len(line_ids_concilied)>1:
                    tuple_ids = tuple(line_ids_concilied)
                    operador = 'in'
                else:
                    tuple_ids = (line_ids_concilied[0])
                    operador = '='
                total_moves = len(line_ids_concilied)
                sql = "update account_move_line set bank_c_id=%s where id %s %s" %(this.id,operador,tuple_ids)
                cr.execute(sql)
            if this.line_ids:
                for line_id in line_ids:
                    linea = line_obj.browse(cr, uid, line_id)
                    creditos += linea.debit
                    debitos += linea.credit
                    if linea.concilied_ok:
                        conciliados += 1
                no_conciliados = total_moves - conciliados
                #pendientes del anio anterior
                line_ant_ids = line_ant_obj.search(cr, uid, [('concilied_ok','=',True)])
                if line_ant_ids:
                    for line_ant_id in line_ant_ids:
                        line_ant = line_ant_obj.browse(cr, uid, line_ant_id)
                        debitos += line_ant.amount
                if not this.no_edit:
                    conciliation_obj.write(cr, uid, this.id,{
                        'total_movimientos':total_moves,
                        'total_conciliados':conciliados,
                        'total_sinconciliar':no_conciliados,
                        'saldo_inicial_sistema':inicial,
                        'saldo_final_sistema':final,
                        'total_debitos':debitos,
                        'total_creditos':creditos,
                    })
                else:
                    conciliation_obj.write(cr, uid, this.id,{
                        'total_movimientos':total_moves,
                        'total_conciliados':conciliados,
                        'total_sinconciliar':no_conciliados,
                        'saldo_inicial_sistema':inicial,
                        'saldo_final_sistema':final,
                        'total_debitos':debitos,
                        'total_creditos':creditos,
                    })
        return True

    def bankTotal(self, cr, uid, ids, context):
        self.bank_all(cr, uid, ids, context)
        aux_debit = aux_credit = 0
        for this in self.browse(cr, uid, ids):
            #final = this.saldo_inicial_sistema + this.monto_conciliado_creditos - this.total_debitos
            #final = this.inicial_estado_cuenta + this.monto_conciliado_creditos - this.total_debitos
            #final = this.saldo_inicial_sistema + this.total_creditos - this.total_debitos
            if this.line_ids:
                for line in this.line_ids:
                    if line.concilied_ok and line.state=='valid' and line.move_id.state=='posted':
                        aux_debit += line.debit
                        aux_credit += line.credit
#                        if line.debit:
#                            aux_debit += line.debit
#                        else:
#                            aux_credit += line.credit
            #anio anterior
            if this.line_antes_ids:
                for line in this.line_antes_ids:
                    if line.concilied_ok:
                        aux_credit += line.amount
            self.write(cr, uid, this.id,{
                'monto_conciliado_debitos':aux_credit,
                'monto_conciliado_creditos':aux_debit,
            #    'saldo_final_sistema':final,
            })
        return True

    def bank_concilied(self, cr, uid, ids, context):
        if context is None:
            context = {}
        line_obj = self.pool.get('account.move.line')
        mark_line = self.pool.get('mark.line')
        aux_ids = []
        for this in self.browse(cr, uid, ids):
            mark_ids = mark_line.search(cr, uid, [('b_id','=',this.id),('concilied_ok','=',False)])
            if mark_ids:
                if len(mark_ids)>1:
                    tuple_ids = tuple(mark_ids)
                    operador = 'in'
                else:
                    tuple_ids = (mark_ids[0])
                    operador = '='
                sql_ids = "update mark_line set b_id=%s where id %s %s" %('NULL', operador,tuple_ids)
                cr.execute(sql_ids)
            mark_ids = mark_line.search(cr, uid, [('b_id','=',this.id),('concilied_ok','=',True)])
            if mark_ids:
                if len(mark_ids)>1:
                    tuple_ids = tuple(mark_ids)
                    operador = 'in'
                else:
                    tuple_ids = (mark_ids[0])
                    operador = '='
                sql_ids = "update mark_line set b_id=%s where id %s %s" %(this.id, operador,tuple_ids)
                cr.execute(sql_ids)
            #hacer con sql
            if this.line_ids:
                for line in this.line_ids:
                    aux_ids.append(line.id)
                if len(aux_ids)>1:
                    tuple_ids = tuple(aux_ids)
                    operador = 'in'
                else:
                    tuple_ids = (aux_ids[0])
                    operador = '='
                sql_ids = "update account_move_line set bank_c_id=%s where id %s %s" %('NULL', operador,tuple_ids)
                cr.execute(sql_ids)
            line_ids = line_obj.search(cr, uid, [('account_id','=',this.name.default_debit_account_id.id),
                                                 ('concilied_ok','=',True),
                                                 ('date_concilied','>=',this.period_id.date_start),
                                                 ('date_concilied','<=',this.period_id.date_stop)
                                             ])
#            line_ids = line_obj.search(cr, uid, [('account_id','=',this.name.default_debit_account_id.id),
#                                                 ('concilied_ok','=',True),
#                                                 ('period_id','=',this.period_id.id)])
            if line_ids:
                if len(line_ids)>1:
                    tuple_ids = tuple(line_ids)
                    operador = 'in'
                else:
                    tuple_ids = (line_ids[0])
                    operador = '='
                sql_ids = "update account_move_line set bank_c_id=%s where id %s %s" %(this.id, operador,tuple_ids)
                cr.execute(sql_ids)
        return True

    def bank_unconcilied(self, cr, uid, ids, context):
        if context is None:
            context = {}
        line_obj = self.pool.get('account.move.line')
        aux_ids = []
        for this in self.browse(cr, uid, ids):
            #hacer con sql
            if this.line_ids:
                for line in this.line_ids:
                    aux_ids.append(line.id)
                if len(aux_ids)>1:
                    tuple_ids = tuple(aux_ids)
                    operador = 'in'
                else:
                    tuple_ids = (aux_ids[0])
                    operador = '='
                sql_ids = "update account_move_line set bank_c_id=%s where id %s %s" %('NULL', operador,tuple_ids)
                cr.execute(sql_ids)
            line_ids = line_obj.search(cr, uid, [('account_id','=',this.name.default_debit_account_id.id),
                                                 ('concilied_ok','=',False),
                                                 ('period_id','=',this.period_id.id)])
            if line_ids:
                if len(line_ids)>1:
                    tuple_ids = tuple(line_ids)
                    operador = 'in'
                else:
                    tuple_ids = (line_ids[0])
                    operador = '='
                sql_ids = "update account_move_line set bank_c_id=%s where id %s %s" %(this.id, operador,tuple_ids)
                cr.execute(sql_ids)
        return True

    _sql_constraints = [('unique_period_cuenta', 'unique(period_id,name)', u'Solo puede tener un registro por periodo y banco')]
    _defaults = dict(
        state = 'Abierto',
    )


bank_conciliation_mark()
