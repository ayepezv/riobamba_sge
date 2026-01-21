# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
#  mariofchogllo@gmail.com
#  GobERP - Sistema de Gestion Empresarial para GADS, EPS y ONGs.
##############################################################################

__author__ = 'Mario Chogllo'

import xlrd
import base64
import time
import logging
from datetime import date, datetime
from osv import osv, fields
from gt_tool import XLSWriter

class importDec3(osv.TransientModel):
    _name = 'import.dec3'
    _columns = dict(
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
        opcion = fields.selection([('Anticipo','Anticipo'),('Judicial','Judicial')],'Descuento'),
    )
    def import_Dec3(self, cr, uid, ids, context):
        employee_obj = self.pool.get('hr.employee')
        line_obj = self.pool.get('hr.decimo.tercero.line')
        decimo_id = context['active_id']
        for this in self.browse(cr, uid, ids):
            arch = this.datas
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            if this.opcion=='Anticipo':
                for r in range(sh.nrows)[1:]:  
                    aux_cedula = str(sh.cell(r,1).value)
                    aux_monto = sh.cell(r,2).value
                    employee_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)])
                    if employee_ids:
                        lineas_decimo = line_obj.search(cr, uid, [('employee_id','=',employee_ids[0]),('dec_id','=',decimo_id)])
                        if lineas_decimo:
                            line_obj.write(cr, uid, lineas_decimo[0],{'descuento_anticipo':aux_monto})
            else:
                for r in range(sh.nrows)[1:]:  
                    aux_cedula = str(sh.cell(r,1).value)
                    aux_monto = sh.cell(r,2).value
                    employee_ids = employee_obj.search(cr, uid, [('name','=',aux_cedula)])
                    if employee_ids:
                        lineas_decimo = line_obj.search(cr, uid, [('employee_id','=',employee_ids[0]),('dec_id','=',decimo_id)])
                        if lineas_decimo:
                            line_obj.write(cr, uid, lineas_decimo[0],{'descuento_judicial':aux_monto})
        return {'type': 'ir.actions.act_window_close'}

importDec3()

class hr_dec4_export(osv.TransientModel):
    _name='hr.dec4.export'
    _columns = {
        'datas':fields.binary('Archivo'),
        'datas_fname':fields.char('Nombre archivo', size=32),
        'payroll_id': fields.many2one('hr.decimo.cuarto','Rol'),
    }
    
    def rol_padre(self, cr, uid, context={}):
        return context.get('active_id')    

    _defaults = {
                 'payroll_id': rol_padre,
                 }

    def rol_padre(self, cr, uid, context={}):
        return context.get('active_id')

    def generar_archivo_dec4(self, cr, uid, ids, context={}):
        dec_line_obj = self.pool.get('hr.decimo.cuarto.line')
        writer = XLSWriter.XLSWriter()
        total_subtotal = total_dec = total_recibir = 0
        for this in self.browse(cr, uid, ids):
            aux_sql = '''select id,sequence,name from project_program where id in (select program_id from hr_decimo_cuarto_line where dec_id=%s group by program_id order by program_id) order by sequence'''%(this.payroll_id.id)
            cr.execute(aux_sql)
            aux = cr. fetchall()
            writer.append(['DECIMO CUARTO',this.payroll_id.name])
            for aux_programa in aux:
                total_subtotal_s = total_dec_s = total_recibir_s = 0
                writer.append(['PROGRAMA',aux_programa[1],aux_programa[2]])
                writer.append(['Nro.','Funcionario','Subtotal','Desc.Ret.Judicial','Neto A recibir','Partida'])
                dec_line_ids = dec_line_obj.search(cr, uid, [('program_id','=',aux_programa[0]),('dec_id','=',this.payroll_id.id)])
                aux_sec = aux_subtotal = 0
                if dec_line_ids:
                    for dec_line_id in dec_line_ids:
                        aux_sec += 1
                        dec_line = dec_line_obj.browse(cr, uid, dec_line_id)
                        aux_subtotal = dec_line.recibir + dec_line.descuento_judicial
                        total_subtotal += aux_subtotal
                        total_dec += dec_line.descuento_judicial
                        total_recibir += dec_line.recibir
                        total_subtotal_s += aux_subtotal
                        total_dec_s += dec_line.descuento_judicial
                        total_recibir_s += dec_line.recibir
                        aux_partida = dec_line.contract_id.budget_id.code[0:7]+'204'+dec_line.contract_id.budget_id.code[10:]
                        writer.append([aux_sec,dec_line.employee_id.complete_name,aux_subtotal,dec_line.descuento_judicial,dec_line.recibir,aux_partida])
                writer.append(['','TOTAL PROGRAMA',total_subtotal_s,total_dec_s,total_recibir_s])
            writer.append(['','TOTAL DECIMO',total_subtotal,total_dec,total_recibir])
        writer.save("rolDecimo.xls")
        out = open("rolDecimo.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'rolDecimo.xls'})
        
hr_dec4_export()

class hrDecimoTerceroLine(osv.Model):
    _name = 'hr.decimo.tercero.line'

    def _amount_decimo(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'total': 0.0,
                'recibir': 0.0,
                }
            aux_suma = line.dic + line.ene + line.feb + line.mar + line.abr + line.may + line.jun + line.jul + line.ago + line.sep + line.oct + line.nov
            aux_net = aux_suma/12
            res[line.id]['total'] = aux_suma
            res[line.id]['total_dec'] = aux_net
            res[line.id]['recibir']  = aux_net - line.descuento_judicial - line.descuento_anticipo
            res[line.id]['total_decimo'] = aux_net 
        return res

    _columns = dict(
        budget_id = fields.many2one('budget.item','Partida'),
        fy_id = fields.related('dec_id','fy_id',type='many2one',relation='hr.work.period',store=True),
        budget_contrato_id = fields.related('contract_id', 'budget_id', type='many2one', relation='budget.item', string='Partida', store=True),
        dec_id = fields.many2one('hr.decimo.tercero','Decimo'),
        employee_id = fields.related('contract_id', 'employee_id', type="many2one", 
                                    relation='hr.employee', string="Empleado", store=True),
        contract_id = fields.many2one('hr.contract','Empleado'),
        program_id = fields.related('contract_id', 'program_id', type="many2one", 
                                    relation='project.program', string="Programa", store=True),
        dic = fields.float('Dic'),
        ene = fields.float('Ene'),
        feb = fields.float('Feb'),
        mar = fields.float('Mar'),
        abr = fields.float('Abr'),
        may = fields.float('May'),
        jun = fields.float('Jun'),
        jul = fields.float('Jul'),
        ago = fields.float('Ago'),
        sep = fields.float('Sep'),
        oct = fields.float('Oct'),
        nov = fields.float('Nov'),
        descuento_anticipo = fields.float('Descuento Anticipo'),
        descuento_judicial = fields.float('Descuento Judicial'),
        total = fields.function(_amount_decimo, multi="dec",type="float", store=True,string='TOTAL GANADO'),
        total_dec = fields.function(_amount_decimo, multi="dec",type="float", store=True,string='TOTAL DECIMO'),
        recibir = fields.function(_amount_decimo, multi="dec",type="float", store=True,string='RECIBIR'),
        fecha_contrato = fields.date('Fecha Contrato'),
        total_decimo = fields.function(_amount_decimo, multi="dec",type="float", store=True,string='TOTAL DECIMO'),
    )
hrDecimoTerceroLine()


class hrDecimoTercero(osv.Model):
    _name = 'hr.decimo.tercero'

    def regresa_dec3(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{
            'state':'Borrador'
        })
        return True

    def aprobar_dec3(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{
            'state':'Aprobado'
        })
        return True

    def colocarPartidaD3(self, cr, uid, ids, context):
        year_obj = self.pool.get('account.fiscalyear')
        post_obj = self.pool.get('budget.post')
        item_obj = self.pool.get('budget.item')
        dec3_line_obj = self.pool.get('hr.decimo.tercero.line')
        for this in self.browse(cr, uid, ids):
            year_ids = year_obj.search(cr, uid, [('date_start','<=',this.period_end.date_stop),('date_stop','>=',this.period_end.date_stop)],limit=1)
            if year_ids:
                year = year_obj.browse(cr, uid, year_ids[0])
            else:
                raise osv.except_osv('Error de configuracion', 'No hay anio fiscal para la fecha de compromiso.')
            for line in this.line_ids:
                aux_partida_6 = line.contract_id.budget_id.budget_post_id.code[0:3]+'203'
                if this.contract_type.name=='JUBILADO':
                    aux_partida = line.contract_id.budget_id.budget_post_id.code
                else:
                    aux_partida = line.contract_id.budget_id.budget_post_id.code[0:3]+'203'+line.contract_id.budget_id.budget_post_id.code[6:]
                post_ids = post_obj.search(cr, uid, [('code','ilike','%'+aux_partida)])
                if not post_ids:
                    post_ids = post_obj.search(cr, uid, [('code','ilike','%'+aux_partida_6)])
                    if post_ids:
                        item_ids = item_obj.search(cr, uid, [('budget_post_id','in',post_ids),
                                                             ('program_id','=',line.contract_id.program_id.id),('year_id','=',year_ids[0])])
                        if item_ids:
                            dec3_line_obj.write(cr, uid, line.id,{'budget_id':item_ids[0]})
                else:
                    item_ids = item_obj.search(cr, uid, [('budget_post_id','in',post_ids),
                                                         ('program_id','=',line.contract_id.program_id.id),('year_id','=',year_ids[0])])
                    if item_ids:
                        dec3_line_obj.write(cr, uid, line.id,{'budget_id':item_ids[0]})
                    else:
                        post_ids = post_obj.search(cr, uid, [('code','ilike','%'+aux_partida_6)])
                        if post_ids:
                            item_ids = item_obj.search(cr, uid, [('budget_post_id','in',post_ids),
                                                                 ('program_id','=',line.contract_id.program_id.id),('year_id','=',year_ids[0])])
                            if item_ids:
                                dec3_line_obj.write(cr, uid, line.id,{'budget_id':item_ids[0]})
        return True


    def genera_ret_dec3(self, cr, uid, ids, context=None):
        pago_obj = self.pool.get('hr.varios')
        pago_line_obj = self.pool.get('hr.varios.line')
        contract_obj = self.pool.get('hr.contract')
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            aux_desc = 'PAGO RETENCIONES JUDICIALES: ' + this.name
            aux_desc1 = 'PAGO RETENCIONES JUDICIALES SUPA: ' + this.name
            period_ids = period_obj.find(cr, uid, this.period_end.date_stop)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            pago_id = pago_obj.create(cr, uid, {
                'name':aux_desc,
                'period_id':period_ids[0],
            })
            pago_id_2 = pago_obj.create(cr, uid, {
                'name':aux_desc1,
                'period_id':period_ids[0],
            })
            m = k = 0
            for line in this.line_ids:
                total_decimo = line.total_decimo
                total_decimo_origen = line.total_decimo
                total_otras = 0
                if line.descuento_judicial>0:
                    aux_sum_line_ret = 0
                    for line_benef in line.contract_id.employee_id.judicial_ids:
                        aux_sum_line_ret += line_benef.monto 
                    for line_benef in line.contract_id.employee_id.judicial_ids:
                        if total_decimo>0:
                            if line_benef.monto<=total_decimo:
                                aux_monto = line_benef.monto#(line_benef.monto * line.descuento_judicial) / aux_sum_line_ret
                                total_decimo = total_decimo - line_benef.monto
                                total_otras += line_benef.monto		
                            else:
                                aux_monto = abs(total_decimo_origen - total_otras)
                                total_decimo = 0			 
                        #aux_monto =  (line_benef.monto * line.descuento_judicial) / aux_sum_line_ret
                        if line_benef.is_supa:
                            m += 1
                            line_id = pago_line_obj.create(cr, uid, {
                                'name':line_benef.partner_id.id,
                                'varios_id':pago_id_2,
                                'monto':aux_monto,
                                'valor':aux_monto,
                                'descontado_id':line.contract_id.employee_id.id,
                            })
                        else:
                            k += 1
                            line_id = pago_line_obj.create(cr, uid, {
                                'name':line_benef.partner_id.id,
                                'varios_id':pago_id,
                                'monto':aux_monto,
                                'valor':aux_monto,
                                'descontado_id':line.contract_id.employee_id.id,
                            })
            if m==0:
                pago_obj.unlink(cr, uid, [pago_id_2])
            if k==0:
                pago_obj.unlink(cr, uid, [pago_id])
        return True

    def _create_move_dec(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        user_obj = self.pool.get('res.users')
        project_obj = self.pool.get('project.project')
        certificate_obj = self.pool.get('budget.certificate')
        period_obj = self.pool.get('account.period')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        for this in self.browse(cr, uid, ids):
            #sacar diario de egreso
            id_this = this.id
            period_ids = period_obj.find(cr, uid, this.period_end.date_stop)
            if not period_ids:
                raise osv.except_osv('Error configuracion','No existe periodo para la fecha de comprobante.')
            journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
            usuario = user_obj.browse(cr, uid, uid)
            project_ids = project_obj.search(cr, uid, [])
            if this.certificate_id:
                cr.execute("delete from budget_certificate_line where certificate_id=%s"%(this.certificate_id.id))
                cp_id = this.certificate_id.id
            else:
                notes_aux = 'CERTIFICACION PRESUPUESTARIA : ' + this.name
                cp_id = certificate_obj.create(cr, uid, {
                    'department_id':usuario.context_department_id.id,
                    'solicitant_id':usuario.employee_id.id,
                    'project_id':project_ids[0],
                    'partner_id':1,
                    'notes':notes_aux,
                    'date':this.period_end.date_stop,
                    'date_commited':this.period_end.date_stop,                    
                    'date_confirmed':this.period_end.date_stop,
                })
            if this.move_id:
                if this.move_id.state=='draft' and this.move_id.name=='/':
                    cr.execute("delete from account_move_line where move_id=%s"%(this.move_id.id))
                    move_obj.unlink(cr, uid, [this.move_id.id],aux=1)
                    move_id = move_obj.create(cr, uid, {
                        'ref': this.name,
                        'narration':this.name,
                        'journal_id': journal_ids[0],
                        'date': this.period_end.date_stop,
                        'period_id':period_ids[0],
                        'state':'draft',
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
                    'ref': this.name,
                    'narration':this.name,
                    'journal_id': journal_ids[0],
                    'date': this.period_end.date_stop,
                    'period_id':period_ids[0],
                    'state':'draft',
                    'afectacion':True,
                    'partner_id':1,
                    'certificate_id':cp_id,
                    'type':'Nomina',
                    'validar_cp':True,
                })            
            for line in this.detalle_ids:
                line_id = certificate_line_obj.create(cr, uid, {
                    'certificate_id':cp_id,
                    'project_id':line.partida_id.project_id.id,
                    'task_id':line.partida_id.project_id.tasks[0].id,
                    'budget_id':line.partida_id.id,
                    'amount':line.monto,
                    'amount_certified':line.monto,
                    'amount_commited':line.monto,
                })
                linea_aux_rol = certificate_line_obj.browse(cr, uid, line_id)
                account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id)])
                if not account_ids:
                    account_ids = account_obj.search(cr, uid, [('budget_id.code','=',line.partida_id.budget_post_id.code[0:6])])
                    if not account_ids:
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("La partida '%s' no tiene configuracion contable") % (line.partida_id.budget_post_id.code))
                for acc_id in account_ids:
                    account_aux = account_obj.browse(cr, uid, acc_id)
                    if account_aux.account_rec_id.id:
                        account = account_obj.browse(cr, uid, acc_id)
                        aux_cxp = account.account_rec_id.id
                        break
                    elif account_aux.account_pay_id.id:
                        account = account_obj.browse(cr, uid, acc_id)
                        aux_cxp = account.account_pay_id.id
                        break
                if not account:
                    raise osv.except_osv(('Error de Configuracion !'),
                                         ("No hay configuracoin contable de la partida") % (line.partida_id.budget_post_id.code))
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':account.id,
                    'debit':line.monto,
                    'budget_id_cert':line_id,
                    'budget_accrued':True,
                    'name':'decimo',
                })
                move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':aux_cxp,
                        'credit':line.monto,
                        'name':'decimo pagar',
                        'budget_id_cert':line_id,
                })
        self.write(cr, uid, this.id,{
            'move_id':move_id,
            'certificate_id':cp_id,
        })
        return True

    def genera_dec3(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.decimo.tercero.line')
        salary_rule_obj = self.pool.get('hr.salary.rule')
        detalle_obj = self.pool.get('run.programa.detalle')
        budget_item_obj=self.pool.get('budget.item')
        program_obj = self.pool.get('project.program')
        project_obj = self.pool.get('project.project')
        partner_obj = self.pool.get('res.partner')
        config_obj = self.pool.get('hr.account.configuration')
        year_obj = self.pool.get('account.fiscalyear')
        post_obj = self.pool.get('budget.post')
        programas = []
        rubros = []
        contratos = []
        detalle = []
        for this in self.browse(cr, uid, ids):
            year_ids = year_obj.search(cr, uid, [('date_start','<=',this.period_end.date_stop),('date_stop','>=',this.period_end.date_stop)],limit=1)
            if year_ids:
                year = year_obj.browse(cr, uid, year_ids[0])
            else:
                raise osv.except_osv('Error de configuracion', 'No hay anio fiscal para la fecha de compromiso.')
            #sacar diario de egreso
            id_this = this.id
            detalle_antes = detalle_obj.search(cr, uid, [('dec_id','=',id_this)])
            detalle_obj.unlink(cr, uid, detalle_antes)
            rubros = salary_rule_obj.search(cr, uid, [('code','in',('dec3','DEC3'))],limit=1)
            if not rubros:
                raise osv.except_osv('Error de configuracion', 'No existe regla salarias para decimo cuarto definida')
            move_rol = this.move_id
            aux_name = this.name
            partidas = {}
            for line in this.line_ids:
                if line.budget_id:
                    #r = True
                    if this.contract_type.name=='JUBILADO':
                        if line.budget_id.id in partidas:
                            partidas[line.budget_id.id]+=line.total_dec
                        else:
                            partidas[line.budget_id.id]=line.total_dec
                    else:
                        if line.budget_id.budget_post_id.code[3:6]=='203':  #
                            if line.budget_id.id in partidas:
                                partidas[line.budget_id.id]+=line.total_dec
                            else:
                                partidas[line.budget_id.id]=line.total_dec
                        else:
                            aux_name = line.contract_id.employee_id.complete_name
                            raise osv.except_osv(('Error de usuario !'),
                                                 ("Esta usando una partida diferente a decimo tercero en %s") % (aux_name))
                else:
                    raise osv.except_osv('Error de usuario', 'Verifique que todas las lineas tengan colocada la partida presupuestaria')
            for partida in partidas:
                item = budget_item_obj.browse(cr, uid, partida)
                detalle_id = detalle_obj.create(cr, uid, {
                    'dec_id':id_this,
                    'programa_id':item.program_id.id,
                    'rubro_id':rubros[0],
                    'partida_id':item.id,
                    'monto':partidas[partida],
                    'partner_id':1,
                })
            self._create_move_dec(cr, uid, ids)
        return True

    def genera_dec3v2(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.decimo.tercero.line')
        salary_rule_obj = self.pool.get('hr.salary.rule')
        detalle_obj = self.pool.get('run.programa.detalle')
        budget_item_obj=self.pool.get('budget.item')
        program_obj = self.pool.get('project.program')
        project_obj = self.pool.get('project.project')
        partner_obj = self.pool.get('res.partner')
        config_obj = self.pool.get('hr.account.configuration')
        year_obj = self.pool.get('account.fiscalyear')
        programas = []
        rubros = []
        contratos = []
        detalle = []
        for this in self.browse(cr, uid, ids):
            year_ids = year_obj.search(cr, uid, [('date_start','<=',this.period_end.date_stop),('date_stop','>=',this.period_end.date_stop)],limit=1)
            if year_ids:
                year = year_obj.browse(cr, uid, year_ids[0])
            else:
                raise osv.except_osv('Error de configuracion', 'No hay anio fiscal para la fecha de compromiso.')
            #sacar diario de egreso
            id_this = this.id
            detalle_antes = detalle_obj.search(cr, uid, [('dec_id','=',id_this)])
            detalle_obj.unlink(cr, uid, detalle_antes)
            rubros = salary_rule_obj.search(cr, uid, [('code','in',('dec3','DEC3'))],limit=1)
            if not rubros:
                raise osv.except_osv('Error de configuracion', 'No existe regla salarias para decimo cuarto definida')
            move_rol = this.move_id
            aux_name = this.name
            for line in this.line_ids:
                if line.descuento_judicial:
                    #aqui va la misma partida de decimo
                    item_ids_desc = budget_item_obj.search(cr, uid, [('budget_post_id','=',line.contract_id.budget_id.budget_post_id.id),
                                                                 ('date_start','<=',this.period_end.date_start),('date_end','>=',this.period_end.date_start),
                                                                 ('program_id','=',line.contract_id.program_id.id)],limit=1)
                    if not item_ids_desc:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("No existen planificacion de partida en el contrato para el anio en curso %s") % (this.date_start))
                    partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',line.contract_id.employee_id.name)])
                    if not partner_ids:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("El funcionario %s descontado no tiene proveedor creado %s") % (line.contract_id.employee_id.complete_name))
                    config_ids = config_obj.search(cr, uid, [('rule_id','=',rubros[0])])
                    item_contrato = budget_item_obj.browse(cr, uid, item_ids_desc[0])
                    programa_id = line.contract_id.program_id.id
                    if config_ids:
                        for config_line in config_ids:
                            config_aux = config_obj.browse(cr, uid, config_line)
                            if config_aux.budget_id.id == item_contrato.budget_post_id.id:
                                budget_id = item_contrato.id
                                break
                            else:
                                #es rubro que tiene su propia partida
                                conf_aux = config_obj.browse(cr, uid, config_ids[0])#config_ids[0]
                                partida_name = conf_aux.budget_id.name
                                item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('name','=',partida_name),
                                                                            ('date_start','<=',this.period_end.date_start),
                                                                            ('date_end','>=',this.period_end.date_start)],limit=1)
                                if item_ids:
                                    budget_id = item_ids[0]
                            project_ids = project_obj.search(cr, uid, [('program_id','=',programa_id)],limit=1)
                    else:
                        budget_id = contrato_budget_id
                    detalle_id = detalle_obj.create(cr, uid, {
                        'dec_id':id_this,
                        'programa_id':line.contract_id.program_id.id,
                        'rubro_id':rubros[0],
                        'partida_id':budget_id,#item_ids_desc[0],
                        'monto':line.descuento_judicial,
                        'partner_id':partner_ids[0],
                    })
                if not line.program_id.id in programas:
                    programas.append(line.program_id.id)
                if not line.contract_id.budget_id.id in contratos:
                    #aqui deberia tambien buscar entre fechas para colocar
                    item_idsc = budget_item_obj.search(cr, uid, [('budget_post_id','=',line.contract_id.budget_id.budget_post_id.id),
                                                                 ('date_start','<=',this.period_end.date_start),('date_end','>=',this.period_end.date_start),
                                                                 ('program_id','=',line.contract_id.program_id.id)],limit=1)
                    if not item_idsc:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("No existen planificacion de partida en el contrato para el anio en curso %s") % (this.date_start))
                    contratos.append(item_idsc[0])
#                    contratos.append(line.contract_id.budget_id.id)
            for programa_id in programas:
                for contrato_budget_id in contratos:
                    item_contrato = budget_item_obj.browse(cr, uid, contrato_budget_id)
                    dec_line_ids = line_obj.search(cr, uid, [('program_id','=',programa_id),
                                                             ('dec_id','=',this.id)])
                    if dec_line_ids:
                        monto = 0
                        for line_id in dec_line_ids:
                            dec_line = line_obj.browse(cr, uid, line_id)
                            monto += dec_line.recibir
                    config_ids = config_obj.search(cr, uid, [('rule_id','=',rubros[0])])
                    budget_id = ''
                    config_line_aux = False
                    if config_ids:
                        for config_line in config_ids:
                            config_aux = config_obj.browse(cr, uid, config_line)
                            if config_aux.budget_id.id == item_contrato.budget_post_id.id:
                                budget_id = item_contrato.id
                                config_line_aux = config_line
                                break
                        if not budget_id:
                            for config_line in config_ids:
                                conf_aux = config_obj.browse(cr, uid, config_line)#config_ids[0]
                                partida_name = conf_aux.budget_id.name
                                partida_name_upper = conf_aux.budget_id.name.upper()
                                item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('name','in',(partida_name,partida_name_upper)),
                                                                            ('aux_tipo','=',item_contrato.budget_post_id.code[0:1]),
                                                                            ('year_id','=',year_ids[0])],limit=1)
                                if item_ids:
                                    budget_id = item_ids[0]
                                    config_line_aux = config_line
                                    break
                                else:
                                    item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('code_aux','=',conf_aux.budget_id.code),
                                                                                    ('aux_tipo','=',item_contrato.budget_post_id.code[0:1]),
                                                                                    ('year_id','=',year_ids[0])],limit=1)
                                                                                    #          ('date_start','<=',this.date_end),('date_end','>=',this.date_end)],
                                    if item_ids:
                                        budget_id = item_ids[0]
                                        config_line_aux = config_line
                                        break
                                    else:
                                        #riobamba:
                                        aux_code_proyecto = item_contrato.code[10:] #me da el proyecto
                                        aux_code_ext = item_contrato.code[4:]#+aux_code_proyecto
                                        aux_code_ext2 = aux_code_ext[0:3]+'203'+aux_code_ext[6:]
                                        item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('code_aux','=',aux_code_ext2),
                                                                                    ('aux_tipo','=',item_contrato.budget_post_id.code[0:1]),
                                                                                    ('year_id','=',year_ids[0])],limit=1)
                                        if item_ids:
                                            budget_id = item_ids[0]
                                            config_line_aux = config_line
                                            break
                        if not budget_id:        
                            #raise osv.except_osv(('Error de configuracion !'),
                            #                     ("No existe partida %s del programa %s en el presupuesto del anio, para el rubro %s") % 
                            #                     (item_contrato.budget_post_id.code,item_contrato.program_id.sequence,'dec 3'))
                            project_ids = project_obj.search(cr, uid, [('program_id','=',programa_id)],limit=1)
                    else:
                        budget_id = contrato_budget_id
                programa = program_obj.browse(cr, uid, programa_id)
                aux_pr = programa.sequence + ' - ' + programa.name
                if budget_id:
                    detalle_id = detalle_obj.create(cr, uid, {
                        'dec_id':id_this,
                        'programa_id':programa_id,
                        'rubro_id':rubros[0],
                        'partida_id':budget_id,
                        'monto':monto,
                        'partner_id':1,
                    })
            self._create_move_dec(cr, uid, ids)
        return True

    def genera_dec3anterior(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.decimo.tercero.line')
        salary_rule_obj = self.pool.get('hr.salary.rule')
        detalle_obj = self.pool.get('run.programa.detalle')
        budget_item_obj=self.pool.get('budget.item')
        program_obj = self.pool.get('project.program')
        project_obj = self.pool.get('project.project')
        config_obj = self.pool.get('hr.account.configuration')
        programas = []
        rubros = []
        contratos = []
        detalle = []
        for this in self.browse(cr, uid, ids):
            #sacar diario de egreso
            id_this = this.id
            detalle_antes = detalle_obj.search(cr, uid, [('dec_id','=',id_this)])
            detalle_obj.unlink(cr, uid, detalle_antes)
            rubros = salary_rule_obj.search(cr, uid, [('code','in',('dec3','DEC3'))],limit=1)
            if not rubros:
                raise osv.except_osv('Error de configuracion', 'No existe regla salarias para decimo tercero definida')
            move_rol = this.move_id
            aux_name = this.name
            for line in this.line_ids:
                if not line.program_id.id in programas:
                    programas.append(line.program_id.id)
                if not line.contract_id.budget_id.id in contratos:
                    #aqui deberia tambien buscar entre fechas para colocar
                    item_idsc = budget_item_obj.search(cr, uid, [('budget_post_id','=',line.contract_id.budget_id.budget_post_id.id),
                                                                 ('date_start','<=',this.period_end.date_start),('date_end','>=',this.period_end.date_start),
                                                                 ('program_id','=',line.contract_id.program_id.id)],limit=1)
                    if not item_idsc:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("No existen planificacion de partida en el contrato para el anio en curso %s") % (this.date_start))
                    contratos.append(item_idsc[0])
#                    contratos.append(line.contract_id.budget_id.id)
            for programa_id in programas:
                for contrato_budget_id in contratos:
                    item_contrato = budget_item_obj.browse(cr, uid, contrato_budget_id)
                    dec_line_ids = line_obj.search(cr, uid, [('program_id','=',programa_id),
                                                             ('dec_id','=',this.id)])
                    if dec_line_ids:
                        monto = 0
                        for line_id in dec_line_ids:
                            dec_line = line_obj.browse(cr, uid, line_id)
                            monto += dec_line.total_dec
                    config_ids = config_obj.search(cr, uid, [('rule_id','=',rubros[0])])
                    if config_ids:
                        for config_line in config_ids:
                            config_aux = config_obj.browse(cr, uid, config_line)
                            if config_aux.budget_id.id == item_contrato.budget_post_id.id:
                                budget_id = item_contrato.id
                                break
                            else:
                                #es rubro que tiene su propia partida
                                conf_aux = config_obj.browse(cr, uid, config_ids[0])#config_ids[0]
                                partida_name = conf_aux.budget_id.name
                                item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('name','=',partida_name),
                                                                            ('date_start','<=',this.period_end.date_start),
                                                                            ('date_end','>=',this.period_end.date_start)],limit=1)
                                if item_ids:
                                    budget_id = item_ids[0]
                            project_ids = project_obj.search(cr, uid, [('program_id','=',programa_id)],limit=1)
                    else:
                        budget_id = contrato_budget_id
                programa = program_obj.browse(cr, uid, programa_id)
                aux_pr = programa.sequence + ' - ' + programa.name
                detalle_id = detalle_obj.create(cr, uid, {
                    'dec_id':id_this,
                    'programa_id':programa_id,
                    'rubro_id':rubros[0],
                    'partida_id':budget_id,
                    'monto':monto,
                })
            self._create_move_dec(cr, uid, ids)
        return True

    def autorizar_dec3(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{
            'state':'Autorizado'
        })
        return True

    def compute_dec3(self, cr, uid, ids, context=None):
        dict_aux = {0:'dic',1:'ene',2:'feb',3:'mar',4:'abr',5:'may',6:'jun',7:'jul',8:'ago',9:'sep',10:'oct',11:'nov',12:'dic'}
        dict_value = {}
        contract_obj = self.pool.get('hr.contract')
        payslip_obj = self.pool.get('hr.payslip')
        payslip_line_obj = self.pool.get('hr.payslip.line')
        rule_obj = self.pool.get('hr.salary.rule')
        period_obj = self.pool.get('hr.work.period.line')
        dec_line_obj = self.pool.get('hr.decimo.tercero.line')
        dict_value = {'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'01':0,'02':0}
        for this in self.browse(cr, uid, ids):
            rule_ids = rule_obj.search(cr, uid, [('code','in',('DEC3','dec3'))])
            if not rule_ids:
                print "no rules decimo"
            lines_antes_ids = dec_line_obj.search(cr, uid, [('dec_id','=',this.id)])
            if lines_antes_ids:
                dec_line_obj.unlink(cr, uid, lines_antes_ids)
            if not this.period_start.date_start<this.period_end.date_start:
                raise osv.except_osv(('Operación no permitida !'), ('El periodo final debe ser mayor al inicial'))
            period_ids = period_obj.search(cr, uid, [('date_start','>=',this.period_start.date_start),('date_stop','<=',this.period_end.date_stop)])
            print "PERIODDD", period_ids
            if period_ids:
                if len(period_ids)!=12:
                    raise osv.except_osv(('Error de usuario!'), ('El numero de periodos debe ser 12'))
                if this.activos:
                    contract_ids = contract_obj.search(cr, uid, [('subtype_id','=',this.contract_type.id),('activo','=',True),('decimo_opc','=','Acumular')])
                else:
                    contract_ids = contract_obj.search(cr, uid, [('subtype_id','=',this.contract_type.id),('activo','=',True),('decimo_opc','=','Acumular')])
#                    contract_ids = contract_obj.search(cr, uid, [('subtype_id','=',this.contract_type.id)])
#                contract_ids = contract_obj.search(cr, uid, [('subtype_id','=',this.contract_type.id),('date_start','>=',this.period_start.date_start)])
                if contract_ids:
                    for contract_id in contract_ids:
                        dict_value = {'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'01':0,'02':0}
                        dict_aux = {0:'dic',1:'ene',2:'feb',3:'mar',4:'abr',5:'may',6:'jun',7:'jul',8:'ago',9:'sep',10:'oct',11:'nov',12:'dic'}
                        contrato = contract_obj.browse(cr, uid, contract_id)
                        other_contract_ids = contract_obj.search(cr, uid, [('employee_id','=',contrato.employee_id.id)])
#                        other_contract_ids.append(contract_id)
                        payslip_ids = payslip_obj.search(cr, uid, [('contract_id','in',other_contract_ids),('period_id','in',period_ids)])
#                        payslip_ids = payslip_obj.search(cr, uid, [('contract_id','=',contract_id),('period_id','in',period_ids)])
                        aux_judicial = 0
                        if contrato.employee_id.judicial_ids:
                            for judicial_id in contrato.employee_id.judicial_ids:
                                aux_judicial += judicial_id.monto
                        wage = contrato.wage
                        j = 0 
                        if not payslip_ids:
                            continue
                        dec_line_id = dec_line_obj.create(cr, uid, {
                            'dec_id':this.id,
                            'contract_id':contract_id,
                        })
                        l = 0 
                        m = 0
                        for payslip_id in payslip_ids:
                            aux_monto = 0 
                            #busco si cobro decimo en rol
                            payslip = payslip_obj.browse(cr, uid, payslip_id)
                            payslip_line_ids = payslip_line_obj.search(cr, uid, [('contract_id','=',payslip.contract_id.id),('period_id','=',payslip.period_id.id),
                                                                                 ('salary_rule_id','in',rule_ids),('slip_id','in',payslip_ids)])
#                            payslip_line_ids = payslip_line_obj.search(cr, uid, [('contract_id','=',payslip.contract_id.id),
#                                                                                 ('salary_rule_id','in',rule_ids),('slip_id','=',payslip.id)])
                            if not payslip_line_ids:
                                aux_monto = payslip.basic + payslip.aportable #+ payslip.allowance
                            else:
                                #if contrato.struct_id.id==4 and payslip.date_from=='2017-03-01':
                                #    aux_monto = payslip.aportable
                                #break
                                print "cobro en rol decimo", payslip.number
                            if dict_value[payslip.period_id.name[0:2]]==0:
                                dict_value[payslip.period_id.name[0:2]]=aux_monto
                            else:
                                dict_value[payslip.period_id.name[0:2]]+=aux_monto
                            #dict_value[m]=aux_monto
                            m+=1
                            j += 1
                        dec_line_obj.write(cr, uid, dec_line_id,{
                            'mar':dict_value['03'],
                            'abr':dict_value['04'],
                            'may':dict_value['05'],
                            'jun':dict_value['06'],
                            'jul':dict_value['07'],
                            'ago':dict_value['08'],
                            'sep':dict_value['09'],
                            'oct':dict_value['10'],
                            'nov':dict_value['11'],
                            'dic':dict_value['12'],
                            'ene':dict_value['01'],
                            'feb':dict_value['02'],
                            'descuento_judicial':aux_judicial,
                            'fecha_contrato':contrato.date_start,
                        })
            aux_str = "PAGO DECIMO TERCERO " + this.contract_type.name + 'DE: ' + this.period_start.name + ' A: ' + this.period_end.name
            self.write(cr, uid, ids, {
                'name':aux_str,
            })
        return True

    def _total_decimo(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = {0.0}
            aux_total = 0
            for line in this.line_ids:
                aux_total += line.recibir
        res[this.id] = aux_total
        return res

    def pagado_dec3(self, cr, uid, id, context=None):
        self.write(cr, uid, id, {'state':'Pagado'})
        return True


    def create(self, cr, uid, values, context=None):
        values['creado_por'] = uid 
        values['fecha_creacion'] = time.strftime('%Y-%m-%d')
        return super(hrDecimoTercero, self).create(cr, uid, values, context=context) 

    _columns = dict(
        fecha_creacion = fields.date('Fecha Creacion'),
        creado_por = fields.many2one('res.users','Creado Por'),
        activos = fields.boolean('Solo Contratos Activos'),
        fy_id = fields.many2one('hr.work.period','Anio Fiscal'),
        total = fields.function(_total_decimo,type="float", store=True,string='TOTAL DECIMO'),
        certificate_id = fields.many2one('budget.certificate','Certificado'),
        detalle_ids = fields.one2many('run.programa.detalle','dec_id','Detalle'),
        name = fields.char('Descripcion',size=256),
        contract_type = fields.many2one('hr.contract.type.type','Tipo Contrato'),
        period_start = fields.many2one('hr.work.period.line','Desde'),
        move_id = fields.many2one('account.move','Comprobante Contable'),
        period_end = fields.many2one('hr.work.period.line','Hasta'),
        state = fields.selection([('Borrador','Borrador'),('Aprobado','Aprobado'),('Autorizado','Autorizado'),('Pagado','Pagado')],'Estado'),
        line_ids = fields.one2many('hr.decimo.tercero.line','dec_id','Detalle'),
        )
    _defaults = dict(
        state = 'Borrador',
        activos = True,
        )
hrDecimoTercero()
class runProgramaDetalle(osv.Model):
    _inherit = 'run.programa.detalle'
    _columns = dict(
        dec_id = fields.many2one('hr.decimo.tercero','Decimo Tercero'),
        dec4_id = fields.many2one('hr.decimo.cuarto','Decimo Cuarto'),
    )
runProgramaDetalle()
class hrDecimoCuartoLine(osv.Model):
    _name = 'hr.decimo.cuarto.line'
    _order = 'complete_name asc,code_partida desc'

    def _amount_decimo(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            aux_decimo = line.dec_id.basico
            res[line.id] = {
                'total': 0.0,
                'recibir': 0.0,
                }
            aux_suma = line.dic + line.ene + line.feb + line.mar + line.abr + line.may + line.jun + line.jul + line.ago + line.sep + line.oct + line.nov
            aux_net = aux_suma/12
            #si es 360 else el proporcional
            aux_net_dias = (aux_net * line.dias_lab)/360
            res[line.id]['total'] = aux_suma  
            aux_decimo = (line.dias_lab*aux_decimo)/(360.00)
            res[line.id]['total_decimo'] = aux_decimo
            res[line.id]['recibir']  = line.ajuste + aux_decimo - line.descuento_judicial  #ya se considera si acumula o cobra
#            if line.acumula:
#                res[line.id]['recibir']  = aux_decimo - line.descuento_judicial
#            else:
#                res[line.id]['recibir']  = 0
        return res

    _columns = dict(
        ajuste = fields.float('valor Ajuste'),
        acumula = fields.boolean('Acum.'),
        complete_name = fields.related('employee_id','complete_name',type='char',size=128,store=True),
        fy_id = fields.related('dec_id','fy_id',type='many2one',relation='hr.work.period',store=True),
        code_partida = fields.related('budget_id','code',type='char',size=32,store=True),
        budget_id = fields.many2one('budget.item','Partida'),
        budget_contrato_id = fields.related('contract_id', 'budget_id', type='many2one', relation='budget.item', string='Partida', store=True),
        program_id = fields.related('contract_id', 'program_id', type="many2one", 
                                    relation='project.program', string="Programa", store=True),
        employee_id = fields.many2one('hr.employee','Empleado'),
#        employee_id = fields.related('contract_id', 'employee_id', type="many2one", 
#                                     relation='hr.employee', string="Empleado", store=True),
        dec_id = fields.many2one('hr.decimo.cuarto','Decimo'),
        contract_id = fields.many2one('hr.contract','Empleado'),
        mar = fields.float('Mar/Ago'),
        abr = fields.float('Abr/Sep'),
        may = fields.float('May/Oct'),
        jun = fields.float('Jun/Nov'),
        jul = fields.float('Jul/Dic'),
        ago = fields.float('Ago/Ene'),
        sep = fields.float('Sep/Feb'),
        oct = fields.float('Oct/Mar'),
        nov = fields.float('Nov/Abr'),
        dic = fields.float('Dic/May'),
        ene = fields.float('Ene/Jun'),
        feb = fields.float('Feb/Jul'),
        dias_lab = fields.integer('Dias Laborados'),
        descuento_judicial = fields.float('Descuento Judicial'),
        total = fields.function(_amount_decimo, multi="dec",type="float", store=True,string='TOTAL'),        
        total_decimo = fields.function(_amount_decimo, multi="dec",type="float", store=True,string='TOTAL DECIMO'),
        recibir = fields.function(_amount_decimo, multi="dec",type="float", store=True,string='RECIBIR'),
        fecha_contrato = fields.date('Fecha Contrato'),
        cedula = fields.char('Cedula',size=13),
        
    )
hrDecimoCuartoLine()


class hrDecimoCuarto(osv.Model):
    _name = 'hr.decimo.cuarto'
    _order = 'date_stop desc,state asc'

    def load_wizard_xls(self, cr, uid, ids, context=None):
        return {
        'type': 'ir.actions.act_window',
        'name': 'Importar XLS Décimo Cuarto',
        'view_mode': 'form',
        'view_id': False,
        'view_type': 'form',
        'res_model': 'import.sheet.d4',
        'nodestroy': True,
        'target': 'new',
        'context': context,
        }    

    def colocarPartidaD4(self, cr, uid, ids, context):
        year_obj = self.pool.get('account.fiscalyear')
        post_obj = self.pool.get('budget.post')
        item_obj = self.pool.get('budget.item')
        dec4_line_obj = self.pool.get('hr.decimo.cuarto.line')
        for this in self.browse(cr, uid, ids):
            year_ids = year_obj.search(cr, uid, [('date_start','<=',this.date_stop),('date_stop','>=',this.date_stop)],limit=1)
            if year_ids:
                year = year_obj.browse(cr, uid, year_ids[0])
            else:
                raise osv.except_osv('Error de configuracion', 'No hay anio fiscal para la fecha de compromiso.')
            for line in this.line_ids:
                aux_partida_6 = line.contract_id.budget_id.budget_post_id.code[0:3]+'204'
                if this.contract_type.name=='JUBILADO':
                    aux_partida = line.contract_id.budget_id.budget_post_id.code
                else:
                    aux_partida = line.contract_id.budget_id.budget_post_id.code[0:3]+'204'+line.contract_id.budget_id.budget_post_id.code[6:]
                post_ids = post_obj.search(cr, uid, [('code','ilike','%'+aux_partida)])
                if not post_ids:
                    post_ids = post_obj.search(cr, uid, [('code','ilike','%'+aux_partida_6)])
                    if post_ids:
                        item_ids = item_obj.search(cr, uid, [('budget_post_id','in',post_ids),
                                                             ('program_id','=',line.contract_id.program_id.id),('year_id','=',year_ids[0])])
                        if item_ids:
                            dec4_line_obj.write(cr, uid, line.id,{'budget_id':item_ids[0]})
                else:
                    item_ids = item_obj.search(cr, uid, [('budget_post_id','in',post_ids),
                                                         ('program_id','=',line.contract_id.program_id.id),('year_id','=',year_ids[0])])
                    if item_ids:
                        dec4_line_obj.write(cr, uid, line.id,{'budget_id':item_ids[0]})
                    else:
                        post_ids = post_obj.search(cr, uid, [('code','ilike','%'+aux_partida_6)])
                        if post_ids:
                            item_ids = item_obj.search(cr, uid, [('budget_post_id','in',post_ids),
                                                                 ('program_id','=',line.contract_id.program_id.id),('year_id','=',year_ids[0])])
                            if item_ids:
                                dec4_line_obj.write(cr, uid, line.id,{'budget_id':item_ids[0]})
        return True

    def regresa_dec4(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{
            'state':'Borrador'
        })
        return True

    def genera_ret_dec4(self, cr, uid, ids, context=None):
        pago_obj = self.pool.get('hr.varios')
        pago_line_obj = self.pool.get('hr.varios.line')
        contract_obj = self.pool.get('hr.contract')
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            aux_desc = 'PAGO RETENCIONES JUDICIALES: ' + this.name
            aux_desc1 = 'PAGO RETENCIONES JUDICIALES SUPA: ' + this.name
            period_ids = period_obj.find(cr, uid, this.period_end.date_stop)
            pago_id = pago_obj.create(cr, uid, {
                'name':aux_desc[0:63],
                'period_id':period_ids[0],
            })
            pago_id_2 = pago_obj.create(cr, uid, {
                'name':aux_desc1[0:63],
                'period_id':period_ids[0],
            })
            m = k = 0
            for line in this.line_ids:
                total_decimo = line.total_decimo
                total_decimo_origen = line.total_decimo
                total_otras = 0
                if line.descuento_judicial>0:
                    aux_sum_line_ret = 0
                    for line_benef in line.contract_id.employee_id.judicial_ids:
                        aux_sum_line_ret += line_benef.monto 
                    for line_benef in line.contract_id.employee_id.judicial_ids:
                        if line_benef.monto>0:
                            if total_decimo>0:
                                if line_benef.monto<=total_decimo:
                                    aux_monto = line_benef.monto#(line_benef.monto * line.descuento_judicial) / aux_sum_line_ret
                                    total_decimo = total_decimo - line_benef.monto
                                    total_otras += line_benef.monto		
                                else:
                                    aux_monto = abs(total_decimo_origen - total_otras)
                                    total_decimo = 0			 
                            #aux_monto =  (line_benef.monto * line.descuento_judicial) / aux_sum_line_ret
                            if line_benef.is_supa:
                                m += 1
                                line_id = pago_line_obj.create(cr, uid, {
                                    'name':line_benef.partner_id.id,
                                    'varios_id':pago_id_2,
                                    'monto':aux_monto,
                                    'valor':aux_monto,
                                    'descontado_id':line.contract_id.employee_id.id,
                                })
                            else:
                                k += 1
                                line_id = pago_line_obj.create(cr, uid, {
                                    'name':line_benef.partner_id.id,
                                    'varios_id':pago_id,
                                    'monto':aux_monto,
                                    'valor':aux_monto,
                                    'descontado_id':line.contract_id.employee_id.id,
                                })
            if m==0:
                pago_obj.unlink(cr, uid, [pago_id_2])
            if k==0:
                pago_obj.unlink(cr, uid, [pago_id])
        return True

    def _create_move_dec(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        user_obj = self.pool.get('res.users')
        project_obj = self.pool.get('project.project')
        certificate_obj = self.pool.get('budget.certificate')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        for this in self.browse(cr, uid, ids):
            #sacar diario de egreso
            id_this = this.id
            journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
            usuario = user_obj.browse(cr, uid, uid)
            project_ids = project_obj.search(cr, uid, [])
            if this.certificate_id:
                cr.execute("delete from budget_certificate_line where certificate_id=%s"%(this.certificate_id.id))
                cp_id = this.certificate_id.id
            else:
                notes_aux = 'CERTIFICACION PRESUPUESTARIA : ' + this.name
                cp_id = certificate_obj.create(cr, uid, {
                    'department_id':usuario.context_department_id.id,
                    'solicitant_id':usuario.employee_id.id,
                    'project_id':project_ids[0],
                    'partner_id':1,
                    'notes':notes_aux,
                    'date':time.strftime('%Y-%m-%d'),
                    'date_commited':time.strftime('%Y-%m-%d'),                    
                    'date_confirmed':time.strftime('%Y-%m-%d'),
                })
            if this.move_id:
                if this.move_id.state=='draft' and this.move_id.name=='/':
                    cr.execute("delete from account_move_line where move_id=%s"%(this.move_id.id))
                    move_obj.unlink(cr, uid, [this.move_id.id],aux=1)
                    move_id = move_obj.create(cr, uid, {
                        'ref': this.name,
                        'narration':this.name,
                        'journal_id': journal_ids[0],
                        'date': this.date_stop,
                        'state':'draft',
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
                    'ref': this.name,
                    'narration':this.name,
                    'journal_id': journal_ids[0],
                    'date': this.date_stop,
                    'state':'draft',
                    'afectacion':True,
                    'partner_id':1,
                    'certificate_id':cp_id,
                    'type':'Nomina',
                    'validar_cp':True,
                })            
            for line in this.detalle_ids:
                line_id = certificate_line_obj.create(cr, uid, {
                    'certificate_id':cp_id,
                    'project_id':line.partida_id.project_id.id,
                    'task_id':line.partida_id.project_id.tasks[0].id,
                    'budget_id':line.partida_id.id,
                    'amount':line.monto,
                    'amount_certified':line.monto,
                    'amount_commited':line.monto,
                })
                linea_aux_rol = certificate_line_obj.browse(cr, uid, line_id)
                account_ids = account_obj.search(cr, uid, [('budget_id','=',line.partida_id.budget_post_id.id)])
                if not account_ids:
                    account_ids = account_obj.search(cr, uid, [('budget_id.code','=',line.partida_id.budget_post_id.code[0:6])])
                    if not account_ids:
                        aux_msg_1 = line.partida_id.budget_post_id.code + ' - ' + line.partida_id.budget_post_id.name
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("No esta relacionada la partida '%s' a cuenta contable") % (aux_msg_1))
                if len(account_ids)>1:
                    for acc_id in account_ids:
                        account_aux = account_obj.browse(cr, uid, acc_id)
                        if account_aux.account_rec_id.id:
                            account = account_obj.browse(cr, uid, acc_id)
                        elif account_aux.account_pay_id:
                            account = account_obj.browse(cr, uid, acc_id)
                else:
                    if not account_ids:
                        aux_msg_1 = line.partida_id.budget_post_id.code + ' - ' + line.partida_id.budget_post_id.name
                        raise osv.except_osv(('Error de Configuracion !'),
                                             ("No esta relacionada la partida '%s' a cuenta contable") % (aux_msg_1))
                    account = account_obj.browse(cr, uid, account_ids[0])
                if not account:
                    aux_msg_1 = line.partida_id.budget_post_id.code + ' - ' + line.partida_id.budget_post_id.name
                    raise osv.except_osv(('Error de Configuracion !'),
                                         ("No esta relacionada la partida '%s' a cuenta contable") % (aux_msg_1))
                    print "RAISE DE BO  HAY CONFIGURADOIN DE LA CUENTA"
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'account_id':account.id,
                    'debit':line.monto,
                    'budget_id_cert':line_id,
                    'budget_accrued':True,
                    'name':'ingreso',
                    'partner_id':line.partner_id.id,
                })
                if account.account_rec_id:
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':account.account_rec_id.id,
                        'credit':line.monto,
                        'name':'ingreso',
                        'budget_id_cert':line_id,
                        'partner_id':line.partner_id.id,
                    })
                elif account.account_pay_id:
                    move_line_obj.create(cr, uid, {
                        'move_id':move_id,
                        'account_id':account.account_pay_id.id,
                        'credit':line.monto,
                        'name':'ingreso',
                        'budget_id_cert':line_id,
                        'partner_id':line.partner_id.id,
                    })
                else:
                    aux_msg_1 = account.code + ' - ' + account.name
                    raise osv.except_osv(('Error de Configuracion !'),
                                         ("La cuenta '%s' no tiene parametrizado la cuenta de pago") % (aux_msg_1))
        self.write(cr, uid, this.id,{
            'move_id':move_id,
            'certificate_id':cp_id,
        })
        return True

    def genera_dec4(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.decimo.cuarto.line')
        salary_rule_obj = self.pool.get('hr.salary.rule')
        detalle_obj = self.pool.get('run.programa.detalle')
        budget_item_obj=self.pool.get('budget.item')
        program_obj = self.pool.get('project.program')
        project_obj = self.pool.get('project.project')
        partner_obj = self.pool.get('res.partner')
        config_obj = self.pool.get('hr.account.configuration')
        year_obj = self.pool.get('account.fiscalyear')
        post_obj = self.pool.get('budget.post')
        programas = []
        rubros = []
        contratos = []
        detalle = []
        for this in self.browse(cr, uid, ids):
            year_ids = year_obj.search(cr, uid, [('date_start','<=',this.date_stop),('date_stop','>=',this.date_stop)],limit=1)
            if year_ids:
                year = year_obj.browse(cr, uid, year_ids[0])
            else:
                raise osv.except_osv('Error de configuracion', 'No hay anio fiscal para la fecha de compromiso.')
            #sacar diario de egreso
            id_this = this.id
            detalle_antes = detalle_obj.search(cr, uid, [('dec4_id','=',id_this)])
            detalle_obj.unlink(cr, uid, detalle_antes)
            rubros = salary_rule_obj.search(cr, uid, [('code','in',('dec4','DEC4'))],limit=1)
            if not rubros:
                raise osv.except_osv('Error de configuracion', 'No existe regla salarias para decimo cuarto definida')
            move_rol = this.move_id
            aux_name = this.name
            partidas = {}
            for line in this.line_ids:
                if line.budget_id:
                    if line.acumula:
                        r = True
                        if r:#line.budget_id.budget_post_id.code[3:6]=='204':
                            if line.budget_id.id in partidas:
                                partidas[line.budget_id.id]+=line.total_decimo
                            else:
                                partidas[line.budget_id.id]=line.total_decimo
                        else:
                            aux_name = line.contract_id.employee_id.complete_name
                            raise osv.except_osv(('Error de usuario !'),
                                                 ("Esta usando una partida diferente a decimo cuarto en %s") % (aux_name))
                else:
                    raise osv.except_osv('Error de usuario', 'Verifique que todas las lineas tengan colocada la partida presupuestaria')
            for partida in partidas:
                item = budget_item_obj.browse(cr, uid, partida)
                if partidas[partida]>0:
                    detalle_id = detalle_obj.create(cr, uid, {
                        'dec4_id':id_this,
                        'programa_id':item.program_id.id,
                        'rubro_id':rubros[0],
                        'partida_id':item.id,
                        'monto':partidas[partida],
                        'partner_id':1,
                    })
            self._create_move_dec(cr, uid, ids)
        return True

    def genera_dec4V2(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('hr.decimo.cuarto.line')
        salary_rule_obj = self.pool.get('hr.salary.rule')
        detalle_obj = self.pool.get('run.programa.detalle')
        budget_item_obj=self.pool.get('budget.item')
        program_obj = self.pool.get('project.program')
        project_obj = self.pool.get('project.project')
        partner_obj = self.pool.get('res.partner')
        config_obj = self.pool.get('hr.account.configuration')
        programas = []
        rubros = []
        contratos = []
        detalle = []
        for this in self.browse(cr, uid, ids):
            #sacar diario de egreso
            id_this = this.id
            detalle_antes = detalle_obj.search(cr, uid, [('dec4_id','=',id_this)])
            detalle_obj.unlink(cr, uid, detalle_antes)
            rubros = salary_rule_obj.search(cr, uid, [('code','in',('dec4','DEC4'))],limit=1)
            if not rubros:
                raise osv.except_osv('Error de configuracion', 'No existe regla salarias para decimo cuarto definida')
            move_rol = this.move_id
            aux_name = this.name
            for line in this.line_ids:
                if line.descuento_judicial:
                    #aqui va la misma partida de decimo
                    item_ids_desc = budget_item_obj.search(cr, uid, [('budget_post_id','=',line.contract_id.budget_id.budget_post_id.id),
                                                                 ('date_start','<=',this.period_end.date_start),('date_end','>=',this.period_end.date_start),
                                                                 ('program_id','=',line.contract_id.program_id.id)],limit=1)
                    if not item_ids_desc:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("No existen planificacion de partida en el contrato para el anio en curso %s") % (this.date_start))
                    partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',line.contract_id.employee_id.name)])
                    if not partner_ids:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("El funcionario %s descontado no tiene proveedor creado %s") % (line.contract_id.employee_id.complete_name))
                    config_ids = config_obj.search(cr, uid, [('rule_id','=',rubros[0])])
                    item_contrato = budget_item_obj.browse(cr, uid, item_ids_desc[0])
                    programa_id = line.contract_id.program_id.id
                    if config_ids:
                        for config_line in config_ids:
                            config_aux = config_obj.browse(cr, uid, config_line)
                            if config_aux.budget_id.id == item_contrato.budget_post_id.id:
                                budget_id = item_contrato.id
                                break
                            else:
                                #es rubro que tiene su propia partida
                                conf_aux = config_obj.browse(cr, uid, config_ids[0])#config_ids[0]
                                partida_name = conf_aux.budget_id.name
                                item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('name','=',partida_name),
                                                                            ('date_start','<=',this.period_end.date_start),
                                                                            ('date_end','>=',this.period_end.date_start)],limit=1)
                                if item_ids:
                                    budget_id = item_ids[0]
                            project_ids = project_obj.search(cr, uid, [('program_id','=',programa_id)],limit=1)
                    else:
                        budget_id = contrato_budget_id
                    detalle_id = detalle_obj.create(cr, uid, {
                        'dec4_id':id_this,
                        'programa_id':line.contract_id.program_id.id,
                        'rubro_id':rubros[0],
                        'partida_id':budget_id,#item_ids_desc[0],
                        'monto':line.descuento_judicial,
                        'partner_id':partner_ids[0],
                    })
                if not line.program_id.id in programas:
                    programas.append(line.program_id.id)
                if not line.contract_id.budget_id.id in contratos:
                    #aqui deberia tambien buscar entre fechas para colocar
                    item_idsc = budget_item_obj.search(cr, uid, [('budget_post_id','=',line.contract_id.budget_id.budget_post_id.id),
                                                                 ('date_start','<=',this.period_end.date_start),('date_end','>=',this.period_end.date_start),
                                                                 ('program_id','=',line.contract_id.program_id.id)],limit=1)
                    if not item_idsc:
                        raise osv.except_osv(('Error de configuracion !'),
                                             ("No existen planificacion de partida en el contrato para el anio en curso %s") % (this.date_start))
                    contratos.append(item_idsc[0])
#                    contratos.append(line.contract_id.budget_id.id)
            for programa_id in programas:
                for contrato_budget_id in contratos:
                    item_contrato = budget_item_obj.browse(cr, uid, contrato_budget_id)
                    dec_line_ids = line_obj.search(cr, uid, [('program_id','=',programa_id),
                                                             ('dec_id','=',this.id)])
                    if dec_line_ids:
                        monto = 0
                        for line_id in dec_line_ids:
                            dec_line = line_obj.browse(cr, uid, line_id)
                            monto += dec_line.recibir
                    config_ids = config_obj.search(cr, uid, [('rule_id','=',rubros[0])])
                    if config_ids:
                        for config_line in config_ids:
                            config_aux = config_obj.browse(cr, uid, config_line)
                            if config_aux.budget_id.id == item_contrato.budget_post_id.id:
                                budget_id = item_contrato.id
                                break
                            else:
                                #es rubro que tiene su propia partida
                                conf_aux = config_obj.browse(cr, uid, config_ids[0])#config_ids[0]
                                partida_name = conf_aux.budget_id.name
                                item_ids = budget_item_obj.search(cr, uid, [('program_id','=',programa_id),('name','=',partida_name),
                                                                            ('date_start','<=',this.period_end.date_start),
                                                                            ('date_end','>=',this.period_end.date_start)],limit=1)
                                if item_ids:
                                    budget_id = item_ids[0]
                            project_ids = project_obj.search(cr, uid, [('program_id','=',programa_id)],limit=1)
                    else:
                        budget_id = contrato_budget_id
                programa = program_obj.browse(cr, uid, programa_id)
                aux_pr = programa.sequence + ' - ' + programa.name
                detalle_id = detalle_obj.create(cr, uid, {
                    'dec4_id':id_this,
                    'programa_id':programa_id,
                    'rubro_id':rubros[0],
                    'partida_id':budget_id,
                    'monto':monto,
                    'partner_id':1,
                })
            self._create_move_dec(cr, uid, ids)
        return True
    
    def autorizar_dec4(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{
            'state':'Autorizado'
        })
        return True

    def aprobar_dec4(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{
            'state':'Aprobado'
        })
        return True

    def _total_decimo(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = {0.0}
            aux_total = 0
            for line in this.line_ids:
                aux_total += line.recibir
        res[this.id] = aux_total
        return res

    def compute_dec4(self, cr, uid, ids, context=None):
        #dict_aux = {0:'mar',1:'abr',2:'may',3:'jun',4:'jul',5:'ago',6:'sep',7:'oct',8:'nov',9:'dic',10:'ene',11:'feb'}
        dict_value = {}
        contract_obj = self.pool.get('hr.contract')
        payslip_obj = self.pool.get('hr.payslip')
        period_obj = self.pool.get('hr.work.period.line')
        payslip_line_obj = self.pool.get('hr.payslip.line')
        dec_line_obj = self.pool.get('hr.decimo.cuarto.line')
        dec_obj = self.pool.get('hr.decimo.cuarto')
        rule_obj = self.pool.get('hr.salary.rule')
        permiso_obj = self.pool.get('permiso.hora')
        parameter_obj = self.pool.get('ir.config_parameter')
        val_ids = parameter_obj.search(cr, uid, [('key','=','upto')],limit=1)
        band_val = False
        if val_ids:
            val = parameter_obj.browse(cr, uid, val_ids[0]).value
            band_val = True
        regimen = 'costa'
        regimen_ids = parameter_obj.search(cr, uid, [('key','=','regimen')],limit=1)
        if regimen_ids:
            regimen = parameter_obj.browse(cr, uid, regimen_ids[0]).value
        if regimen=='costa':
            dict_aux = {'03':'mar','04':'abr','05':'may','06':'jun','07':'jul','08':'ago','09':'sep','10':'oct','11':'nov','12':'dic','01':'ene','02':'feb'}
            dict_value = {'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'01':0,'02':0}
        else:
            dict_aux = {'03':'mar','04':'abr','05':'may','06':'jun','07':'jul','08':'ago','09':'sep','10':'oct','11':'nov','12':'dic','01':'ene','02':'feb'}
            dict_value = {'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'01':0,'02':0}
        for this in self.browse(cr, uid, ids):
            dec_ot_ids = dec_obj.search(cr, uid, [('id','!=',this.id)])
            if dec_ot_ids:
                for dec_ot_id in dec_ot_ids:
                    dec_ot = dec_obj.browse(cr, uid, dec_ot_id)
                    if not dec_ot.date_start or not dec_ot.date_stop:
                        dec_obj.write(cr, uid, dec_ot_id,{'date_start':dec_ot.period_start.date_start,'date_stop':dec_ot.period_end.date_stop})
            if this.basico<=0:
                raise osv.except_osv(('Error de usuario !'), ('El campo salario basico debe ser mayor a cero'))
            rule_ids = rule_obj.search(cr, uid, [('code','in',('DEC4','dec4'))])
            if not rule_ids:
                print "no rules decimo"
            lines_antes_ids = dec_line_obj.search(cr, uid, [('dec_id','=',this.id)])
            if lines_antes_ids:
                dec_line_obj.unlink(cr, uid, lines_antes_ids)
            if not this.date_start<this.date_stop:
                raise osv.except_osv(('Operación no permitida !'), ('El periodo final debe ser mayor al inicial'))
            period_ids = period_obj.search(cr, uid, [('date_start','>=',this.date_start),('date_stop','<=',this.date_stop)])
#            period_ids = period_obj.search(cr, uid, [('date_start','>=',this.period_start.date_start),('date_stop','<=',this.period_end.date_stop)])
            #sacar el basico
            wage = this.basico
            if period_ids:
                contract_ids = contract_obj.search(cr, uid, [('subtype_id','=',this.contract_type.id),('activo','=',True)])
                if contract_ids:
                    for contract_id in contract_ids:
                        aux_dias = laborado_actual = laborado_antes = dias_trabajados = 0
                        dict_aux = {'03':'mar','04':'abr','05':'may','06':'jun','07':'jul','08':'ago','09':'sep','10':'oct','11':'nov','12':'dic','01':'ene','02':'feb'}
                        dict_value = {'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'01':0,'02':0}
                        contrato = contract_obj.browse(cr, uid, contract_id)
                        if band_val and this.date_stop<=val:
                            payslip_ids = payslip_obj.search(cr, uid, [('employee_id','=',contrato.employee_id.id),('period_id','in',period_ids)])
                        else:
                            payslip_ids = payslip_obj.search(cr, uid, [('contract_id','=',contract_id),('period_id','in',period_ids)])
                        if contrato.date_start<=this.period_start.date_start and not contrato.date_end:
                            laborado_actual = 360
                        else:
                            inicio = contrato.date_start.split('-')
                            fin = this.date_stop.split('-')
                            dateinicio = date( int(inicio[0]), int(inicio[1]), int(inicio[2]) )
                            datefin = date( int(fin[0]), int(fin[1]), int(fin[2]) )
                            delta = datefin - dateinicio
                            laborado_actual = abs(delta.days)
                        contract_prev_ids = contract_obj.search(cr, uid, [('employee_id','=',contrato.employee_id.id),
                                                                          ('id','!=',contract_id),('date_end','<=',this.date_stop),
                                                                          ('date_end','>=',this.date_start),
                                                                          ],order='date_start asc')
                        if contract_prev_ids:
                            for contract_prev_id in contract_prev_ids:
                                contrato_previo = contract_obj.browse(cr, uid, contract_prev_id)
                                inicio = contrato_previo.date_end.split('-')
                                fin = this.date_start.split('-')
                                dateinicio = date( int(inicio[0]), int(inicio[1]), int(inicio[2]) )
                                datefin = date( int(fin[0]), int(fin[1]), int(fin[2]) )
                                delta = datefin - dateinicio
                                laborado_antes += abs(delta.days)
                        #considero permisos licencia sin sueldo
                        permiso_ids = permiso_obj.search(cr, uid, [('tipo','=','Dias'),('tipo2','=','LICENCIASIN'),
                                                                   ('date','>=',this.date_start),('date_end','<=',this.date_stop)])
                        dias_permiso = 0
                        if permiso_ids:
                            for permiso_id in permiso_ids:
                                permiso = permiso_obj.browse(cr, uid, permiso_id)
                                dias_permiso += permiso.total_dias
                        aux_dias = laborado_actual + laborado_antes
                        if aux_dias>360:
                            aux_dias = 360
                        aux_dias = aux_dias - dias_permiso
                        aux_monto_total = aux_judicial = total_cobrar = 0
                        if contrato.employee_id.judicial_ids:
                            for judicial_id in contrato.employee_id.judicial_ids:
                                aux_judicial += judicial_id.monto
                        j = 0 
                        if not payslip_ids:
                            continue
                        aux_acumula = False
                        aux_ajuste = this.ajuste_decimo
                        if contrato.decimo_opc in ('Acumular','Decimo 3'):
                            aux_acumula = True
                            aux_ajuste = 0
                        dec_line_id = dec_line_obj.create(cr, uid, {
                            'dec_id':this.id,
                            'contract_id':contract_id,
                            'employee_id':contrato.employee_id.id,
                            'cedula':contrato.employee_id.name,
                            'acumula':aux_acumula,
                            'ajuste':aux_ajuste,
                        })
                        l = 0 
                        m = 0
                        for period_id in period_ids:
                            periodo = period_obj.browse(cr, uid, period_id)
                        #for payslip_id in payslip_ids:
                            aux_monto = 0
                            #payslip = payslip_obj.browse(cr, uid, payslip_id)
                            if band_val and this.date_stop<=val:
                                payslip_ids2 = payslip_obj.search(cr, uid, [('employee_id','=',contrato.employee_id.id),('period_id','=',period_id)])
                            else:
                                payslip_ids2 = payslip_obj.search(cr, uid, [('contract_id','=',contract_id),('period_id','=',period_id)])
                            if not payslip_ids2:
                                aux_monto = 0#wage
                            else:
                                if band_val and this.date_stop<=val:
                                    payslip_line_ids = payslip_line_obj.search(cr, uid, [('employee_id','=',contrato.employee_id.id),('period_id','=',period_id),
                                                                                         ('salary_rule_id','in',rule_ids),('slip_id','in',payslip_ids)])
                                else:
                                    payslip_line_ids = payslip_line_obj.search(cr, uid, [('contract_id','=',contract_id),('period_id','=',period_id),
                                                                                         ('salary_rule_id','in',rule_ids),('slip_id','in',payslip_ids)])
                                if not payslip_line_ids:
                                    #aux_monto = wage
                                    #sumo los dias del rol
                                    payslip_dia = payslip_obj.browse(cr, uid, payslip_ids2[0])
                                    if payslip_dia.worked_days_line_ids:
                                        dias_trabajados1 = payslip_dia.worked_days_line_ids[0].number_of_days
                                    else:
                                        dias_trabajados1 = 30
                                    dias_trabajados += dias_trabajados1
                                    aux_monto = (dias_trabajados1 * wage)/30
                            total_cobrar += aux_monto
                            dict_value[periodo.name[0:2]]=aux_monto
                            m+=1
                            j += 1
                            aux_monto_total += aux_monto
#                        import pdb
#                        pdb.set_trace()
                        aux_total_proporcional = (aux_monto_total*dias_trabajados)/(360*12)
                        #proporcional dias
                        if aux_total_proporcional<aux_judicial:
                            aux_judicial = aux_total_proporcional
                        dec_line_obj.write(cr, uid, dec_line_id,{
                            'mar':dict_value['03'],
                            'abr':dict_value['04'],
                            'may':dict_value['05'],
                            'jun':dict_value['06'],
                            'jul':dict_value['07'],
                            'ago':dict_value['08'],
                            'sep':dict_value['09'],
                            'oct':dict_value['10'],
                            'nov':dict_value['11'],
                            'dic':dict_value['12'],
                            'ene':dict_value['01'],
                            'feb':dict_value['02'],
                            'dias_lab':dias_trabajados,#aux_dias,
                            'descuento_judicial':aux_judicial,
                            'fecha_contrato':contrato.date_start,
                        })
                else:
                    raise osv.except_osv(('Error de usuario !'), ('No existen contratos activos'))
            else:
                raise osv.except_osv(('Error de usuario !'), ('No existen periodos entre las fechas seleccionadas'))
            aux_str = "PAGO DECIMO CUARTO " + this.contract_type.name + 'DE: ' + this.date_start + ' A: ' + this.date_stop
            self.write(cr, uid, ids, {
                'name':aux_str,
            })
        return True

    def compute_dec4V2(self, cr, uid, ids, context=None):
        #dict_aux = {0:'mar',1:'abr',2:'may',3:'jun',4:'jul',5:'ago',6:'sep',7:'oct',8:'nov',9:'dic',10:'ene',11:'feb'}
        dict_value = {}
        contract_obj = self.pool.get('hr.contract')
        payslip_obj = self.pool.get('hr.payslip')
        period_obj = self.pool.get('hr.work.period.line')
        payslip_line_obj = self.pool.get('hr.payslip.line')
        dec_line_obj = self.pool.get('hr.decimo.cuarto.line')
        rule_obj = self.pool.get('hr.salary.rule')
        permiso_obj = self.pool.get('permiso.hora')
        parameter_obj = self.pool.get('ir.config_parameter')
        regimen = 'costa'
        regimen_ids = parameter_obj.search(cr, uid, [('key','=','regimen')],limit=1)
        if regimen_ids:
            regimen = parameter_obj.browse(cr, uid, regimen_ids[0]).value
        if regimen=='costa':
            dict_aux = {'03':'mar','04':'abr','05':'may','06':'jun','07':'jul','08':'ago','09':'sep','10':'oct','11':'nov','12':'dic','01':'ene','02':'feb'}
            dict_value = {'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'01':0,'02':0}
        else:
            dict_aux = {'03':'mar','04':'abr','05':'may','06':'jun','07':'jul','08':'ago','09':'sep','10':'oct','11':'nov','12':'dic','01':'ene','02':'feb'}
            dict_value = {'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'01':0,'02':0}
        for this in self.browse(cr, uid, ids):
            if this.basico<=0:
                raise osv.except_osv(('Error de usuario !'), ('El campo salario basico debe ser mayor a cero'))
            rule_ids = rule_obj.search(cr, uid, [('code','in',('DEC4','dec4'))])
            if not rule_ids:
                print "no rules decimo"
            lines_antes_ids = dec_line_obj.search(cr, uid, [('dec_id','=',this.id)])
            if lines_antes_ids:
                dec_line_obj.unlink(cr, uid, lines_antes_ids)
            if not this.date_start<this.date_start:
                raise osv.except_osv(('Operación no permitida !'), ('El periodo final debe ser mayor al inicial'))
            period_ids = period_obj.search(cr, uid, [('date_start','>=',this.period_start.date_start),('date_stop','<=',this.period_end.date_stop)])
            #sacar el basico
            wage = this.basico
            if period_ids:
                contract_ids = contract_obj.search(cr, uid, [('subtype_id','=',this.contract_type.id),('activo','=',True)])
                if contract_ids:
                    for contract_id in contract_ids:
                        aux_dias = laborado_actual = laborado_antes = 0
                        dict_aux = {'03':'mar','04':'abr','05':'may','06':'jun','07':'jul','08':'ago','09':'sep','10':'oct','11':'nov','12':'dic','01':'ene','02':'feb'}
                        dict_value = {'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'01':0,'02':0}
                        payslip_ids = payslip_obj.search(cr, uid, [('contract_id','=',contract_id),('period_id','in',period_ids)])
                        contrato = contract_obj.browse(cr, uid, contract_id)
#                        if contrato.name=='CT346':
#                            import pdb
#                            pdb.set_trace()
                        if contrato.date_start<=this.period_start.date_start and not contrato.date_end:
                            laborado_actual = 360
                        else:
                            inicio = contrato.date_start.split('-')
                            fin = this.period_end.date_stop.split('-')
                            dateinicio = date( int(inicio[0]), int(inicio[1]), int(inicio[2]) )
                            datefin = date( int(fin[0]), int(fin[1]), int(fin[2]) )
                            delta = datefin - dateinicio
                            laborado_actual = abs(delta.days)
                        contract_prev_ids = contract_obj.search(cr, uid, [('employee_id','=',contrato.employee_id.id),
                                                                          ('id','!=',contract_id),('date_end','<=',this.period_end.date_stop),
                                                                          ('date_end','>=',this.period_start.date_start),
                                                                          ],order='date_start asc')
                        if contract_prev_ids:
                            for contract_prev_id in contract_prev_ids:
                                contrato_previo = contract_obj.browse(cr, uid, contract_prev_id)
                                inicio = contrato_previo.date_end.split('-')
                                fin = this.period_start.date_start.split('-')
                                dateinicio = date( int(inicio[0]), int(inicio[1]), int(inicio[2]) )
                                datefin = date( int(fin[0]), int(fin[1]), int(fin[2]) )
                                delta = datefin - dateinicio
                                laborado_antes += abs(delta.days)
                        #considero permisos licencia sin sueldo
                        permiso_ids = permiso_obj.search(cr, uid, [('tipo','=','Dias'),('tipo2','=','LICENCIASIN'),
                                                                   ('date','>=',this.period_start.date_start),('date_end','<=',this.period_end.date_stop)])
                        dias_permiso = 0
                        if permiso_ids:
                            for permiso_id in permiso_ids:
                                permiso = permiso_obj.browse(cr, uid, permiso_id)
                                dias_permiso += permiso.total_dias
                        aux_dias = laborado_actual + laborado_antes
                        if aux_dias>360:
                            aux_dias = 360
                        aux_dias = aux_dias - dias_permiso
                        aux_monto_total = aux_judicial = total_cobrar = 0
                        if contrato.employee_id.judicial_ids:
                            for judicial_id in contrato.employee_id.judicial_ids:
                                aux_judicial += judicial_id.monto
                        j = 0 
                        if not payslip_ids:
                            continue
                        dec_line_id = dec_line_obj.create(cr, uid, {
                            'dec_id':this.id,
                            'contract_id':contract_id,
                        })
                        l = 0 
                        m = 0
                        for period_id in period_ids:
                            periodo = period_obj.browse(cr, uid, period_id)
                        #for payslip_id in payslip_ids:
                            aux_monto = 0
                            #payslip = payslip_obj.browse(cr, uid, payslip_id)
                            payslip_ids2 = payslip_obj.search(cr, uid, [('contract_id','=',contract_id),('period_id','=',period_id)])
                            if not payslip_ids2:
                                aux_monto = wage#0
                            else:
                                payslip_line_ids = payslip_line_obj.search(cr, uid, [('contract_id','=',contract_id),('period_id','=',period_id),
                                                                                     ('salary_rule_id','in',rule_ids),('slip_id','in',payslip_ids)])
                                if not payslip_line_ids:
                                    aux_monto = wage
                            total_cobrar += aux_monto
                            dict_value[periodo.name[0:2]]=aux_monto
                            m+=1
                            j += 1
                            aux_monto_total += aux_monto
                        aux_total_proporcional = (aux_monto_total*aux_dias)/(360*12)
                        #proporcional dias
                        if aux_total_proporcional<aux_judicial:
                            aux_judicial = aux_total_proporcional
                        dec_line_obj.write(cr, uid, dec_line_id,{
                            'mar':dict_value['03'],
                            'abr':dict_value['04'],
                            'may':dict_value['05'],
                            'jun':dict_value['06'],
                            'jul':dict_value['07'],
                            'ago':dict_value['08'],
                            'sep':dict_value['09'],
                            'oct':dict_value['10'],
                            'nov':dict_value['11'],
                            'dic':dict_value['12'],
                            'ene':dict_value['01'],
                            'feb':dict_value['02'],
                            'dias_lab':aux_dias,
                            'descuento_judicial':aux_judicial,
                            'fecha_contrato':contrato.date_start,
                        })
            aux_str = "PAGO DECIMO CUARTO " + this.contract_type.name + 'DE: ' + this.period_start.name + ' A: ' + this.period_end.name
            self.write(cr, uid, ids, {
                'name':aux_str,
            })
        return True

    def pagado_dec4(self, cr, uid, id, context=None):
        self.write(cr, uid, id, {'state':'Pagado'})
        return True

    def create(self, cr, uid, values, context=None):
        values['creado_por'] = uid 
        values['fecha_creacion'] = time.strftime('%Y-%m-%d')
        return super(hrDecimoCuarto, self).create(cr, uid, values, context=context)    

    _columns = dict(
        ajuste_decimo = fields.float('Valor Ajuste Decimo Mensualiza',help="Si carga un valor aqui este se va a agregar a las personas que mensualizan el decimo en el rol"),
        date_start = fields.date('Fecha Desde'),
        date_stop = fields.date('Fecha Hasta'),
        fecha_creacion = fields.date('Fecha Creacion'),
        creado_por = fields.many2one('res.users','Creado Por'),
        fy_id = fields.many2one('hr.work.period','Anio Fiscal'),
        total = fields.function(_total_decimo,type="float", store=True,string='TOTAL DECIMO'),
        basico = fields.float('Salario Basico'),
        certificate_id = fields.many2one('budget.certificate','Certificado'),
        detalle_ids = fields.one2many('run.programa.detalle','dec4_id','Detalle'),
        name = fields.char('Descripcion',size=128),
        contract_type = fields.many2one('hr.contract.type.type','Tipo Contrato'),
        period_start = fields.many2one('hr.work.period.line','Desde'),
        move_id = fields.many2one('account.move','Comprobante Contable'),
        period_end = fields.many2one('hr.work.period.line','Hasta'),
        line_ids = fields.one2many('hr.decimo.cuarto.line','dec_id','Detalle'),
        state = fields.selection([('Borrador','Borrador'),('Aprobado','Aprobado'),('Autorizado','Autorizado'),('Pagado','Pagado')],'Estado'),
        )
    _defaults = dict(
        state = 'Borrador'
        )
hrDecimoCuarto()
