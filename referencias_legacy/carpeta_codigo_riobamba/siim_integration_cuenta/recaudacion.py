
##############################################################################
#    Autor
#    Mario Chogllo
##############################################################################
from XLSWriter import XLSWriter
import base64
import xlrd
from tools import ustr
import time
from osv import osv, fields
import decimal_precision as dp

DP = dp.get_precision('Budget')

class recaudadoPartidaActAntLine(osv.TransientModel):
    _name = 'recaudado.partida.ant.line'
    _order = 'date asc'
    _columns = dict(
        ant_id = fields.many2one('recaudado.partida.ant','Detalle'),
        date = fields.date('Fecha'),
        move_id = fields.char('Comprobante Contable',size=16),
        desc = fields.char('Detalle',size=128),
        actual = fields.float('Actual'),
        anterior = fields.float('Anterior'),
        total = fields.float('Total'),
    )
recaudadoPartidaActAntLine()
class recaudadoPartidaActAnt(osv.TransientModel):
    _name = 'recaudado.partida.ant'
    _columns = dict(
        poa_id = fields.many2one('budget.poa','Presupuestos'),
        date_start = fields.date('Desde'),
        date_end = fields.date('Hasta'),
        item_id = fields.many2one('budget.item','Partida'),
        line_ids = fields.one2many('recaudado.partida.ant.line','ant_id','Detalle'),
        is_conta = fields.boolean('Reg. Contables'),
    )

    def printRecAnt(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        solicitud = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [solicitud.id], 'model': 'recaudado.partida.ant'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'recant',
            'model': 'recaudado.partida.ant',
            'datas': datas,
            'nodestroy': True,                        
            }

    
    def computeRecAnt(self, cr, uid, ids, context=None):
        rec_obj = self.pool.get('account.recaudacion')
        line_obj = self.pool.get('recaudacion.line')
        line_report_obj = self.pool.get('recaudado.partida.ant.line')
        move_line_obj = self.pool.get('account.move.line')
        lista_move = []
        for this in self.browse(cr, uid, ids):
            lines_antes = line_report_obj.search(cr, uid, [('ant_id','=',this.id)])
            if lines_antes:
                line_report_obj.unlink(cr, uid, lines_antes)
            rec_ids = []
            if not this.is_conta:
                rec_ids = rec_obj.search(cr, uid, [('date','<=',this.date_end),('date','>=',this.date_start)])
            if rec_ids:
                line_actual1_ids = line_obj.search(cr, uid, [('rec_id','in',rec_ids),('partida_id','=',this.item_id.code_aux)])
                if line_actual1_ids:
                    actual_base = line_obj.browse(cr, uid, line_actual1_ids[0])
                else:
                    raise osv.except_osv('Error de usuario', 'Seleccione rango de fechas correcto')
                for rec_id in rec_ids:
                    recaudacion = rec_obj.browse(cr, uid, rec_id)
                    total = actual = anterior = 0
                    line_actual_ids = line_obj.search(cr, uid, [('rec_id','=',rec_id),('partida_id','=',this.item_id.code_aux)])
                    if line_actual_ids:
                        for line_actual_id in line_actual_ids:
                            line_actual = line_obj.browse(cr, uid, line_actual_id)
                            actual += line_actual.valor
                        line_anterior_ids = line_obj.search(cr, uid, [('rec_id','=',rec_id),('desc','=',line_actual.desc),('partida_id','!=',this.item_id.code_aux)])
                        if line_anterior_ids:
                            for line_anterior_id in line_anterior_ids:
                                line_anterior = line_obj.browse(cr, uid, line_anterior_id)
                                anterior += line_anterior.valor
                        total = actual + anterior
                        if total>0:
                            lista_move.append(recaudacion.move_id.id)
                            line_report_obj.create(cr, uid, {
                                'ant_id':this.id,
                                'move_id':recaudacion.move_id.name,
                                'desc':recaudacion.move_id.narration,
                                'actual':actual,
                                'anterior':anterior,
                                'total':total,
                                'date':recaudacion.move_id.date,
                            })
                    else:
                        aux_nombre_partida = this.item_id.budget_post_id.name
                        line_anterior_ids = line_obj.search(cr, uid, [('rec_id','=',rec_id),('desc','=',actual_base.desc),
                                                                      ('partida_id','!=',this.item_id.code_aux)])
                        if line_anterior_ids:
                            for line_anterior_id in line_anterior_ids:
                                lista_move.append(recaudacion.move_id.id)
                                line_anterior = line_obj.browse(cr, uid, line_anterior_id)
                                line_report_obj.create(cr, uid, {
                                    'ant_id':this.id,
                                    'move_id':recaudacion.move_id.name,
                                    'desc':recaudacion.move_id.narration,
                                    'actual':0,
                                    'anterior':line_anterior.valor,
                                    'total':line_anterior.valor,
                                    'date':recaudacion.move_id.date,
                                })  
            ###de otros moves
            move_line_ids = move_line_obj.search(cr, uid, [('move_id','not in',lista_move),('budget_id','=',this.item_id.id),
                                                           ('date','>=',this.date_start),('date','<=',this.date_end),('credit','!=',0)])
            aux = 0
            if move_line_ids:
                for move_line_id in move_line_ids:
                    move_line = move_line_obj.browse(cr, uid, move_line_id)
                    if move_line.account_id.code[0:1]=='1':
                        aux = move_line.debit + move_line.credit
                        line_report_obj.create(cr, uid, {
                            'ant_id':this.id,
                            'move_id':move_line.move_id.name,
                            'desc':move_line.move_id.narration,
                            'actual':aux,
                            'anterior':0,
                            'total':aux,
                            'date':move_line.move_id.date,
                        })
                    if this.is_conta:
                        move_line = move_line_obj.browse(cr, uid, move_line_id)
                        aux = move_line.debit + move_line.credit
                        line_report_obj.create(cr, uid, {
                            'ant_id':this.id,
                            'move_id':move_line.move_id.name,
                            'desc':move_line.move_id.narration,
                            'actual':aux,
                            'anterior':0,
                            'total':aux,
                            'date':move_line.move_id.date,
                        })
        return True

recaudadoPartidaActAnt()
class recLine(osv.Model):
    _inherit = 'recaudacion.line'
    _order = "account_id asc"

    def _get_code_budget(self, cr, uid, ids, name, args, context=None):
        res = {}
        account_obj = self.pool.get('account.account')
        for this in self.browse(cr, uid, ids):
            aux_cuenta = this.account_id.replace('.','')
            aux_cuenta = aux_cuenta.replace('\t','')
            account_ids = account_obj.search(cr, uid, [('code','=',aux_cuenta)])
            if account_ids:
                account = account_obj.browse(cr, uid, account_ids[0])
                res[this.id] = account.budget_id.code
        return res

    _columns = dict(
        partida_id = fields.function(_get_code_budget, store=True, string='Partida',type='char',size=32),
        updated = fields.boolean('Actualizado'),
    )
recLine()

##########################

class accountRecaudacionCuenta(osv.Model):
    _inherit = 'account.recaudacion'

    def contabilizar_recaudado(self, cr, uid, ids, context=None):
        '''SE VERIFICA LA PARTIDA PRESUPUESTARIA SI ES VENTA(TRUE) TIENE EL DOBLE MOVIMIENTO DE CUENTAS
        CASO CONTRARIO SOLO LA CTA POR COBRAR POR QUE ES EMISIONES Y SI ES ANIO ANTERIOR VA EL MOVIMIENTO CON ANIOS ANTERIORES
        '''
        item_obj = self.pool.get('budget.item')
        itemm_obj = self.pool.get('budget.item.migrated')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        partida_obj = self.pool.get('budget.post')
        rec_line = self.pool.get('recaudacion.line')
        parent_obj = self.pool.get('account.recaudacion')
        period_obj = self.pool.get('account.period')
        parameter_obj = self.pool.get('ir.config_parameter')
        certificate_obj = self.pool.get('budget.certificate')
        project_obj = self.pool.get('project.project')
        for this in self.browse(cr, uid, ids):
            aux_narration = "ASIENTO CONTABLE DE RECAUDACION MUNICIPAL: " + this.name
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            anterior_dict = {}
            date_aux = this.date
            name_aux = 'RECAUDACION'
            certificate_ids = certificate_obj.search(cr, uid, [('tipo_aux','=','ingreso'),
                                                               ('date','<=',this.date),('date_confirmed','>=',this.date)],limit=1)
            if not certificate_ids:
                raise osv.except_osv('Error de configuracion', 'No existe certificado de ingresos')
            period_ids = period_obj.find(cr, uid, this.date)
            if not period_ids:
                raise osv.except_osv('Error de configuracion', 'No existe periodo para el comprobante')
            if this.move_id:
                if this.move_id.state=='draft' and this.move_id.name=='/':
                    cr.execute("delete from account_move_line where move_id=%s"%(this.move_id.id))
                    move_obj.unlink(cr, uid, [this.move_id.id],aux=1)
                    move_id = move_obj.create(cr, uid, {
                        'certificate_id':certificate_ids[0],
                        'ref': this.name,
                        'narration':aux_narration,
                        'journal_id': this.journal_id.id,
                        'date': this.date,
                        'state':'draft',
                        'afectacion':True,
                        'partner_id':1,
                        'period_id': period_ids[0],
                        'type':'Recaudacion',
                    })
                elif this.move_id.state=='anulado':
                    move_id = move_obj.create(cr, uid, {
                        'certificate_id':certificate_ids[0],
                        'ref': this.name,
                        'narration':aux_narration,
                        'journal_id': this.journal_id.id,
                        'date': this.date,
                        'state':'draft',
                        'afectacion':True,
                        'partner_id':1,
                        'period_id': period_ids[0],
                        'type':'Recaudacion',
                    })
                elif this.move_id.state in ('posted','draft'):
                    move_obj.write(cr, uid, [this.move_id.id],{
                        'state':'draft',
                    })
                    move_id = this.move_id.id
                    cr.execute("delete from account_move_line where move_id=%s"%(this.move_id.id))
            else:
                move_id = move_obj.create(cr, uid, {
                    'certificate_id':certificate_ids[0],
                    'ref': this.name,
                    'narration':aux_narration,
                    'journal_id': this.journal_id.id,
                    'date': this.date,
                    'state':'draft',
                    'afectacion':True,
                    'partner_id':1,
                    'period_id': period_ids[0],
                    'type':'Recaudacion',
                    })
            move = move_obj.browse(cr, uid, move_id)
            self.write(cr, uid, this.id,{'move_id':move_id})
            anterior = anterior_mejora = 0
            for line in this.recaudacion_ids:
                aux_code_budget = line.partida_id
                valor = line.actual_value
                aux_code1 = line.account_id.replace('.','')
                j = 0
                aux_code = ''
                for j in range(len(aux_code1)):
                    if aux_code1[j].isdigit():
                        aux_code+=aux_code1[j]
                account_ids = account_obj.search(cr, uid, [('code','=',aux_code)])
                if not account_ids:
                    raise osv.except_osv(('Error de Configuracion !'),
                                         ("No esta creada la cuenta contable '%s'") % (aux_code))
                account = account_obj.browse(cr, uid, account_ids[0])
                account_id = account.id
                #preguntar si es del GAD traer partida
                if aux_code[0:3] in ('212','112'):
                    if valor>0:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,account_id,valor,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,1,False))
                elif aux_code=='1138102001':
                    if valor>0:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,account_id,valor,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,1,False))
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,account_id,valor,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,1,False))
                elif aux_code[0:3]=='124':
                    if account.code=='12498010013021':
                        anterior_mejora += valor
                    else:
                        more_ant = ''
                        #aqui buscar si esta activado varias 11398
                        more_ant_ids = parameter_obj.search(cr, uid, [('key','=','more11398')],limit=1)
                        if more_ant_ids:
                            more_ant = parameter_obj.browse(cr, uid, more_ant_ids[0]).value
                        if more_ant=='Si':
                            #armo un diccionario cuenta valor
                            if not account.account_rec_id:
                                raise osv.except_osv(('Error de Configuracion !'),
                                                     ("La cuenta 124 '%s' no tiene la cuenta por cobrar configurada (11398)") % (account.code))
                            if not account.account_rec_id.id in anterior_dict:
                                anterior_dict[account.account_rec_id.id] = valor
                            else:
                                anterior_dict[account.account_rec_id.id] += valor
                        anterior += valor
                    if valor>0:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,account_id,valor,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,1,False))
                elif aux_code[0:1]=='6' and aux_code_budget[0:1]=='5':
                    #es gasto
                    post_gasto_ids = partida_obj.search(cr, uid, [('code','=',line.partida_id)])
                    if not post_gasto_ids:
                        raise osv.except_osv(('Error Configuracion !'),
                                             ("No existe la partida '%s' en el catalogo") % (line.partida_id)) 
                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',post_gasto_ids[0]),('date_start','<=',this.date),('date_end','>=',this.date)],limit=1)
                    if not item_ids:
                        raise osv.except_osv(('Error Configuracion !'),
                                             ("No existe presupuesto para la partida '%s'") % (line.partida_id)) 
                    item_descuento = item_obj.browse(cr, uid, item_ids[0])
                    itemm_anterior = itemm_obj.search(cr, uid, [('program_code','=',item_descuento.program_id.sequence),
                                                                ('commited_amount','=',line.valor),('date','=',this.date)])
                    context_unlink = {}
                    context_unlink['elimina']='Si'
                    if itemm_anterior:
                        itemm_obj.unlink(cr, uid, itemm_anterior,context_unlink)
                    aux_desc = item_descuento.budget_post_id.code + ' - ' + item_descuento.budget_post_id.name
                    itemm_id = itemm_obj.create(cr, uid, {
                        'budget_item_id':item_ids[0],
                        'budget_post_id':item_descuento.budget_post_id.id,
                        'commited_amount':line.valor,#aux_total,
                        'date':this.date,
                        'program_code':item_descuento.program_id.sequence,
                        'type_budget':'gasto',
                        'move_id':move_id,
                        'is_pronto':True,
                        'desc':aux_desc,
                    })
                    project_ids = project_obj.search(cr, uid, [('type_budget','=','ingreso')],limit=1)
                    project = project_obj.browse(cr, uid, project_ids[0])
                    certificate_id = certificate_line_obj.create(cr, uid, {
                        'project_id':project.id,
                        'task_id':project.tasks[0].id,
                        'budget_id':item_ids[0],
                        'amount_commited':0,
                        #'certificate_id':certificate_ing_ids[0],
                    })
                    certificate = certificate_line_obj.browse(cr, uid, certificate_id)
                    b_id = certificate.budget_id.id
                    p_id = certificate.budget_post.id
                    account_ids = account_obj.search(cr, uid, [('budget_id','=',post_gasto_ids[0])])
                    if not account_ids:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("No existe cuenta contable asociada a la partida '%s'")%(line.partida_id))
                    for account_id in account_ids:
                        account = account_obj.browse(cr, uid, account_id)
                        if account.account_rec_id:
                            break
                    aux_mseg_nocxp = account.code + ' - ' + account.name
                    if not account.account_rec_id:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("No existe cuenta por cobrar asociada a la cuenta '%s'")%(aux_mseg_nocxp))
                    cxp = account.account_rec_id.id
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_accrued,budget_id_cert,budget_id,budget_post) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,line.valor,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,True,certificate_id,b_id,p_id))
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,budget_id_cert,budget_id,budget_post) VALUES (%s,%s, %s, %s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,line.valor,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,True,certificate_id,b_id,p_id))
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_accrued,budget_paid,name,migrado,budget_id_cert,budget_id,budget_post) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.id,line.valor,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,False,False,name_aux,False,certificate_id,b_id,p_id))
                else:
                    if not account.budget_id:
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("La cuenta '%s' no tiene asociada partida") % (account.code))                     
                    partida = account.budget_id
                    certificate_line_ids = certificate_line_obj.search(cr, uid,[('budget_post','=',partida.id),('certificate_id','=',certificate_ids[0])],limit=1)
                    if not certificate_line_ids:
                        partida_aux = account.budget_id.code
                        code_aux = account.code
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("No se a planificado monto para la partida, no hay certificado ingreso '%s' para la cuenta '%s'") % (partida_aux,code_aux))
                    certificate = certificate_line_obj.browse(cr, uid, certificate_line_ids[0])
                    b_id = certificate.budget_id.id
                    p_id = certificate.budget_post.id
                    if valor>0:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id,valor,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,certificate_line_ids[0],b_id,p_id,False,True,1,False))
                        if line.is_emision:
                            band_emision = False
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id,valor,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,certificate_line_ids[0],b_id,p_id,False,False,1,False))
                            #cuenta de la 6
                            account_pat_ids = account_obj.search(cr, uid, [('account_rec_id','=',account.id)])
                            if account_pat_ids:
                                account_pat_id = account_pat_ids[0]
                                band_emision = True
                            else:
                                account_pat_ids = account_obj.search(cr, uid, [('budget_id','=',account.budget_id.id)])
                                if account_pat_ids:
                                    for account_pat_id in account_pat_ids:
                                        account_pat = account_obj.browse(cr, uid, account_pat_id)
                                        if account_pat.code[0:2]=='62':
                                            band_emision = True
                                            break
                                if not band_emision:
                                    #buscar patrimonial con la partida de mayor
                                    budget_post_ids = partida_obj.search(cr, uid, [('code','=',account.budget_id.code[0:6])])
                                    if budget_post_ids:
                                        account_pat_ids = account_obj.search(cr, uid, [('budget_id','in',budget_post_ids)])
                                        if account_pat_ids:
                                            for account_pat_id in account_pat_ids:
                                                account_pat = account_obj.browse(cr, uid, account_pat_id)
                                                if account_pat.code[0:2]=='62':
                                                    band_emision = True
                                                    break
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_pat_id,valor,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,certificate_line_ids[0],b_id,p_id,True,False,1,False))
                            account_pat_ids = []
                            if not band_emision:
                                raise osv.except_osv(('Error de Configuracion !'),
                                                     ("No hay cuenta de patrimonio de la cuenta por cobrar '%s'") % (account.code))
            ##anio anterior
            if anterior>0:
                more_ant = ''
                #aqui buscar si esta activado varias 11398
                more_ant_ids = parameter_obj.search(cr, uid, [('key','=','more11398')],limit=1)
                if more_ant_ids:
                    more_ant = parameter_obj.browse(cr, uid, more_ant_ids[0]).value
                if more_ant=='Si':
                    certificate_ids = certificate_line_obj.search(cr, uid, [('budget_id','=',this.partida_anterior.id)],limit=1)
                    if not certificate_ids:
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("No se a planificado monto para la partida '%s'") % (this.partida_anterior.budget_post_id.code))
                    certificate = certificate_line_obj.browse(cr, uid, certificate_ids[0])
                    b_id = certificate.budget_id.id
                    p_id = certificate.budget_post.id
                    for anterior_det in anterior_dict:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s,%s ,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,anterior_det,round(anterior_dict[anterior_det],2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Anterior',certificate_ids[0],b_id,p_id,True,True,3,False))
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s,%s ,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,anterior_det,round(anterior_dict[anterior_det],2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Anterior',certificate_ids[0],b_id,p_id,False,False,3,False))
                else:
                    certificate_ids = certificate_line_obj.search(cr, uid, [('budget_id','=',this.partida_anterior.id)],limit=1)
                    if not certificate_ids:
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("No se a planificado monto para la partida '%s'") % (this.partida_anterior.budget_post_id.code))
                    certificate = certificate_line_obj.browse(cr, uid, certificate_ids[0])
                    b_id = certificate.budget_id.id
                    p_id = certificate.budget_post.id
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s,%s ,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,this.acc_ant_id.id,round(anterior,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Anterior',certificate_ids[0],b_id,p_id,True,True,3,False))
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s,%s ,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,this.acc_ant_id.id,round(anterior,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Anterior',certificate_ids[0],b_id,p_id,False,False,3,False))
            ##anterior mejoras
            if anterior_mejora>0:
                item_mejora_antes = item_obj.search(cr, uid, [('code_aux','=','38010104'),('date_start','<=',this.date),('date_end','>=',this.date)])
                certificate_ids = certificate_line_obj.search(cr, uid, [('budget_id','=',item_mejora_antes[0])],limit=1)
                if not certificate_ids:
                    raise osv.except_osv(('Error de Configuracion !'),
                                         ("No se a planificado monto para la partida '%s'") % (this.partida_anterior.budget_post_id.code))
                certificate = certificate_line_obj.browse(cr, uid, certificate_ids[0])
                b_id = certificate.budget_id.id
                p_id = certificate.budget_post.id
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s,%s ,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,this.acc_ant_id.id,round(anterior_mejora,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Anterior',certificate_ids[0],b_id,p_id,True,True,3,False))
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s,%s ,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,this.acc_ant_id.id,round(anterior_mejora,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Anterior',certificate_ids[0],b_id,p_id,False,False,3,False))
            ####
            for dinero_line in this.formapago_ids:
                if dinero_line.account_id:
                    aux_cta_pago = dinero_line.account_id.id
                    aux_ref_pago = dinero_line.account_id.name
                else:
                    journal = dinero_line.journal_id
                    if not journal.default_debit_account_id:
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("No hay cuenta para forma de pago '%s'") % (journal.name))
                    if not journal.default_debit_account_id.id:
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("No hay cuenta para forma de pago '%s'") % (journal.name))
                    aux_cta_pago = journal.default_debit_account_id.id
                    aux_ref_pago = journal.name
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,aux_cta_pago,round(dinero_line.monto,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,aux_ref_pago,2,False))
            
        return True

    def resumen_recaudado(self, cr, uid, ids, context=None):
        import psycopg2
        line_line_obj = self.pool.get('recaudacion.line.line')
        detalle_obj = self.pool.get('recaudacion.detalle')
        parent_obj = self.pool.get('account.recaudacion')
        budget_post = self.pool.get('budget.post')
        budget_item_obj = self.pool.get('budget.item')
        parameter_obj = self.pool.get('ir.config_parameter')
        account_obj = self.pool.get('account.account')
        poa_obj = self.pool.get('budget.poa')
        cert_obj = self.pool.get('budget.certificate')
        pago_obj = self.pool.get('account.recaudacion.pago')
        antes_tercero = self.pool.get('recaudacion.tercero')
        recaudacion_line_obj = self.pool.get('recaudacion.line')
        #primero ejecuto query positivo anio actual para generar las lineas
        for this in self.browse(cr, uid, ids):
            cert_ids = cert_obj.search(cr, uid, [('ref_doc','=','Ingresos')])
            if not cert_ids:
                raise osv.except_osv('Configuracion Incompleto', 'No ha creado presupuesto de ingreso.')
            ##
            for line_anterior in this.recaudacion_ids:
                recaudacion_line_obj.unlink(cr, uid, line_anterior.id)
            id_recaudacion = this.id
            #ejecutar el sql para que traiga los datos
            usuario_ids = parameter_obj.search(cr, uid, [('key','=','usrsiim')],limit=1)
            usuario = parameter_obj.browse(cr, uid, usuario_ids[0]).value
            clave_ids = parameter_obj.search(cr, uid, [('key','=','passsiim')],limit=1)
            clave = parameter_obj.browse(cr, uid, clave_ids[0]).value
            base_ids = parameter_obj.search(cr, uid, [('key','=','basesiim')],limit=1)
            base = parameter_obj.browse(cr, uid, base_ids[0]).value
            server_ids = parameter_obj.search(cr, uid, [('key','=','serverip')],limit=1)
            server = parameter_obj.browse(cr, uid, server_ids[0]).value
            puerto=5432
            dbconn_siim = psycopg2.connect(dbname="siim", host="172.16.0.134", port=5432, user="postgres", password="planerp1977")
            cursor = dbconn_siim.cursor()
            str_date_ini = "'" + this.date + "'"
            str_date_end = "'" + this.date_end + "'"
            datas = []
            data_desc = {}
            monto_ant = monto_act = monto = 0 
            #cargar todo lo recaudado
            self.cargar_recaudado(cr, uid, ids)
            aux = '''select * from recaudacion_cuenta where "fechaCobro"=%s''' % (str_date_ini)
            cursor.execute(aux)
            for row in cursor.fetchall():
                ##buscar la partida de esa cuenta y pasarle si es emision
                aux_code1 = row[1].replace('.','')
                j = 0
                aux_code = ''
                for j in range(len(aux_code1)):
                    if aux_code1[j].isdigit():
                        aux_code+=aux_code1[j]
                if aux_code[0:7]=='2120304':
                    aux_code = '2120304'
                account_ids = account_obj.search(cr, uid, [('code','=',aux_code)])
                is_emision = False
                if account_ids:
                    account = account_obj.browse(cr, uid, account_ids[0])
                    if account.budget_id:
                        is_emision = account.budget_id.is_emision
                else:
                    raise osv.except_osv(('Error Configuracion !'),
                                         ("No existe cuenta contable '%s'") % (ustr(row[1]))) 
                aux_cta = row[1] 
                #riobamba
                if row[1].replace('.','')[0:7]=='2120304':
                    aux_cta = '2120304'
                line_id = recaudacion_line_obj.create(cr, uid, {
                    'partida_id':'0000000',
                    'account_id':aux_cta,
                    'desc':row[2],
                    'actual_value':row[3],
                    'rec_id':id_recaudacion,
                    'is_emision':is_emision,
                })
        return True

    def cargar_recaudado(self, cr, uid, ids, context=None):
        import psycopg2
        parent_obj = self.pool.get('account.recaudacion')
        recaudacion_line_obj = self.pool.get('recaudacion.line')
        line_line_obj = self.pool.get('recaudacion.line.line')
        detalle_obj = self.pool.get('recaudacion.detalle')
        parameter_obj = self.pool.get('ir.config_parameter')
        budget_obj = self.pool.get('budget.post')
        account_obj = self.pool.get('account.account')
        journal_obj = self.pool.get('account.journal')
        pago_obj = self.pool.get('account.recaudacion.pago')
        cert_obj = self.pool.get('budget.certificate')
        for this in self.browse(cr, uid, ids):
            #valida cert de ingreso
            cert_ids = cert_obj.search(cr, uid, [('ref_doc','=','Ingresos')])
            if not cert_ids:
                raise osv.except_osv('Configuracion Incompleto', 'No ha creado presupuesto de ingreso.')
            ##
            for line_anterior in this.recaudacion_ids:
                recaudacion_line_obj.unlink(cr, uid, line_anterior.id)
            for line_pago in this.formapago_ids:
                pago_obj.unlink(cr, uid, line_pago.id)
            line_line_ids = line_line_obj.search(cr, uid, [('parent_id','=',this.id)])
            line_line_obj.unlink(cr, uid, line_line_ids)
            detalle_ids = detalle_obj.search(cr, uid, [('rec_id','=',this.id)])
            detalle_obj.unlink(cr, uid, detalle_ids)
            id_recaudacion = this.id
            #ejecutar el sql para que traiga los datos
            usuario_ids = parameter_obj.search(cr, uid, [('key','=','usrsiim')],limit=1)
            usuario = parameter_obj.browse(cr, uid, usuario_ids[0]).value
            clave_ids = parameter_obj.search(cr, uid, [('key','=','passsiim')],limit=1)
            clave = parameter_obj.browse(cr, uid, clave_ids[0]).value
            base_ids = parameter_obj.search(cr, uid, [('key','=','basesiim')],limit=1)
            base = parameter_obj.browse(cr, uid, base_ids[0]).value
            server_ids = parameter_obj.search(cr, uid, [('key','=','serverip')],limit=1)
            server = parameter_obj.browse(cr, uid, server_ids[0]).value
            puerto=5432
            dbconn_siim = psycopg2.connect(dbname="siim", host="172.16.0.134", port=5432, user="postgres", password="planerp1977")
            cursor = dbconn_siim.cursor()
            str_date_ini = "'" + this.date + "'"
            str_date_end = "'" + this.date_end + "'"
            datas = []
            data_desc = {}
            monto_ant = monto_act = monto = 0 
            #cargar todo lo recaudado
            aux = '''select * from recaudacion_linea where "fechaCobro"=%s''' % (str_date_ini)
            cursor.execute(aux)
            for row in cursor.fetchall():
                aux_acc = ustr(row[7])
                if len(aux_acc)>2:
                    account_id = aux_acc 
                else:
                    if float(row[5])>0:
                        aux_pp = ustr(row[6])
                        partida_aux_1 = aux_pp.replace(".",'')
                        partida_aux = partida_aux_1#[0:6]
                        partida_ids = budget_obj.search(cr, uid, [('code','=',partida_aux)])
                        if partida_ids:
                            account_ids = account_obj.search(cr, uid, [('budget_id','=',partida_ids[0])],limit=1)
                            if account_ids:
                                account = account_obj.browse(cr, uid, account_ids[0])
                                account_id = account.code
                            else:
                                account_id = ustr(row[6])
                        else:
                            #aumentado mario
                            account_id=aux_acc
                            #account_id = ustr(row[6])
                    #aumentado mario
                    else:
                         account_id=aux_acc
                part = ustr(row[6])
                if account_id == '2120112':
                    part = '00.00.00'
#                import pdb
#                pdb.set_trace()
                if float(row[5])>0:
                    detalle_obj.create(cr, uid, {
                        'name':ustr(row[1]),
                        'anio':ustr(row[2]),
                        'date_emi':str(row[3]),
                        'date':this.date,
                        'monto':row[5],
                        'partida_id':part,
                        'account_id':account_id,
                        'rec_id':id_recaudacion,
                        'modulo':ustr(row[10]),
                        'modulo_id': row[11],
                    })
                else:
                    detalle_obj.create(cr, uid, {
                        'name':ustr(row[1]),
                        'anio':ustr(row[2]),
                        'date_emi':str(row[3]),
                        'date':this.date,
                        'monto':row[5],
                        'partida_id':part,
                        'account_id':account_id, # antes comentado
                        'rec_id':id_recaudacion,
                        'modulo':ustr(row[10]),
                        'modulo_id': row[11],                        
                    }) 
            aux = "Recaudacion - " + str(this.date)
            self.write(cr, uid, ids, {
                    'name':aux,
                    })
            aux= '''select aux."formaPago",sum(aux."Total Recaudado") "Total Recaudado" from (select dp.id,(SELECT rfp.descripcion from recaudacion_forma_pago rfp where rfp.id = dp."formaPago") as "formaPago",ROUND((SUM(fd.cantidad*fd."valorUnitario") * (dp.valor/rr."totalPagar"))::NUMERIC, 2) "Total Recaudado"  from detalle_pago dp, registro_recaudacion rr, registro_recaudacion_factura rrf, factura f, factura_detalle fd, rubro r where f.pagado=1 and f.estado in(1,2) and f.id=fd.id_factura and fd.estado=1 and dp.id_registro_recaudacion=rr.id and rr.id=rrf.id_registro_recaudacion and rrf.id_factura=fd.id_factura and fd.id_rubro=r.id and dp.estado=1 and rrf.estado=1 and dp."fechaCreacion"  between %s and %s and ROUND(dp.valor::NUMERIC, 2)>=0.01 and ROUND(rr."totalPagar"::NUMERIC, 2)>=0.01 group by dp.id, dp."formaPago", dp.valor, rr."totalPagar" union (select -1 "formaPago", 'Contado' as "formaPago",sum(fd."valorUnitario"*fd.cantidad) "Total Recaudado" from factura f, factura_detalle fd, rubro r  where f."fechaCobro" between %s and %s and fd.id_rubro=r.id and fd.id_factura=f.id and f.id_modulo=38 and f.estado=1 and pagado=1 )) aux group by aux."formaPago"''' % (str_date_ini,str_date_ini,str_date_ini,str_date_ini)
            cursor.execute(aux)
            for row in cursor.fetchall():
                if row[0]=='Contado':
                    journal_ids = journal_obj.search(cr, uid, [('name','=','EFECTIVO')],limit=1)
                    journal_id = journal_ids[0]
                elif row[0]=='Cheque':
                    journal_ids = journal_obj.search(cr, uid, [('name','=','CHEQUE')],limit=1)
                    journal_id = journal_ids[0]
                elif row[0]=='Tarjeta Credito':
                    journal_ids = journal_obj.search(cr, uid, [('name','=','TARJETA CREDITO')],limit=1)
                    journal_id = journal_ids[0]
                elif row[0]=='Nota Credito':
                    journal_ids = journal_obj.search(cr, uid, [('name','=','NOTA DE CREDITO')],limit=1)
                    journal_id = journal_ids[0]
                elif row[0] in ('SPI - Transferencia','SPI Transferencia'):
                    journal_ids = journal_obj.search(cr, uid, [('name','=','SPI')],limit=1)
                    journal_id = journal_ids[0]
                else:
                    journal_ids = journal_obj.search(cr, uid, [('name','=','SPI')],limit=1)
                    journal_id = journal_ids[0]
                if not journal_ids:
                    raise osv.except_osv(('Error Configuracion !'),
                                         ("No existe diario para la forma de pago '%s'") % (ustr(row[0]))) 
                line_pago_id = pago_obj.create(cr, uid, {
                    'rec_id':this.id,
                    'journal_id':journal_id,
                    'monto':row[1],
                })
            cursor.close()
            dbconn_siim.close
        return True

accountRecaudacionCuenta()
