
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

class recLine(osv.Model):
    _inherit = 'recaudacion.line'
    _order = "account_id asc"
recLine()

##########################

class budgetPostExt(osv.Model):
    _inherit = 'budget.post'
    _columns = dict(
        solo_actual = fields.boolean('Solo Actual',help='Si marca este campo el sistema no considera anio anterior en la contabilizacion'),
    )
budgetPostExt()

class recaudacionDetalleExt(osv.Model):
    _inherit = 'recaudacion.detalle'

    def _calc_partida(self, cr, uid, ids, fields, arg, context=None):
        result = {}
        partida_obj = self.pool.get('budget.post')
        for obj in self.browse(cr, uid, ids, context=context):
            code_aux = obj.partida_id
            code_dos = code_aux.replace('.','')
#            partida_aux_ids = partida_obj.search(cr, uid, [('code','=', code_dos[0:6])])
            partida_aux_ids = partida_obj.search(cr, uid, [('code','=', code_dos)])
            if partida_aux_ids:
                result[obj.id] = partida_aux_ids[0]
            else:
                if len(code_dos) > 6:
                    sql_update = "UPDATE recaudacion_detalle set partida_id='00.00.00' where id=%s"%(obj.id)
                    cr.execute(sql_update)
                    partida_aux_ids = partida_obj.search(cr, uid, [('code','=', '000000')])
                    if partida_aux_ids:
                        result[obj.id] = partida_aux_ids[0]
                else:
                    #si es de las por pagar no al raise
                    if obj.account_id.replace('.','')[0:3]=='212':
                        sql_update = "UPDATE recaudacion_detalle set partida_id='00.00.00' where id=%s"%(obj.id)
                        cr.execute(sql_update)
                        partida_aux_ids = partida_obj.search(cr, uid, [('code','=', '000000')])
                        if partida_aux_ids:
                            result[obj.id] = partida_aux_ids[0]
                    else:
                        raise osv.except_osv(('Error Configuracion !'),
                                             ("No existe la partida '%s'") % (ustr(code_aux))) 
                    
        return result

    _columns = dict(
        partida_id2 = fields.function(_calc_partida, type='many2one', relation="budget.post", store=True),
    )


recaudacionDetalleExt()



class accountRecaudacionExt(osv.Model):
    _inherit = 'account.recaudacion'

    _columns = dict(
        otros_id = fields.one2many('otros.recaudacion','otro_id','Otros Por pagar/cobrar'),
    )

    def contabilizar_recaudado(self, cr, uid, ids, context=None):
        '''SE VERIFICA LA PARTIDA PRESUPUESTARIA SI ES VENTA(TRUE) TIENE EL DOBLE MOVIMIENTO DE CUENTAS
        CASO CONTRARIO SOLO LA CTA POR COBRAR POR QUE ES EMISIONES Y SI ES ANIO ANTERIOR VA EL MOVIMIENTO CON ANIOS ANTERIORES
        '''
        item_obj = self.pool.get('budget.item')
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
        for this in self.browse(cr, uid, ids):
            aux_narration = "ASIENTO CONTABLE DE RECAUDACION MUNICIPAL: " + this.name
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
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
            j = k = l = 0
            aux_anterior = 0
            restadas = []
            aux_anterior_mejora = 0
            aux_suma_mejora = 0
            for line in this.recaudacion_ids:
                aux_sin_partida = 0
                #verificar si es del mismo dia la emision pasa con todo el movimiento else solo contra la cta por cobrar
                #si es del mismo dia
                rubro_name = line.desc
                partida_p = line.partida_id
                #por el momento quitar el punto
                partida_aux1 = partida_p.replace(".",'')
                mm = ''
                if int(partida_aux1[0:2])>0 and partida_aux1[0:3]!='212':
                    if partida_aux1=='13049901':
                        aux_anterior_mejora += line.anterior_value
                    #primero los que tienen afectacion a partidas
                    partida_aux = partida_aux1
                    partida_ids = partida_obj.search(cr, uid, [('code','=',partida_aux)],limit=1)
                    if partida_ids:
                        partida = partida_obj.browse(cr, uid, partida_ids[0])
                        #modificado para que tome la patromonial
                        account_ids = account_obj.search(cr, uid, [('budget_id','=',partida_ids[0])])
                        if not account_ids:
                            #busco con la mayor a 6
                            account_ids = account_obj.search(cr, uid, [('budget_id','=',partida_aux[0:6])])
                            if not account_ids:
                                raise osv.except_osv(('Error de Configuracion !'),
                                                     ("No se a configurado cuenta contable para la partida '%s'") % (partida_aux))
                        if len(account_ids)>1:
                            for acc_id in account_ids:
                                account = account_obj.browse(cr, uid, acc_id)
                                if account.account_rec_id:
                                    continue
                            if not account:
                                raise osv.except_osv(('Error de Configuracion !'),
                                                     ("No se a configurado cuenta contable por pagar para la partida '%s'") % (partida_aux))
                        else:
                            #si la cta de line es la account_ids toma la cxp de la cta patrimonial, else toma la cta de la linea
                            account = account_obj.browse(cr, uid, account_ids[0])
                        if (line.account_id == account.code) and account.account_rec_id:
                            cxp = account.account_rec_id.id
                        elif not line.account_id:
                            cxp = account.account_rec_id.id
                        else:
                            cxp = account.account_rec_id.id
                        if account.account_rec_id.anterior_id:
                            cxp_id_anterior = account.account_rec_id.anterior_id.id
                        else:
                            cxp_id_anterior = cxp
                        certificate_line_ids = certificate_line_obj.search(cr, uid, 
                                                                           [('budget_post','=',partida.id),('certificate_id','=',certificate_ids[0])],limit=1)
                        if not certificate_line_ids:
                            raise osv.except_osv(('Error de Configuracion !'),
                                                 ("No se a planificado monto para la partida, no hay certificado ingreso '%s'") % (partida_aux))
                        if certificate_line_ids:
                            certificate = certificate_line_obj.browse(cr, uid, certificate_line_ids[0])
                            b_id = certificate.budget_id.id
                            p_id = certificate.budget_post.id
                    else:
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("No hay partida para '%s'") % (partida_aux))
                        #account_ids = account_obj.search(cr, uid, [('code','=',line.account_id)],limit=1)
#                    account = account_obj.browse(cr, uid, account_ids[0])
#                    cxp = account.account_rec_id.id
                    #tomar en cuenta los descuentos para quitar al valor
                    #busco con la misma partida y si es menos le resto
                    venta_valor = 0
                    if partida.venta: #preguntar si es venta haga esto con el total, aqui se devenga y paga el mismo valor
                        venta_valor = line.dia_value + line.actual_value #+ line.anterior_value
                        aux_anterior += line.anterior_value
                        if not account.account_rec_id:
                            raise osv.except_osv(('Error de Configuracion !'),
                                                 ("No existe cuenta por cobrar asociada a la cuenta '%s'") % (account.code)) 
                        cxp = account.account_rec_id.id
                        #linea  entrada cta patrimonial 621, preguntar si hace devengado tambien
                        devenga_ids = parameter_obj.search(cr, uid, [('key','=','devenga')],limit=1)
                        if devenga_ids:
                            devenga = parameter_obj.browse(cr, uid, devenga_ids[0]).value
                        if devenga_ids:
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.id,round(venta_valor,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,certificate_line_ids[0],b_id,p_id,True,False,1,False))
                            #entrada cxc debe
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,round(venta_valor,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,certificate_line_ids[0],b_id,p_id,False,False,1,False))
                        #linea  entrada cxc haber
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,round(venta_valor,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,certificate_line_ids[0],b_id,p_id,False,True,1,False))
                    else: #no es venta solo contra la cxc
                        #aqui debe ir la cxp pero basado en la partida
                        rec_line.write(cr, uid,line.id,{'is_anterior':True})
                        aux_anterior += line.anterior_value
                        if not cxp:
                            cxp = account.id
                        aux_noVenta = 0 
                        aux_noVenta = line.dia_value + line.actual_value
                        if aux_noVenta>0:
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_paid,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,round(aux_noVenta,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,certificate_line_ids[0],b_id,p_id,True,3,False))
                    #saco valor de mejora a sumar

                    if line.partida_id=='38010101002':
                        aux_suma_mejora += line.actual_value 
                    #aqui colocar la 124 de esa cuenta al haber si es mejora de partida 38010101002 no hacer 124 y esto va a mejora Actual 1131321
                    if cxp_id_anterior and line.anterior_value>0:
                        if line.partida_id!='38010101002':
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_paid,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp_id_anterior,round(line.anterior_value,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,certificate_line_ids[0],b_id,p_id,False,3,False))
                    else:
                        if line.anterior_value>0:
                            account_aux = '12498010013021'
                            account_ids = account_obj.search(cr, uid, [('code','=',account_aux)],limit=1)
                            cr.execute('''
                            INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_paid,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_ids[0],round(line.anterior_value,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,certificate_line_ids[0],b_id,p_id,False,3,False))
            for line_tercero in this.tercero_ids:
                code_aux3 = line_tercero.name.replace('.','')
                account_ids = account_obj.search(cr, uid, [('code','=',code_aux3)])
                if not account_ids:
                    raise osv.except_osv(('Error de Configuracion !'),
                                         ("No hay cuenta contable de fondo ajeno '%s'") % (line_tercero.name))
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,account_ids[0],line_tercero.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,3,False))
            #lineas de la recaudacion
            for dinero_line in this.formapago_ids:
                journal = dinero_line.journal_id
                if not journal.default_debit_account_id.id:
                      raise osv.except_osv(('Error de Configuracion !'),
                                           ("No hay cuenta para forma de pago '%s'") % (journal.name))
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,seq,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)''',(move_id,journal.default_debit_account_id.id,round(dinero_line.monto,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,journal.name,2,False))
            #asiento simultaneo cartera vencida partidas 38
            ##mejoras AA
            if aux_anterior_mejora>0:
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
                move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s,%s ,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,this.acc_ant_id.id,round(aux_anterior_mejora,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Anterior',certificate_ids[0],b_id,p_id,True,True,3,False))
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s,%s ,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,this.acc_ant_id.id,round(aux_anterior_mejora,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Anterior',certificate_ids[0],b_id,p_id,False,False,3,False))
            ##demas rubros AA
            aux_anterior = aux_anterior - aux_anterior_mejora
            certificate_ids = certificate_line_obj.search(cr, uid, [('budget_id','=',this.partida_anterior.id)],limit=1)
            if not certificate_ids:
                raise osv.except_osv(('Error de Configuracion !'),
                                     ("No se a planificado monto para la partida '%s'") % (this.partida_anterior.budget_post_id.code))
            certificate = certificate_line_obj.browse(cr, uid, certificate_ids[0])
            b_id = certificate.budget_id.id
            p_id = certificate.budget_post.id
            cr.execute('''
            INSERT INTO account_move_line (
            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s,%s ,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,this.acc_ant_id.id,round(aux_anterior,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Anterior',certificate_ids[0],b_id,p_id,True,True,3,False))
            cr.execute('''
            INSERT INTO account_move_line (
            move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_id,budget_post,budget_accrued,budget_paid,seq,migrado) VALUES (%s,%s,%s ,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,this.acc_ant_id.id,round(aux_anterior,2),move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,'Anterior',certificate_ids[0],b_id,p_id,False,False,3,False))
        #sumar el valor de mejora actual: pasar de 38 a 1131321
        account_ids = account_obj.search(cr, uid, [('code','=','1131321')],limit=1)
        move_line_ids = move_line_obj.search(cr, uid, [('account_id','=',account_ids[0]),('move_id','=',move_id)])
        if move_line_ids:
            move_line = move_line_obj.browse(cr, uid, move_line_ids[0])
            antes_value = move_line.credit
            new_value = antes_value + aux_suma_mejora
            move_line_obj.write(cr, uid, move_line_ids[0],{
                'credit':new_value,
            })
        self.write(cr, uid, ids, {
            'move_id':move_id,
                })
        parent_obj.exportRecaudoAnterior(cr, uid, ids)
        return True

    def resumen_recaudado(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('recaudacion.line')
        line_line_obj = self.pool.get('recaudacion.line.line')
        detalle_obj = self.pool.get('recaudacion.detalle')
        parent_obj = self.pool.get('account.recaudacion')
        budget_post = self.pool.get('budget.post')
        budget_item_obj = self.pool.get('budget.item')
        account_obj = self.pool.get('account.account')
        poa_obj = self.pool.get('budget.poa')
        antes_tercero = self.pool.get('recaudacion.tercero')
        #primero ejecuto query positivo anio actual para generar las lineas
        for this in self.browse(cr, uid, ids):
            #antes tercero
            antes3_ids = antes_tercero.search(cr, uid, [('rec_id','=',this.id)])
            if antes3_ids:
                antes_tercero.unlink(cr, uid, antes3_ids)
            ##
            ant_ids = line_obj.search(cr, uid, [('rec_id','=',this.id)])
            if ant_ids:
                line_obj.unlink(cr, uid, ant_ids)
            poa_ids = poa_obj.search(cr, uid, [('date_start','<=',this.date),('date_end','>=',this.date)])
            if not poa_ids:
                raise osv.except_osv('Configuracion Incompleto', 'No hay POA definido para la fecha de recaudacion.')
            #RIOBAMBA
#            sql_positivo = """
#            select substring(partida_id,0,9) as partida_id,budget_post.name,account_id,anio,modulo,modulo_id,partida_id2,sum(monto) as total
#            from recaudacion_detalle,budget_post 
#            where budget_post.id=recaudacion_detalle.partida_id2
#            and date='%s' and monto>0 and anio>='%s' group by partida_id,partida_id2,budget_post.name,account_id,modulo,modulo_id,anio order by modulo, total desc
#            """ %(this.date,'2015')
            #sacar el anio actual
            anio_actual = this.date[0:4]
            sql_positivo = """
            select partida_id,budget_post.name,account_id,anio,modulo,modulo_id,partida_id2,sum(monto) as total
            from recaudacion_detalle,budget_post 
            where budget_post.id=recaudacion_detalle.partida_id2
            and date='%s' and monto>0 and anio>='%s' group by partida_id,partida_id2,budget_post.name,account_id,modulo,modulo_id,anio order by modulo, total desc
            """ %(this.date,anio_actual)
            cr.execute(sql_positivo)
            data = cr.fetchall()
            terceros = {}
            for line_new in data:
                #busco linea con partida_id, cuenta_id
                #logica de terceros
                if int(line_new[0].replace('.',''))==0:
                    if not terceros.has_key(line_new[2]):
                        terceros[line_new[2]] = line_new[7]
                    else:
                        terceros[line_new[2]] += line_new[7]
                ####################
                aux_rec = budget_post.read(cr, uid, line_new[6],['aux_recaudacion'])
                if aux_rec['aux_recaudacion'] == True:
                    #busco por partida y cuenta
                    line_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('account_id','=',line_new[2]),('partida_id','=',line_new[0])])
                    account_id_aux = line_new[2]
                else:
                    line_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('partida_id','=',line_new[0])])
                    account_id_aux = line_new[2]
                if line_ids:
                    #suma a la linea y agrega el modulo
                    line_data = line_obj.read(cr, uid, line_ids[0], ['modulo','actual_value'])
                    if line_new[4] not in line_data['modulo']:
                        new_module_string = line_data['modulo'] + ' -- '+ line_new[4]
                    else:
                        new_module_string = line_data['modulo']
                    new_actual_value = line_data['actual_value'] + line_new[7]
                    line_obj.write(cr, uid, line_ids[0], {'actual_value': new_actual_value, 'modulo': new_module_string})
                else:
                    #busco budget_item
                    budget_item_ids = budget_item_obj.search(cr, uid, [('poa_id','=',poa_ids[0]),('budget_post_id.code','=',line_new[0])])
                    if budget_item_ids:
                        desc_aux = line_new[1] 
                    else:
                        desc_aux = line_new[1]
                    line_obj.create(cr, uid, {
                        'rec_id': this.id,
                        'partida_id': line_new[0],
                        #FIX, ver de donde sacar el account_id
                        'account_id': account_id_aux,
                        'desc': desc_aux + ' - ' + line_new[0] + ' - ' + line_new[2],
                        'actual_value': line_new[7],
                        'modulo': line_new[4],
                        'modulo_id': line_new[5],
                        
                    })
            #segundo ejecuto query positivo anio anteriores para generar detalle de lineas
            sql_positivo2 = """
            select partida_id,budget_post.name,account_id,anio,modulo,partida_id2,sum(monto) as total
            from recaudacion_detalle,budget_post 
            where budget_post.id=recaudacion_detalle.partida_id2
            and date='%s' and monto>0 and anio<'%s' group by partida_id,partida_id2,budget_post.name,account_id,modulo,anio order by modulo, total desc
            """ %(this.date,anio_actual)
            cr.execute(sql_positivo2)
            data = cr.fetchall()
            for line_line in data:
                #busco line_line con misma partida, creo detalle con anio
#                post_ids = budget_post.search(cr, uid, [('code','=',line_line[0].replace('.',''))])
                if int(line_line[0].replace('.',''))==0:
                    if not terceros.has_key(line_line[2]):
                        terceros[line_line[2]] = line_line[6]
                    else:
                        terceros[line_line[2]] += line_line[6]
                aux_rec = budget_post.read(cr, uid, line_line[5],['aux_recaudacion'])
                if aux_rec['aux_recaudacion'] == True:
                    #busco por partida y cuenta
                    line_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('is_venta','=',False),('modulo','like',line_line[4])])
                    account_id_aux = line_line[2]
                else:
                    line_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('is_venta','=',False),('partida_id','=',line_line[0])])
                    account_id_aux = line_line[2]
                post = budget_post.browse(cr, uid, line_line[5])
                if not line_ids:
                #crea line_line
                    #busco budget_item
                    budget_item_ids = budget_item_obj.search(cr, uid, [('poa_id','=',poa_ids[0]),('budget_post_id.code','=',line_line[0].replace('.',''))])
                    #preguntar si no esto un raise
                    if not budget_item_ids:
                        raise osv.except_osv('Configuracion Incompleto', 'No esta planificada la partida %s.'%(line_line[0]))
                    budget_aux = budget_item_obj.browse(cr, uid, budget_item_ids[0])
                    if budget_item_ids:
                        desc_aux = line_line[1] 
                    else:
                        desc_aux = line_line[4]
                    line_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('partida_id','=',line_line[0])])
                    if line_ids:
            #            line_id = line_ids[0]  #mc
                        #sumo en la linea actual
                        line_data = line_obj.read(cr, uid, line_ids[0], ['id','actual_value'])
                        if post.solo_actual:
                            line_obj.write(cr, uid, [line_ids[0]],{'actual_value': line_data['actual_value']+line_line[6],'anterior_value':0})###
                        line_id = line_ids[0]
                    else:
                        #no existe una linea con esa partida, entonces creo una linea con esa partida
                #        line_obj.create(cr, uid, {
                        #aqui preguntar si no hace anterior ponga a actual_value line_new[0] id partida
                        if post.solo_actual:
                            line_id = line_obj.create(cr, uid, {  #mc
                                'rec_id': this.id,
                                'partida_id': line_line[0],
                                #FIX, ver de donde sacar el account_id
                                'account_id': line_line[2],
                                'desc': line_line[0] + ' - ' + line_line[1],
                                'actual_value': line_line[6],
                                #'anterior_value': line_line[6],
                                'modulo': line_line[4],
                                'modulo_id': line_line[5],
                            })
                        else:
                            line_id = line_obj.create(cr, uid, {  #mc
                                'rec_id': this.id,
                                'partida_id': line_line[0],
                                #FIX, ver de donde sacar el account_id
                                'account_id': line_line[2],
                                'desc': line_line[0] + ' - ' + line_line[1],
                                #'actual_value': line_line[6],
                                'anterior_value': line_line[6],
                                'modulo': line_line[4],
                                'modulo_id': line_line[5],
                            })
                        #line_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('is_venta','=',False)])
#                        continue
                else:
                    line_id = line_ids[0]
                #busco linea hija por anio                
                line_line_ids = line_line_obj.search(cr, uid, [('line_id','=',line_id),('anio','=',line_line[3])])
                if line_line_ids:
                    line_line_data = line_line_obj.read(cr, uid, line_line_ids[0], ['valor'])
                    new_line_line_valor = line_line_data['valor'] + line_line[6]
                    line_line_obj.write(cr, uid, line_line_ids[0],{'valor': new_line_line_valor})
                else:
                #crea la linea hija
                    if not post.solo_actual:
                        line_line_obj.create(cr, uid, {
                            'line_id': line_id,
                            'anio': line_line[3],
                            'valor': line_line[6],
                        })
            #luego ejecuto query negativo para restar de las lineas con monto mayor con el mismo modulo
            
            sql_negativo = """
            select substring(partida_id,0,9) as partida_id,partida_id2,anio,modulo,modulo_id,monto,account_id
                from recaudacion_detalle
                where date='%s' and monto<0 order by monto
            """ %(this.date)
            cr.execute(sql_negativo)
            data = cr.fetchall()
            for line_negative in data:
                #terceros
                if int(line_negative[0].replace('.',''))==0:
                    if not terceros.has_key(line_negative[6]):
                        terceros[line_negative[6]] = line_negative[5]
                    else:
                        terceros[line_negative[6]] += line_negative[5]
                #############
                aux_rec = budget_post.read(cr, uid, line_negative[1],['aux_recaudacion'])
                if aux_rec['aux_recaudacion'] == True:
                    if line_negative[2]>=anio_actual:
                        #busco linea de recaudacion con mismo modulo y valor mayor al monto
                        data2_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('actual_value','>=',line_negative[5]*-1)], order='actual_value desc', limit=1)
                        actual_value = line_obj.read(cr, uid, data2_ids[0], ['actual_value'])
                        line_id = data2_ids[0]
                        #resto en el actual value del recaudacion_line
                        line_obj.write(cr, uid, [line_id],{'actual_value':actual_value['actual_value']+line_negative[5]})
                    else:
                        
                        #busco linea de recaudacion con mismo modulo y anio y valor mayor al monto
                        line_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('modulo','like',line_negative[3]),('is_venta','=',False)])
                        line_line_ids = line_line_obj.search(cr, uid, [('line_id','in', line_ids),('anio','=',line_negative[2]),('valor','>=',line_negative[5]*-1)])
                        if line_line_ids:
                            line_line_read = line_line_obj.read(cr, uid, line_line_ids[0],['valor'])
                            line_line_obj.write(cr, uid, [line_line_ids[0]],{'valor': line_line_read['valor']+line_negative[5]})
                        else:
                            data2_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('actual_value','>=',line_negative[5]*-1)], order='actual_value desc', limit=1)
                            actual_value = line_obj.read(cr, uid, data2_ids[0], ['actual_value'])
                            line_id = data2_ids[0]
                            #resto en el actual value del recaudacion_line
                            line_obj.write(cr, uid, [line_id],{'actual_value':actual_value['actual_value']+line_negative[5]})
                else:
                    #busco linea de recaudacion con misma partida e igual anio
                    if line_negative[2]>=anio_actual:
                        #busco linea de recaudacion con misma partida y resto del valor actual
                        data2_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('partida_id','=',line_negative[0])], order='actual_value desc', limit=1)
                        actual_value = line_obj.read(cr, uid, data2_ids[0], ['actual_value'])
                        line_id = data2_ids[0]
                        #resto en el actual value del recaudacion_line
                        line_obj.write(cr, uid, [line_id],{'actual_value':actual_value['actual_value']+line_negative[5]})
                    else:
                        #busco linea de recaudacion con mismo modulo y anio y valor mayor al monto
                        line_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('is_venta','=',False),('modulo','like',line_negative[3])])
                        line_line_ids = line_line_obj.search(cr, uid, [('line_id','in', line_ids),('valor','>=',line_negative[5]*-1),('anio','=',line_negative[2])])
                        if line_line_ids:
                            line_line_read = line_line_obj.read(cr, uid, line_line_ids[0],['valor'])
                            line_line_obj.write(cr, uid, [line_line_ids[0]],{'valor': line_line_read['valor']+line_negative[5]})
                        else:
                            data2_ids = line_obj.search(cr, uid, [('rec_id','=',this.id),('actual_value','>=',line_negative[5]*-1)], order='actual_value desc', limit=1)
                            actual_value = line_obj.read(cr, uid, data2_ids[0], ['actual_value'])
                            line_id = data2_ids[0]
                            #resto en el actual value del recaudacion_line
                            line_obj.write(cr, uid, [line_id],{'actual_value':actual_value['actual_value']+line_negative[5]})
            tercero_obj = self.pool.get('recaudacion.tercero')
            for tercero_line in terceros:
                tercero_id = tercero_obj.create(cr, uid, {
                    'name':tercero_line,
                    'monto':terceros[tercero_line],
                    'rec_id':this.id,
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
            dbconn_siim = psycopg2.connect(dbname=base, host=server, port=5432, user=usuario, password=clave)
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
            aux = '''select aux."formaPago",sum(aux."Total Recaudado") "Total Recaudado" from (select case dp."formaPago" when 1 then 'Contado' when 2 then 'Cheque' when 3 then 'Nota Credito' when 4 then 'SPI - Transferencia' when 5 then 'Tarjeta Credito' else 'Otros' end as "formaPago", SUM(dp.valor) "Total Recaudado" from detalle_pago dp where dp.estado=1 and dp."fechaCreacion"  between %s and %s group by "formaPago" union (select 'Contado' as "formaPago",sum(fd."valorUnitario"*fd.cantidad) "Total Recaudado" from factura f, factura_detalle fd where f."fechaCobro" between %s and %s and  fd.id_factura=f.id and id_modulo=38 and f.estado=1 and pagado=1)) aux group by aux."formaPago"''' % (str_date_ini,str_date_ini,str_date_ini,str_date_ini)
            cursor.execute(aux)
            for row in cursor.fetchall():
                if row[0]=='Contado':
                    journal_ids = journal_obj.search(cr, uid, [('name','=','EFECTIVO')],limit=1)
                elif row[0]=='Cheque':
                    journal_ids = journal_obj.search(cr, uid, [('name','=','CHEQUE')],limit=1)
                elif row[0]=='Tarjeta Credito':
                    journal_ids = journal_obj.search(cr, uid, [('name','=','TARJETA CREDITO')],limit=1)
                elif row[0]=='Nota Credito':
                    journal_ids = journal_obj.search(cr, uid, [('name','=','NOTA DE CREDITO')],limit=1)
                elif row[0] in ('SPI - Transferencia','SPI Transferencia'):
                    journal_ids = journal_obj.search(cr, uid, [('name','=','SPI')],limit=1)   
                if not journal_ids:
                    raise osv.except_osv(('Error Configuracion !'),
                                         ("No existe diario para la forma de pago '%s'") % (ustr(row[0]))) 
                line_pago_id = pago_obj.create(cr, uid, {
                    'rec_id':this.id,
                    'journal_id':journal_ids[0],
                    'monto':row[1],
                })
            cursor.close()
            dbconn_siim.close
        return True

accountRecaudacionExt()
