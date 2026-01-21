# -*- coding: utf-8 -*-
##############################################################################

# Mario Chogllo
# mariofchogllo@gmail.com
##############################################################################
import base64
from osv import fields, osv
import time
from tools import ustr
from gt_tool import XLSWriter
import xlrd

class hr_inherit_payslip_account(osv.osv):
    _inherit = 'hr.payslip.run'

    def contabilizar_payslip_run(self, cr, uid, ids, context=None):
        '''EN ESTE METODO SERIA MAS OPIMO USAR SQL DIRECTO PARA OPTIMIZAR EL TIEMPO'''
        move_obj = self.pool.get('account.move')
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        partner_obj = self.pool.get('res.partner')
        journal_obj = self.pool.get('account.journal')
        config_obj = self.pool.get('hr.account.configuration')
        period_obj = self.pool.get('account.period')
        pay_line = self.pool.get('hr.payslip.line')
        slip_obj = self.pool.get('hr.payslip')
        certificate_obj = self.pool.get('budget.certificate')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        project_obj = self.pool.get('project.project')
        user_obj = self.pool.get('res.users')
        total_aux = deduction_aux = basic_aux = s_o_ing = 0
        state_aux = 'draft'
        company_aux = 1
        currency_aux = 2
        band = False
        anticipo_aux = []
        quincena_aux = []
        for this in self.browse(cr, uid, ids):
            #certificacion presupuestaria
            aux_name = 'ASIENTO - ' + ustr(this.name) + ' DEL:  ' + ustr(this.period_id.name)
            usuario = user_obj.browse(cr, uid, uid)
            project_ids = project_obj.search(cr, uid, [])
            notes_aux = 'CERTIFICACION PRESUPUESTARIA DE NOMINA: ' + ustr(this.name) + ' DEL:  ' + ustr(this.period_id.name)
            if this.certificate_id:
                if this.certificate_id.name=='/':
                    cr.execute("delete from budget_certificate_line where certificate_id=%s"%(this.certificate_id.id))
                    certificate_obj.unlink(cr, uid, [this.certificate_id.id],context)
                    cp_id = certificate_obj.create(cr, uid, {
                        'department_id':usuario.context_department_id.id,
                        'solicitant_id':usuario.employee_id.id,
                        'project_id':project_ids[0],
                        'partner_id':1,
                        'notes':notes_aux,
                        'date':this.date_end,
                        'date_confirmed':this.date_end,
                        'date_commited':this.date_end,
                    })
                else:
                    cr.execute("delete from budget_certificate_line where certificate_id=%s"%(this.certificate_id.id))
                    cp_id = this.certificate_id.id
            else:
                cp_id = certificate_obj.create(cr, uid, {
                    'department_id':usuario.context_department_id.id,
                    'solicitant_id':usuario.employee_id.id,
                    'project_id':project_ids[0],
                    'partner_id':1,
                    'notes':notes_aux,
                    'date':this.date_end,
                    'date_confirmed':this.date_end,
                    'date_commited':this.date_end,
                })
            journal_ids = journal_obj.search(cr, uid, [('name','=','ROLES')],limit=1)
            if not journal_ids:
                raise osv.except_osv(('Error de Configuracion !'),
                                     ("No existe diario de ROLES, cree uno por favor"))
            period_ids = period_obj.search(cr, uid, [('date_start','<=',this.date_end),('date_stop','>=',this.date_end)])
            if not period_ids:
                raise osv.except_osv(('Error de Configuracion !'),
                                     ("No existe periodo contable para la fecha de rol"))
            if this.move_id:
                if this.move_id.state=='draft' and this.move_id.name=='/':
                    cr.execute("delete from account_move_line where move_id=%s"%(this.move_id.id))
                    move_obj.unlink(cr, uid, [this.move_id.id],aux=1)
                    move_id = move_obj.create(cr, uid, {
                        'ref': aux_name,
                        'narration':aux_name,
                        'journal_id': journal_ids[0],
                        'date': this.date_end,
                        'state':'draft',
                        'period_id':period_ids[0],
                        'afectacion':True,
                        'partner_id':1,
                        'certificate_id':cp_id,
                        'type':'Nomina',
                        'validar_cp':True,
                    })
                else:
                    cr.execute("delete from account_move_line where move_id=%s"%(this.move_id.id))
                    move_id = this.move_id.id
            else:
                move_id = move_obj.create(cr, uid, {
                    'ref': aux_name,
                    'narration':aux_name,
                    'journal_id': journal_ids[0],
                    'date': this.date_end,
                    'state':'draft',
                    'afectacion':True,
                    'period_id':period_ids[0],
                    'partner_id':1,
                    'certificate_id':cp_id,
                    'type':'Nomina',
                    'validar_cp':True,
                })

            for rol in this.slip_ids:
                deduction_aux += rol.deduction
                basic_aux += rol.basic
            total_aux = basic_aux - deduction_aux
            #asiento
            move = move_obj.browse(cr, uid, move_id)
            date_aux = move.date
            name_aux = 'ROL'
            for line in this.detalle_ids:
                #lineas del CP
                #no considerar lineas de descuentos
                line_id = certificate_line_obj.create(cr, uid, {
                    #'certificate_id':cp_id,
                    'project_id':line.partida_id.project_id.id,
                    'task_id':line.partida_id.project_id.tasks[0].id,
                    'budget_id':line.partida_id.id,
                    'amount':line.monto,
                    'amount_certified':line.monto,
                    'amount_commited':line.monto,
                })
                linea_aux_rol = certificate_line_obj.browse(cr, uid, line_id)
                b_id = linea_aux_rol.budget_id.id
                p_id = linea_aux_rol.budget_post.id
                #lo que suma y el extra rol van a debe
                #primero el sueldo basico y el a pagar de sueldo
                partner_id = 1
                if line.rubro_id.partner_id:
                    partner_id = line.rubro_id.partner_id.id
                if line.rubro_id.category_id.code=='BASIC':
                    certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,})
                    #sacar los roles del programa y aqui por cada uno sacar los totales
                    s_basic_aux = eg_aux = aux_total_det = 0
                    #ojo aqui tambien debe ser no con la partida sino con el post
#                    roles_aux = slip_obj.search(cr, uid, [('program_id','=',line.programa_id.id),('payslip_run_id','=',this.id),('budget_id','=',line.partida_id.id)])
                    roles_aux = slip_obj.search(cr, uid, [('program_id','=',line.programa_id.id),('payslip_run_id','=',this.id),('budget_id2','=',line.partida_id.budget_post_id.id)])
                    aux_total_det = s_basic_aux = s_o_ing = eg_aux = aux_3 = 0 
                    for rol_aux_id in roles_aux:
                        rol_aux = slip_obj.browse(cr, uid, rol_aux_id)
                        s_basic_aux += rol_aux.basic
                        s_o_ing += rol_aux.allowance
                        eg_aux += rol_aux.deduction
                    aux_3 = s_basic_aux + s_o_ing
                    aux_total_det = s_basic_aux - eg_aux
                    account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id),('type','!=','view')])
                    if not account_ids:
                        aux_msg_1 = line.partida_id.budget_post_id.code
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("La partida '%s' no tiene parametrizado la cuenta") % (aux_msg_1))
                    for account_id in account_ids:
                        account = account_obj.browse(cr, uid, account_id)
                        if account.account_pay_id or account.account_rec_id:
                            break#continue
                    #SQL
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.id,s_basic_aux,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'Sueldo',False,True,partner_id))
                    if account.account_rec_id:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.account_rec_id.id,aux_total_det,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'neto',False,False,partner_id))
                    elif account.account_pay_id:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.account_pay_id.id,aux_total_det,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'neto',False,False,partner_id))
                    else:
                        aux_msg_1 = account.code + ' - ' + account.name
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("La cuenta '%s' no tiene parametrizado la cuenta de pago") % (aux_msg_1))
                #extra rol apt patronal
                elif line.rubro_id.category_id.code=='COMP':
                    band_comp = False
                    certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,})
                    account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id)])
                    if not account_ids:
                        print "No partida cuenta"
                    account = account_obj.browse(cr, uid, account_ids[0])
                    for account_id in account_ids:
                        account = account_obj.browse(cr, uid, account_id)
                        if account.account_rec_id:
                            account_comp = account.account_rec_id.id
                            band_comp = True
                            break
                        elif account.account_pay_id:
                            account_comp = account.account_pay_id.id
                            band_comp=True
                            break
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'Patronal',False,True,partner_id))
                    if band_comp:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_comp,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,'patronal',False,False,partner_id))
                    else:
                        aux_msg_1 = account.code + ' - ' + account.name
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("La cuenta '%s' no tiene parametrizado la cuenta de pago") % (aux_msg_1))
                #Ingresos
                elif line.rubro_id.category_id.code in ('ING','APT'):
                    aux_desc = line.rubro_id.name
                    aux_ref = 'ingreso'
                    certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,})
                    account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id),('type','!=','view')])
                    if not account_ids:
                        aux_msg_1 = line.partida_id.budget_post_id.code + ' - ' + line.partida_id.budget_post_id.name
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("La partida '%s' no tiene parametrizado la relacion con cuenta patrimonial de gasto") % (aux_msg_1))
                    if len(account_ids)>1:
                        for acc_id in account_ids:
                            account_aux = account_obj.browse(cr, uid, acc_id)
                            if account_aux.account_rec_id.id or account_aux.account_pay_id.id:
                                account = account_obj.browse(cr, uid, acc_id)
                    else:
                        if not account_ids:
                            print "RAOSE DE NO CUNETA PARTIDA CONFIGURACON"
                        account = account_obj.browse(cr, uid, account_ids[0])
                    if not account:
                        print "RAISE DE BO  HAY CONFIGURADOIN DE LA CUENTA"
                    cr.execute('''
                    INSERT INTO account_move_line (
                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,ref,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,aux_desc,False,True,'ingreso',partner_id))
                    if account.account_rec_id:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,ref,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.account_rec_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,aux_desc,False,False,'ingreso',partner_id))
                    elif account.account_pay_id:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado,budget_accrued,ref,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.account_pay_id.id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,line_id,b_id,p_id,aux_desc,False,False,'ingreso',partner_id))
                    else:
                        aux_msg_1 = account.code + ' - ' + account.name
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("La cuenta '%s' no tiene parametrizado la cuenta de pago") % (aux_msg_1))
                elif line.rubro_id.category_id.code == 'EGR':
                    #Anticipos de salario tiene 3 lineas
                    #hacer sql para insertar directo seria mucho mas rapido
                    #separar la primera quincena
                    if "Anticipo" in line.rubro_id.name:
                        if line.programa_id.id in anticipo_aux:
                            continue
                        #saco los anticipos de los empleados del rol
                        else:
                            anticipo_ids = pay_line.search(cr, uid, [('run_id','=',this.id),('salary_rule_id','=',line.rubro_id.id),
                                                                     ('program_id','=',line.programa_id.id)])
                        if anticipo_ids:
                            no_cta = []
                            for anticipo_id in anticipo_ids:
                                anticipo = pay_line.browse(cr, uid, anticipo_id)
                                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',anticipo.employee_id.name)],limit=1)
                                if partner_ids:
                                    partner= partner_obj.browse(cr, uid, partner_ids[0])
                                else:
                                    print "NO partner de empleado"
                                if partner.anticipo_id:
                                    account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id)])
                                    if not account_ids:
                                        print "No partida cuenta"
                                    for account_id in account_ids:
                                        account = account_obj.browse(cr, uid, account_id)
                                        if account.account_rec_id:
                                            account_id_ant = account.account_rec_id.id
                                            break
                                        elif account.account_pay_id:
                                            account_id_ant = account.account_pay_id.id
                                            break
                                        else:
                                            #aux_msg_1 = account.code + ' - ' + account.name
                                            #raise osv.except_osv(('Error de Configuracion !'),
                                            #                     ("La cuenta '%s' no tiene parametrizado la cuenta de pago") % (aux_msg_1))
                                            account_id_ant = account_obj.browse(cr, uid, account_ids[0])
#                                    if not account_id_ant:
#                                        aux_msg_ant = anticipo.employee_id.complete_name
#                                        raise osv.except_osv(('Error de Configuracion !'),
#                                                             ("No hay cuenta de anticipo para '%s'") % (aux_msg_ant))
                                    #hacer con sqls para optimizar
                                    anticipo_acc_id = partner.anticipo_id.id 
                                    if line.rubro_id.account_id:
                                        anticipo_acc_id = line.rubro_id.account_id.id
                                    name_aux = line.rubro_id.name
                                    cr.execute('''
                                    INSERT INTO account_move_line (
                                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,partner_id) VALUES (%s,%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s)''',(move_id,anticipo_acc_id,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False,partner.id))
                                    cr.execute('''
                                    INSERT INTO account_move_line (
                                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_paid,migrado,budget_post,budget_id,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id_ant,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,True,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,partner.id))
                                    cr.execute('''
                                    INSERT INTO account_move_line (
                                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,migrado,budget_post,budget_id,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id_ant,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,partner.id))
                                else:
                                    no_cta.append(partner.name)
                            if no_cta:
                                str_empleados = ''
                                for n_cta in no_cta:
                                    str_empleados += n_cta + ' - '  
                                raise osv.except_osv(('Error de Configuracion !'),
                                                     ("Los funcionarios '%s' no tiene parametrizado la cuenta de anticipo") % (str_empleados))
                            #no considerar esto en limon
                            varios_opcion = 'No'
                            parameter_obj = self.pool.get('ir.config_parameter')
                            varios_anticipos_programa_ids = parameter_obj.search(cr, uid, [('key','=','anticipoPrograma')],limit=1)
                            if varios_anticipos_programa_ids:
                                varios_opcion = parameter_obj.browse(cr, uid, varios_anticipos_programa_ids[0]).value
                            if varios_opcion=='No':
                                anticipo_aux.append(line.programa_id.id)
                            band = True
                    #egresos en general
                    elif line.rubro_id.name in ('PRIMERA QUINCENA'):
                        if line.programa_id.id in quincena_aux:
                            continue
                        #saco los anticipos de los empleados del rol
                        else:
                            anticipo_ids = pay_line.search(cr, uid, [('run_id','=',this.id),('salary_rule_id','=',line.rubro_id.id),
                                                                     ('program_id','=',line.programa_id.id)])
                        if anticipo_ids:
                            for anticipo_id in anticipo_ids:
                                anticipo = pay_line.browse(cr, uid, anticipo_id)
                                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',anticipo.employee_id.name)],limit=1)
                                if partner_ids:
                                    partner= partner_obj.browse(cr, uid, partner_ids[0])
                                else:
                                    print "NO partner de empleado"
                                if partner.anticipo_id:
                                    account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id)])
                                    if not account_ids:
                                        print "No partida cuenta"
                                    for account_id in account_ids:
                                        account = account_obj.browse(cr, uid, account_id)
                                        if account.account_rec_id:
                                            account_quin_id = account.account_rec_id.id
                                            break
                                        elif account.account_pay_id:
                                            account_quin_id = account.account_pay_id.id
                                            break
                                        else:
                                            account_quin_id = account_obj.browse(cr, uid, account_ids[0]).id
                                    #hacer con sqls para optimizar
                                    name_aux = 'Antic. 1er Quincena'
                                    cr.execute('''
                                    INSERT INTO account_move_line (
                                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado) VALUES (%s,%s,%s, %s, %s, %s, %s, %s,%s,%s,%s)''',(move_id,partner.anticipo_id.id,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False))
                                    cr.execute('''
                                    INSERT INTO account_move_line (
                                    move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_paid,migrado,budget_post,budget_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_quin_id,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,True,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id))
                                    cr.execute('''
                                    INSERT INTO account_move_line (
                                    move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,migrado,budget_post,budget_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_quin_id,anticipo.amount,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id))
                                else:
                                    raise osv.except_osv(('Error de Configuracion !'),
                                                         ("El proveedor '%s' no tiene parametrizado la cuenta de anticipo") % (partner.name))
                            quincena_aux.append(line.programa_id.id)
                            band = True
                    else:
                        #revisar la afectacion presupuestaria
                        #aqui sacar directo de la tabla la cuenta por pagar que esta en el rubro, pero de la tabla de configuracion
                        budget_item = line.partida_id
                        config_ids = config_obj.search(cr, uid, [('rule_id','=',line.rubro_id.id),('budget_id','=',budget_item.budget_post_id.id)])
                        if not config_ids:
                            print "NO configuracion de rubro",line.rubro_id.name
                            aux_bd = budget_item.budget_post_id.code + ' - ' + budget_item.budget_post_id.name  
                            config_ids = config_obj.search(cr, uid, [('rule_id','=',line.rubro_id.id)])
                            if not config_ids:
                                raise osv.except_osv(('Error de Configuracion !'),
                                                     ("El rubro '%s' no tiene parametrizado para la partida") % (line.rubro_id.name))
                        config = config_obj.browse(cr, uid, config_ids[0])
                        account_id = config.pay_account_id.id
                        name_aux = line.rubro_id.name
                        cr.execute('''
                        INSERT INTO account_move_line (
                            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,budget_id_cert,budget_paid,migrado,budget_post,budget_id,partner_id) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_id,line.monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,line_id,False,False,linea_aux_rol.budget_post.id,linea_aux_rol.budget_id.id,partner_id))
                else:
                    print "fds"
#            certificate_obj.action_request(cr, uid, [cp_id], context)
#            certificate_obj.action_certified(cr, uid, [cp_id], context)
#            certificate_obj.action_commited(cr, uid, [cp_id], context)
            self.write(cr, uid, this.id,{
                'move_id':move_id,
                'certificate_id':cp_id,
            })
        return True

    def _create_budget_tthh(self, cr, uid, ids, context=None):
        '''EN ESTE METODO SERIA MAS OPIMO USAR SQL DIRECTO PARA OPTIMIZAR EL TIEMPO'''
        move_obj = self.pool.get('account.move')
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        partner_obj = self.pool.get('res.partner')
        journal_obj = self.pool.get('account.journal')
        config_obj = self.pool.get('hr.account.configuration')
        period_obj = self.pool.get('account.period')
        pay_line = self.pool.get('hr.payslip.line')
        slip_obj = self.pool.get('hr.payslip')
        certificate_obj = self.pool.get('budget.certificate')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        project_obj = self.pool.get('project.project')
        user_obj = self.pool.get('res.users')
        total_aux = deduction_aux = basic_aux = s_o_ing = 0
        state_aux = 'draft'
        company_aux = 1
        currency_aux = 2
        band = False
        anticipo_aux = []
        quincena_aux = []
        for this in self.browse(cr, uid, ids):
            #certificacion presupuestaria
            aux_name = 'ASIENTO - ' + ustr(this.name) + ' DEL:  ' + ustr(this.period_id.name)
            usuario = user_obj.browse(cr, uid, uid)
            project_ids = project_obj.search(cr, uid, [])
            notes_aux = 'CERTIFICACION PRESUPUESTARIA DE NOMINA: ' + ustr(this.name) + ' DEL:  ' + ustr(this.period_id.name)
            if this.move_id:
                if this.move_id.state=='posted':
                    raise osv.except_osv(('Error de Usuario !'),
                                     ("El asiento de rol esta contabilizado no puede ejecutar esta accion"))
            if this.certificate_id:
                if this.certificate_id.name=='/':
                    cr.execute("delete from budget_certificate_line where certificate_id=%s"%(this.certificate_id.id))
                    certificate_obj.unlink(cr, uid, [this.certificate_id.id],context)
                    cp_id = certificate_obj.create(cr, uid, {
                        'department_id':usuario.context_department_id.id,
                        'solicitant_id':usuario.employee_id.id,
                        'project_id':project_ids[0],
                        'partner_id':1,
                        'notes':notes_aux,
                        'date':this.date_end,
                        'date_confirmed':this.date_end,
                        'date_commited':this.date_end,
                    })
                else:
                    cr.execute("delete from budget_certificate_line where certificate_id=%s"%(this.certificate_id.id))
                    cp_id = this.certificate_id.id
            else:
                cp_id = certificate_obj.create(cr, uid, {
                    'department_id':usuario.context_department_id.id,
                    'solicitant_id':usuario.employee_id.id,
                    'project_id':project_ids[0],
                    'partner_id':1,
                    'notes':notes_aux,
                    'date':this.date_end,
                    'date_confirmed':this.date_end,
                    'date_commited':this.date_end,
                })
            period_ids = period_obj.search(cr, uid, [('date_start','<=',this.date_end),('date_stop','>=',this.date_end)])
            if not period_ids:
                raise osv.except_osv(('Error de Configuracion !'),
                                     ("No existe periodo contable para la fecha de rol"))
            for rol in this.slip_ids:
                deduction_aux += rol.deduction
                basic_aux += rol.basic
            total_aux = basic_aux - deduction_aux
            for line in this.detalle_ids:
                #lineas del CP
                #no considerar lineas de descuentos
                line_id = certificate_line_obj.create(cr, uid, {
                    #'certificate_id':cp_id,
                    'project_id':line.partida_id.project_id.id,
                    'task_id':line.partida_id.project_id.tasks[0].id,
                    'budget_id':line.partida_id.id,
                    'amount':line.monto,
                    'amount_certified':line.monto,
                    'amount_commited':line.monto,
                })
                linea_aux_rol = certificate_line_obj.browse(cr, uid, line_id)
                b_id = linea_aux_rol.budget_id.id
                p_id = linea_aux_rol.budget_post.id
                #lo que suma y el extra rol van a debe
                #primero el sueldo basico y el a pagar de sueldo
                partner_id = 1
                if line.rubro_id.partner_id:
                    partner_id = line.rubro_id.partner_id.id
                if line.rubro_id.category_id.code=='BASIC':
                    certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,})
                    #sacar los roles del programa y aqui por cada uno sacar los totales
                    s_basic_aux = eg_aux = aux_total_det = 0
                    #ojo aqui tambien debe ser no con la partida sino con el post
#                    roles_aux = slip_obj.search(cr, uid, [('program_id','=',line.programa_id.id),('payslip_run_id','=',this.id),('budget_id','=',line.partida_id.id)])
                    roles_aux = slip_obj.search(cr, uid, [('program_id','=',line.programa_id.id),('payslip_run_id','=',this.id),('budget_id2','=',line.partida_id.budget_post_id.id)])
                    aux_total_det = s_basic_aux = s_o_ing = eg_aux = aux_3 = 0 
                    for rol_aux_id in roles_aux:
                        rol_aux = slip_obj.browse(cr, uid, rol_aux_id)
                        s_basic_aux += rol_aux.basic
                        s_o_ing += rol_aux.allowance
                        eg_aux += rol_aux.deduction
                    aux_3 = s_basic_aux + s_o_ing
                    aux_total_det = s_basic_aux - eg_aux
                #extra rol apt patronal
                elif line.rubro_id.category_id.code=='COMP':
                    certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,})
                #Ingresos
                elif line.rubro_id.category_id.code in ('ING','APT'):
                    aux_desc = line.rubro_id.name
                    aux_ref = 'ingreso'
                    certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,})
                elif line.rubro_id.category_id.code == 'EGR':
                    certificate_line_obj.write(cr, uid, line_id,{'certificate_id':cp_id,})
            self.write(cr, uid, this.id,{
                'certificate_id':cp_id,
            })
        return True
    
    def presupuesto_payslip_run(self, cr, uid, ids, context=None):
        payslip_line_obj = self.pool.get('hr.payslip.line')
        detalle_obj = self.pool.get('run.programa.detalle')
        budget_item_obj=self.pool.get('budget.item')
        rule_obj = self.pool.get('hr.salary.rule')
        program_obj = self.pool.get('project.program')
        project_obj = self.pool.get('project.project')
        config_obj = self.pool.get('hr.account.configuration')
        programas = []
        rubros = []
        contratos = []
        detalle = []
        for this in self.browse(cr, uid, ids):
            id_this = this.id
            detalle_antes = detalle_obj.search(cr, uid, [('run_id','=',id_this)])
            detalle_obj.unlink(cr, uid, detalle_antes)
            slip_aux = []
            for line in this.slip_ids:#roles individuales
                slip_aux.append(line.id)
                lineas_rol = payslip_line_obj.search(cr, uid, [('slip_id','=',line.id)])
                if len(lineas_rol)>1:
                    tuple_ids = tuple(lineas_rol)
                    operador = 'in'
                else:
                    tuple_ids = (lineas_rol[0])
                    operador = '='
                if lineas_rol:
                    sql_update = "UPDATE hr_payslip_line set budget_id2=%s where id %s %s"%(line.budget_id2.id,operador,tuple_ids)
                    cr.execute(sql_update)
                if not line.program_id.id in programas:
                    programas.append(line.program_id.id)
                for rubro in line.line_ids:#payslip line
                    if rubro.salary_rule_id.category_id.code not in ('NET'):
                        if not rubro.salary_rule_id.id in rubros:
                            rubros.append(rubro.salary_rule_id.id)
                if not line.contract_id.budget_id.id in contratos:
                    #aqui deberia tambien buscar entre fechas para colocar
                    item_idsc = budget_item_obj.search(cr, uid, [('budget_post_id','=',line.contract_id.budget_id.budget_post_id.id),
                                                                 ('date_start','<=',this.date_start),('date_end','>=',this.date_start),
                                                                 ('program_id','=',line.contract_id.program_id.id)],limit=1)
                    if not item_idsc:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("No existen planificacion de partida en el contrato para el anio en curso %s") % (this.date_start))
                    if not item_idsc[0] in contratos:
                        contratos.append(item_idsc[0])
                    #contratos.append(line.contract_id.budget_id.id)
            #poner el budget_id2 de cada rol en las lineas de rol
#        for programa_id in programas:
            for rubro_id in rubros:
                for contrato_budget_id in contratos:
                    item_contrato = budget_item_obj.browse(cr, uid, contrato_budget_id)
                    rubro = rule_obj.browse(cr, uid, rubro_id)
                    programa_id = item_contrato.program_id.id
                    payslip_line_ids = payslip_line_obj.search(cr, uid, [('program_id','=',programa_id),('budget_id2','=',item_contrato.budget_post_id.id),
                                                                         ('slip_id','in',slip_aux),('salary_rule_id','=',rubro_id)])
#                    if not payslip_line_ids:
#                        payslip_line_ids = payslip_line_obj.search(cr, uid, [('program_id','=',programa_id),('budget_id','=',item_contrato.id),
#                                                                             ('slip_id','in',slip_aux),('salary_rule_id','=',rubro_id)])
                    monto = 0 
                    if payslip_line_ids:
                        for line_id in payslip_line_ids:
                            payslip_line = payslip_line_obj.browse(cr, uid, line_id)
                            monto += payslip_line.amount
                        config_ids = config_obj.search(cr, uid, [('rule_id','=',rubro_id)])
                        if config_ids:
                            for config_line in config_ids:
                                config_aux = config_obj.browse(cr, uid, config_line)
                                if config_aux.budget_id.id == item_contrato.budget_post_id.id:
                                    budget_id = item_contrato.id
                                    break
                                else:
                                    conf_aux = config_obj.browse(cr, uid, config_ids[0])#config_ids[0]
                                    partida_name = conf_aux.budget_id.name
                                    item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('name','=',partida_name),
                                                                                ('date_start','<=',this.date_start),('date_end','>=',this.date_start)],limit=1)
                                    if item_ids:
                                        budget_id = item_ids[0]
                                    else:
                                        budget_id = contrato_budget_id
                            project_ids = project_obj.search(cr, uid, [('program_id','=',programa_id)],limit=1)
                        else:
                            budget_id = contrato_budget_id
                        programa = program_obj.browse(cr, uid, programa_id)
                        aux_pr = programa.sequence + ' - ' + programa.name
                        detalle_id = detalle_obj.create(cr, uid, {
                            'run_id':id_this,
                            'programa_id':programa_id,
                            'rubro_id':rubro_id,
                            'partida_id':budget_id,
                            'monto':monto,
                        })
            self._create_budget_tthh(cr, uid, ids)
        return True


hr_inherit_payslip_account()
