# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
#
##############################################################################

import time
from datetime import datetime
from dateutil import relativedelta

from osv import fields, osv
from tools.translate import _

##envio de mail
class sendMailRol(osv.TransientModel):
    _name = 'send.mail.rol'
    _columns = dict(
        period_id = fields.many2one('hr.work.period.line','Periodo'),
        rol_id = fields.many2one('hr.payslip.run','Rol'),
    )
    def sendRol(self, cr, uid, ids, context):
        for this in self.browse(cr, uid, ids):
            for rol_ind in this.rol_id.line_ids:
                print "send"
        return {'type': 'ir.actions.act_window_close'}

sendMailRol()
##

class replanificarDescuentosLine(osv.TransientModel):
    _name = 'replanificar.descuentos.line'
    _columns = dict(
        rol_id = fields.many2one('replanificar.descuentos','Descuentos'),
        rubro = fields.char('Rubro',size=128),
        valor = fields.float('Monto'),
    )
replanificarDescuentosLine()

class replanificarDescuentos(osv.TransientModel):
    _name = 'replanificar.descuentos'

    def action_replanificar_descuentos(self, cr, uid, ids, context):
        payslip_obj = self.pool.get('hr.payslip')
        ie_line_obj = self.pool.get('hr.ie.line')
        no_desc = self.pool.get('no.descontado')
        replanificar_line_obj = self.pool.get('replanificar.descuentos.line')
        payslip = payslip_obj.browse(cr, uid, context['active_id'])
        for this in self.browse(cr, uid, ids):
            if payslip.net<0:
                diferencia = abs(payslip.net)
                ie_line_ids = ie_line_obj.search(cr, uid, [('employee_id','=',payslip.employee_id.id),('period_id','=',payslip.period_id.id)
                                                           ,('state','=','pendiente')])
                if ie_line_ids:
                    quitar = []
                    aux = 0
                    for line_id in ie_line_ids:
                        ie_line = ie_line_obj.browse(cr, uid, line_id)
                        aux += ie_line.valor
                        if aux>=diferencia:
                            quitar.append(line_id)
                            break
                else:
                    raise osv.except_osv(_("Advertencia !"), _("El funcionario no tiene rubros que replanificar"))
                #payslip_obj.compute_sheet(cr, uid, [payslip.id])
            for quita_id in quitar:
                linea_quitada = ie_line_obj.browse(cr, uid, quita_id)
                replanificar_line_obj.create(cr, uid, {
                    'rubro':linea_quitada.categ_id.name,
                    'valor':linea_quitada.valor,
                    'rol_id':this.id,
                })
                no_desc.create(cr, uid, {
                    'name':linea_quitada.categ_id.name,
                    'valor':linea_quitada.valor,
                    'payslip_id':payslip.id,
                })
                ie_line_obj.write(cr, uid, quita_id,{'state':'draft'})
        return True

    _columns = dict(
        contract_id = fields.many2one('hr.contract','Funcionario'),
        detalle_ids = fields.one2many('replanificar.descuentos.line','rol_id','Descuentos'),
    )
replanificarDescuentos()

class inherit_hr_payslip_employees(osv.osv_memory):

    _inherit ='hr.payslip.employees'
    _columns = {
        'dec_fr':fields.selection([('Decimo','Decimo'),('Fondo Reserva','Fondo Reserva')],'Otro ROL'),
        'contract_ids': fields.many2many('hr.contract', 'hr_contract_group_rel', 'payslip_id', 'contract_id', 'Contratos'),
        'otra_estructura': fields.many2one('hr.payroll.structure','Aplicar otra estructura', help='Seleccionar en el caso que desee que se aplique otra estructura de salario diferente a la del contrato del servidor')
    }
    
    def cargar_empleados(self, cr, uid, ids, contratos, empleados, context={}):
        res = []
        obj_contrato = self.pool.get('hr.contract')
        if contratos:
            for registro in contratos:
                for contrato_id in registro[2]:
                    contrato = obj_contrato.browse(cr, uid, contrato_id)
                    res.append(contrato.employee_id.id)
                
        print res
        return {'value': {'employee_ids': res}}
    
    def compute_sheet(self, cr, uid, ids, context=None):
        emp_pool = self.pool.get('hr.employee')
        obj_contrato = self.pool.get('hr.contract')
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
        if not data['contract_ids']:
            raise osv.except_osv(_("Advertencia !"), _("Debe seleccionar al menos 1 empleado para elaborar el rol"))
        #for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
        lista_emp_no = []
        for contrato in obj_contrato.browse(cr, uid, data['contract_ids'], context=context):
            emp = contrato.employee_id
            if not emp.department_id:
                lista_emp_no.append(emp.complete_name)
        if lista_emp_no:
            str_empleados = ''
            for no_dp in lista_emp_no:
                str_empleados += no_dp + ' - '  
            raise osv.except_osv(("Error de configuracion !"), ("Los funcionarios %s no tiene asignado un departamento") % (str_empleados))
        for contrato in obj_contrato.browse(cr, uid, data['contract_ids'], context=context):
            if data['dec_fr']=='Decimo':
                if contrato.decimo_opc=='Acumular':
                    continue
#            if data['dec_fr']=='Fondo Reserva':
#                if not contrato.fondo_reserva:
#                    continue
            context.update({'contract':True})
            slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, contrato.employee_id.id, contrato.id, context=context)
            encargo_ids1 = self.pool.get('hr.contract.encargo').search(cr, uid, [('contract_id','=',contrato.id),
                                                                                 ('date_start','<=',to_date),
                                                                                 ('date_stop','>=',to_date),
                                                                                 ('state','=','aprobado')])
            encargo_ids2 = self.pool.get('hr.contract.encargo').search(cr, uid, [('contract_id','=',contrato.id),
                                                                                 ('date_start','<=',to_date),
                                                                                 ('date_stop','=',False),
                                                                                 ('state','=','aprobado')])
            encargo_ids = list(set(encargo_ids1 + encargo_ids2))
            department_id = contrato.employee_id.department_id.id
            job_id = contrato.employee_id.job_id.id
#            if encargo_ids:
#                for encargo in self.pool.get('hr.contract.encargo').browse(cr, uid, encargo_ids):
#                    department_id = encargo.job_id.department_id.id
            aux_partida_ind = ''
            if contrato.budget_ind:
                aux_partida_ind = contrato.budget_ind
            res = {
                'employee_id': contrato.employee_id.id,
                'name': slip_data['value'].get('name', False),
                'struct_id': contrato.struct_id.id,
                'contract_id': contrato.id,
                'payslip_run_id': context.get('active_id', False),
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': credit_note,
                'department_id': department_id,
                'program_id':contrato.program_id.id,
                'budget_id':contrato.budget_id.id,
                'budget_id2':contrato.budget_id.budget_post_id.id,
                'budget_id_ind':aux_partida_ind,
                'job_id': job_id,
            }
            slip_ids.append(slip_pool.create(cr, uid, res, context=context))
        if data.has_key('otra_estructura'):
            if data['otra_estructura']!=False:
                context['otra_estructura'] = data['otra_estructura']
            else:
                context['otra_estructura'] = False
        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

inherit_hr_payslip_employees()
