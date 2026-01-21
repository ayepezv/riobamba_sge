# -*- coding: utf-8 -*-

from osv import osv, fields
#########por pagar SRi

class pagarSriLine(osv.TransientModel):
    _name = 'pagar.sri.line'
    _order = 'code asc'
    _columns = dict(
        partner_id = fields.many2one('res.partner','Beneficiario'),
        ref = fields.char('Referencia',size=32),
        name = fields.char('Desc',size=10),
        account_id = fields.many2one('account.account','Cuenta'),
        budget_id = fields.many2one('budget.item','Partida'),
        code = fields.char('Code',size=64),
        certificate_line_id = fields.many2one('budget.certificate.line','Certificado linea'),
        monto = fields.float('Monto'),
        saldo = fields.float('Saldo'),
        move_id = fields.many2one('account.move','Comprobante'),
        move_line_id = fields.many2one('account.move.line','Cuenta por pagar'),
        monto_pago = fields.float('Monto a pagar'),
        pagar = fields.boolean('Pagar'),
        i_id = fields.many2one('pagar.sri','Pagar'),
        desc = fields.char('Descripcion',size=64),
    )

    def agregaComprobante(self, cr, uid, ids, context=None):
        print "agrega"
        return True

pagarSriLine()
class pagarSri(osv.TransientModel):
    _name = 'pagar.sri'
    _columns = dict(
        total_pago = fields.float('Total A Pagar'),
        bank_id = fields.many2one('account.journal','Banco'),
        partner_id = fields.many2one('res.partner','Beneficiario'),
        date = fields.date('Fecha Corte'),
        date_start = fields.date('Fecha Inicio'),
        line_ids = fields.one2many('pagar.sri.line','i_id','Detalle'),
        opc = fields.selection([('ComprobanteExistente','Comprobante Existente'),('NuevoComprobante','Nuevo Comprobante')],'Opcion'),
        move_id = fields.many2one('account.move','Comprobante Contable'),
        cp_id = fields.many2one('budget.certificate','Documento presupuestario'),
    )

    def computePagarSri(self, cr, uid, ids, context=None):
        pagar_obj = self.pool.get('pagar.sri')
        for this in self.browse(cr, uid, ids):
            aux = 0 
            for line in this.line_ids:
                if line.pagar:
                    aux += line.monto_pago
        pagar_obj.write(cr, uid, ids[0],{'total_pago':aux})

    def print_pagar_sri(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'pagar.sri'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pagar.sri',
            'model': 'pagar.sri',
            'datas': datas,
            'nodestroy': True,                        
            }    


    def default_get(self, cr, uid, fields, context=None):
        company_obj = self.pool.get('res.company')
        if context is None:
            context = {}
        res = {}
        compania = company_obj.browse(cr, uid, 1)
        partner_id = compania.tax_company_id.id
        res.update({'opc':'NuevoComprobante','partner_id':partner_id})
        return res

    def pagarSri(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        cert_line_obj = self.pool.get('budget.certificate.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            if not this.bank_id:
                raise osv.except_osv('Error de usuario', 'Debe seleccionar el banco')
            if this.opc=='ComprobanteExistente' and this.move_id:
                move_id = this.move_id.id
            else:
                journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
                if not journal_ids:
                    raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
                period_ids = period_obj.find(cr, uid, this.date)
                if not period_ids:
                    raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
                aux_name = "PAGO " + this.partner_id.name
                if this.cp_id:
                    move_id = move_obj.create(cr, uid, {
                        'ref': aux_name,
                        'narration':aux_name,
                        'journal_id': journal_ids[0],
                        'date': this.date,
                        'period_id':period_ids[0],
                        'state':'draft',
                        'afectacion':True,
                        'partner_id':this.partner_id.id,
                        'type':'Impuestos',
                        'no_cp':False,
                        'validar_cp':True,
                        'certificate_id':this.cp_id.id,
                    })
                else:
                    move_id = move_obj.create(cr, uid, {
                        'ref': aux_name,
                        'narration':aux_name,
                        'journal_id': journal_ids[0],
                        'date': this.date,
                        'period_id':period_ids[0],
                        'state':'draft',
                        'afectacion':True,
                        'partner_id':this.partner_id.id,
                        'type':'Impuestos',
                        'no_cp':True,
                        'validar_cp':True,
                    })
            aux_banco = 0
            for line in this.line_ids:
                if line.pagar and line.monto_pago>0 and line.monto_pago<=line.monto:
                    if line.account_id.code[0:3]=='224':
                        if not this.cp_id:
                            raise osv.except_osv('Error de usuario','En pagos de anio anterior cuentas 224 debe seleccionar el compromiso presupuestario.')
                    aux_banco += line.monto_pago
                    if this.cp_id:
                        move_line_id = move_line_obj.create(cr, uid, {
                            'partner_id':this.partner_id.id,
                            'move_id':move_id,
                            'move_line_cxp':line.move_line_id.id,
                            'debit':line.monto_pago,
                            'budget_paid':True,
                            'budget_accrued':True,
                            'account_id':line.account_id.id,
                            'budget_id_cert':this.cp_id.line_ids[0].id,
                        })
                    else:
                        move_line_id = move_line_obj.create(cr, uid, {
                            'partner_id':this.partner_id.id,
                            'move_id':move_id,
                            'move_line_cxp':line.move_line_id.id,
                            'debit':line.monto_pago,
                            'budget_paid':True,
                            'account_id':line.account_id.id,
                            'budget_id_cert':line.certificate_line_id.id,
                        })
            move_line_id = move_line_obj.create(cr, uid, {
                'partner_id':this.partner_id.id,
                'move_id':move_id,
                'credit':aux_banco,
                'account_id':this.bank_id.default_debit_account_id.id,
            })
        return {'type':'ir.actions.act_window_close' }

    def loadPagarSri(self, cr, uid, ids, context=None):
        aux_date = '2017-01-01'
        tercero_obj = self.pool.get('hr.pago.terceros')
        move_obj = self.pool.get('account.move')
        sri_line_obj = self.pool.get('pagar.sri.line')
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        company_obj = self.pool.get('res.company')
        item_obj = self.pool.get('budget.item')
        invoice_obj = self.pool.get('account.invoice')
        compania = company_obj.browse(cr, uid, 1)
        partner_id = compania.tax_company_id.id
        for this in self.browse(cr, uid, ids):
            lineas_antes = sri_line_obj.search(cr, uid, [('i_id','=',this.id)])
            if lineas_antes:
                sri_line_obj.unlink(cr, uid, lineas_antes)
            move_line_ids = move_line_obj.search(cr, uid, [('partner_id','=',partner_id),('date','>=',this.date_start),
                                                           ('date','<=',this.date),('move_id.state','=','posted')])
            if move_line_ids:
                for move_line_id in move_line_ids:
                    move_line = move_line_obj.browse(cr, uid, move_line_id)
                    pagos_ids = move_line_obj.search(cr, uid, [('move_line_cxp','=',move_line_id),('move_id.state','=','posted')])
                    pagado = 0
                    if pagos_ids:
                        for pago_id in pagos_ids:
                            pago = move_line_obj.browse(cr, uid, pago_id)
                            pagado += pago.debit
                    if (move_line.account_id.code[0:3] in ('213','224','212') and (move_line.credit>pagado)):
                        partner_id = move_line.move_id.partner_id.id
                        aux_factura = move_line.ref
                        invoice_ids = invoice_obj.search(cr, uid, [('reference','=',aux_factura),
                                                                   ('date_invoice','>=',this.date_start),('date_invoice','<=',this.date)])
                        if invoice_ids:
                            invoice = invoice_obj.browse(cr, uid, invoice_ids[0])
                            partner_id = invoice.partner_id.id
                        sri_line_obj.create(cr, uid, {
                            'i_id':this.id,
                            'pagar':True,
                            'ref':move_line.ref,
                            'partner_id':partner_id,
                            'budget_id':move_line.budget_id.id,
                            'account_id':move_line.account_id.id,
                            'monto':move_line.credit,
                            'saldo':(move_line.credit-pagado),
                            'move_id':move_line.move_id.id,
                            'move_line_id':move_line.id,
                            'monto_pago':move_line.saldo,
                            'certificate_line_id':move_line.budget_id_cert.id,
                        })

    def loadPagarSriV2(self, cr, uid, ids, context=None):
        tercero_obj = self.pool.get('hr.pago.terceros')
        move_obj = self.pool.get('account.move')
        sri_line_obj = self.pool.get('pagar.sri.line')
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        company_obj = self.pool.get('res.company')
        item_obj = self.pool.get('budget.item')
        compania = company_obj.browse(cr, uid, 1)
        partner_id = compania.tax_company_id.id
        for this in self.browse(cr, uid, ids):
            lineas_antes = sri_line_obj.search(cr, uid, [('i_id','=',this.id)])
            if lineas_antes:
                sri_line_obj.unlink(cr, uid, lineas_antes)
            move_line_ids1 = move_line_obj.search(cr, uid, [('partner_id','=',partner_id),('date','>=',this.date_start),
                                                           ('date','<=',this.date),('move_id.state','=','posted')])
            if move_line_ids1:
                if len(move_line_ids1)>1:
                    tuple_ids = tuple(move_line_ids1)
                    operador = 'in'
                else:
                    tuple_ids = (move_line_ids1[0])
                    operador = '='
                sql = '''select account_id from account_move_line where id %s %s group by account_id''' % (operador,tuple_ids)
                cr.execute(sql)
                res = cr.fetchall()
                if res:
                    debe_mayor = haber_mayor = 0
                    for account_id in res:
                        partida_dic = {}
                        account = account_obj.browse(cr, uid, account_id[0])
                        if account.code[0:3] in ('213','224'):
                            debe = haber = 0
                            move_line_ids = move_line_obj.search(cr, uid, [('partner_id','=',partner_id),('account_id','=',account_id[0]),
                                                                           ('date','>=',this.date_start),
                                                                           ('move_id.state','=','posted'),('date','<=',this.date)])
                            for move_line_id in move_line_ids:
                                move_line = move_line_obj.browse(cr, uid, move_line_id)
                                if not move_line.budget_id.id in partida_dic:
                                    partida_dic[move_line.budget_id.id] = []
                                    partida_dic[move_line.budget_id.id].append(move_line.debit)
                                    partida_dic[move_line.budget_id.id].append(move_line.credit)
                                else:
                                    partida_dic[move_line.budget_id.id][0] += move_line.debit
                                    partida_dic[move_line.budget_id.id][1] += move_line.credit
                                debe += move_line.debit
                                haber += move_line.credit
                            if haber>debe:
                                for partida in partida_dic:
                                    aux_monto = 0
                                    if partida_dic[partida][1]>partida_dic[partida][0]:
                                        aux_monto = partida_dic[partida][1]-partida_dic[partida][0]
                                        partida_ = item_obj.browse(cr, uid, partida)
                                        sri_line_obj.create(cr, uid, {
                                            'i_id':this.id,
                                            'budget_id':partida,
                                            'account_id':account_id,
                                            'monto':aux_monto,
                                            'code':partida_.code,
                                        })
            else:
                raise osv.except_osv('Aviso', 'No hay movimientos del SRI en el periodo seleccionado')
        return True

pagarSri()

##############POR COBRAR

class cxcLineLine(osv.TransientModel):
    _name = 'cxc.line.line'
    _columns = dict(
        l_id = fields.many2one('cxc.partner.line','CxC'),
        name = fields.char('Detalle',size=256),
        monto = fields.float('Monto Anticipado'),
        devengado = fields.float('Devengado'),
        saldo = fields.float('Saldo'),
    )
cxcLineLine()
class cxcPartnerLine(osv.TransientModel):
    _name = 'cxc.partner.line'
    _order = 'partner_name asc'
    _columns = dict(
        line_ids = fields.one2many('cxc.line.line','l_id','Detalle'),
        partner_name = fields.related('partner_id','name',type='char',size=64,store=True),
        cxc_id = fields.many2one('cxc.partner','Por cobrar'),
        partner_id = fields.many2one('res.partner','Beneficiario'),
        monto = fields.float('Monto Anticipado'),
        devengado = fields.float('Devengado'),
        saldo = fields.float('Saldo'),
    )
cxcPartnerLine()

class cxcPartner(osv.TransientModel):
    _name = 'cxc.partner'
    _columns = dict(
        date = fields.date('Fecha'),
        partner_id = fields.many2one('res.partner','Beneficiario'),
        line_ids = fields.one2many('cxc.partner.line','cxc_id','Detalle Cuentas por cobrar'),
    )

    def print_cxc_partner(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.cxc.partner'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cxc.partner',
            'model': 'cxc.partner',
            'datas': datas,
            'nodestroy': True,                        
            }

    def loadCxc(self, cr, uid, ids, context):
        line_obj = self.pool.get('cxc.partner.line')
        line_line_obj = self.pool.get('cxc.line.line')
        anticipo_obj = self.pool.get('account.voucher')
        account_obj = self.pool.get('account.account')
        fiscal_obj = self.pool.get('account.fiscalyear')
        partner_list = {}
        for this in self.browse(cr, uid, ids):
            lines_antes = line_obj.search(cr, uid, [('cxc_id','=',this.id)])
            if lines_antes:
                line_obj.unlink(cr, uid, lines_antes)
            #anticipos de proveedor
            if this.partner_id:
                lista_ids_detalle = []
                anticipo_ids = anticipo_obj.search(cr, uid, [('internal_type','=','AP'),('partner_id','=',this.partner_id.id)])
                if anticipo_ids:
                    anticipo_aux = devengado_all = 0
                    for anticipo_id in anticipo_ids:
                        anticipo = anticipo_obj.browse(cr, uid, anticipo_id)
                        devengado = saldo = 0
                        for line_devengado in anticipo.dev_ids:
                            if line_devengado.name or line_devengado.is_migrado:
                                if line_devengado.name.state=='posted' or line_devengado.is_migrado:
                                    devengado += line_devengado.monto
                        anticipo_aux += anticipo.amount
                        saldo = anticipo.amount - devengado
                        devengado_all += devengado
                        if not anticipo.partner_id.id in partner_list:
                            partner_list[anticipo.partner_id.id] = saldo#anticipo.saldo
                        else:
                            partner_list[anticipo.partner_id.id] += saldo#anticipo.saldo
                        id_line_line = line_line_obj.create(cr, uid, {
                            'name':anticipo.narration,
                            'monto':anticipo.amount,
                            'devengado':devengado,
                            'saldo':saldo,
                        })
                        lista_ids_detalle.append(id_line_line)
                    for partner in partner_list:
                        if partner_list[partner]>0:
                            line_id = line_obj.create(cr, uid, {
                                'partner_id':partner,
                                'saldo':partner_list[partner],
                                'devengado':devengado_all,
                                'monto':anticipo_aux,
                                'cxc_id':this.id,
                            })
                    line_line_obj.write(cr, uid, lista_ids_detalle,{'l_id':line_id})
            else:
                cr.execute(''' select partner_id from account_voucher where internal_type='AP' group by partner_id''')
                for res in cr.fetchall():
                    lista_ids_detalle = []
                    anticipo_ids = anticipo_obj.search(cr, uid, [('internal_type','=','AP'),('partner_id','=',res[0])])
                    monto_all = devengado_all = saldo_all = 0
                    if anticipo_ids:
                        for anticipo_id in anticipo_ids:
                            anticipo = anticipo_obj.browse(cr, uid, anticipo_id)
                            anticipo_aux = devengado = saldo = 0
                            for line_devengado in anticipo.dev_ids:
                                if line_devengado.name or line_devengado.is_migrado:
                                    if line_devengado.name.state=='posted' or line_devengado.is_migrado:
                                        devengado += line_devengado.monto
                            devengado_all += devengado
                            anticipo_aux += anticipo.amount
                            monto_all += anticipo_aux
                            saldo = anticipo.amount - devengado
                            saldo_all += saldo
                            id_line_line = line_line_obj.create(cr, uid, {
                                'name':anticipo.narration,
                                'monto':anticipo.amount,
                                'devengado':devengado,
                                'saldo':saldo,
                            })
                            lista_ids_detalle.append(id_line_line)
                    if saldo_all>0:
                        line_id = line_obj.create(cr, uid, {
                            'partner_id':res[0],
                            'saldo':saldo_all,
                            'devengado':devengado_all,
                            'monto':monto_all,
                            'cxc_id':this.id,
                        })
                        line_line_obj.write(cr, uid, lista_ids_detalle,{'l_id':line_id})
            #recaudacion cxc tesorera
#            if not this.partner_id:
#                account_ids = account_obj.search(cr, uid, [('type','=','receivable')])
#                fiscal_id = fiscal_obj.find(cr, uid, this.date)
#                ctx = {}
#                if fiscal_id:
#                    fiscal = fiscal_obj.browse(cr, uid, fiscal_id)
#                ctx['fiscalyear'] = fiscal.id
#                ctx['date_from'] = fiscal.date_start
#                ctx['date_to'] =  fiscal.date_stop
#                ctx['state'] = 'posted'
#                aux_monto = 0
#                for account_id in account_ids:
#                    account = account_obj.browse(cr, uid, account_id)
#                    if account.code[0:3]=='113':
#                        account_aux = account_obj.read(cr, uid, account_id, ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx)
#                        if account_aux['balance']!=0:
#                            aux_monto += abs(account_aux['balance'])
#                if aux_monto>0:
#                    line_obj.create(cr, uid, {
#                        'partner_id':1,
#                        'monto':aux_monto,
#                        'cxc_id':this.id,
#                    })
            #124 revisar
        return True
        
        _defaults = dict(
            date = time.strftime('%Y-%m-%d'),
        )

cxcPartner()

##################################################
class wizardPagarCxP(osv.Model):
    _name = 'wizard.pagar.cxp'

    def action_pagar_cxp(self, cr, uid, ids, context):
        for this in self.browse(cr, uid, ids):
            print "VELE"
        return {'type':'ir.actions.act_window_close' }

    _columns = dict(
        date = fields.date('Fecha Pago',required=True),
        monto = fields.float('Monto Pago',required=True),
        line_ids = fields.one2many('account.move.line','wcxp_id','Cuentas por pagar'),
    )
wizardPagarCxP()

class movePorPagar(osv.Model):
    _name = 'move.por.pagar'
    _columns = dict(
        cxp_id = fields.many2one('cxp.partner.line','Proveedor'),
        move_id = fields.many2one('account.move','Comprobante'),
        move_line_id = fields.many2one('account.move.line','Asiento'),
        saldo = fields.float('Saldo por pagar'),
        narration = fields.related('move_id','narration',type='text',string='Detalle',store=True),
        date = fields.related('move_id','date',type='date',string='Fecha',store=True),
    )
movePorPagar()

class cxpPartnerLine(osv.Model):
    _name = 'cxp.partner.line'
    _order = 'partner_name'
    _columns = dict(
        partner_name = fields.char('Proveedor Nombre',size=128),
        partner_id = fields.many2one('res.partner','Beneficiario'),
        monto = fields.float('Monto'),
        cxp_id = fields.many2one('cxp.partner','Cuenta x pagar'),
        line_ids = fields.one2many('move.por.pagar','cxp_id','Comprobantes contables por pagar'),
    )
cxpPartnerLine()

class cxpPartner(osv.Model):
    _name = 'cxp.partner'
    _columns = dict(
        partner_id = fields.many2one('res.partner','Beneficiario'),
        line_ids = fields.one2many('cxp.partner.line','cxp_id','Detalle'),
    )

    def print_cxp_partner(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.cxp.partner'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cxp.partner',
            'model': 'cxp.partner',
            'datas': datas,
            'nodestroy': True,                        
            }


    def load_cxp_partner(self, cr, uid, ids, context):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        line_obj = self.pool.get('cxp.partner.line')
        account_obj = self.pool.get('account.account')
        line_por_pagar = self.pool.get('move.por.pagar')
        tax_obj = self.pool.get('account.tax')
        partner_obj = self.pool.get('res.partner')
        company_obj = self.pool.get('res.company')
        partner_ids = []
        ids_creado = []
        cuentas_debe = {}
        cuentas_haber = {}
        company = company_obj.browse(cr, uid, 1)
        aux_date = '2017-01-01'
        for this in self.browse(cr, uid, ids):
            if this.partner_id:
                partner_ids.append(this.partner_id.id)
            else:
                aux_state = "'" + 'posted' + "'"
                sql = """select partner_id from account_move where state=%s and date>='%s' group by partner_id""" % (aux_state,aux_date)
                cr.execute(sql)
                data = cr.fetchall()
                for id_partner in data:
                    if id_partner not in (1,company.tax_company_id.id,company.iess_id.id):
                        if not id_partner[0] in partner_ids:
                            partner_ids.append(id_partner[0])
            if partner_ids:
                for this in self.browse(cr, uid, ids):
                    line_antes = line_obj.search(cr, uid, [('cxp_id','=',this.id)])
                    if line_antes:
                        line_obj.unlink(cr, uid, line_antes)
                    for partner_id in partner_ids:
                        total_partner = 0
                        line_creada = ''
                        partner = partner_obj.browse(cr, uid, partner_id)
                        partner_name = partner.name
                        move_line_ids = move_line_obj.search(cr, uid, [('saldo','>',0),('partner_id','=',partner_id),('move_id.type','!=','Nomina'),
                                                                       ('date','>=',aux_date),('move_id.state','=','posted')])
                        lista_moves = []
                        if move_line_ids:
                            for move_line_id in move_line_ids:
                                move_line = move_line_obj.browse(cr, uid, move_line_id)
                                if move_line.account_id.code[0:3]!='213':
                                    continue
                                pagos_ids = move_line_obj.search(cr, uid, [('move_line_cxp','=',move_line_id),('move_id.state','=','posted')])
                                pagado = 0
                                if pagos_ids:
                                    for pago_id in pagos_ids:
                                        pago = move_line_obj.browse(cr, uid, pago_id)
                                        pagado += pago.debit
                                if (move_line.account_id.code[0:3]=='213' and (move_line.credit>pagado)):
                                    line_cxp_id = line_por_pagar.create(cr, uid, {
                                        'move_id':move_line.move_id.id,
                                        'saldo':move_line.saldo,
                                        'move_line_id':move_line.id,
                                    })
                                    lista_moves.append(line_cxp_id)
                                    total_partner += move_line.saldo
                            if lista_moves:
                                line_creada = line_obj.create(cr, uid, {
                                    'partner_id':partner_id,
                                    'partner_name':partner_name,
                                    'monto':total_partner,
                                    'cxp_id':this.id,
                                })    
                                for lista_move_id in lista_moves:
                                    line_por_pagar.write(cr, uid, lista_move_id,{
                                        'cxp_id':line_creada,
                                    })
        return True

    def load_cxp_partnerV1(self, cr, uid, ids, context):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        line_obj = self.pool.get('cxp.partner.line')
        account_obj = self.pool.get('account.account')
        line_por_pagar = self.pool.get('move.por.pagar')
        partner_ids = []
        ids_creado = []
        cuentas_debe = {}
        cuentas_haber = {}
        for this in self.browse(cr, uid, ids):
            if this.partner_id:
                partner_ids.append(this.partner_id.id)
            else:
                aux_state = "'" + 'posted' + "'"
                sql = """select partner_id from account_move where state=%s group by partner_id""" % (aux_state)
                cr.execute(sql)
                data = cr.fetchall()
                for id_partner in data:
                    if id_partner!=1:
                        if not id_partner[0] in partner_ids:
                            partner_ids.append(id_partner[0])
        if partner_ids:
            for this in self.browse(cr, uid, ids):
                line_antes = line_obj.search(cr, uid, [('cxp_id','=',this.id)])
                if line_antes:
                    line_obj.unlink(cr, uid, line_antes)
                for partner_id in partner_ids:
                    move_ids = move_obj.search(cr, uid, [('partner_id','=',partner_id),('state','=','posted')])
                    if move_ids:
                        total_cxp = total_pagado = total_banco = iva_por_pagar = renta_por_pagar = iva_pagado = aux_monto =0
                        for move_id in move_ids:
                            move = move_obj.browse(cr, uid, move_id)
                            cuentas_debe = {}
                            cuentas_haber = {}
                            total_pagado_c = total_iva_pagar_c =total_banco_c = total_cxp_c = 0
                            for move_line in move.line_id:
                                if move_line.debit>0:
                                    if move_line.account_id.id in cuentas_debe:
                                        cuentas_debe[move_line.account_id.id]+=move_line.debit
                                    else:
                                        cuentas_debe[move_line.account_id.id]=move_line.debit
                                else:
                                    if move_line.account_id.id in cuentas_haber:
                                        cuentas_haber[move_line.account_id.id]+=move_line.credit
                                    else:
                                        cuentas_haber[move_line.account_id.id]=move_line.credit
                            for cuenta_debe in cuentas_debe:
                                account = account_obj.browse(cr, uid, cuenta_debe)
                                if account.code[0:3]=='213':
                                    if ('IVA' or 'iva' or 'Iva') in account.name:
                                        iva_pagado += cuentas_debe[cuenta_debe]
                                    else:
                                        total_pagado += cuentas_debe[cuenta_debe]
                                        total_pagado_c += cuentas_debe[cuenta_debe]
                            for cuenta_haber in cuentas_haber:
                                account = account_obj.browse(cr, uid, cuenta_haber)
                                if account.code[0:3]=='213':
                                    #total_cxp += cuentas_haber[cuenta_haber]
                                    #total_cxp_c += cuentas_haber[cuenta_haber]
                                    if ('IVA' or 'iva' or 'Iva') in account.name:
                                        total_iva_pagar_c += cuentas_haber[cuenta_haber]
                                    else:
                                        #aqui falta hacer q no considere la renta
                                        if not account.partner_id:
                                            total_cxp += cuentas_haber[cuenta_haber]
                                            total_cxp_c += cuentas_haber[cuenta_haber]
                                else:
                                    if account.code[0:3]=='111':
                                        total_banco += cuentas_haber[cuenta_haber]
                                        total_banco_c += cuentas_haber[cuenta_haber]
                            #add el move que tiene cta por pagar
                            if total_cxp_c > total_banco_c:
                                aux_monto_c = abs(total_banco_c - total_cxp_c)
                                id_cxp = line_por_pagar.create(cr, uid, {
                                    'move_id':move_id,
                                    'saldo':aux_monto_c,
                                })
                                ids_creado.append(id_cxp)
                        if total_cxp > total_banco:
                            aux_monto += abs(total_banco - total_cxp)
#                            aux_monto = abs(total_banco - total_cxp)
                            id_linea = line_obj.create(cr, uid, {
                                'partner_id':partner_id,
                                'monto':aux_monto,
                                'cxp_id':this.id,
                            })
                            for id_creado in ids_creado:
                                line_por_pagar.write(cr, uid, id_creado,{
                                    'cxp_id':id_linea,
                                })
        return True

cxpPartner()
