# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
import addons
from tools import ustr
from osv import fields, osv
from time import strftime
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser
import time
from gt_tool import XLSWriter, fechas

class remuneracionLotaip(osv.TransientModel):
    _name = 'remuneracion.lotaip'
    _columns = dict(
        period_id = fields.many2one('hr.work.period.line','Periodo'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=128),
    )

    def remuneracionLotaip(self, cr, uid, ids, context=None):
        from xlrd import open_workbook
        from xlutils.copy import copy
        rol_obj = self.pool.get('hr.payslip')
        contract_obj = self.pool.get('hr.contract')
        hora_obj = self.pool.get('hr.he.register.alone')
        sub_obj = self.pool.get('hr.contract.encargo')
        rule_obj = self.pool.get('hr.salary.rule')
        line_obj = self.pool.get('hr.payslip.line')
        period_obj = self.pool.get('hr.work.period.line')
        dec3_line = self.pool.get('hr.decimo.tercero.line')
        dec4_line = self.pool.get('hr.decimo.cuarto.line')
        xls_path = addons.get_module_resource('gt_hr_payroll_ec','xls','Literal c remuneracion mensual por puestos.xls')
        rb = open_workbook(xls_path,formatting_info=True) #xlrd
        user = self.pool.get('res.users').browse(cr, uid, uid)
        for this in self.browse(cr, uid, ids, context):
            wb = copy(rb)
            ws = wb.get_sheet(0)
            aux = '''select contract_id from hr_payslip where period_id=%s group by contract_id''' % (str(this.period_id.id))
            #escritura de datos en el formulario de excel
            cr.execute(aux)
            aux = 4
            for row in cr.fetchall():
                contrato = contract_obj.browse(cr, uid, row[0])
                sueldo = contrato.wage
                anual = sueldo*12
                #dec = anual/12
                period_ids = period_obj.search(cr, uid, [('period_id','=',this.period_id.period_id.id)])
                #aqui tomar de los decimos tercero mensualizados o si ha cobrado el decimo del anio
                rule_ids = rule_obj.search(cr, uid, [('code','in',('DEC3','dec3'))])
                if not rule_ids:
                    print "no dec 3"
                line_dec3_ids = line_obj.search(cr, uid, [('contract_id','=',row[0]),('salary_rule_id','in',rule_ids)])
                aux_dec3 = aux_dec4 = total = 0 
                if line_dec3_ids:
                    for line_dec3_id in line_dec3_ids:
                        line_dec3 = line_obj.browse(cr, uid, line_dec3_id)
                        aux_dec3 += line_dec3.amount
                else:
                    dec3_ids = dec3_line.search(cr, uid, [('contract_id','=',row[0]),('dec_id.period_start','<=',this.period_id.id)])
                    if dec3_ids:
                        dec3 = dec3_line.browse(cr, uid, dec3_ids[0])
                        aux_dec3 = dec3.recibir
                ##dec 4
                rule_ids = rule_obj.search(cr, uid, [('code','in',('DEC4','dec4'))])
                if not rule_ids:
                    print "no dec 4"
                line_dec4_ids = line_obj.search(cr, uid, [('contract_id','=',row[0]),('salary_rule_id','in',rule_ids)])
                aux_dec4 = 0 
                if line_dec4_ids:
                    for line_dec4_id in line_dec4_ids:
                        line_dec4 = line_obj.browse(cr, uid, line_dec4_id)
                        aux_dec4 += line_dec3.amount
                else:
                    dec4_ids = dec4_line.search(cr, uid, [('contract_id','=',row[0]),('dec_id.period_start','<=',this.period_id.id)])
                    if dec4_ids:
                        dec4 = dec4_line.browse(cr, uid, dec4_ids[0])
                        aux_dec4 = dec4.recibir
                ######
                extras_ids = hora_obj.search(cr, uid, [('period_id','=',this.period_id.id),('state','=','done'),('contract_id','=',contrato.id)])
                aux_hora = 0
                if extras_ids:
                    for extra_id in extras_ids:
                        extra = hora_obj.browse(cr, uid, extra_id)
                        aux_hora += extra.total
                subro_ids = sub_obj.search(cr, uid, [('period_id','=',this.period_id.id),('state','=','aprobado'),('contract_id','=',contrato.id)])
                aux_subro = 0
                if subro_ids:
                    for sub_id in subro_ids:
                        sub = sub_obj.browse(cr, uid, sub_id)
                        aux_subro += sub.monto
                total = anual+aux_dec3+aux_dec4+aux_hora+aux_subro
                ws.write(aux,0,contrato.employee_id.name)
                ws.write(aux,1,contrato.employee_id.complete_name)
                ws.write(aux,2,contrato.employee_id.job_id.name)
                ws.write(aux,3,contrato.type_id.name)
                ws.write(aux,4,contrato.budget_id.code)
                ws.write(aux,5,'GRADO PROPIO')
                ws.write(aux,6,sueldo)
                ws.write(aux,7,anual)
                ws.write(aux,8,aux_dec3)
                ws.write(aux,9,aux_dec4)
                ws.write(aux,10,aux_hora)
                ws.write(aux,11,aux_subro)
                ws.write(aux,12,total)
                aux += 1
            ws.write(aux,0,'')
            ws.write(aux,1,'')
            aux+=1
            ws.write(aux,0,ustr('FECHA ACTUALIZACION DE LA INFORMACION'))
            ws.write(aux,1,this.period_id.date_stop)
            aux+=1
            ws.write(aux,0,ustr('PERIODICIDAD DE ACTUALIZACIÓN DE LA INFORMACIÓN:'))
            ws.write(aux,1,'MENSUAL')
            aux+=1
            ws.write(aux,0,'UNIDAD POSEEDORA DE LA INFORMACION - LITERAL c):')
            ws.write(aux,1,'DIRECCION DE TALENTO HUMANO')
            aux+=1
            ws.write(aux,0,ustr('RESPONSABLE DE LA UNIDAD POSEEDORA DE LA INFORMACIÓN DEL LITERAL c):'))
            ws.write(aux,1,ustr(user.context_department_id.manager_id.complete_name))
            aux+=1
            ws.write(aux,0,ustr('CORREO ELECTRÓNICO DEL O LA RESPONSABLE DE LA UNIDAD POSEEDORA DE LA INFORMACIÓN:'))
            ws.write(aux,1,ustr(user.context_department_id.manager_id.email))
            aux+=1
            ws.write(aux,0,ustr('NÚMERO TELEFÓNICO DEL O LA RESPONSABLE DE LA UNIDAD POSEEDORA DE LA INFORMACIÓN:'))
            ws.write(aux,1,user.context_department_id.manager_id.house_phone)
            nombre = "Literal c remuneracion mensual por puestos.xls"
            wb.save(nombre)
            out = open(nombre,"rb").read().encode("base64")
            self.write(cr, uid, this.id, {'datas':out, 'name':"Literal c remuneracion mensual por puestos.xls",
                                          'datas_fname': 'Literal c remuneracion mensual por puestos.xls'})
        return True

remuneracionLotaip()

##reporte mensual general

class resumenRolDetalle(osv.TransientModel):
    _name = 'resumen.rol.detalle'
    _columns = dict(
        line_id = fields.many2one('resumen.rol.line','Detalle'),
        res_id = fields.many2one('resumen.rol','Detalle'),
        contract_id = fields.many2one('hr.contract','Funcionario'),
        rmu = fields.float('Total RMU'),
        ingresos = fields.float('Total Ingresos'),
        egresos = fields.float('Total Egresos'),
        total = fields.float('Total Recibir'),
    )
resumenRolDetalle()

class resumenRolLine(osv.TransientModel):
    _name = 'resumen.rol.line'
    _columns = dict(
        line_ids = fields.one2many('resumen.rol.detalle','line_id','Detalle'),
        r_id = fields.many2one('resumen.rol','Rol resumen'),
        tipo_id = fields.many2one('hr.contract.type.type','Tipo Contrato'),
        total_funcionarios = fields.integer('Total Funcionarios'),
        total_rmu = fields.float('Total RMU'),
        total_ingresos = fields.float('Total Ingresos'),
        total_egresos = fields.float('Total Egresos'),
        total = fields.float('Total Recibir'),
    )
resumenRolLine()

class resumenRol(osv.TransientModel):
    _name = 'resumen.rol'
    _columns = dict(
        line2_ids = fields.one2many('resumen.rol.detalle','res_id','Detalle'),
        period_id = fields.many2one('hr.work.period.line','Mes'),
        total_funcionarios = fields.integer('Total Funcionarios'),
        total_ingresos = fields.float('Total Ingresos'),
        total_rmu = fields.float('Total RMU'),
        total_egresos = fields.float('Total Egresos'),
        total = fields.float('Total Recibir'),
        line_ids = fields.one2many('resumen.rol.line','r_id','Detalle'),
    )

    def printResumenRol(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.resumen.rol'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'resumen_rol',
            'model': 'resumen.rol',
            'datas': datas,
            'nodestroy': True,                        
            }

    def printResumenRolDetalle(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.resumen.rol'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'resumen_rol_detalle',
            'model': 'resumen.rol',
            'datas': datas,
            'nodestroy': True,                        
            }

    def generarResumenRol(self, cr, uid, ids, context=None):
        general_obj = self.pool.get('hr.payslip.run')
        rol_line_obj = self.pool.get('resumen.rol.line')
        detalle_obj = self.pool.get('resumen.rol.detalle')
        for this in self.browse(cr, uid, ids):
            antes_ids = rol_line_obj.search(cr, uid, [('r_id','=',this.id)])
            antes2_ids = detalle_obj.search(cr, uid, [('res_id','=',this.id)])
            if antes_ids:
                rol_line_obj.unlink(cr, uid, antes_ids)
            if antes2_ids:
                detalle_obj.unlink(cr, uid, antes2_ids)
            run_ids = general_obj.search(cr, uid, [('period_id','=',this.period_id.id),('state','in',('Autorizado','Pagado'))])
            aux_total_funcionarios = total_ingresos_g = total_egresos_g = total_g = total_rmu_g =0
            if run_ids:
                for run_id in run_ids:
                    run = general_obj.browse(cr, uid, run_id)
                    if run.slip_ids:
                        aux_total_funcionarios += len(run.slip_ids)
                        total_ingresos = total_egresos = total = total_rmu = 0
                        for rol in run.slip_ids:
                            detalle_obj.create(cr, uid, {
                                'res_id':this.id,
                                'contract_id':rol.contract_id.id,
                                'rmu':rol.basic,
                                'ingresos':rol.basic+rol.allowance+rol.aportable,
                                'egresos':rol.deduction,
                                'total':rol.net,
                            })
                            total_ingresos += (rol.basic+rol.allowance+rol.aportable)
                            total_egresos += rol.deduction
                            total += rol.net
                            total_rmu += rol.basic
                        total_ingresos_g += total_ingresos
                        total_egresos_g += total_egresos
                        total_g += total
                        total_rmu_g += total_rmu
                        rol_line_id = rol_line_obj.create(cr, uid, {
                            'r_id':this.id,
                            'total_funcionarios':len(run.slip_ids),
                            'tipo_id':run.contract_type_id.id,
                            'total_ingresos':total_ingresos,
                            'total_egresos':total_egresos,
                            'total':total,
                            'total_rmu':total_rmu,
                        })              
                
            self.write(cr, uid, this.id,{
                'total_funcionarios':aux_total_funcionarios,
                'total_ingresos':total_ingresos_g,
                'total_egresos':total_egresos_g,
                'total':total_g,
                'total_rmu':total_rmu_g,
            })            
        return True

resumenRol()


class noDescontado(osv.Model):
    _name = 'no.descontado'
    _columns = dict(
        employee_id = fields.many2one('hr.employee','Empleado'),
        run_id = fields.many2one('hr.payslip.run','Rol'),
        name = fields.char('Rubro',size=128),
        inicial = fields.float('Original'),
        descontado = fields.float('Descontado'),
        saldo = fields.float('Saldo'),
    )
noDescontado()

class noCobro(osv.Model):
    _name = 'hr.no.cobro'
    _columns = dict(
        contract_id = fields.many2one('hr.contract','Funcionario'),
        period_id = fields.many2one('hr.work.period.line','Mes'),
        tipo = fields.selection([('Sancion','Sancion'),('Licencia','Licencia')],'Tipo'),
    )
noCobro()

class rubroCxp(osv.Model):
    _name = 'rubro.cxp'
    _columns = dict(
        rc_id = fields.many2one('hr.salary.rule','Regla'),
        name = fields.char('Codigo Corto',size=5,required=True),
        account_id = fields.many2one('account.account','Cuenta',required=True),
    )
rubroCxp()

class ruleAccount(osv.Model):
    _name = 'rule.account'
    _columns = dict(
        rc_id = fields.many2one('hr.salary.rule','Regla'),
        tipo_id = fields.many2one('hr.contract.type.type','Tipo Rol',required=True),
        account_id = fields.many2one('account.account','Cuenta Tercero',required=True),
    )
ruleAccount()
class rulePartner(osv.Model):
    _inherit = 'hr.salary.rule'
    _columns = dict(
#        pagar = fields.boolean('Pagar'),
#        tipo_a = fields.boolean('Tipo AA'),
        cxp_ids = fields.one2many('rubro.cxp','rc_id','Detalle CxC'),
        account_ids = fields.one2many('rule.account','rc_id','Detalle Fondo Tercero'),
        is_ingreso_gad = fields.boolean('Es ingreso GAD'),
        is_rendicion = fields.boolean('Es descuento rendicion cuentas'),
        is_replanifica = fields.boolean('Reajjustar automatico'),
        account_id = fields.many2one('account.account','Cuenta Contable'),
        tercero_id = fields.many2one('account.account','Cuenta Contable Tercero(212..)'),
        is_tercero = fields.boolean('Pago Tercero'),
        partner_id = fields.many2one('res.partner','Proveedor'),
        agrupar = fields.boolean('Agrupar',help="Si marca este campo los valores se agruparan en otros ingresos o egresos respectivamente segun su naturaleza"),
        is_ingreso_anticipo = fields.boolean('Es ingreso anticipo',help="Marque este campo y el sistema creara un movimiento de anticipo entregado al funcionario"),
    )

    _defaults = dict(
        is_ingreso_anticipo = False,
        is_ingreso_gad = False,
    )

    _sql_constraints = [
        ('unique_name', 'unique(name)', u'El rubro es único.'),
        ('unique_code', 'unique(code)', u'El codigo del rubro es único.'),
    ]
rulePartner()

class payslipLine(osv.Model):
    _inherit = "hr.payslip.line"
    _columns = dict(
        program_id = fields.related('slip_id', 'program_id', type='many2one', relation='project.program', string='Programa', store=True),
#        program_id = fields.many2one('project.program','Programa'),
        run_id = fields.related('slip_id', 'payslip_run_id', type='many2one', relation='hr.payslip.run', string='Rol General', store=True),
        budget_id2 = fields.related('slip_id', 'budget_id2', type='many2one', relation='budget.post', string='Partida', store=True),
#        budget_id2 = fields.many2one('budget.post','Partida'),
        contract_id = fields.related('slip_id', 'contract_id', type='many2one', relation='hr.contract', string='Contrato', store=True),
        budget_id = fields.related('contract_id', 'budget_id', type='many2one', relation='budget.item', string='Partida', store=True),
        period_id = fields.related('slip_id', 'period_id', type='many2one', relation='hr.work.period.line', string='Periodo', store=True),
    )
    _sql_constraints = [
        ('amount_total', 'CHECK (amount>=0)', 'Valor erroneo en descuento, solo puede haber positivo!'),
    ]
payslipLine()

class hr_payslip_ec(osv.osv):
    _inherit = "hr.payslip"
    #_order = 'date_start desc'

    def print_rol_ind(self, cr, uid, ids, vals , context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'hr.payslip'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'rol_individual_gpa',
            'model': 'hr.payslip',
            'datas': datas,
            'nodestroy': True,                        
            }


    def send_rol_by_email(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'gt_hr_payroll_ec', 'email_template_edi_payslip')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'hr.payslip',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def write1(self, cr, uid, ids, vals , context=None):
        for rol in self.browse(cr, uid, ids, context):
            if rol.payslip_run_id.state in ('close','','Autorizado','Pagado','Contabilizado'):
                raise osv.except_osv('Error', 'No pueden modificar roles autorizados, pagados o contabilizados')
        return super(hr_payslip_ec, self).write(cr, uid, ids ,vals, context=None)    

    def unlink(self, cr, uid, ids, context=None):
        payslip_obj = self.pool.get('hr.payslip')
        run_obj = self.pool.get('hr.payslip.run')
        for rol in self.browse(cr, uid, ids, context):
            if rol.payslip_run_id.state in ('close','','Autorizado','Pagado','Contabilizado'):
                raise osv.except_osv('Error', 'No pueden eliminar roles autorizados, pagados o contabilizados')
        return super(hr_payslip_ec, self).unlink(cr, uid, ids)

    def _calculate_salary(self, cr, uid, ids, field_names, arg, context=None):
        vals = {}
        slip_line_pool = self.pool.get('hr.payslip.line')
        slip_obj = self.pool.get('hr.payslip')
        for employee in self.browse(cr, uid, ids, context=context):
            vals[employee.id] = {'basic':0.0, 'net':0.0, 'allowance':0.0, 'deduction':0.0, 'aportable':0.0, 'provision': 0.0}
            line_ids = slip_line_pool.search(cr, uid, [('slip_id','=', employee.id)])
            for payslip_line in slip_line_pool.browse(cr, uid, line_ids, context):
                if payslip_line.category_id.code=='BASIC':
                    vals[employee.id]['basic'] = vals[employee.id]['basic'] + payslip_line.amount
                if payslip_line.category_id.code=='ING':
                    vals[employee.id]['allowance'] = vals[employee.id]['allowance'] + payslip_line.amount
                if payslip_line.category_id.code=='EGR':
                    vals[employee.id]['deduction'] = vals[employee.id]['deduction'] + payslip_line.amount
                if payslip_line.category_id.code=='APT':
                    vals[employee.id]['aportable'] = vals[employee.id]['aportable'] + payslip_line.amount
#                if payslip_line.category_id.code=='NET':
#                    vals[employee.id]['net'] = vals[employee.id]['net'] + payslip_line.amount
                if payslip_line.category_id.code=='PROV':
                    vals[employee.id]['provision'] = vals[employee.id]['provision'] + payslip_line.amount
            vals[employee.id]['net'] = vals[employee.id]['basic'] + vals[employee.id]['allowance'] - vals[employee.id]['deduction'] + vals[employee.id]['aportable']
            #slip_obj.compute_sheet(cr, uid, [employee.id],context)
        return vals
    
    
    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        def verificar_ausencia_contrato(contrato, dia):
            resultado = True #True indica que no laboró ese dia
            if contrato.date_start:
                dia_inicio = datetime.strptime(contrato.date_start, "%Y-%m-%d")
                if dia >= dia_inicio:
                    if contrato.date_end:
                        dia_fin = datetime.strptime(contrato.date_end, "%Y-%m-%d")
                        if dia <= dia_fin:
                            resultado = False
                    else:
                        resultado = False
            return resultado
        
        def was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
            if holiday_ids:
                #res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id
                #res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0]
            return res
        
        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            leaves = {}
            attendances = {
                           'name': "Dias Laborados",
                           'sequence': 1,
                           'code': 'WORK100',
                           'number_of_days': 0.0,
                           'number_of_hours': 0.0,
                           'contract_id': contract.id,
                           }
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            #for day in range(0, nb_of_days):
            for day in range(0, 30):
                leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                leave_contract = verificar_ausencia_contrato(contract, day_from + timedelta(days=day))
                if leave_type:
                    #preguntar si es falta ahi resta
                    #if he was on leave, fill the leaves dict
                    if leave_type in leaves:
                        leaves[leave_type]['number_of_days'] += 1.0
                        #leaves[leave_type]['number_of_hours'] += working_hours_on_day
                    else:
                        leaves[leave_type] = {
                            'name': leave_type.name,
                            'sequence': 5,
                            'code': leave_type.code,
                            #'code': '-' + str(leave_type.discount_rate),
                            'number_of_days': 1.0,
                            #'number_of_hours': working_hours_on_day,
                            'contract_id': contract.id,
                            #'holidays_id': leave_type.id,
                        }
                else:
                    if leave_contract:
                        pass
                    else:
                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        #attendances['number_of_hours'] += working_hours_on_day
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves
        return res

    def _get_anios(self,cr, uid, ids, field_name, arg, context):
        res = {}
        contract_obj = self.pool.get('hr.contract')
        for obj in self.browse(cr, uid, ids, context):
            aux_date_contract = obj.contract_id.date_start
#            other_contracts = contract_obj.search(cr, uid, [('employee_id','=',obj.contract_id.employee_id.id),('id','!=',obj.contract_id.id)],order='date_start asc')
#            if other_contracts:
#                contract_anterior = contract_obj.browse(cr, uid, other_contract_ids[0])
#                aux_date_contract = contract_anterior.date_start
            if aux_date_contract<'2004-01-01':
                aux_date_contract = '2003-01-01'
#            else:
#                print 'menor'
            day_from = datetime.strptime(aux_date_contract,"%Y-%m-%d")
            day_to = datetime.strptime(obj.date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            anio = nb_of_days//365
            res[obj.id] = anio
        return res

    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        res = []
        contract_obj = self.pool.get('hr.contract')
        rule_obj = self.pool.get('hr.salary.rule')

        structure_ids = contract_obj.get_all_structures(cr, uid, contract_ids, context=context)
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        
        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
            for rule in rule_obj.browse(cr, uid, sorted_rule_ids, context=context):
                if rule.input_ids:
                    for input in rule.input_ids:
                        inputs = {
                             'name': input.name,
                             'code': input.code,
                             'contract_id': contract.id,
                        }
                        res += [inputs]
        #ADD INPUTS HEREEEEEE
        period_line_obj = self.pool.get('hr.work.period.line')
        ie_line_obj = self.pool.get('hr.ie.line')
        he_line_obj = self.pool.get('hr.he.register.line')
        semanal = False
        try:
            salidas_obj = self.pool.get('salidas.solicitud')
        except:
            pass
        #for payslip in self.browse(cr, uid, ids):
        period_ids = period_line_obj.search(cr, uid, [('date_start', '>=', date_from),
                                                      ('date_stop', '<=', date_to)])
        if not period_ids:
            period_ids = period_line_obj.search(cr, uid, [('date_start', '<=', date_to),
                                                          ('date_stop', '>=', date_to)])
        if not period_ids:
            raise osv.except_osv('Error de configuracion', 'No hay periodo para la fechas de rol')
        for periodo in period_ids:
            for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
                #BUSCAMOS LOS INGRESOS/EGRESOS DEL MES
                #preguntar si semanal
                if semanal and contract.subtype_id.name=='OBREROS':
                    ie_ids = ie_line_obj.search(cr, uid, [('date','>=',date_from),('date','<=',date_to),
                                                          ('employee_id', '=', contract.employee_id.id),
                                                          ('state', '=', 'pendiente')])
                    #                    ie_ids = ie_line_obj.search(cr, uid, [('period_id', '=', periodo),('date','>=',date_from),('date','<=',date_to),
                    #                                                          ('employee_id', '=', contract.employee_id.id),
                    #                                                          ('state', '=', 'pendiente')])
                else:
                    ie_ids = ie_line_obj.search(cr, uid, [('period_id', '=', periodo),
                                                          ('employee_id', '=', contract.employee_id.id),
                                                          ('state', '=', 'pendiente')])
                for ie in ie_line_obj.browse(cr, uid, ie_ids, context=context):
                    inputs = {
                        'name': ie.categ_id.name,
                        #'code': ie.categ_id.category_id.code,
                        'code': ie.categ_id.code,
                        'contract_id': contract.id,
                        'ie_id': ie.id,
                        'label': ie.label,
                        'amount': ie.valor,
                    }
                    res += [inputs]
                #BUSCAMOS LAS SALIDAS AL CAMPO DEL MES
                try:
                    if salidas_obj:
                        salidas_ids = salidas_obj.search(cr, uid, [('period_id', '=', periodo),
                                                                   ('employee_id', '=', contract.employee_id.id),
                                                                   ('state', '=', 'done')])
                        for salida in salidas_obj.browse(cr, uid, salidas_ids, context=context):
                            inputs = {
                                      'name': 'Gastos de alimentacion: ' + salida.name,
                                      'code': 'ING',
                                      'contract_id': contract.id,
                                      #'ie_id': ie.id,
                                      'amount': salida.valor,
                                      }
                            res += [inputs]
                except:
                    pass
        return res

    

    def get_payslip_lines(self, cr, uid, contract_ids, payslip_id, context):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, pool, cr, uid, employee_id, dict):
                self.pool = pool
                self.cr = cr
                self.uid = uid
                self.employee_id = employee_id
                self.dict = dict

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                result = 0.0
                self.cr.execute("SELECT sum(amount) as sum\
                            FROM hr_payslip as hp, hr_payslip_input as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                           (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()[0]
                return res or 0.0
        
#        class dec_3(BrowsableObject):
#            def decimo_3(self, contrato, periodo):
#                import pdb
#                pdb.set_trace()
#                ie_line_obj = self.pool.get('hr.ie.line')
#                categ_obj = self.pool.get('hr.salary.rule')
#                categ_ids = categ_obj.search('category_id','=','Ingresos Aportables')
#                ie_ids = ie_line_obj.search(cr, uid, [('period_id','=',periodo.id),('categ_id','in',categ_ids)])
#                if ie_ids:
#                    aux_ie = 0 
#                    for ie_id in ie_ids:
#                        ie = ie_line_obj.browse(cr, uid, ie_id)
#                        aux_ie += ie.valor
#                total_aportable = aux_ie + contrato.wage
#                decimo3 = total_aportable/12
#                return decimo3
    
        class sri_ec(BrowsableObject):
            def decimo_3(self, contrato, periodo,dias):
                ie_line_obj = self.pool.get('hr.ie.line')
                categ_obj = self.pool.get('hr.salary.rule')
                categ_ids = categ_obj.search(cr, uid, [('category_id','=','Ingresos Aportables')])
                ie_ids = ie_line_obj.search(cr, uid, [('period_id','=',periodo.id),('state','=','pendiente'),
                                                      ('categ_id','in',categ_ids),('employee_id','=',contrato.employee_id.id)])
                aux_ie = 0 
                if ie_ids:
                    for ie_id in ie_ids:
                        ie = ie_line_obj.browse(cr, uid, ie_id)
                        aux_ie += ie.valor
                total_aportable = aux_ie + contrato.wage
                #total_aportable / 30 por num dias
                #decimo3 = total_aportable/12
                decimo3 = (total_aportable/360) * dias
                return decimo3


            def total_aportable(self, contrato, periodo,dias):
                ie_line_obj = self.pool.get('hr.ie.line')
                categ_obj = self.pool.get('hr.salary.rule')
                categ_ids = categ_obj.search(cr, uid, [('category_id','=','Ingresos Aportables')])
                ie_ids = ie_line_obj.search(cr, uid, [('period_id','=',periodo.id),('categ_id','in',categ_ids),
                                                      ('state','=','pendiente'),('employee_id','=',contrato.employee_id.id)])
                aux_ie = 0 
                if ie_ids:
                    for ie_id in ie_ids:
                        ie = ie_line_obj.browse(cr, uid, ie_id)
                        aux_ie += ie.valor
                total_aportable = aux_ie + contrato.wage
                return total_aportable

            def dias_fr(self, contrato, periodo,dias):
                #fecha_inicio = contrato.date_start
                fecha_inicio = datetime.strptime(contrato.date_start, '%Y-%m-%d')
                fecha_mas_anio = fecha_inicio
                dias_aux = 0
                day = fecha_inicio.day
                month = fecha_inicio.month
                year = fecha_inicio.year
                fecha_mas_anio = (datetime(year, month, day) + relativedelta(months=12))
                # si fecha mas anio esta en ese mes, else 30
                dias_return = 30
                date_end_rol = datetime.strptime(periodo.date_stop, '%Y-%m-%d')
                date_start_rol = datetime.strptime(periodo.date_start, '%Y-%m-%d')
                if fecha_mas_anio<=date_end_rol and fecha_mas_anio>=date_start_rol:
                    day = 30
                    if date_end_rol.month==2:
                        day = date_end_rol.day #30
                    month = date_end_rol.month
                    year = date_end_rol.year
                    fecha_rol = datetime(year, month, day)
                    dias_aux = fecha_mas_anio - fecha_rol
                    if date_end_rol.month==2:
                        dias_return = abs(dias_aux.days) + 3
                    else:
                        dias_return = abs(dias_aux.days) + 1
                elif fecha_inicio<=date_end_rol and fecha_inicio>=date_start_rol:
                    day = 30
                    if date_end_rol.month==2:
                        day = date_end_rol.day  #30
                    month = date_end_rol.month
                    year = date_end_rol.year
                    fecha_rol = datetime(year, month, day)
                    dias_aux = fecha_inicio - fecha_rol
                    if date_end_rol.month==2:
                        dias_return = abs(dias_aux.days) + 3
                    else:
                        dias_return = abs(dias_aux.days) + 1
                return dias_return

            def fr_adicional(self, contrato, periodo,dias):
                ie_line_obj = self.pool.get('hr.ie.line')
                categ_obj = self.pool.get('hr.salary.rule')
                categ_ids = categ_obj.search(cr, uid, [('category_id','=','Ingresos Aportables')])
                ie_ids = ie_line_obj.search(cr, uid, [('period_id','=',periodo.id),('categ_id','in',categ_ids),('employee_id','=',contrato.employee_id.id)])
                aux_ie = 0 
                if ie_ids:
                    for ie_id in ie_ids:
                        ie = ie_line_obj.browse(cr, uid, ie_id)
                        aux_ie += ie.valor
                total_aportable = aux_ie + contrato.wage
                #total_aportable / 30 por num dias
                #decimo3 = total_aportable/12
                fr = total_aportable
                return fr

            def tabla_impuesto_renta(self):
                obj_tabla = self.pool.get('hr.base.retention')
                tabla_ids = obj_tabla.search(self.cr, self.uid, {'active':True})
                if tabla_ids:
                    tabla = obj_tabla.browse(self.cr, self.uid, tabla_ids[0])
                    return tabla.retention_line
                return False
            
            def proyecciones_empleado(self, fy):
                obj_projection = self.pool.get('hr.anual.projection')
                pass
            
            def impuesto_renta(self, contrato, periodo, actual, actual_np, porcentaje_iess):
                import time
                period_obj = self.pool.get('hr.work.period.line')
                if periodo==0:
                    period_ids = period_obj.search(cr, uid, [('date_start','<=',time.strftime('%Y-%m-%d')),('date_stop','>=',time.strftime('%Y-%m-%d'))])
                    periodo = period_obj.browse(cr, uid,period_ids[0])
                obj_rent_tax = self.pool.get('hr.rent.tax')
                obj_anual_tax = self.pool.get('hr.anual.rent.tax')
                valor = valor_anual = 0.0
                mes = int(periodo.month2)
                #proceso para obtener los valores anteriores
                anterior = 0
                anterior_np = 0
                aportado = 0
                
                id_renta_anual = 0
                if contrato.employee_id.rent_tax_ids:
                    for retenido_anual in contrato.employee_id.rent_tax_ids:
                        if retenido_anual.fy_id.id == periodo.period_id.id:
                            id_renta_anual = retenido_anual.id
                            if retenido_anual.line_ids:
                                for retenido in retenido_anual.line_ids:
                                    if retenido.period_id.id == periodo.id:
                                        obj_rent_tax.unlink(self.cr, self.uid, retenido.id)
                    for retenido_anual in contrato.employee_id.rent_tax_ids:
                        if retenido_anual.fy_id.id == periodo.period_id.id:
                            for retenido in retenido_anual.line_ids:
                                if retenido.period_id.id != periodo.id:
                                    anterior = anterior + retenido.apt_proy
                                    anterior_np = anterior_np + retenido.apt_noproy
                                    aportado = aportado + retenido.valor
                else:
                    id_renta_anual = obj_anual_tax.create(self.cr, self.uid, {'name': periodo.period_id.name,
                                                                              'fy_id': periodo.period_id.id,
                                                                              'employee_id': contrato.employee_id.id})
                anterior_iess = anterior*porcentaje_iess
                anterior_iess_np = anterior_np*porcentaje_iess
                base_imponible = (actual*(12))# + actual_np + anterior + anterior_np#(actual*(13.0-mes)) + actual_np + anterior + anterior_np
                #actual_iess = ((actual*(13.0-mes))*porcentaje_iess) + (actual_np*porcentaje_iess)
                actual_iess = ((actual*(12))*porcentaje_iess)
                base_imponible = base_imponible - actual_iess#(actual_iess + anterior_iess + anterior_iess_np)
                #base_imponible = (base_imponible*12.0)/mes
                
                deducible = 0
                if contrato.employee_id.projection_ids:
                    for deducible_anual in contrato.employee_id.projection_ids:
                        if deducible_anual.fy_id == periodo.period_id:
                            for deducible_line in deducible_anual.line_ids:
                                deducible = deducible + deducible_line.value 
                #print base_imponible
                tabla_obj = self.pool.get("hr.base.retention")
                linea_obj = self.pool.get("hr.base.retention.line")
                
                tabla_ids = tabla_obj.search(self.cr, self.uid, [('active','=',True)])
                if tabla_ids:
                    for tabla in tabla_obj.browse(self.cr, self.uid, tabla_ids):
                        if tabla.max_deduction < deducible and tabla.max_deduction > 0:
                            deducible = tabla.max_deduction
                        base_imponible = base_imponible - deducible
                        linea_id = linea_obj.search(self.cr, self.uid, [('retention_id','=', tabla.id),
                                                                        ('basic_fraction','<=', base_imponible),
                                                                        ('excess_to','>=', base_imponible)])
                        #print linea_id
                        for linea in linea_obj.browse(self.cr, self.uid, linea_id):
                            #print linea.basic_fraction
                            valor_anual = linea.basic_fraction_tax
                            valor_anual = valor_anual + (((base_imponible - linea.basic_fraction)/100)*linea.percent)
                            #print valor_anual
                            valor = (valor_anual)/(12)#(valor_anual - aportado)/(13.0-mes)
                            obj_rent_tax.create(self.cr, self.uid, {'period_id': periodo.id,
                                                                    'apt_proy': actual,
                                                                    'apt_noproy': actual_np,
                                                                    'valor': valor,
                                                                    'tl_id': id_renta_anual})
                return valor

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                result = 0.0
                self.cr.execute("SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours\
                            FROM hr_payslip as hp, hr_payslip_worked_days as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done'\
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                           (self.employee_id, from_date, to_date, code))
                return self.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0
            
            def leaves_detail(self, date_from, date_to):
                obj_holidays = self.pool.get('hr.holidays')
                leaves = {'WORK100':{'name': "Dias Laborados",
                                     'code': 'WORK100',
                                     'number_of_days': 0.0,
                                     }
                          }
                day_from = datetime.strptime(date_from,"%Y-%m-%d")
                day_to = datetime.strptime(date_to,"%Y-%m-%d")
                nb_of_days = (day_to - day_from).days + 1
                for day in range(0, nb_of_days):
                    holiday_ids = obj_holidays.search(self.cr, self.uid, [('state','=','validate'),('employee_id','=',self.employee_id),('type','=','remove'),
                                                                          ('date_from','<=',str(day_from + timedelta(days=day))),
                                                                          ('date_to','>=',str(day_from + timedelta(days=day)))])
                    if holiday_ids:
                        leave = obj_holidays.browse(self.cr, self.uid, holiday_ids[0])
                        leave_type = leave.holiday_status_id
                            #if he was on leave, fill the leaves dict
                        if leave_type.code in leaves:
                            leaves[leave_type.code]['number_of_days'] += 1.0
                        else:
                            leaves[leave_type.code] = {'name': leave_type.name,
                                                       'code': leave_type.code,
                                                       'number_of_days': 1.0,
                                                       }
                    else:
                        leaves['WORK100']['number_of_days'] += 1.0
                return leaves

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                self.cr.execute("SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)\
                            FROM hr_payslip as hp, hr_payslip_line as pl \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s",
                            (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()
                return res and res[0] or 0.0

        #we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules = {}
        categories_dict = {}
        blacklist = []
        payslip_obj = self.pool.get('hr.payslip')
        inputs_obj = self.pool.get('hr.payslip.worked_days')
        obj_rule = self.pool.get('hr.salary.rule')
        payslip = payslip_obj.browse(cr, uid, payslip_id, context=context)
        worked_days = {}
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days[worked_days_line.code] = worked_days_line
        inputs = {}
        for input_line in payslip.input_line_ids:
            if inputs.has_key(input_line.code):
                inputs[input_line.code].amount +=  input_line.amount
            else:
                inputs[input_line.code] = input_line

        categories_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, categories_dict)
        input_obj = InputLine(self.pool, cr, uid, payslip.employee_id.id, inputs)
        worked_days_obj = WorkedDays(self.pool, cr, uid, payslip.employee_id.id, worked_days)
        payslip_obj = Payslips(self.pool, cr, uid, payslip.employee_id.id, payslip)
        rules_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, rules)
        
        #localdict = {'categories': categories_obj, 'rules': rules_obj, 'payslip': payslip_obj, 'worked_days': worked_days_obj, 'inputs': input_obj}
        
        sri_ec_obj = sri_ec(self.pool, cr, uid, payslip.employee_id.id, payslip_obj)
        localdict = {'categories': categories_obj, 'rules': rules_obj, 'payslip': payslip_obj, 'worked_days': worked_days_obj, 'inputs': input_obj, 'sri_ec': sri_ec_obj, 'date_time':fechas}
        
        #AQUI SE OBTIENE LA ESTRUCTURA DEL CONTRATO
        structure_ids = []
        if context.has_key('otra_estructura'):
            #aplico la estructura indicada en el wizard
            if context['otra_estructura']!=False:
                structure_ids = [context['otra_estructura'][0]]
                #structure_ids = [contract.struct_id.id for contract in self.pool.get('hr.contract').browse(cr, uid, [context['otra_estructura'][0]], context=context)]
                structure_ids = list(set(self.pool.get('hr.payroll.structure')._get_parent_structure(cr, uid, structure_ids, context=context)))
            else:
                structure_ids = self.pool.get('hr.contract').get_all_structures(cr, uid, contract_ids, context=context)
        else:
            #get the ids of the structures on the contracts and their parent id as well
            structure_ids = self.pool.get('hr.contract').get_all_structures(cr, uid, contract_ids, context=context)
            #get the rules of the structure and thier children
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
        #run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]

        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            employee = contract.employee_id
            localdict.update({'employee': employee, 'contract': contract})
            for rule in obj_rule.browse(cr, uid, sorted_rule_ids, context=context):
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                #check if the rule can be applied
                if obj_rule.satisfy_condition(cr, uid, rule.id, localdict, context=context) and rule.id not in blacklist:
                    #compute the amount of the rule
                    amount, qty, rate = obj_rule.compute_rule(cr, uid, rule.id, localdict, context=context)
                    #check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    #set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules[rule.code] = rule
                    #sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    #create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    #blacklist this rule and its children
                    blacklist += [id for id, seq in self.pool.get('hr.salary.rule')._recursive_search_of_rules(cr, uid, [rule], context=context)]

        result = [value for code, value in result_dict.items()]
        return result
    
    
    _columns = {
        'basic': fields.function(_calculate_salary, method=True, store=True, multi='dc', string='Remuneracion unificada', type='float'),
        'net': fields.function(_calculate_salary, method=True, store=True, multi='dc', string='Total a recibir', type='float'),
        'allowance': fields.function(_calculate_salary, method=True, store=True, multi='dc', string='Total otros ingresos', type='float'),
        'deduction': fields.function(_calculate_salary, method=True, store=True, multi='dc', string='Total egresos', type='float'),
        'aportable': fields.function(_calculate_salary, method=True, store=True, multi='dc', string='Total otros ingresos aportables', type='float'),
        'provision': fields.function(_calculate_salary, method=True, store=True, multi='dc', string='Total extra rol', type='float'),
        'period_id': fields.related('payslip_run_id', 'period_id', type='many2one', relation='hr.work.period.line', string='Periodo', store=True),
#        'program_id': fields.related('contract_id', 'program_id', type='many2one', relation='project.program', string='Programa', store=True),
        'program_id': fields.many2one('project.program','Programa'), 
        'budget_id':fields.many2one('budget.item','Partida'),
        'budget_id2':fields.many2one('budget.post','Partida'),
        'budget_id_ind':fields.char('Partida Individual',size=64),
        'job_id':fields.many2one('hr.job','Cargo'),
#        'budget_id': fields.related('contract_id', 'budget_id', type='many2one', relation='budget.item', string='Partida', store=True),
#        'budget_id2' : fields.related('budget_id', 'budget_post_id', type='many2one', relation='budget.post', string='Partida', store=True),
        'department_id': fields.many2one('hr.department','Departamento', required=True),
#        'job_id': fields.many2one('hr.job','Puesto de Trabajo', required=True),
        #el job debe ser related
        'anios_sindicato':fields.function(_get_anios, type='integer',store=True,string='Anios Sindicato'),
#        'job_id': fields.related('contract_id', 'job_id', type='many2one', relation='hr.job', string='Puesto Trabajo', store=True),
#        'department_id': fields.related('contract_id', 'department_id', type='many2one', relation='hr.department', string='Departamento', store=True),
        'rev':fields.boolean('REvPP'),
        'state':fields.selection([('draft','Borrador'),('Aprobado','Aprobado'),('Autorizado','Autorizado'),('Pagado','Pagado')],'Estado',readonly=True),
    }
    
    
hr_payslip_ec

class hr_payslip_input_ec(osv.Model):

    _inherit = 'hr.payslip.input'

    _columns = {
        'ie_id': fields.many2one('hr.ie.line',u'Ingreso/Egreso'),
        'label': fields.char(u'Etiqueta', size=50),
    }

hr_payslip_input_ec()

class hr_payslip_run_ec(osv.osv):
    _inherit = "hr.payslip.run"
    _order = 'date_start desc'

    def colocar_etiquetas(self, cr, uid, ids, context={}):
        obj_payslip = self.pool.get('hr.payslip')
        obj_payslip_line = self.pool.get('hr.payslip.line')
        obj_inputs = self.pool.get('hr.payslip.input')
        for payroll in self.browse(cr, uid, ids, context=context):
            #for payslip in payroll.slip_ids:
                for payslip in payroll.slip_ids:
                    for linea in payslip.line_ids:
                        input_ids = obj_inputs.search(cr, uid, [('payslip_id','=',payslip.id),('code','=',linea.code)])
                        etiqueta = ''
                        for input_line in obj_inputs.browse(cr, uid, input_ids):
                            if len(input_ids)<=1:
                              if input_line.label:
                                etiqueta = etiqueta + " [" + ustr(input_line.label or '') + "]"
                            if len(input_ids)>1:
                                etiqueta = etiqueta + " [" + ustr(input_line.label or '') + " $" + ustr(input_line.amount) + "]"
                        if etiqueta:
                            etiqueta = linea.salary_rule_id.name + etiqueta
                            obj_payslip_line.write(cr, uid, linea.id, {'name': etiqueta})
        return True

    def send_payslip_run(self, cr, uid, ids, context=None):
        mail_message = self.pool.get('mail.message')
        parameter_obj = self.pool.get('ir.config_parameter')
        user_obj = self.pool.get('res.users')
        rol_obj = self.pool.get('hr.payslip')
        email_from_ids = parameter_obj.search(cr, uid, [('key','=','email_fromtthh')],limit=1)
        if email_from_ids:
            email_from = parameter_obj.browse(cr, uid, email_from_ids[0]).value
        else:
            raise osv.except_osv('Error','No ha contratado esta funcionalidad comuniquese con el administrador del sistema.')
        user = user_obj.browse(cr, uid, uid)
        for this in self.browse(cr, uid, ids, context):
            for rol in this.slip_ids:
                if rol.employee_id.work_email or rol.employee_id.email:
                    aux_ingresos = 0
                    razonSocial = user.company_id.name
                    aux_ingresos = rol.basic+rol.aportable+rol.allowance
                    msg = " Estimado  %s, \n\n El rol de pagos de %s ha sido generado. \nDETALLE ROL\nINGRESOS:%s\nEGRESOS:%s\nTOTAL RECIBIR:%s\nPuede Descargar el rol desde el menu: Gestion Documental-->Empleados-->Roles\n Saludos Cordiales\n%s,"  %(rol.employee_id.complete_name,rol.period_id.name,str(aux_ingresos),str(rol.deduction),str(rol.net),razonSocial)
                    vals_msg = {
                        'subject': 'Confirmacion de acreditacion de rol - ' + razonSocial,
                        'body_text': msg,
                        'email_from': email_from,
                        'email_bcc' : rol.employee_id.email,
                        'email_to': rol.employee_id.work_email,
                        'state': 'outgoing',
                    }
                    email_msg_id = mail_message.create(cr, uid, vals_msg, context)
                    try:
                        mail_message.send(cr, uid, [email_msg_id])
                    except:
                        pass
        return True
                

    def unlink(self, cr, uid, ids, context=None):
        payslip_obj = self.pool.get('hr.payslip')
        payslip_line_obj = self.pool.get('hr.payslip.line')
        for general in self.browse(cr, uid, ids, context):
            if general.state in ('close','Aprobado','Autorizado','Pagado','Contabilizado'):
                raise osv.except_osv('Error', 'No pueden eliminar roles autorizados, pagados o contabilizados')
            for line in general.slip_ids:
                line_ids = payslip_line_obj.search(cr, uid, [('slip_id','=',line.id)])
                payslip_line_obj.unlink(cr, uid, line_ids)
                payslip_obj.unlink(cr, uid, [line.id])
        return super(hr_payslip_run_ec, self).unlink(cr, uid, ids)

    def _calculate_summary(self, cr, uid, ids, fields, args,context=None):
        vals = {}
        slip_line_pool = self.pool.get('hr.payslip')
        for employee in self.browse(cr, uid, ids, context=context):
            vals[employee.id] = {'basic':0.0, 'net':0.0, 'allowance':0.0, 'deduction':0.0, 'aportable':0.0, 'provision': 0.0}
            line_ids = slip_line_pool.search(cr, uid, [('payslip_run_id','=', employee.id)])
            for payslip_line in slip_line_pool.browse(cr, uid, line_ids, context):
                vals[employee.id]['basic'] = vals[employee.id]['basic'] + payslip_line.basic
                vals[employee.id]['allowance'] = vals[employee.id]['allowance'] + payslip_line.allowance
                vals[employee.id]['deduction'] = vals[employee.id]['deduction'] + payslip_line.deduction
                vals[employee.id]['aportable'] = vals[employee.id]['aportable'] + payslip_line.aportable
                vals[employee.id]['net'] = vals[employee.id]['net'] + payslip_line.net
                vals[employee.id]['provision'] = vals[employee.id]['provision'] + payslip_line.provision
            self.write(cr, uid, employee.id, vals[employee.id], context)
        return vals
        #return vals
        
    def recalcular_roles(self, cr, uid, ids, context={}):
        obj_payslip = self.pool.get('hr.payslip')
        for run in self.browse(cr, uid, ids):
            aux_net_all = aux_net = 0
            for payslip in run.slip_ids:
                aux_net = payslip.basic + payslip.aportable + payslip.allowance - payslip.deduction
                obj_payslip.write(cr, uid, payslip.id,{'net':aux_net})
                aux_net_all += aux_net
            self.write(cr, uid, run.id,{'net2':aux_net_all})
        return True
        
    def cambiar_fechas(self, cr, uid, ids, periodo_id, context=None):
        vals={}
        obj_period = self.pool.get('hr.work.period.line')
        if periodo_id:
            for periodo in obj_period.browse(cr, uid, [periodo_id], context):
                vals['value'] = {'date_start':periodo.date_start, 'date_end':periodo.date_stop}
        return vals
    
    def periodo_de_fecha(self, cr, uid, ids, context=None):
        obj_period = self.pool.get('hr.work.period.line')
        fecha = time.strftime('%Y-%m-%d')
        ids_periodo = obj_period.search(cr, uid, [('date_start','<=',fecha),
                                                  ('date_stop','>=',fecha),])
        print ids_periodo
        if ids_periodo:
            return ids_periodo[0]
        else:
            return False
    
    def ajustar_payslip_run(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        partner_obj = self.pool.get('res.partner')
        run_obj = self.pool.get('hr.payslip.run')
        slip_obj = self.pool.get('hr.payslip')
        no_desc = self.pool.get('no.descontado')
        ie_line_obj = self.pool.get('hr.ie.line')
        replanificar_line_obj = self.pool.get('replanificar.descuentos.line')
        partner_aux = bank_aux = '0'
        i = j = 0
        for this in self.browse(cr, uid, ids):
            from_date = this.date_start
            to_date = this.date_end
            for payslip in this.slip_ids:
                if payslip.net<0:
                    diferencia = abs(payslip.net)
                    ie_line_ids = ie_line_obj.search(cr, uid, [('employee_id','=',payslip.employee_id.id),('period_id','=',payslip.period_id.id)
                                                               ,('state','=','pendiente')])
                    if ie_line_ids:
                        quitar = {}
                        aux = 0
                        for line_id in ie_line_ids:
                            ie_line = ie_line_obj.browse(cr, uid, line_id)
                            aux += ie_line.valor
                            if aux>=diferencia:
                                descontado = aux - diferencia
                                saldo = ie_line.valor - descontado
                                quitar[line_id] = descontado
                                #eliminar el rol y crear de nuevo
                                no_desc.create(cr, uid, {
                                    'name':ie_line.categ_id.name,
                                    'inicial':ie_line.valor,
                                    'descontado':descontado,
                                    'saldo':saldo,
                                    'employee_id':payslip.employee_id.id,
                                    'run_id':this.id,
                                })
                                ie_line_obj.write(cr, uid, line_id,{'valor':descontado})
                                break
                    else:
                        raise osv.except_osv(_("Advertencia !"), _("El funcionario no tiene rubros que replanificar"))
        return True

    def _valida_saldo(self, cr, uid, ids, context=None):    
        dict_partidas = {}
        item_obj = self.pool.get('budget.item')
        poa_obj = self.pool.get('budget.poa')
        for this in self.browse(cr, uid, ids):
            context = {}
            poa_ids = poa_obj.search(cr, uid, [('date_start','<=',this.date_end),('date_end','>=',this.date_end)])
            if poa_ids:
                poa = poa_obj.browse(cr, uid, poa_ids[0])
                context = {'by_date':True,'date_start': poa.date_start, 'date_end': poa.date_end,'poa_id':poa_ids[0]}
                for rol in this.slip_ids:
                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',rol.contract_id.budget_id.budget_post_id.id),
                                                         ('program_id','=',rol.contract_id.program_id.id),
                                                         ('date_start','<=',rol.date_to),('date_end','>=',rol.date_to)])
                    if item_ids:
                        if not item_ids[0] in dict_partidas:
                            dict_partidas[item_ids[0]] = rol.basic
                        else:
                            dict_partidas[item_ids[0]] += rol.basic
                for partida_id in dict_partidas:
                    budget_item = item_obj.browse(cr, uid, partida_id,context)
                    aux_saldo = budget_item.commited_balance
                    if aux_saldo<=dict_partidas[partida_id]:
                        raise osv.except_osv("Error !", "Error la partida %s no tiene saldo"%(ustr(budget_item.code)))                 
        return True

    def aprobar_payslip_run(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        partner_obj = self.pool.get('res.partner')
        run_obj = self.pool.get('hr.payslip.run')
        user_obj = self.pool.get('res.users')
        slip_obj = self.pool.get('hr.payslip')
        partner_aux = bank_aux = '0'
        i = j = 0
        self.colocar_etiquetas(cr, uid, ids)
        for this in self.browse(cr, uid, ids):
#            self._valida_saldo(cr, uid, ids)
            #mil
#            user = user_obj.browse(cr, uid, uid)
#            if not user.context_department_id.manager_id.user_id.id!=uid:
#                raise osv.except_osv("Error de permisos!", "Usted no es usuario autorizador")
            for line in this.slip_ids:
                if line.net<0:
                    raise osv.except_osv("Error !", "El funcionario %s tiene rol negativo, ejecute la accion replanificar descuentos"%(ustr(line.employee_id.complete_name)))
                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',line.employee_id.name)])
#                if not partner_ids:
#                    partner_aux += line.employee_id.complete_name + ' - '
#                    j += 1
                #partner = partner_obj.browse(cr, uid, partner_ids[0])
                if partner_ids:
                    partner = partner_obj.browse(cr, uid, partner_ids[0])
                    if not len(partner.bank_ids)>0:
                        bank_aux += line.employee_id.complete_name + ' - '
                        i += 1
                else:
                    partner_aux += line.employee_id.complete_name + ' - '
                    j += 1
            if j>0:
                raise osv.except_osv("Error !", "El/Los funcionarios %s debe tener asociado un proveedor"%(ustr(partner_aux)))
            if i>0:
                    raise osv.except_osv("Error !", "El/los funcionario %s debe tener asociado cuenta de banco"%(ustr(bank_aux)))
            run_obj.write(cr, uid, [this.id],{
                'state':'Aprobado',
            })
            for line in this.slip_ids:
                slip_obj.write(cr, uid, line.id,{'state':'Aprobado'})
        return True
         
    def contabilizar_payslip_run(self, cr, uid, ids, context=None):
        return True

    def reversaconta_payslip_run(self, cr, uid, ids, context=None):
        return True
   
    def pagado_payslip_run(self, cr, uid, ids, context=None):
        mail_message = self.pool.get('mail.message')
        parameter_obj = self.pool.get('ir.config_parameter')
        run_obj = self.pool.get('hr.payslip.run')
        rol_obj = self.pool.get('hr.payslip')
        user_obj = self.pool.get('res.users')
        email_from_ids = parameter_obj.search(cr, uid, [('key','=','email_fromtthh')],limit=1)
        if email_from_ids:
            email_from = parameter_obj.browse(cr, uid, email_from_ids[0]).value
        else:
            print "no snd"
            #raise osv.except_osv('Error','No ha configurado la direccion de correo para envio de roles.')
        for this in self.browse(cr, uid, ids):
            run_obj.write(cr, uid, [this.id],{
                'state':'Pagado',
            })
            if email_from_ids:
                user = user_obj.browse(cr, uid, uid)
                #paso a pagado los roles y envio mail
            for rol in this.slip_ids:
                rol_obj.write(cr, uid, rol.id,{'state':'Pagado'})
                for inputs in rol.input_line_ids:
                    if inputs.ie_id:
                        self.pool.get('hr.ie.line').write(cr, uid, inputs.ie_id.id, {'state': 'pagado'}, context=context)
                if email_from_ids:
                    if rol.employee_id.work_email or rol.employee_id.email:
                        razonSocial = user.company_id.name
                        msg = " Estimado  %s, \n\n El rol de pagos de %s ha sido acreditado en su cuenta. \n\n Saludos\n%s,"  %(rol.employee_id.complete_name,rol.period_id.name,razonSocial)
                        vals_msg = {
                            'subject': 'Confirmacion de acreditacion de rol - ' + razonSocial,
                            'body_text': msg,
                            'email_from': email_from,
                            'email_bcc' : rol.employee_id.email,
                            'email_to': rol.employee_id.work_email,
                            'state': 'outgoing',
                        }
                        email_msg_id = mail_message.create(cr, uid, vals_msg, context)
                        try:
                            mail_message.send(cr, uid, [email_msg_id])
                        except:
                            pass
        return True

    def draft_payslip_run(self, cr, uid, ids, context=None):
        
        slip_obj = self.pool.get('hr.payslip')
        run_obj = self.pool.get('hr.payslip.run')
        for this in self.browse(cr, uid, ids):
            run_obj.write(cr, uid, [this.id],{
                'state':'draft',
            })
            for line in this.slip_ids:
                slip_obj.write(cr, uid, line.id,{'state':'draft'})
        return True

    def autorizar_payslip_run(self, cr, uid, ids, context=None):
        run_obj = self.pool.get('hr.payslip.run')
        slip_obj = self.pool.get('hr.payslip')
        r_obj = self.pool.get('hr.salary.rule')
        post_obj = self.pool.get('budget.post')
        rule_obj = self.pool.get('hr.salary.rule.category')
        config_obj = self.pool.get('hr.account.configuration')
        for this in self.browse(cr, uid, ids):
            run_obj.write(cr, uid, [this.id],{
                'state':'Autorizado',
            })
            #validar que  haya configuracion de rubros con partida
#            rules_ids = rule_obj.search(cr, uid, [('name','in',('Basic','Total'))])
            rules_ids = rule_obj.search(cr, uid, [('name','=','Egresos')])
            aux_sql = '''select salary_rule_id,budget_id2 from hr_payslip_line where slip_id in (select id from hr_payslip where payslip_run_id=%s
            ) and category_id=%s group by  salary_rule_id,budget_id2 order by salary_rule_id'''%(this.id,str(rules_ids[0]))
#            aux_sql = '''select salary_rule_id,budget_id2 from hr_payslip_line where slip_id in (select id from hr_payslip where payslip_run_id=%s
#            ) and category_id not in %s group by  salary_rule_id,budget_id2 order by salary_rule_id'''%(this.id,str(tuple(rules_ids)))
            cr.execute(aux_sql)
            result = cr.fetchall()
            for line_res in result:
                config_ids = config_obj.search(cr, uid, [('rule_id','=',line_res[0]),('budget_id','=',line_res[1])])
                if not config_ids:
                    rubro = r_obj.browse(cr, uid, line_res[0])
                    post = post_obj.browse(cr, uid, line_res[1])
                    aux_post = post.code + ' ' + post.name
                    #mensaje = ustr('El rubro %s no tiene configuracion para la partida %s en el menu Partidas por rubro.' %(rubro.name,aux_post))
                    #raise osv.except_osv('Error', mensaje)
            for line in this.slip_ids:
                slip_obj.write(cr, uid, line.id,{'state':'Autorizado'})
    
    def _get_payslips(self, cr, uid, ids, context=None):
        result = {}
        for work in self.pool.get('hr.payslip').browse(cr, uid, ids, context=context):
            if work.payslip_run_id: result[work.payslip_run_id.id] = True
        return result.keys()
    
    _STORE_VAR = {'hr.payslip.run': (lambda self, cr, uid, ids, c={}: ids, ['slip_ids'], 10),
                  'hr.payslip': (_get_payslips, ['basic', 'net', 'allowance', 'deduction', 'aportable', 'provision'], 10)}
    
    def _total_dias_rol(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            inicio = this.date_start.split('-')
            fin = this.date_end.split('-')
            dateinicio = date( int(inicio[0]), int(inicio[1]), int(inicio[2]) )
            datefin = date( int(fin[0]), int(fin[1]), int(fin[2]) )
            delta = datefin - dateinicio
            res[this.id] = delta.days + 1
        return res

    _columns = {
        'contabilizado':fields.boolean('Contabilizado'),
        'normal':fields.boolean('Rol Normal'),
        'basic': fields.function(_calculate_summary, method=True, store=_STORE_VAR, multi='pr', string='Remuneración unificada'),
        'net': fields.function(_calculate_summary, method=True, store=_STORE_VAR, multi='pr', string='Total a recibir'),
        'allowance': fields.function(_calculate_summary, method=True, store=_STORE_VAR, multi='pr', string='Total otros ingresos'),
        'deduction': fields.function(_calculate_summary, method=True, store=_STORE_VAR, multi='pr', string='Total egresos'),
        'aportable': fields.function(_calculate_summary, method=True, store=_STORE_VAR, multi='pr', string='Total otros ingresos aportables'),
        'provision': fields.function(_calculate_summary, method=True, store=_STORE_VAR, multi='pr', string='Total provisiones'),
        #                'basic': fields.float('Remuneración unificada'),
        'net2': fields.float('Total a recibir'),
        #                'allowance': fields.float('Total otros ingresos'),
        #                'deduction': fields.float('Total egresos'),
        #                'aportable': fields.float('Total otros ingresos aportables'),
        #                'provision': fields.float('Total extra rol'),
        'paga_fr':fields.boolean('Paga Fondo Reserva',help='Activa este campo para pagar los fondos de reserva en el rol, aplicado para obreros'),
        'period_id': fields.many2one('hr.work.period.line','Periodo',readonly=True, states={'draft': [('readonly', False)]}),
        'total_dias': fields.function(_total_dias_rol, method=True, string="Total Dias", store=True, type="integer"), 
        'contract_type_id': fields.many2one('hr.contract.type.type','Tipo de contrato',readonly=True, states={'draft': [('readonly', False)]}),
        'state':fields.selection([('draft','Borrador'),('Aprobado','Aprobado'),('Autorizado','Autorizado'),('Pagado','Pagado')],'Estado',readonly=True),
        'no_ids':fields.one2many('no.descontado','run_id','No descontado'),
                }
    
    
    _defaults = {
        'period_id':periodo_de_fecha,
        'normal':True,
    }

hr_payslip_run_ec()


class hr_payslip_employees_ec(osv.osv_memory):

    _inherit ='hr.payslip.employees'
    _description = 'Genera Payslip de todos los empleados seleccionados'
    
    def get_contract_type(self, cr, uid, context={}):
        payroll_id = context.get('active_id')
        obj_payroll = self.pool.get('hr.payslip.run')
        payroll = obj_payroll.browse(cr, uid, payroll_id, context)
        if payroll.contract_type_id:
            return payroll.contract_type_id.id
        return False

    def get_date_start(self, cr, uid, context={}):
        payroll_id = context.get('active_id')
        obj_payroll = self.pool.get('hr.payslip.run')
        payroll = obj_payroll.browse(cr, uid, payroll_id, context)
        return payroll.date_start

    def get_date_end(self, cr, uid, context={}):
        payroll_id = context.get('active_id')
        obj_payroll = self.pool.get('hr.payslip.run')
        payroll = obj_payroll.browse(cr, uid, payroll_id, context)
        return payroll.date_end

    
    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees'),
        'contract_type_id': fields.many2one('hr.contract.type.type','Tipo de contrato'),
        'date_start': fields.date('date start'),
        'date_end': fields.date('date end'),
    }
    
    _defaults = {
                'contract_type_id': get_contract_type,
                'date_start': get_date_start,
                'date_end': get_date_end,
                }
    
    
        
    
    def compute_sheet_respaldo(self, cr, uid, ids, context=None):
        emp_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('hr.payslip')
        run_pool = self.pool.get('hr.payslip.run')
        slip_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, context['active_id'], ['date_start', 'date_end', 'credit_note'])
        from_date =  run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        credit_note = run_data.get('credit_note', False)
        if not data['employee_ids']:
            raise osv.except_osv("Error !", "Debe seleccionar empleados para generar los Roles de Pago")
        for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
            slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False, context=context)
            res = {
                'employee_id': emp.id,
                'name': slip_data['value'].get('name', False),
                'struct_id': slip_data['value'].get('struct_id', False),
                'contract_id': slip_data['value'].get('contract_id', False),
                'payslip_run_id': context.get('active_id', False),
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': credit_note,
            }
            slip_ids.append(slip_pool.create(cr, uid, res, context=context))
        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        run_pool._calculate_summary(cr, uid, [context['active_id']], context)
        return {'type': 'ir.actions.act_window_close'}

hr_payslip_employees_ec()
