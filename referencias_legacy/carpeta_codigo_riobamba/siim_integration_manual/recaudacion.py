
##############################################################################
#    Autores
#    Mario Chogllo
#    Diego Abad A
##############################################################################
from XLSWriter import XLSWriter
import base64
import xlrd
from tools import ustr
import time
from osv import osv, fields
import decimal_precision as dp

DP = dp.get_precision('Budget')

class budgetTitulo(osv.Model):
    _name = 'budget.titulo'
    _columns = dict(
        name = fields.many2one('budget.post','Partida',required=True),
        is_titulo = fields.boolean('Anio Anterior'),
    )
budgetTitulo()

class recaudacionManualLine(osv.Model):
    _name = 'recaudacion.manual.line'

    def onchange_budget_manual(self, cr, uid, ids, budget_id, context={}):
        post_obj = self.pool.get('budget.post')
        post = post_obj.browse(cr, uid, budget_id)
        vals = {}
        band = False
        if post.venta:
            band=True
        return {'value':{'genera_emision':True}} 

    _columns = dict(
        mn_id = fields.many2one('recaudacion.manual'),
        budget_id = fields.many2one('budget.post','Partida'),
        account_id = fields.many2one('account.account','Cuenta'),
        genera_emision = fields.boolean('Con Emision?'),
        monto = fields.float('Valor'),
    )
recaudacionManualLine()

class recaudacionManual(osv.Model):
    _name = 'recaudacion.manual'

    def generarComprobanteManual(self, cr, uid, ids, context=None):
        certificate_line_obj = self.pool.get('budget.certificate.line')
        certificate_obj = self.pool.get('budget.certificate')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        project_obj = self.pool.get('project.project')
        item_obj = self.pool.get('budget.item')
        itemm_obj = self.pool.get('budget.item.migrated')
        post_obj = self.pool.get('budget.post')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        manual_obj = self.pool.get('recaudacion.manual')
        for this in self.browse(cr, uid, ids):
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            name_aux = 'Cobro'
            date_aux = this.name
            #sacar diario de ingreso
            journal_ids = journal_obj.search(cr, uid, [('name','=','INGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv('Error de configuracion', 'No existe diario de INGRESOS por favor cree uno')
            period_ids = period_obj.find(cr, uid, this.name)
            period = period_obj.browse(cr, uid, period_ids[0])
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            if this.move_id:
                if this.move_id.state=='draft' and this.move_id.name=='/':
                    move_obj.unlink(cr, uid, [this.move_id.id],1)
                    move_id = move_obj.create(cr, uid, {
                        'ref': this.desc,
                        'narration':this.desc,
                        'journal_id': journal_ids[0],
                        'date': this.name,
                        'period_id':period_ids[0],
                        'state':'draft',
                        'afectacion':True,
                        'no_cp':True,
                        'partner_id':1,
                        'type':'Recaudacion',
                    })
                else:
                    if this.move_id.state=='posted':
                        state_aux='valid'
                    cr.execute("delete from account_move_line where move_id=%s"%(this.move_id.id))
                    move_id = this.move_id.id
            else:
                move_id = move_obj.create(cr, uid, {
                    'ref': this.desc,
                    'narration':this.desc,
                    'journal_id': journal_ids[0],
                    'date': this.name,
                    'period_id':period_ids[0],
                    'state':'draft',
                    'afectacion':True,
                    'no_cp':True,
                    'partner_id':1,
                    'type':'Recaudacion',
                })
            manual_obj.write(cr, uid, this.id, {
                'move_id':move_id,
            })
            move = move_obj.browse(cr, uid, move_id)
            aux_total = 0
            banco_account_id = this.bank_id.default_debit_account_id.id
            for line in this.line_ids:
                if line.monto<=0:
                    raise osv.except_osv(('Error de usuario !'),
                                         ("El monto en las lineas debe ser mayor a cero, revisar %s")%(line.budget_id.code))
                project_ids = project_obj.search(cr, uid, [('type_budget','=','ingreso')],limit=1)
                project = project_obj.browse(cr, uid, project_ids[0])
                item_ids = item_obj.search(cr, uid, [('budget_post_id','=',line.budget_id.id),('date_start','<=',this.name),('date_end','>=',this.name)],limit=1)
                if not item_ids:
                    raise osv.except_osv(('Error Configuracion !'),
                                         ("No existe la partida '%s'") % (line.budget_id.code)) 
                if line.budget_id.tipo=='e':
                    #saco el de ingrso
                    certificate_ing_ids = certificate_obj.search(cr, uid, [('tipo_aux','=','ingreso'),
                                                                           ('date','<=',this.name),('date_confirmed','>=',this.name)],limit=1)
                    if not certificate_ing_ids:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("Debe existir presupuesto de ingreso"))
                    item_descuento = item_obj.browse(cr, uid, item_ids[0])
                    itemm_anterior = itemm_obj.search(cr, uid, [('program_code','=',item_descuento.program_id.sequence),
                                                                ('commited_amount','=',aux_total),('date','=',this.name)])
                    context_unlink = {}
                    context_unlink['elimina']='Si'
                    if itemm_anterior:
                        itemm_obj.unlink(cr, uid, itemm_anterior,context_unlink)
                    aux_desc = item_descuento.budget_post_id.code + ' - ' + item_descuento.budget_post_id.name
                    itemm_id = itemm_obj.create(cr, uid, {
                        'budget_item_id':item_ids[0],
                        'budget_post_id':item_descuento.budget_post_id.id,
                        'commited_amount':line.monto,#aux_total,
                        'date':this.name,
                        'program_code':item_descuento.program_id.sequence,
                        'type_budget':'gasto',
                        'move_id':move_id,
                        'is_pronto':True,
                        'desc':aux_desc,
                    })
                    certificate_id = certificate_line_obj.create(cr, uid, {
                        'project_id':project.id,
                        'task_id':project.tasks[0].id,
                        'budget_id':item_ids[0],
#                        'amount_commited':line.monto,
                        'certificate_id':certificate_ing_ids[0],
                    })
                else:
                    certificate_id = certificate_line_obj.create(cr, uid, {
                        'project_id':project.id,
                        'task_id':project.tasks[0].id,
                        'budget_id':item_ids[0],
                        'amount_commited':line.monto,
                    })
                certificate = certificate_line_obj.browse(cr, uid, certificate_id)
                b_id = certificate.budget_id.id
                p_id = certificate.budget_post.id
                account_ids = account_obj.search(cr, uid, [('budget_id','=',line.budget_id.id)])
                if not account_ids:
                    #busco la partida de mayor
                    budget_ids_mayor = post_obj.search(cr, uid, [('code','=',line.budget_id.code[0:6])])
                    account_ids = account_obj.search(cr, uid, [('budget_id','=',budget_ids_mayor[0])])
                    if not account_ids:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("No existe cuenta contable asociada a la partida '%s'")%(line.budget_id.code))
                for account_id in account_ids:
                    account = account_obj.browse(cr, uid, account_id)
                    if account.account_rec_id or account.account_pay_id:
                        break
#                    account = account_obj.browse(cr, uid, account_ids[0])
                aux_mseg_nocxp = account.code + ' - ' + account.name + ' - ' + certificate.budget_id.code
                if not account.account_rec_id or account.account_pay_id:
                    #buscar con la de mayor
                    budget_ids_mayor = post_obj.search(cr, uid, [('code','=',line.budget_id.code[0:6])])
                    account_ids = account_obj.search(cr, uid, [('budget_id','=',budget_ids_mayor[0])])
                    if not account_ids:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("No existe cuenta contable asociada a la partida '%s'")%(line.budget_id.code))
                    for account_id in account_ids:
                        account = account_obj.browse(cr, uid, account_id)
                        if account.account_rec_id or account.account_pay_id:
                            break
#                    raise osv.except_osv(('Error de configuracion !'),
#                                         ("No existe cuenta por cobrar asociada a la cuenta '%s'")%(aux_mseg_nocxp))
                if account.account_rec_id:
                    cxp = account.account_rec_id.id
                elif account.account_pay_id:
                    cxp = account.account_pay_id.id
                else:
                    raise osv.except_osv(('Error de configuracion !'),
                                         ("No existe cuenta por cobrar asociada a la cuenta '%s'")%(aux_mseg_nocxp))
                monto = line.monto
                if not this.bank_id.default_debit_account_id.id:
                    raise osv.except_osv(('Error de configuracion !'),
                                        ("El banco seleccionado no tiene configurada la cuenta contable"))

                if line.genera_emision:
                    #entrada cxc debe
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_accrued,budget_id_cert,budget_id,budget_post) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,True,certificate_id,b_id,p_id))
                    #linea  entrada cxc haber
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,budget_id_cert,budget_id,budget_post) VALUES (%s,%s, %s, %s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,True,certificate_id,b_id,p_id))
                    #linea  entrada cta patrimonial 621
                    #pregunto si es gasto cambia al haber
                    if line.budget_id.tipo=='e':
                        aux_total -= line.monto
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_accrued,budget_paid,name,migrado,budget_id_cert,budget_id,budget_post) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.id,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,False,False,name_aux,False,certificate_id,b_id,p_id))
                    else:
                        aux_total += line.monto
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_accrued,budget_paid,name,migrado,budget_id_cert,budget_id,budget_post) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.id,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,False,False,name_aux,False,certificate_id,b_id,p_id))
                else:
                    #validar si hay saldo para recaudar
                    item_aux = item_obj.browse(cr, uid, item_ids[0])
                    context = {'by_date':True,'date_start':period.fiscalyear_id.date_start, 'date_end': this.name,'poa_id':item_aux.poa_id.id}
                    item = item_obj.browse(cr, uid, item_ids[0],context=context)
                    if not item.devengado_amount >= line.monto:
                        aux_msg = line.budget_id.code + ' - ' + line.budget_id.name
                        raise osv.except_osv(('Error de usuario !'),
                                             ("La partida '%s' no tiene saldo por recaudar") % (aux_msg)) 
                    aux_total += line.monto
                    #linea  entrada cxc haber
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,budget_id_cert,budget_id,budget_post) VALUES (%s,%s, %s, %s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,True,certificate_id,b_id,p_id))
            cr.execute('''
            INSERT INTO account_move_line (
            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s)''',(move_id,banco_account_id,aux_total,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False))
        return True

    def _get_estado(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 'Pendiente'
        for this in self.browse(cr, uid, ids):
            if this.move_id.state=='posted':
                aux = 'Realizado'
            res[this.id] = aux
        return res

    _columns = dict(
        state = fields.function(_get_estado,string='ESTADO',type="char",size=10,store=True),
        name = fields.date('Fecha'),
        desc = fields.char('Descripcion',size=256),
        bank_id = fields.many2one('account.journal','Banco'),
        line_ids = fields.one2many('recaudacion.manual.line','mn_id','Detalle'),
        move_id = fields.many2one('account.move','Comprobante Generado'),
    )
recaudacionManual()
