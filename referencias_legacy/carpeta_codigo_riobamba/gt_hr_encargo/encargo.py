# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from osv import osv, fields
from datetime import date, datetime, timedelta
from time import strftime
from dateutil.relativedelta import relativedelta
from dateutil import parser

class hr_contract_encargo(osv.osv):
	_name = 'hr.contract.encargo'
	_description = "Registros de Encargo y Subrogaciones a un empleado"
	_columns = {
                'rubro_id':fields.many2one('hr.ie.line','Rubro Detalle'),
		'contract_id': fields.many2one('hr.contract','Contrato del Empleado'),
		'date_start': fields.date('Fecha de inicio'),
		'date_stop': fields.date('Fecha de fin'),
		'job_id': fields.many2one('hr.job','Puesto Encargado', required=True),
		'wage':fields.float('Salario del puesto'),
                'monto':fields.float('Monto Rol'),
		'type':fields.selection([('funciones','Funciones'),('encargo','Encargo'),('subrogacion','Subrogación')],'Tipo de encargo',required=True),
                'period_id':fields.many2one('hr.work.period.line','Periodo Rol'),
                'categ_id':fields.many2one('hr.salary.rule','Rubro Encargo'),
		#'encargo_id': fields.many2one('hr.contract','Contrato encargado'),
		#'job_id': fields.related('encargo_id','job_id', type='many2one', relation='hr.job', string='Puesto Encargado'),
		#'department_id': fields.related('encargo_id','department_id', type='many2one', relation='hr.department', string='Departamento del puesto encargado'),
		#'wage': fields.related('encargo_id','wage', type='float', string='Salario del puesto encargado'),
		#'to_payroll': fields.boolean('Subroga?',help='Activar esta casilla en caso que este empleado obtenga un beneficio economico en rol de pagos por el encargo'),
		'state': fields.selection([('draft','Borrador'),('aprobado','Aprobado'),('rechazado','Rechazado')],'Estado'),
	}
	
	_defaults = {
                'type':'funciones',
                'state':'draft',
        }
	
        def unlink(self, cr, uid, ids, context=None):
                line_obj = self.pool.get('hr.ie.line')
                for obj in self.browse(cr, uid, ids, context):
                        if obj.state=='aprobado':
                                raise osv.except_osv('Aviso','No se permite borrar aprobados.')
                        if obj.rubro_id:
                                line_obj.unlink(cr, uid, [obj.rubro_id.id])
                res = super(hr_contract_encargo, self).unlink(cr, uid, ids, context)
                return res

	def draft_enviado(self, cr, uid, ids, context=None):
		for registro in self.browse(cr, uid, ids, context):
			return self.write(cr, uid, ids, {'state':'solicitado'})
		
	def rechazar(self, cr, uid, ids, context=None):
                line_obj = self.pool.get('hr.ie.line')
		for registro in self.browse(cr, uid, ids, context):
                        if registro.rubro_id:
                                line_obj.write(cr, uid, registro.rubro_id.id,{
                                        'state':'draft',
                                })
                                line_obj.unlink(cr, uid, [registro.rubro_id.id])
			return self.write(cr, uid, ids, {'state':'rechazado'})

        def calcula_subrogacion(self, cr, uid, ids, context=None):
                for this in self.browse(cr, uid, ids):
                        monto = 0
                        sueldo_calculo = this.wage - this.contract_id.wage
                        valor_dia = sueldo_calculo/30
                        inicio = this.date_start.split('-')
                        fin = this.date_stop.split('-')
                        dateinicio = date( int(inicio[0]), int(inicio[1]), int(inicio[2]) )
                        datefin = date( int(fin[0]), int(fin[1]), int(fin[2]) )
                        delta = datefin - dateinicio
                        dias = delta.days + 1
                        monto = valor_dia * dias
                return self.write(cr, uid, ids, {'monto':monto})
		
	def enviado_aprobado(self, cr, uid, ids, context=None):
                ie_line_obj = self.pool.get('hr.ie.line')
		for registro in self.browse(cr, uid, ids, context):
                        contrato = registro.contract_id
                        valor = registro.monto
                        ie_creado = ie_line_obj.create(cr, uid,{                         
                                'name': contrato.employee_id.complete_name,
                                'employee_id': contrato.employee_id.id,
                                'date': registro.date_start,
                                'valor': float("%.2f" % valor),
                                'categ_id': registro.categ_id.id,
                                'period_id': registro.period_id.id,
                                'state': 'pendiente',})
			self.write(cr, uid, ids, {'state':'aprobado','rubro_id':ie_creado,})
		
	def onchange_trabajo(self, cr, uid, ids, job_id, context=None):
		obj_job = self.pool.get('hr.job')
		job = obj_job.browse(cr, uid, job_id, context)
		if job.grupo_id:
			return {'value': {'wage': job.grupo_id.rmu}}
		return False
	
                

hr_contract_encargo()

class inherit_hr_contract_encargo(osv.osv):
    _inherit = 'hr.contract'
    _columns={
        'encargos_ids' : fields.one2many('hr.contract.encargo', 'contract_id','Encargo y Subrogacion'),
	}
inherit_hr_contract_encargo()

