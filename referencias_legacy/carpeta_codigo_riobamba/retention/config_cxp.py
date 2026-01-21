# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
##############################################################################

from osv import osv, fields
from tools.translate import _

class cajaBancosLine(osv.Model):
    _name = 'caja.bancos.line'
    _columns  = dict(
        account_id = fields.many2one('account.account','Cuenta Banco o Caja'),
        monto = fields.float('Monto'),
        c_id = fields.many2one('caja.bancos','Caja'),
    )
cajaBancosLine()
class cajaBancos(osv.Model):
    _name = 'caja.bancos'
    _columns = dict(
        name = fields.many2one('account.fiscalyear','Periodo Fiscal'),
        cuenta = fields.char('Cuenta Mayor bancos y caja(Disponibilidades 111)',size=4),
        line_ids = fields.one2many('caja.bancos.line','c_id','Detalle'),
        budget_id = fields.many2one('budget.item','Partida'),
        fecha = fields.date('Fecha'),
    )

    def generaAsientoCaja(self, cr, uid, ids, context):
        item_obj = self.pool.get('budget.item.migrated')
        for this in self.browse(cr, uid, ids):
            if not this.budget_id.poa_id.state=='Abierto':
                raise osv.except_osv('Error de Usuario','El presupuesto del año a aplicar no esta abierto.')
            total = 0
            for line in this.line_ids:
                total+=line.monto
            if this.budget_id:
                #item_anterior = item_obj.search(cr, uid, [('budget_item_id','=',this.budget_id.id),('date','=',this.budget_id.date_start)])
                #context = {'elimina':True}
                #if item_anterior:
                #    item_obj.unlink(cr, uid, item_anterior,context)
                item_id = item_obj.create(cr, uid, {
                    'budget_item_id':this.budget_id.id,
                    'budget_post_id':this.budget_id.budget_post_id.id,
                    'paid_amount':total,
                    'devengado_amount':total,
                    'date':this.fecha,
                    'program_code':'0000',
                    'type_budget':'ingreso',
                })
        return True

    def loadCuentasCaja(self, cr, uid, ids, context):
        account_obj = self.pool.get('account.account')
        line_obj = self.pool.get('caja.bancos.line')
        for this in self.browse(cr, uid, ids):
            line_antes = line_obj.search(cr, uid, [('c_id','=',this.id)])
            if line_antes:
                line_obj.unlink(cr, uid, line_antes)
            ctx = {}
            ctx['fiscalyear'] = this.name.id
            ctx['date_from'] = this.name.date_start
            ctx['date_to'] =  this.name.date_stop
            ctx['state'] = 'posted'
            cuenta_aux = this.cuenta
            aux_str = "'"+'%' + cuenta_aux + '%'+"'"
            aux_str_2 = "'"+'view'+"'"
            aux = '''select id from account_account where substring(code,%s,%s) ilike %s and type!=%s''' % (str(1),str(len(cuenta_aux)),aux_str,aux_str_2)
            cr.execute(aux)
            for acc in cr.dictfetchall():
                aux_cuenta_id = acc['id']
                account = account_obj.read(cr, uid, aux_cuenta_id, ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx) 
                if account['balance']!=0:
                    line_obj.create(cr, uid, {
                        'c_id':this.id,
                        'account_id':aux_cuenta_id,
                        'monto':abs(account['balance']),
                    })
        return True

    _defaults = dict(
        cuenta = '111',
    )
cajaBancos()

class clonaRegla(osv.TransientModel):
    _name = 'clona.regla'
    _columns = dict(
        regla_id = fields.many2one('regla.cierre','Regla a clonar'),
    )

    def action_clonaRegla(self, cr, uid, ids, context):
        regla_obj = self.pool.get('regla.cierre')
        regla_line_obj = self.pool.get('regla.cierre.line')
        regla = regla_obj.browse(cr, uid, context['active_id'])
        for this in self.browse(cr, uid, ids):
            for line in regla.origen_ids:
                line_antes_ids = regla_line_obj.search(cr, uid, [('origen_id','=',line.origen_id.id),('regla_id','=',this.regla_id.id)])
                if line_antes_ids:
                    line_antes = regla_line_obj.browse(cr, uid, line_antes_ids[0])
                    regla_line_obj.write(cr, uid, line.id,{
                        'destino_id':line_antes.destino_id.id,
                    })
        return {'type':'ir.actions.act_window_close' }

    def action_clonaRegla2(self, cr, uid, ids, context):
        regla_obj = self.pool.get('regla.cierre')
        regla_line_obj = self.pool.get('regla.cierre.line')
        regla = regla_obj.browse(cr, uid, context['active_id'])
        regla_pasa = []
        for this in self.browse(cr, uid, ids):
            regla_id = regla_obj.create(cr, uid, {
                'name':regla.name,
                'tipo_origen':regla.tipo_origen,
                'fiscal_id':this.year_id.id,
                'origen':regla.origen,
                'destino_account':regla.destino_account.id,
            })
            regla_pasa.append(regla_id)

        #ahora voy colocando las cuentas de cada linea
        regla_nueva = regla_obj.browse(cr, uid, regla_id)
        regla_obj.loadCuentasCierre(self, cr, uid, [regla_nueva.id])
        for line in regla_nueva.origen_ids:
            line_antes_ids = regla_line_obj.search(cr, uid, [('origen_id','=',line.origen_id.id),('regla_id','=',regla.id)])
            if line_antes_ids:
                line_antes = regla_line_obj.browse(cr, uid, line_antes_ids[0])
                regla_line_obj.write(cr, uid, line.id,{
                    'destino_id':line_antes.destino_id.id,
                })
        return {'type':'ir.actions.act_window_close' }
clonaRegla()

class reglaCierreLine(osv.Model):
    _name = 'regla.cierre.line'
    _order = 'codigo asc'
    _columns = dict(
        codigo = fields.related('origen_id','code',type='char',size=128,store=True),
        regla_id = fields.many2one('regla.cierre','Regla'),
        origen_id = fields.many2one('account.account','Origen'),
        destino_id = fields.many2one('account.account','Destino'),
    )
reglaCierreLine()

class reglaCierre(osv.Model):
    _name = 'regla.cierre'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
                name = record.name + " - " + record.fiscal_id.name
                res.append((record.id, name))
        return res    

    def loadCuentasCierre(self, cr, uid, ids, context):
        cierre_obj = self.pool.get('regla.cierre')
        account_obj = self.pool.get('account.account')
        line_obj = self.pool.get('regla.cierre.line')
        type_obj = self.pool.get('account.account.type')
        for this in self.browse(cr, uid, ids):
            lineas_antes = line_obj.search(cr, uid, [('regla_id','=',this.id)])
#            if lineas_antes:
#                line_obj.unlink(cr, uid, lineas_antes)
            #user type para creacion de cuenta
            cierre_obj.write(cr, uid, this.id,{'c_id':uid})
            aux_texto = ''
            if this.destino_account:
                if this.destino_account.code[0:1]=='1':
                    aux_texto= 'CXCAA '
                    type_ids = type_obj.search(cr, uid, [('name','=','Activo')])
                elif this.destino_account.code[0:1]=='2':
                    aux_texto= 'CXPAA '
                    type_ids = type_obj.search(cr, uid, [('name','in',('Pasivo','Pasivos'))])
                else:
                    type_ids = type_obj.search(cr, uid, [('name','=','Patrimonio')])
            else:
                type_ids = type_obj.search(cr, uid, [('name','=','Activo')])
            if not type_ids:
                type_ids = type_obj.search(cr, uid, [])
            ctx = {}
            ctx['fiscalyear'] = this.fiscal_id.id
            ctx['date_from'] = this.fiscal_id.date_start
            ctx['date_to'] =  this.fiscal_id.date_stop
            ctx['state'] = 'posted'
            cuenta_aux = this.origen
            aux_str = "'"+'%' + cuenta_aux + '%'+"'"
            aux_str_2 = "'"+'view'+"'"
            aux = '''select id from account_account where substring(code,%s,%s) ilike %s and type!=%s''' % (str(1),str(len(cuenta_aux)),aux_str,aux_str_2)
            print "AUX", aux
            cr.execute(aux)
            for acc in cr.fetchall():
                aux_cuenta_id = acc[0]
                account = account_obj.read(cr, uid, aux_cuenta_id, ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx)
                if account['balance']!=0:
                    if this.destino_account:
                        if this.detallado:
                            #milagro hay una cuenta por cada proveedor pero con el mismo codigo
#                            if account['code']=='2138403011':
#                                import pdb
#                                pdb.set_trace()
                            aux_code_origen = '0'+account['code'][3:]
                            aux_code_destino = this.destino_account.code
                            aux_code_busca = aux_code_destino+aux_code_origen
                            destino_ids = account_obj.search(cr, uid, [('code','ilike','%'+aux_code_busca+'%')])
                            parent_ids = account_obj.search(cr, uid, [('code','=',aux_code_busca[0:len(aux_code_busca)-3])])
                            if not parent_ids:
                                parent_ids = account_obj.search(cr, uid, [('code','=',aux_code_busca[0:len(aux_code_busca)-2])])
                                if not parent_ids:
                                    print "NO PARENT"
                            if destino_ids:
                                destino_id = destino_ids[0]
                            else:#creo la cuenta
                                aux_name = aux_texto + account['name']
                                destino_id = account_obj.create(cr, uid, {
                                    'code':aux_code_busca,
                                    'code_aux':aux_code_busca,
                                    'name':aux_name,
                                    'type':'payable',
                                    'user_type':type_ids[0],
                                    'parent_id':parent_ids[0],
                                })
                            #busco si esta ya no crea la linea
                            line_antes = line_obj.search(cr, uid, [('origen_id','=',aux_cuenta_id),('regla_id','=',this.id)])
                            if not line_antes:
                                line_obj.create(cr, uid, {
                                    'regla_id':this.id,
                                    'origen_id':aux_cuenta_id,
                                    'destino_id':destino_id,
                                })
                        else:
                            line_antes = line_obj.search(cr, uid, [('origen_id','=',aux_cuenta_id),('regla_id','=',this.id)])
                            if not line_antes:
                                line_obj.create(cr, uid, {
                                    'regla_id':this.id,
                                    'origen_id':aux_cuenta_id,
                                    'destino_id':this.destino_account.id,
                                })
                    else:
                        line_obj.create(cr, uid, {
                            'regla_id':this.id,
                            'origen_id':aux_cuenta_id,
                        })
        return True
            

    def generaAsientoCierre(self, cr, uid, ids, context):
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        creadas = []
        for this in self.browse(cr, uid, ids):
            journal_ids = journal_obj.search(cr, uid, [('type','=','situation'),('centralisation','=',False)],limit=1)
            if not journal_ids:
                raise osv.except_osv('Error configuracion','No esta creada un diario de situacion cierre, verifique que este falso el campo centralizado del diario.')
            period_ids = period_obj.find(cr, uid, this.fiscal_id.date_stop)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            ctx = {}
            journal_id = journal_ids[0]
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            name_aux = 'Asiento Cierre ' + this.name + ' ' + this.fiscal_id.name
            date_aux = this.fiscal_id.date_stop
            move_id = move_obj.create(cr, uid, {
                'ref': name_aux,
                'narration':name_aux,
                'journal_id': journal_id,
                'date': date_aux,
                'period_id':period_ids[0],
                'state':'draft',
                'afectacion':False,
                'partner_id':1,
                'type2_id':'Cierre',
            })
            move = move_obj.browse(cr, uid, move_id)
            ctx['fiscalyear'] = this.fiscal_id.id
            ctx['date_from'] = this.fiscal_id.date_start
            ctx['date_to'] =  this.fiscal_id.date_stop
            ctx['state'] = 'posted'
            aux_contra = 0
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            for line in this.origen_ids:
                if line.origen_id.id in creadas:
                    continue
                if line.origen_id.type=='view':
                    aux_codigo_cuenta = line.origen_id.code + ' - ' + line.origen_id.name
                    raise osv.except_osv('Error de usuario','La cuenta %s es de tipo vista'%(aux_codigo_cuenta))
                if line.destino_id.type=='view':
                    aux_codigo_cuenta = line.origen_id.code + ' - ' + line.origen_id.name
                    raise osv.except_osv('Error de usuario','La cuenta %s es de tipo vista'%(aux_codigo_cuenta))
                account = account_obj.read(cr, uid, line.origen_id.id, ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx)
                if account['balance']!=0:
                    if this.tipo_origen=='Debe':
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,line.origen_id.id,abs(account['balance']),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'',False))
                        if not line.destino_id:
                            aux_codigo_cuenta = line.origen_id.code + ' - ' + line.origen_id.name
                            raise osv.except_osv('Error de usuario','La cuenta %s no tiene configurada cuenta destino'%(aux_codigo_cuenta))
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,line.destino_id.id,abs(account['balance']),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'',False))
                    else:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,line.origen_id.id,abs(account['balance']),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'',False))
                        if not line.destino_id:
                            aux_codigo_cuenta = line.origen_id.code + ' - ' + line.origen_id.name
                            raise osv.except_osv('Error de usuario','La cuenta %s no tiene configurada cuenta destino'%(aux_codigo_cuenta))
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,line.destino_id.id,abs(account['balance']),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'',False))
                    creadas.append(line.origen_id.id)
        return True

    _columns = dict(
        c_id = fields.many2one('res.users','C'),
        detallado = fields.boolean('Detallado cuentas'),
        date_start = fields.date('Fecha Desde'),
        date_end = fields.date('Fecha Hasta'),
        name = fields.char('Descripcion',size=256,required=True),
        tipo_origen = fields.selection([('Debe','Debe'),('Haber','Haber')],'Trasladar a'),
        tipo_destino = fields.selection([('Debe','Debe'),('Haber','Haber')],'Tipo Destino'),
        origen_ids = fields.one2many('regla.cierre.line','regla_id','Movimiento Cuentas'),
        origen = fields.char('Cuentas Origen',size=10),
        destino_account = fields.many2one('account.account','Cuentas Destino'),
#        destino_ids = fields.many2many('account.account','d_c_id','Destino'),
        fiscal_id = fields.many2one('account.fiscalyear','Periodo'),
    )
reglaCierre()

#regla cierre traspaso
class reglaCierreLinet(osv.Model):
    _name = 'regla.cierre.linet'
    _columns = dict(
        regla_id = fields.many2one('regla.cierret','Regla'),
        origen_id = fields.many2one('account.account','Origen'),
        destino_id = fields.many2one('account.account','Destino'),
    )
reglaCierreLinet()

class reglaCierret(osv.Model):
    _name = 'regla.cierret'

    def loadCuentasCierret(self, cr, uid, ids, context):
        account_obj = self.pool.get('account.account')
        line_obj = self.pool.get('regla.cierre.linet')
        for this in self.browse(cr, uid, ids):
            ctx = {}
            ctx['fiscalyear'] = this.fiscal_id.id
            ctx['date_from'] = this.fiscal_id.date_start
            ctx['date_to'] =  this.fiscal_id.date_stop
            ctx['state'] = 'posted'
            cuenta_aux = this.origen
            aux_str = "'"+'%' + cuenta_aux + '%'+"'"
            aux_str_2 = "'"+'view'+"'"
            aux = '''select id from account_account where substring(code,%s,%s) ilike %s and type!=%s''' % (str(1),str(len(cuenta_aux)),aux_str,aux_str_2)
            cr.execute(aux)
            for acc in cr.dictfetchall():
                aux_cuenta_id = acc['id']
                account = account_obj.read(cr, uid, aux_cuenta_id, ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx)
                if account['balance']!=0:
                    if this.destino_account:
                        line_obj.create(cr, uid, {
                            'regla_id':this.id,
                            'origen_id':aux_cuenta_id,
                            'destino_id':this.destino_account.id,
                        })
                    else:
                        line_obj.create(cr, uid, {
                            'regla_id':this.id,
                            'origen_id':aux_cuenta_id,
                        })
        return True
            

    def generaAsientoCierret(self, cr, uid, ids, context):
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        creadas = []
        for this in self.browse(cr, uid, ids):
            journal_ids = journal_obj.search(cr, uid, [('type','=','situation'),('centralisation','=',False)],limit=1)
            if not journal_ids:
                raise osv.except_osv('Error configuracion','No esta creada un diario de situacion cierre, verifique que este falso el campo centralizado del diario.')
            period_ids = period_obj.find(cr, uid, this.fiscal_id.date_stop)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            ctx = {}
            journal_id = journal_ids[0]
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            name_aux = 'Asiento Traspaso ' + this.name + ' ' + this.fiscal_id.name
            date_aux = this.fiscal_id.date_stop
            move_id = move_obj.create(cr, uid, {
                'ref': name_aux,
                'narration':name_aux,
                'journal_id': journal_id,
                'date': date_aux,
                'period_id':period_ids[0],
                'state':'draft',
                'afectacion':False,
                'partner_id':1,
            })
            move = move_obj.browse(cr, uid, move_id)
            ctx['fiscalyear'] = this.fiscal_id.id
            ctx['date_from'] = this.fiscal_id.date_start
            ctx['date_to'] =  this.fiscal_id.date_stop
            ctx['state'] = 'posted'
            aux_contra = 0
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            for line in this.origen_ids:
                if line.origen_id.id in creadas:
                    continue
                account = account_obj.read(cr, uid, line.origen_id.id, ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx)
                if account['balance']!=0:
                    if this.tipo_origen=='Debe':
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,line.origen_id.id,abs(account['balance']),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'',False))
                        if not line.destino_id:
                            aux_codigo_cuenta = line.origen_id.code + ' - ' + line.origen_id.name
                            raise osv.except_osv('Error de usuario','La cuenta %s no tiene configurada cuenta destino'%(aux_codigo_cuenta))
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,line.destino_id.id,abs(account['balance']),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'',False))
                    else:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,line.origen_id.id,abs(account['balance']),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'',False))
                        if not line.destino_id:
                            aux_codigo_cuenta = line.origen_id.code + ' - ' + line.origen_id.name
                            raise osv.except_osv('Error de usuario','La cuenta %s no tiene configurada cuenta destino'%(aux_codigo_cuenta))
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado) VALUES (%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,line.destino_id.id,abs(account['balance']),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'',False))
                    creadas.append(line.origen_id.id)
        return True

    _columns = dict(
        date_start = fields.date('Fecha Desde'),
        date_end = fields.date('Fecha Hasta'),
        name = fields.char('Descripcion',size=256,required=True),
        tipo_origen = fields.selection([('Debe','Debe'),('Haber','Haber')],'Trasladar a'),
        tipo_destino = fields.selection([('Debe','Debe'),('Haber','Haber')],'Tipo Destino'),
        origen_ids = fields.one2many('regla.cierre.linet','regla_id','Movimiento Cuentas'),
        origen = fields.char('Cuentas Origen',size=10),
        destino_account = fields.many2one('account.account','Cuentas Destino'),
#        destino_ids = fields.many2many('account.account','d_c_id','Destino'),
        fiscal_id = fields.many2one('account.fiscalyear','Periodo'),
    )
reglaCierret()
##

class traspasoCuenta(osv.Model):
    _name = 'traspaso.cuenta'
    _columns = dict(
        name = fields.many2one('account.account','Cuenta Origen',required=True),
        account_id = fields.many2one('account.account','Cuenta Destino',required=True),
    )
traspasoCuenta()

class cuentaAnterior(osv.Model):
    _name = 'cuenta.anterior'
    _columns = dict(
        budget_id = fields.many2one('budget.item','Partida Anios Anteriores'),
        account_id = fields.many2one('account.account','Cuenta Anios Anteriores'),
    )
cuentaAnterior()
    

class payFondoSRI(osv.Model):
    _name = 'pay.fondo.sri'
    _columns = dict(
        account_id = fields.char('Cuenta por pagar',size=15),
        account_id2 = fields.char('Cuenta Fondo Tercero/SRI',size=15),
    )
payFondoSRI()

class cuentaPartida(osv.Model):
    _name = 'cuenta.partida'
    _columns = dict(
#        name = fields.many2one('account.account','Cuenta', required=True),
        name = fields.char('Cuenta',size=16,required=True),
        code = fields.char('Codigo',size=16,required=True),
        budget_debe = fields.many2one('budget.post','Partida Debe'),
        budget_haber = fields.many2one('budget.post','Partida Haber'),
    )
cuentaPartida()

class ctaPartida(osv.Model):
    _name = 'cta.partida'
    _order = 'partida asc'
    _columns = dict(
        cta = fields.char('Cuenta Mayor',size=10,required=True),
        ctap = fields.char('Cuenta Mayor Patrimonial',size=10,required=True),
        partida = fields.char('Partida Mayor',size=10,required=True),
    )
ctaPartida()

class config_cxp(osv.Model):
    _name = 'config.cxp'
    _columns = dict(
        budget = fields.many2one('budget.user.type','Aplicacion Presupuestaria',required=True),
#        cxp_id = fields.many2one('config.cxp','Tabla'),
#        budget = fields.selection([('corriente','CORRIENTE'),
 #                                  ('inversion','INVERSION'),
 #                                 ('general','GENERAL'),
 #                                  ('ogastos','OTROS GASTOS (CORRIENTE)'),
  #                                 ('opublica','OBRAS PUBLICAS (INVERSION)'),
   #                                ('ginversion', 'GASTOS DE INVERSION'),
   #                             ('tranf','TRANSF. DE INVERSION'),
   #                                ('bienesld','BIENES DE LARGA DURACION (INVERSION)')],
   #                               string='Aplicacion Presupuestaria.', required=True),
        account_id = fields.many2one('account.account','Cuenta Contable',required=True),
        )
config_cxp()

class ctas_categ(osv.Model):
    _name = 'ctas.categ'
    _columns = dict(
        categ_id = fields.many2one('product.category','Linea/Categoria'),
        account_ex_normal = fields.many2one('account.account','Corriente', domain=[('type','!=','view')]),
        account_ex_program = fields.many2one('account.account','Inversion Programa', domain=[('type','!=','view')]),
        account_ex_project = fields.many2one('account.account','Inversion Proyecto', domain=[('type','!=','view')]),
        account_expense = fields.many2one('account.account','Gasto Corriente', domain=[('type','!=','view')]),
        account_expense_inv = fields.many2one('account.account','Gasto Inversion', domain=[('type','!=','view')]),
        account_comp_id = fields.many2one('account.account', 'Cuenta Complemento', domain=[('type','!=','view')]),
        budget_ex = fields.many2one('budget.post','Partida Corriente',domain=[('internal_type','in',('gasto','normal'))]),
        budget_inv = fields.many2one('budget.post','Partida Inversion',domain=[('internal_type','in',('gasto','normal'))]),
        )

    def get_by_category(self, cr, uid, categ_id, budget, in_type):
        """
        budget: selection de la categoria
        """
        res = self.search(cr, uid, [('categ_id','=',categ_id)], limit=1)
        obj = self.browse(cr, uid, res[0])
        acc_id = obj.account_ex_normal.id
        if in_type == 'corriente':
            return obj.account_ex_normal.id
        else:
            if in_type == 'obra':
                return obj.account_ex_project.id
            else:
                return obj.account_ex_program.id
        return acc_id

ctas_categ()

#class config_cxp_line(osv.Model):
   # _name = 'config.cxp.line'
   # _columns = dict(
#        cxp_id = fields.many2one('config.cxp','Tabla'),
       # budget = fields.selection([('corriente','CORRIENTE'),
        #                           ('inversion','INVERSION'),
       #                            ('general','GENERAL'),
      #                             ('ogastos','OTROS GASTOS (CORRIENTE)'),
     #                              ('opublica','OBRAS PUBLICAS (INVERSION)'),
    #                               ('ginversion', 'GASTOS DE INVERSION'),
   #                                ('tranf','TRANSF. DE INVERSION'),
  #                                 ('bienesld','BIENES DE LARGA DURACION (INVERSION)')],
 #                                 string='Aplicacion Presupuestaria.', required=True),
  #      account_id = fields.many2one('account.account','Cuenta Contable',required=True),
 #       )
#config_cxp_line()

#class config_cxp(osv.Model):
#    _name = 'config.cxp'
#    _columns = dict(
#        name = fields.char('Descripcion',size=64,required=True),
#        line_ids = fields.one2many('config.cxp.line','cxp_id','Lineas'),
#        )

#config_cxp()
