# -*- coding: utf-8 -*-
##############################################################################
#
# GADMLI
#
##############################################################################

from osv import osv, fields
import time
import netsvc
from gt_tool import tool

class notificaPersonales(osv.TransientModel):
    _name = 'notifica.personales'
    _columns = dict(
        period_id = fields.many2one('hr.work.period','Anio Fiscal'),
    )

    def send_personal_notification(self, cr, uid, ids, context=None):
        mail_message = self.pool.get('mail.message')
        parameter_obj = self.pool.get('ir.config_parameter')
        user_obj = self.pool.get('res.users')
        contract_obj = self.pool.get('hr.contract')
        contract_ids = contract_obj.search(cr, uid, [('activo','=',True)])
        email_from_ids = parameter_obj.search(cr, uid, [('key','=','email_fromtthh')],limit=1)
        if email_from_ids:
            email_from = parameter_obj.browse(cr, uid, email_from_ids[0]).value
        else:
            raise osv.except_osv('Error','No ha contratado esta funcionalidad comuniquese con el administrador del sistema.')
        wage_limit = 800
        limit_ids = parameter_obj.search(cr, uid, [('key','=','wage_limit')],limit=1)
        if limit_ids:
            wage_limit = parameter_obj.browse(cr, uid, limit_ids[0]).value
        user = user_obj.browse(cr, uid, uid)
        for this in self.browse(cr, uid, ids):
            if this.period_id.habilita_proyeccion:
                if contract_ids:
                    for contract_id in contract_ids:
                        contract = contract_obj.browse(cr, uid, contract_id)
                        if contract.employee_id.work_email or contract.employee_id.email and contract.wage>=wage_limit:
                            razonSocial = user.company_id.name
                            aux_year = this.period_id.name
                            aux_name = contract.employee_id.complete_name
                            msg = " Estimado  %s, \n\n Por favor ingresar la informacion de gastos personales para el periodo %s \nPuede hacerlo en el sistema desde el menu: Gestion Documental-->Empleados-->Gastos personales-->Registrar\n Saludos Cordiales"  %(aux_name,aux_year)
                            vals_msg = {
                                'subject': 'Notificacion de TTHH - ' + razonSocial,
                                'body_text': msg,
                                'email_from': email_from,
                                'email_bcc' : contract.employee_id.email,
                                'email_to': contract.employee_id.work_email,
                                'state': 'outgoing',
                            }
                            email_msg_id = mail_message.create(cr, uid, vals_msg, context)
                            try:
                                mail_message.send(cr, uid, [email_msg_id])
                            except:
                                pass

notificaPersonales()

class funcionarioWorkPeriod(osv.Model):
    _inherit = 'hr.work.period'
    _columns = dict(
        habilita_proyeccion = fields.boolean('Habilitar Carga Gastos Personales'),
    )
funcionarioWorkPeriod()

class funcionarioProyeccion(osv.Model):
    _name = 'funcionario.proyeccion'

    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            if formulario.state != 'Borrador':
                raise osv.except_osv('Error', 'No pueden eliminar solicitudes que han iniciado proceso')
            else:
                return super(funcionarioProyeccion, self).unlink(cr, uid, ids, context)

    def create(self, cr, uid, vals, context=None):
        period_obj = self.pool.get('hr.work.period')
        period = period_obj.browse(cr, uid, vals['year_id']) 
        if not period.habilita_proyeccion:
            raise osv.except_osv('Error de acceso', 'No esta habilitado el periodo seleccionado para cargar proyecciones de gastos personales')
        else:
            return super(funcionarioProyeccion, self).create(cr, uid, vals, context)

    _columns = dict(
        creado_id = fields.many2one('res.users','Creado por'),
        name = fields.many2one('hr.employee','Funcionario'),
        year_id = fields.many2one('hr.work.period','Anio Fiscal'),
        projection_id = fields.many2one('hr.deduction','Concepto Deduccion'),
        amount = fields.float('Monto'),
        state = fields.selection([('Borrador','Borrador'),('Registrado','Registrado'),('Revisado','Revisado')],'Estado'),
    )

    def proyeccionRegistro(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{'state':'Registrado'})
        return True

    def proyeccionRevisado(self, cr, uid, ids, context=None):
        #creo la linea en el empleado
        anual_obj = self.pool.get('hr.anual.projection')
        line_obj = self.pool.get('hr.projection.line')
        self.write(cr, uid, ids,{'state':'Revisado'})
        for this in self.browse(cr, uid, ids):
            anual_ids = anual_obj.search(cr, uid, [('fy_id','=',this.year_id.id),('employee_id','=',this.name.id)])
            if anual_ids:
                line_obj.create(cr, uid, {
                    'value':this.amount,
                    'pl_id':anual_ids[0],
                    'projection_id':this.projection_id.id,
                })
            else:
                aux_desc = 'Gastos Personales ' + this.year_id.name
                anual_id = anual_obj.create(cr, uid, {
                    'name':aux_desc,
                    'fy_id':this.year_id.id,
                    'employee_id':this.name.id,
                })
                line_obj.create(cr, uid, {
                    'value':this.amount,
                    'pl_id':anual_id,
                    'projection_id':this.projection_id.id,
                })
        return True

    def _get_uid(self, cr, uid, ids, context=None):
        return uid

    def _get_empleado(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        if user.employee_id:
            return user.employee_id.id
        else:
            raise osv.except_osv(('Error de configuracion !'), ('El usuario logeado no tiene asociado un empleado'))

    _defaults = dict(
        state = 'Borrador',
        name = _get_empleado,
        creado_id = _get_uid,
    )
funcionarioProyeccion()

class verificar_funcionario(osv.TransientModel):
    _name = 'verificar.funcionario'

    def onchange_verificar_funcionario(self, cr, uid, ids, empleado_id, context={}):
        res = {}
        if empleado_id:
            item_obj = self.pool.get('hr.employee')
            item = item_obj.browse(cr, uid, empleado_id,context=context)
            return {'value':{'direccion':item.address,'correop':item.email,'correot':item.work_email,
                             'departamento':item.department_id.name,'puesto':item.job_id.name,'telefonocasa':item.house_phone,
                             'telefonocelular':item.mobile_phone,
                             'cumple':item.birthday,'diasd':item.total_normal,'diast':item.tomados}}
        else:
            return res

    _columns = dict(
        empleado_id=fields.many2one('hr.employee','Empleado'),
        puesto = fields.char('Puesto de Trabajo', size=200),
        #titulo = fields.char('Titulo', size=200),
        telefonocasa = fields.char('Telefono Convencional',size=15),
        telefonocelular = fields.char('Telefono Celular',size=15),
        direccion = fields.char('Direccion',size=256),
        correop = fields.char('Correo Personal', size=240),
        correot = fields.char('Correo del Trabajo', size=240),
        departamento = fields.char('Departamento', size=128),
        cumple = fields.date('Fecha de Nacimiento'),
        diasd = fields.float('Dias Disponibles'),
        diast = fields.float('Dias Tomados'),

    )


    def _get_empleado(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        employee_id = False
        if user.employee_id:
            employee_id = user.employee_id.id
        return employee_id
    
    _defaults = dict(
        empleado_id = _get_empleado,
    )
    
verificar_funcionario()

