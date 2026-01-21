# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from osv import osv, fields
from tools import ustr
from gt_tool import tool, fechas
from datetime import date, datetime, timedelta
from time import strftime
import decimal_precision as dp

'''
class Desvinculation(osv.osv):
    _name = 'desvinculation'

    _OUT_TYPE = [('contrato','Por las causas legalmente previstas en el contrato'),
                 ('acuerdo','Por acuerdo de las partes'),
                 ('conclusion','Por la conclusión de la obra, período de labor o servicios objeto del contrato'),
                 ('muerte_empleador','Por muerte o incapacidad del empleador o extinción de la persona jurídicamente contratante'),
                 ('muerte_trabajador','Por muerte del trabajador o incapacidad permanente y total del trabajador'),
                 ('fuerza_mayor','Por caso fortuito o fuerza mayor que imposibiliten el trabajo y los contratantes no pudieron preveer o evitar'),
                 ('vbueno_empleador','Por voluntad del empleador previo visto bueno'),
                 ('vbueno_trabajador','Por voluntad del trabajador previo visto bueno'),
                 ('desahucio','Por desahucio'),
                 ('despido','Por despido intempestivo'),]
    
    _columns = dict(
        name = fields.text('Descripción'),
        contract_id = fields.many2one('hr.contract','Contrato'),
        employee_id = fields.related('contract_id','employee_id', type='many2one', 
                                       relation='hr.employee',string='Empleado', store=True),
        date = fields.date('Fecha de Salida'),
        #date_out = fields.date('Fecha salida'),
        out_type = fields.selection(_OUT_TYPE,'Tipo de Salida'),
        #solicitante_id = fields.many2one('hr.employee','Solicitante'),
	#revisado_id =  fields.many2one('hr.employee','Revisado'),
	#aprobado_id = fields.many2one('hr.employee','Aprobado'),
        state = fields.selection([('draft','Borrador'),('confirmed','Confirmado')],'Estado'),
        #memo = fields.text('Motivo Salida'),
        #line_ids =  fields.one2many('desvin.line','desvinculation_id','Lineas'),
        )

Desvinculation()

class desvinculationLine(osv.osv):
    _name='desvinculation.line'
    _columns={
        'name':fields.char('Desc.',size=64),
	'desvinculation_id':fields.many2one('desvinculation','Desvinculacion'),
	'concepto':fields.char('Concepto',size=128),
	'valor':fields.float('Valor'),
	}
desvinculationLine()
'''

class hr_liquidation_line(osv.osv):
    '''
    Liquidation Line
    '''

    _name = 'hr.liquidation.line'
    _description = 'Linea de Liquidación'
    _order = 'contract_id'

    _columns = {
        'liquidation_id':fields.many2one('hr.liquidation.compute', 'Liquidación', required=True, ondelete='cascade'),
        'salary_rule_id':fields.many2one('hr.salary.rule', 'Rubro', required=True),
        'employee_id':fields.many2one('hr.employee', 'Empleado'),
        'contract_id':fields.many2one('hr.contract', 'Contrato',select=True),
        'rate': fields.float('Porcentaje (%)', digits_compute=dp.get_precision('Payroll Rate')),
        'amount': fields.float('Monto', digits_compute=dp.get_precision('Payroll')),
        'quantity': fields.float('Cantidad', digits_compute=dp.get_precision('Payroll')),
    }

    _defaults = {
        'quantity': 1.0,
        'rate': 100.0,
    }

hr_liquidation_line()


class motivoSalida(osv.Model):
    _name = 'motivo.salida'
    _columns = dict(
        name = fields.char('Motivo',size=32,required=True),
    )
motivoSalida()
class hr_liquidation_compute(osv.osv):
    _name = "hr.liquidation.compute"
    
    _columns = {
        'pago_id':fields.many2one('hr.varios','Pago'),
        'create_user_id': fields.many2one('res.users','Creado por'),
        'date': fields.date('Fecha Liquidacion',required=True),
        'name': fields.char('Código', size=20),
        'description': fields.char('Descripción', size=100),
        'contract_id': fields.many2one('hr.contract','Contrato de empleado', required=True),
        'salida_id': fields.many2one('motivo.salida','Motivo de Salida',required=True),
        'state': fields.selection([('draft','Borrador'),
                                   ('Anulado','Anulado'),
                                   ('Liquidado','Liquidado')],'Estado'),
        'line_ids': fields.one2many('hr.liquidation.line', 'liquidation_id', 'Lineas de Liquidación'),
        'mujer_embarazada': fields.boolean('Es mujer embarazada?', help='Active el casillero si se trata de una mujer embarazada'),
        'jefe_sindical': fields.boolean('Es jefe sindical?', help='Active el casillero si se trata de un jefe sindical'),
        'empleador_iess': fields.boolean('Empleador asume IESS?', help='Active el casillero si el empleador asume el valor a pagar al IESS'),
    }
    
    def _get_user(self, cr, uid, ids, context=None):
        return uid

    _defaults = dict(
        create_user_id = _get_user,
        state = 'draft',
        name = '/',
    )

    def anulaLiquidacion(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'Anulado'})
        return True

    def regresaLiquidacion(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'draft'})
        return True

    def liquidaEmpleado(self, cr, uid, ids, context=None):
        pago_obj = self.pool.get('hr.varios')
        pago_line_obj = self.pool.get('hr.varios.line')
        obj_sequence = self.pool.get('ir.sequence')
        partner_obj = self.pool.get('res.partner')
        period_obj = self.pool.get('account.period')
        asset_obj = self.pool.get('account.asset.asset')
        for this in self.browse(cr, uid, ids):
            aux_monto = 0
            for line in this.line_ids:
                aux_monto += line.amount
            asset_ids = asset_obj.search(cr, uid, [('employee_id','=',this.contract_id.employee_id.id)])
            if asset_ids:
                raise osv.except_osv(('Error de usuario !'), ('No puede liquidar el empleado por que tiene activos a cargo'))
            if not this.pago_id:
                aux_desc = 'LIQUIDACION: ' + this.contract_id.employee_id.complete_name
                period_ids = period_obj.search(cr, uid, [('date_start','<=',this.date),('date_stop','>=',this.date)])
                if not period_ids:
                    raise osv.except_osv(('Error de usuario !'), ('No hay periodo definido para la fecha'))
                pago_id = pago_obj.create(cr, uid, {
                    'name':aux_desc,
                    'period_id':period_ids[0],
                })
                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',this.contract_id.employee_id.name)])
                if not partner_ids:
                    raise osv.except_osv(('Error de usuario !'), ('El funcionario no tiene proveedor creado '))
                line_id = pago_line_obj.create(cr, uid, {
                    'name':partner_ids[0],
                    'varios_id':pago_id,
                    'monto':aux_monto,
                    'valor':aux_monto,
                })
            if this.name=='/':
                aux_code = obj_sequence.get(cr, uid, 'hr.liquidation.compute')
                self.write(cr, uid, ids, {
                    'state':'Liquidado',
                    'name':aux_code,
                })
            else:
                self.write(cr, uid, ids, {
                    'state':'Liquidado',
                })
        return True
    
hr_liquidation_compute()

