# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo 
# mariofchogllo@gmail.com
#
##############################################################################
from tools import ustr
from osv import fields, osv
from time import strftime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
import netsvc
import datetime
from tools.safe_eval import safe_eval as eval
from gt_tool import fechas
import time
from gt_tool import XLSWriter

class calculoVacacionesLine(osv.Model):
    _name = 'calculo.vacaciones.line'
    _order = 'complete_name asc'
    _columns = dict(
        v_id = fields.many2one('calculo.vacaciones','Vacaciones'),
        employee_id = fields.many2one('hr.employee','Empleado'),
        complete_name = fields.related('employee_id','complete_name',type='char',size=256,store=True),
        dias = fields.float('Dias',digits=(14,8)),
        date = fields.date('Fecha'),
    )
calculoVacacionesLine()
class calculoVacaciones(osv.Model):
    _name = 'calculo.vacaciones'
    _columns = dict(
        name = fields.date('Desde'),
        hasta = fields.date('Hasta'),
        line_ids = fields.one2many('calculo.vacaciones.line','v_id','Detalle'),
        state = fields.selection([('Borrador','Borrador'),('Ejecutado','Ejecutado')],'Estado')
    )

    def computeDiasVacaciones(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('calculo.vacaciones.line')
        contract_obj = self.pool.get('hr.contract')
        contract_ids = contract_obj.search(cr, uid, [('activo','=',True)])
        for this in self.browse(cr, uid, ids):
            lines_antes = line_obj.search(cr, uid, [('v_id','=',this.id)])
            if lines_antes:
                line_obj.unlink(cr, uid, lines_antes)
            if contract_ids:
                for contract_id in contract_ids:
                    contrato = contract_obj.browse(cr, uid, contract_id)
                    ahora = 0
                    if contrato.type_id.name=='LOSEP':
                        ahora = 0.083333333
                    else:
                        ahora = 0.041666667
                    line_obj.create(cr, uid, {
                        'date':this.name,
                        'v_id':this.id,
                        'employee_id':contrato.employee_id.id,
                        'dias':ahora,
                    })
        return True

    def executeVacaciones(self, cr, uid, ids, context=None):
        holiday_obj = self.pool.get('holidays.period')
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                holidays_ids = holiday_obj.search(cr, uid, [('employee_id','=',line.employee_id.id),
                                                            ('date_start','<=',line.date),('date_stop','>=',line.date)])
                if holidays_ids:
                    holiday = holiday_obj.browse(cr, uid, holidays_ids[0])
                    ahora = 0
                    antes = holiday.days_normal
                    ahora = antes + line.dias
                    holiday_obj.write(cr, uid, holidays_ids[0],{
                        'days_normal':ahora,
                    })
        self.write(cr, uid, ids, {'state':'Ejecutado'})
        return True

    _defaults = dict(
        name = time.strftime('%Y-%m-%d'),
        hasta = time.strftime('%Y-%m-%d'),
    )
calculoVacaciones()

#saldo vacaciones
class saldoVacLine(osv.TransientModel):
    _name = 'saldo.vac.line'
    _columns = dict(
        r_id = fields.many2one('saldo.vacempleado','Saldo'),
        employee_id = fields.many2one('hr.employee','Funcionario'),
        dias = fields.integer('Dias Disponibles'),
    )
saldoVacLine()

class saldoVacEmpleado(osv.TransientModel):
    _name = 'saldo.vacempleado'
    _columns = dict(
        line_ids = fields.one2many('saldo.vac.line','r_id','Detalle'),
        datas = fields.binary('Archivo'),
        datas_fname = fields.char('Nombre archivo', size=32),
    )

    def exporta_saldovac(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        for this in self.browse(cr, uid, ids):
            self.calcula_saldovac(cr, uid, ids)
            writer = XLSWriter.XLSWriter()
            writer.append(['SALDO VACACIONES'])
            for line in this.line_ids:
                writer.append(['FUNCIONARIO',line.employee_id.complete_name])
                total_empleado = 0
                for line_vaca in line.employee_id.holidays_ids:
                    total_empleado += line_vaca.days_normal
                    writer.append([line_vaca.name,line_vaca.days_normal])
                writer.append(['TOTAL EMPLEADO',total_empleado])
        writer.save("saldoVacaciones.xls")
        out = open("saldoVacaciones.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'datas': out, 'datas_fname': 'saldoVacaciones.xls'})
        return True           

    def calcula_saldovac(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        line_obj = self.pool.get('saldo.vac.line')
        for this in self.browse(cr, uid, ids):
            lineas_antes = line_obj.search(cr, uid, [('r_id','=',this.id)])
            if lineas_antes:
                line_obj.unlink(cr, uid, lineas_antes)
            employee_ids = employee_obj.search(cr, uid, [('total_normal','>',0)])
            if employee_ids:
                for employee_id in employee_ids:
                    empleado = employee_obj.browse(cr, uid, employee_id)
                    line_obj.create(cr, uid, {
                        'employee_id':empleado.id,
                        'dias':empleado.total_normal,
                        'r_id':this.id,
                    })
        return True

saldoVacEmpleado()


#reporte de saldo vacaciones por tipo relacion laboral
class saldoRelabLine(osv.TransientModel):
    _name = 'saldo.relab.line'
    _columns = dict(
        r_id = fields.many2one('saldo.relab','Saldo'),
        employee_id = fields.many2one('hr.employee','Funcionario'),
        dias = fields.integer('Dias Disponibles'),
    )
saldoRelabLine()

class saldoVacRelLab(osv.TransientModel):
    _name = 'saldo.relab'
    _columns = dict(
        tipo_id = fields.many2one('hr.contract.type','Tipo Relacion Laboral'),
        opcion = fields.selection([('Todo','Todo'),('m60','>60'),('m90','>90')],'Opcion'),
        line_ids = fields.one2many('saldo.relab.line','r_id','Detalle'),
    )

    def calcula_saldorelab(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        line_obj = self.pool.get('saldo.relab.line')
        for this in self.browse(cr, uid, ids):
            lineas_antes = line_obj.search(cr, uid, [('r_id','=',this.id)])
            if lineas_antes:
                line_obj.unlink(cr, uid, lineas_antes)
            employee_ids = employee_obj.search(cr, uid, [('total_normal','>',0)])
            if employee_ids:
                if this.tipo_id.name in ('LOSEP','Losep','losep'):
                    contract_ids = contract_obj.search(cr, uid, [('employee_id','in',employee_ids),('type_id.name','in',('LOSEP','Losep','losep'))])
                    if contract_ids:
                        for contract_id in contract_ids:
                            contrato = contract_obj.browse(cr, uid, contract_id)
                            if contrato.employee_id.total_normal>=60:
                                line_obj.create(cr, uid, {
                                    'r_id':this.id,
                                    'employee_id':contrato.employee_id.id,
                                    'dias':contrato.employee_id.total_normal,
                                })
                else:
                    contract_ids = contract_obj.search(cr, uid, [('employee_id','in',employee_ids),('type_id.name','not in',('LOSEP','Losep','losep'))])
                    if contract_ids:
                        for contract_id in contract_ids:
                            contrato = contract_obj.browse(cr, uid, contract_id)
                            if contrato.employee_id.total_normal>=90:
                                line_obj.create(cr, uid, {
                                    'r_id':this.id,
                                    'employee_id':contrato.employee_id.id,
                                    'dias':contrato.employee_id.total_normal,
                                })
        return True

saldoVacRelLab()
##atrasos
class holidayAtraso(osv.Model):
    _name = 'holiday.atraso'
    _columns = dict(
        name = fields.many2one('hr.employee','Funcionario',required=True),
        date = fields.date('Fecha',required=True),
        minutos = fields.integer('Total Minutos'),
        estado = fields.selection([('Realizado','Realizado'),('Liquidado','Liquidado')],'Estado'),
        ref = fields.char('Referencia',size=5),
    )

    def unlink(self, cr, uid, ids, *args, **kwargs):
        for this in self.browse(cr, uid, ids):
            if this.estado=='Liquidado':
                raise osv.except_osv('Error de usuario', 'No puede eliminar el registro ya liquidado')
            else:
                return super(holiday.atraso, self).unlink(cr, uid, ids , context=None)

    _defaults = dict(
        estado = 'Realizado',
    )
holidayAtraso()
##
class liquidaAtraso(osv.Model):
    _name = 'liquida.atraso'
    _description = 'Liquidacion de atrasos'
    _columns = dict(
        code = fields.char('Numero',size=5),
        name = fields.many2one('hr.employee','Funcionario',required=True),
        state = fields.selection([('Borrador','Borrador'),('Liquidado','Liquidado')],'Estado'),
        date = fields.date('Fecha'),
        line_ids = fields.many2many('holiday.atraso','a_l_id','a_id','l_id','Detalle Liquidacion'),
        saldo_id = fields.many2one('holidays.period','Saldo Vacaciones',required=True),
        total_dias = fields.integer('Total Dias'),
        total_minutos = fields.integer('Total Minutos'),
    )

    def calcula_atraso(self, cr, uid, ids, context=None):
        liquida_obj = self.pool.get('liquida.atraso')
        atraso_obj= self.pool.get('holiday.atraso')
        for this in self.browse(cr, uid, ids):
            aux_minutos = saldo_min = 0
            for line in this.line_ids:
                if line.name.id!=this.name.id:
                    raise osv.except_osv(('Error de usuario !'), ('Cuando selecciona el detalle debe asegurarse que sea del mismo funcionario al parecer algun registro esta con funcionario diferente'))
                aux_minutos += line.minutos
            dias = aux_minutos//480
            saldo_min = aux_minutos % 480
        liquida_obj.write(cr, uid, ids, {
            'total_dias':dias,
            'total_minutos':saldo_min,
        })
        return True

    def liquida_atraso(self, cr, uid, ids, context=None):
        dias_obj= self.pool.get('holidays.period')
        atraso_obj= self.pool.get('holiday.atraso')
        for this in self.browse(cr, uid, ids):
            if not this.total_dias>0:
                raise osv.except_osv(('Error de usuario !'), ('No tiene dias a liquidar, asegurese que el total de atrasos marcados sumen al menos un dia y/o verifique que antes de liquidar dio click en le boton calcular'))
            aux_tomados = this.saldo_id.tomados_normal
            if this.saldo_id.days_normal>0:
                aux_saldo  = this.saldo_id.days_normal - this.saldo_id.tomados_normal
                if not aux_saldo>=0:
                    raise osv.except_osv(('Error de usuario !'), ('No tiene numero suficientes de dias disponibles'))
            else:
                raise osv.except_osv(('Error de usuario !'), ('No tiene numero suficientes de dias disponibles'))
            numero_dias = aux_tomados + this.total_dias
            dias_obj.write(cr, uid, this.saldo_id.id,{'tomados_normal':numero_dias})
            if this.code=='/':
                obj_sequence = self.pool.get('ir.sequence')
                aux_numero = obj_sequence.get(cr, uid, 'liquida.atraso')
                self.write(cr, uid, ids[0],{'state':'Liquidado','code':aux_numero})
            else:
                self.write(cr, uid, ids[0],{'state':'Liquidado'})
            for line in this.line_ids:
                atraso_obj.write(cr, uid, line.id,{'estado':'Liquidado'})
            #saldo de minutos
            atraso_obj.create(cr, uid, {
                'name':this.name.id,
                'date':time.strftime('%Y-%m-%d'),
                'minutos':this.total_minutos,
                'ref':this.code,
            })
        return True        
    

    _defaults = dict(
        date = time.strftime('%Y-%m-%d'),
        state = 'Borrador',
        code='/',
    )
liquidaAtraso()

#iquidacion de permisos de horas
class liquidaPermiso(osv.Model):
    _name = 'liquida.permiso'
    _description = 'Liquidacion de permisos horas'
    _columns = dict(
        code = fields.char('Numero',size=5),
        name = fields.many2one('hr.employee','Funcionario',required=True),
        state = fields.selection([('Borrador','Borrador'),('Liquidado','Liquidado')],'Estado'),
        date = fields.date('Fecha'),
        line_ids = fields.many2many('permiso.hora','p_l_id','p_id','l_id','Detalle Liquidacion'),
        saldo_id = fields.many2one('holidays.period','Saldo Vacaciones',required=True),
        total_dias = fields.integer('Total Dias'),
        total_minutos = fields.integer('Total Horas'),
    )

    def calcula_atraso(self, cr, uid, ids, context=None):
        liquida_obj = self.pool.get('liquida.permiso')
        atraso_obj= self.pool.get('holiday.atraso')
        for this in self.browse(cr, uid, ids):
            aux_horas = saldo_min = 0
            for line in this.line_ids:
                if line.employee_id.id!=this.name.id:
                    raise osv.except_osv(('Error de usuario !'), ('Cuando selecciona el detalle debe asegurarse que sea del mismo funcionario al parecer algun registro esta con funcionario diferente'))
                aux_horas += line.total_horas
            dias = aux_horas//8
            saldo_min = aux_horas % 8
        liquida_obj.write(cr, uid, ids, {
            'total_dias':dias,
            'total_minutos':saldo_min,
        })
        return True

    def liquida_permiso(self, cr, uid, ids, context=None):
        dias_obj= self.pool.get('holidays.period')
        permiso_obj= self.pool.get('permiso.hora')
        for this in self.browse(cr, uid, ids):
            if not this.total_dias>0:
                raise osv.except_osv(('Error de usuario !'), ('No tiene dias a liquidar, asegurese que el total de atrasos marcados sumen al menos un dia y/o verifique que antes de liquidar dio click en le boton calcular'))
            aux_tomados = this.saldo_id.tomados_normal
            if this.saldo_id.days_normal>0:
                aux_saldo  = this.saldo_id.days_normal - this.saldo_id.tomados_normal
                if not aux_saldo>=0:
                    raise osv.except_osv(('Error de usuario !'), ('No tiene numero suficientes de dias disponibles'))
            else:
                raise osv.except_osv(('Error de usuario !'), ('No tiene numero suficientes de dias disponibles'))
            numero_dias = aux_tomados + this.total_dias
            dias_obj.write(cr, uid, this.saldo_id.id,{'tomados_normal':numero_dias})
            if this.code=='/':
                obj_sequence = self.pool.get('ir.sequence')
                aux_numero = obj_sequence.get(cr, uid, 'liquida.atraso')
                self.write(cr, uid, ids[0],{'state':'Liquidado','code':aux_numero})
            else:
                self.write(cr, uid, ids[0],{'state':'Liquidado'})
            for line in this.line_ids:
                permiso_obj.write(cr, uid, line.id,{'liquidado':True})
        return True        
    

    _defaults = dict(
        date = time.strftime('%Y-%m-%d'),
        state = 'Borrador',
        code='/',
    )
liquidaPermiso()

class workedDays(osv.Model):
    _inherit = 'hr.payslip.worked_days'
    _columns = dict(
        employee_id = fields.related('contract_id','employee_id',type='many2one',relation='hr.employee',string="Empleado",store=True),
        period_id = fields.related('payslip_id','period_id',type='many2one',relation='hr.work.period.line',string='Periodo',store=True),
    )
workedDays()

class gt_hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
    _order = 'name asc'
    _columns = {
        'code': fields.char('Codigo', size=15, help='Valor mediante el cual este tipo de ausencia será reconocido en las reglas salariales'),
        'max': fields.integer('Maximo de dias', 
                              help='Valor maximo de dias de ausencia continuos que un empleado puede tomar por este tipo, si es 0 aplicara como indefinido')
    }
gt_hr_holidays_status()


class holidays_period(osv.osv):
    _name = 'holidays.period'
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.name + " -DIAS DISPONIBLES: " + str(record.days_normal-record.tomados_normal)
            res.append((record.id, name))
        return res

    _columns = {
        'detalle_ids':fields.one2many('descuenta.holy','holi_id','Descuento'),
        'name': fields.char('Periodo', size=40),
        'employee_id': fields.many2one('hr.employee', 'Empleado'),
        'date_start': fields.date('Fecha inicial periodo'),
        'date_stop': fields.date('Fecha final periodo'),
        'days_normal': fields.float('Días de vacaciones',digits=(14,8)),
        'days_extra': fields.float('Días adicionales de vacaciones'),
        'days_prop_normal': fields.float('Días proporcionales'),
        'days_prop_extra': fields.float('Días proporcionales adicionales'),
        'tomados_normal': fields.float('Días ya tomados'),
        'tomados_extra': fields.float('Días adicionales ya tomados'),
        'asignacion_vacaciones_id' : fields.many2one('hr.holidays', 'Asignación de Vacaciones'),
    }
    
    def create2(self, cr, uid, data, context=None):
        obj_holidays = self.pool.get("hr.holidays")
        #crear peticion de asignacion
        holiday_id = obj_holidays.create(cr, uid, {'name': data['name'],
                                                         'employee_id': data['employee_id'],
                                                         'holiday_status_id': 1,
                                                         'number_of_days_temp': data['days_normal'] + data['days_extra'],
                                                         'holiday_type': 'employee',
                                                         'type': 'add'})
        data['asignacion_vacaciones_id'] = holiday_id
        #validamos la asignacion de vacaciones
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'hr.holidays', holiday_id, 'confirm', cr)
        wf_service.trg_validate(uid, 'hr.holidays', holiday_id, 'validate', cr)
        #finalmente creamos la linea de vacaciones en el empleado, la cual está relacionada a la asignacion en la seccion de ausencias
        new_id = super(holidays_period, self).create(cr, uid, data, context=context)
        return new_id
    
    _defaults = {
                 'days_normal': 0,
                 'days_extra': 0,
                 'days_prop_normal': 0,
                 'days_prop_extra': 0,
                 'tomados_normal': 0,
                 'tomados_extra': 0,
                 }
    
holidays_period()

class hr_employee_holidays(osv.osv):
    _inherit = 'hr.employee'
    
    def _vacaciones_tomadas(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for this in self.browse(cr, uid, ids):
            total = 0
            for detalle_vacaciones in this.holidays_ids:
                total += (detalle_vacaciones.tomados_normal + detalle_vacaciones.tomados_extra) 
            result[this.id] = total
        return result
    
    def _vacaciones_normal(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for this in self.browse(cr, uid, ids):
            total = 0
            for detalle_vacaciones in this.holidays_ids:
                total += detalle_vacaciones.days_normal
                total -= detalle_vacaciones.tomados_normal
            result[this.id] = total
        return result
    
    def _vacaciones_extra(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for this in self.browse(cr, uid, ids):
            total = 0
            for detalle_vacaciones in this.holidays_ids:
                total += detalle_vacaciones.days_extra
                total -= detalle_vacaciones.tomados_extra
            result[this.id] = total
        return result
    
    def _proporcional_normal(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for this in self.browse(cr, uid, ids):
            total = 0
            for detalle_vacaciones in this.holidays_ids:
                total += detalle_vacaciones.days_normal
                total -= detalle_vacaciones.tomados_normal
            result[this.id] = total
        return result
    
    def _proporcional_extra(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for this in self.browse(cr, uid, ids):
            total = 0
            for detalle_vacaciones in this.holidays_ids:
                total += detalle_vacaciones.days_extra
                total -= detalle_vacaciones.tomados_extra
            result[this.id] = total
        return result
    
    def _get_holidays(self, cr, uid, ids, context):
        result = {}
        for holiday in self.pool.get('holidays.period').browse(cr, uid, ids, context=context):
            result[holiday.employee_id.id] = True
        return result.keys()
    
    STORE_VACS = {'holidays.period': (_get_holidays,
                                      ['days_normal','days_extra','tomados_normal','tomados_extra'], 10),
                  }
    
    _columns = {
                'holidays_ids': fields.one2many('holidays.period', 'employee_id', 'Detalle de Vacaciones'),
                'total_normal': fields.function(_vacaciones_normal, method=True, string="Días disponibles", store=STORE_VACS, type="float"),
                'total_extra': fields.function(_vacaciones_extra, method=True, string="Días adicionales disponibles", store=STORE_VACS, type="float"),
                'proporcional_normal': fields.function(_proporcional_normal, method=True, string="Proporcional", store=STORE_VACS, type="float"),
                'proporcional_extra': fields.function(_proporcional_extra, method=True, string="Proporcional adicionales", store=STORE_VACS, type="float"),
                'total_extra': fields.float('Total de dias adicionales'),
                'tomados': fields.function(_vacaciones_tomadas, method=True, string="Total de dias tomados", store=False, type="float"),
                }
    
    def tarea_actualizar_vacaciones_god(self, cr, uid, context=None):
        contract_obj = self.pool.get('hr.contract')
        holiday_obj = self.pool.get('holidays.period')
        print "HACE"
        fecha_actual = time.strftime('%Y-%m-%d')
        contract_ids = contract_obj.search(cr, uid, [('activo','=',True)])
        if contract_ids:
            for contract_id in contract_ids:
                contrato = contract_obj.browse(cr, uid, contract_id)
                holidays_ids = holiday_obj.search(cr, uid, [('employee_id','=',contrato.employee_id.id),
                                                            ('date_start','<=',fecha_actual),('date_stop','>=',fecha_actual)])
                if holidays_ids:
                    holiday = holiday_obj.browse(cr, uid, holidays_ids[0])
                    ahora = 0
                    antes = holiday.days_normal
                    if contrato.type_id.name=='LOSEP':
                        ahora = antes + 0.083333333
                    else:
                        ahora = antes + 0.041666667
                    holiday_obj.write(cr, uid, holidays_ids[0],{
                        'days_normal':ahora,
                    })
        return True
    
    #def tarea_actualizar_vacaciones(self, cr, uid, ids, context=None):
    def tarea_actualizar_vacaciones_2(self, cr, uid, context=None):
        obj_configuration = self.pool.get('hr.base.configuration')
        obj_contrato = self.pool.get('hr.contract')
        obj_periodo = self.pool.get('holidays.period')
        ids_contratos = obj_contrato.search(cr, uid, [('active','=',True)])
        ids_configuration = obj_configuration.search(cr, uid, [('activo', '=', True)], limit=1, context=context)
        if ids_configuration:
            dias_vacaciones = obj_configuration.browse(cr, uid, ids_configuration[0], context).min_vacation 
            #print dias_vacaciones
            for contrato in obj_contrato.browse(cr, uid, ids_contratos, context):
                time_contrato = datetime.datetime.strptime(contrato.date_start, "%Y-%m-%d")
                time_actual = datetime.datetime.today()
                resultado = time_actual - time_contrato
                if resultado.days:
                    if resultado.days>365:
                        #print resultado.days%365.0
                        if (resultado.days%365.0) == 0:
                            periodo_inicio = datetime.datetime(year=time_contrato.year+(resultado.days//365)-1, month=time_contrato.month, day=time_contrato.day)
                            periodo_inicio = periodo_inicio + datetime.timedelta(days=(-1))
                            periodo_fin = datetime.datetime(year=time_contrato.year+(resultado.days//365), month=time_contrato.month, day=time_contrato.day)
                            periodo_fin = periodo_fin + datetime.timedelta(days=(-1))
                            ids_periodo = obj_periodo.search(cr, uid, [('employee_id','=',contrato.employee_id.id),
                                                                       ('date_start','=',periodo_inicio),
                                                                       ('date_stop','=',periodo_fin)])
                            if not(ids_periodo):
                                obj_periodo.create(cr, uid, {'name': 'Periodo: ' + str(periodo_inicio)[:10] + ' - ' + str(periodo_fin)[:10],
                                                             'employee_id': contrato.employee_id.id,
                                                             'date_start': periodo_inicio,
                                                             'date_stop': periodo_fin,
                                                             'days_normal': dias_vacaciones}, context)
                    
    def tarea_actualizar_vacaciones_20140317(self, cr, uid, context=None):
        obj_contrato = self.pool.get('hr.contract')
        obj_periodo = self.pool.get('holidays.period')
        time_actual = datetime.datetime.today()
        ids_contratos = obj_contrato.search(cr, uid, [('date_start','<=',str(time_actual)),
                                                      '|',
                                                      ('date_end','>=',str(time_actual)),
                                                      ('date_end','=',False)])
        #import pdb
        #pdb.set_trace()
        for contrato in obj_contrato.browse(cr, uid, ids_contratos, context):
            time_contrato = datetime.datetime.strptime(contrato.continuidad_desde, "%Y-%m-%d")
            localdict = {'employee': contrato.employee_id, 'contract': contrato, 'date_time': fechas}
            dias_normales = 0
            dias_adicionales = 0
            prop_normales = 0
            prop_adicionales = 0
            try:
                eval(contrato.type_id.formula_normales, localdict, mode='exec', nocopy=True)
                dias_normales = localdict['result']
                eval(contrato.type_id.formula_adicionales, localdict, mode='exec', nocopy=True)
                dias_adicionales = localdict['result']
            except:
                raise osv.except_osv('Error de cómputo', 'Las expresiones python para el cómputo de vacaciones, es erroneo')
            
            periodo_fin = datetime.datetime(year=time_contrato.year+1, month=time_contrato.month, day=time_contrato.day)
            periodo_fin = periodo_fin + datetime.timedelta(days=(-1))
            while periodo_fin < time_actual:
                periodo_fin = datetime.datetime(year=periodo_fin.year+1, month=periodo_fin.month, day=periodo_fin.day)
                periodo_fin = periodo_fin + datetime.timedelta(days=(-1))
            periodo_inicio = datetime.datetime(year=periodo_fin.year-1, month=periodo_fin.month, day=periodo_fin.day)
            periodo_inicio = periodo_inicio + datetime.timedelta(days=(+1))
            nombre = 'Periodo: ' + str(periodo_inicio)[:10] + ' - ' + str(periodo_fin)[:10]
            print nombre
            if periodo_fin.day == time_actual.day and periodo_fin.month == time_actual.month and periodo_fin.year == time_actual.year:
                pass
            else:
                dias_proporcionales = (time_actual - periodo_inicio).days
                prop_normales = (dias_normales*dias_proporcionales)/365.0
                prop_adicionales = (dias_adicionales*dias_proporcionales)/365.0
                dias_normales = 0
                dias_adicionales = 0
            ids_periodo = obj_periodo.search(cr, uid, [('name','=',nombre),
                                                       ('employee_id','=',contrato.employee_id.id)])
            if not ids_periodo:
                ids_periodo = [obj_periodo.create(cr, uid, {'name': nombre,
                                                            'employee_id': contrato.employee_id.id,
                                                            'date_start': periodo_inicio,
                                                            'date_stop': periodo_fin,})]
            obj_periodo.write(cr, uid, ids_periodo, {'days_normal':dias_normales,
                                                     'days_extra':dias_adicionales,
                                                     'days_prop_normal':prop_normales,
                                                     'days_prop_extra':prop_adicionales,
                                                     })
            
    def boton_actualizar_vacaciones_aux(self, cr, uid, ids, context=None):
        obj_contrato = self.pool.get('hr.contract')
        obj_periodo = self.pool.get('holidays.period')
        time_actual = datetime.datetime.today()
        ids_contratos = []
        for this in self.browse(cr, uid, ids):
            ids_contratos1 = obj_contrato.search(cr, uid, [('date_start','<=',str(time_actual)),('employee_id','=',ids[0]),('date_end','>=',str(time_actual))])
            ids_contratos2 = obj_contrato.search(cr, uid, [('date_start','<=',str(time_actual)),('date_end','=',False),('employee_id','=',ids[0])])
            ids_contratos = ids_contratos1 + ids_contratos2
        cr.execute("delete from holidays_period")
        for contrato in obj_contrato.browse(cr, uid, ids_contratos, context):
            time_contrato = datetime.datetime.strptime(contrato.continuidad_desde, "%Y-%m-%d")
            localdict = {'employee': contrato.employee_id, 'contract': contrato, 'date_time': fechas}
            dias_normales = 0
            dias_adicionales = 0
            prop_normales = 0
            prop_adicionales = 0
            periodo_inicio = datetime.datetime(year=time_contrato.year, month=time_contrato.month, day=time_contrato.day)
            periodo_fin = datetime.datetime(year=time_contrato.year+1, month=time_contrato.month, day=time_contrato.day)
            periodo_fin = periodo_fin + datetime.timedelta(days=(-1))
            while periodo_fin <= time_actual:
                dias_normales = 0
                dias_adicionales = 0
                try:
                    eval(contrato.type_id.formula_normales, localdict, mode='exec', nocopy=True)
                    dias_normales = localdict['result']
                    eval(contrato.type_id.formula_adicionales, localdict, mode='exec', nocopy=True)
                    dias_adicionales = localdict['result']
                except:
                    raise osv.except_osv('Error de cómputo', 'Las expresiones python para el cómputo de vacaciones, es erroneo')
                nombre = 'Periodo: ' + str(periodo_inicio)[:10] + ' - ' + str(periodo_fin)[:10]
                ids_periodo = [obj_periodo.create(cr, uid, {'name': nombre,
                                                            'employee_id': contrato.employee_id.id,
                                                            'date_start': periodo_inicio,
                                                            'date_stop': periodo_fin,
                                                            'days_normal':dias_normales,
                                                            'days_extra':dias_adicionales,
                                                            'days_prop_normal':0,
                                                            'days_prop_extra':0,})]
                periodo_inicio = periodo_fin + datetime.timedelta(days=(+1))
                periodo_fin = datetime.datetime(year=periodo_inicio.year+1, month=periodo_inicio.month, day=periodo_inicio.day)
                periodo_fin = periodo_fin + datetime.timedelta(days=(-1))
            if periodo_fin>time_actual:
                nombre = 'Periodo: ' + str(periodo_inicio)[:10] + ' - ' + str(periodo_fin)[:10]
                dias_proporcionales = (time_actual - periodo_inicio).days
                prop_normales = (dias_normales*dias_proporcionales)/365.0
                prop_adicionales = (dias_adicionales*dias_proporcionales)/365.0
                ids_periodo = [obj_periodo.create(cr, uid, {'name': nombre,
                                                            'employee_id': contrato.employee_id.id,
                                                            'date_start': periodo_inicio,
                                                            'date_stop': periodo_fin,
                                                            'days_normal':0,
                                                            'days_extra':0,
                                                            'days_prop_normal':prop_normales,
                                                            'days_prop_extra':prop_adicionales,})]

    def boton_actualizar_vacaciones(self, cr, uid, ids, context=None):
        #solo considerar del anio en curso
        obj_contrato = self.pool.get('hr.contract')
        obj_periodo = self.pool.get('holidays.period')
        time_actual = datetime.datetime.today()
        ids_contratos = []
        for this in self.browse(cr, uid, ids):
            ids_contratos1 = obj_contrato.search(cr, uid, [('date_start','<=',str(time_actual)),('employee_id','=',ids[0]),('date_end','>=',str(time_actual))])
            ids_contratos2 = obj_contrato.search(cr, uid, [('date_start','<=',str(time_actual)),('date_end','=',False),('employee_id','=',ids[0])])
            ids_contratos = ids_contratos1 + ids_contratos2
#        import pdb
#        pdb.set_trace()
        for contrato in obj_contrato.browse(cr, uid, ids_contratos, context):
            time_contrato = datetime.datetime.strptime(contrato.continuidad_desde, "%Y-%m-%d")
            localdict = {'employee': contrato.employee_id, 'contract': contrato, 'date_time': fechas}
            dias_normales = 0
            dias_adicionales = 0
            prop_normales = 0
            prop_adicionales = 0
            periodo_inicio = datetime.datetime(year=time_contrato.year, month=time_contrato.month, day=time_contrato.day)
            periodo_fin = datetime.datetime(year=time_contrato.year+1, month=time_contrato.month, day=time_contrato.day)
            periodo_fin = periodo_fin + datetime.timedelta(days=(-1))
            while periodo_fin <= time_actual:
                dias_normales = 0
                dias_adicionales = 0
                try:
                    eval(contrato.type_id.formula_normales, localdict, mode='exec', nocopy=True)
                    dias_normales = localdict['result']
                    eval(contrato.type_id.formula_adicionales, localdict, mode='exec', nocopy=True)
                    dias_adicionales = localdict['result']
                except:
                    raise osv.except_osv('Error de cómputo', 'Las expresiones python para el cómputo de vacaciones, es erroneo')
                nombre = 'Periodo: ' + str(periodo_inicio)[:10] + ' - ' + str(periodo_fin)[:10]
 #               ids_periodo = [obj_periodo.create(cr, uid, {'name': nombre,
 #                                                           'employee_id': contrato.employee_id.id,
 #                                                           'date_start': periodo_inicio,
 #                                                           'date_stop': periodo_fin,
 #                                                           'days_normal':dias_normales,
 #                                                           'days_extra':dias_adicionales,
 #                                                           'days_prop_normal':0,
 #                                                           'days_prop_extra':0,})]
                periodo_inicio = periodo_fin + datetime.timedelta(days=(+1))
                periodo_fin = datetime.datetime(year=periodo_inicio.year+1, month=periodo_inicio.month, day=periodo_inicio.day)
                periodo_fin = periodo_fin + datetime.timedelta(days=(-1))
            if periodo_fin>time_actual:
                nombre = 'Periodo: ' + str(periodo_inicio)[:10] + ' - ' + str(periodo_fin)[:10]
                dias_proporcionales = (time_actual - periodo_inicio).days
                #solo codigo de trabajo
                if contrato.type_id.name in ('LOSEP','losep','Losep'):
                    dias_normales = 15
                    prop_normales = (dias_normales*dias_proporcionales)/365.0
                    prop_adicionales = (dias_adicionales*dias_proporcionales)/365.0
                    dias_normales = abs(dias_normales + prop_normales)
                ids_periodo = [obj_periodo.create(cr, uid, {'name': nombre,
                                                            'employee_id': contrato.employee_id.id,
                                                            'date_start': periodo_inicio,
                                                            'date_stop': periodo_fin,
                                                            'days_normal':dias_normales,
                                                            'days_extra':dias_adicionales,
                                                            'days_prop_normal':prop_normales,
                                                            'days_prop_extra':prop_adicionales,})]        
        return True
        
    def tarea_actualizar_vacaciones_3(self, cr, uid, context=None):
        obj_contrato = self.pool.get('hr.contract')
        obj_periodo = self.pool.get('holidays.period')
        time_actual = datetime.datetime.today()
        ids_contratos = obj_contrato.search(cr, uid, [('date_start','<=',str(time_actual)),
                                                      '|',
                                                      ('date_end','>=',str(time_actual)),
                                                      ('date_end','=',False)])
        for contrato in obj_contrato.browse(cr, uid, ids_contratos, context):
            print "en contratos"
            time_contrato = datetime.datetime.strptime(contrato.continuidad_desde, "%Y-%m-%d")
            
            print "antes comparar fecha"
            if time_contrato.day == time_actual.day and time_contrato.month == time_actual.month and time_actual.year > time_contrato.year:
                print "despues comparar fecha"
                localdict = {'employee': contrato.employee_id, 'contract': contrato, 'date_time': fechas}
                try:
                    eval(contrato.type_id.formula_normales, localdict, mode='exec', nocopy=True)
                    dias_normales = localdict['result']
                    eval(contrato.type_id.formula_adicionales, localdict, mode='exec', nocopy=True)
                    dias_adicionales = localdict['result']
                except:
                    raise osv.except_osv('Error de computo', 'Las expresiones python para el computo de vacaciones, es erroneo')
                resultado = time_actual - time_contrato
                periodo_fin = datetime.datetime(year=time_actual.year, month=time_actual.month, day=time_actual.day)
                periodo_inicio = datetime.datetime(year=time_actual.year-1, month=time_actual.month, day=time_actual.day)
                periodo_fin = periodo_fin + datetime.timedelta(days=(-1))
                obj_periodo.create(cr, uid, {'name': 'Periodo: ' + str(periodo_inicio)[:10] + ' - ' + str(periodo_fin)[:10],
                                                     'employee_id': contrato.employee_id.id,
                                                     'date_start': periodo_inicio,
                                                     'date_stop': periodo_fin,
                                                     'days_normal': dias_normales,
                                                     'days_extra': dias_adicionales}, context)
    
    def compute_all_holidays_past(self, cr, uid, ids, context=None):
        #actualiza las vacaciones de todos los empleados
        val = 0
        res = {}
        FIXED_DAYS = 15
        EXTRA_YEAR = 5
        BASE_YEAR = 1
        contract_obj = self.pool.get('hr.contract')
        ids_empleados = self.search(cr, uid, [])
        for emp in self.browse(cr, uid, ids_empleados, context):
            res[emp.id] = {
                'dias_vacaciones': 0,
                'dias_vac_adi': 0,
                'dias_disponibles': 0,
                }
            contract_ids = contract_obj.search(cr, uid, [('employee_id','=',emp.id),
                                                         ('activo','=',True)], limit=1)
            if contract_ids:
                contrato = contract_obj.browse(cr, uid, contract_ids[0])
                years=(datetime.today()-datetime.strptime(contrato.date_start,'%Y-%m-%d')).days/365
                if years>=BASE_YEAR:
                    res[emp.id]['dias_vacaciones'] = FIXED_DAYS or 0
                else:
                    res[emp.id]['dias_vacaciones'] = 0
                res[emp.id]['dias_vac_adi'] = 0
                if years>EXTRA_YEAR:
                    res[emp.id]['dias_vac_adi'] = years-EXTRA_YEAR
                if years>15:
                    res[emp.id]['dias_vac_adi'] = 15
                #res[emp.id]['dias_vac_adi'] = years>EXTRA_YEAR and years>15 and 15 or (years-EXTRA_YEAR) or 0
                res[emp.id]['dias_disponibles'] = res[emp.id]['dias_vacaciones'] + res[emp.id]['dias_vac_adi'] + emp.dias_saldo - emp.dias_tomados - emp.dias_adelantado
                self.write(cr, uid, emp.id, {'anios_laborados' : years,
                                             'dias_disponibles' : res[emp.id]['dias_disponibles'],
                                             'dias_vacaciones' : res[emp.id]['dias_vacaciones'],
                                             'dias_vac_adi' : res[emp.id]['dias_vac_adi'],})
        return True
    
hr_employee_holidays()

class gt_hr_holidays(osv.osv):
    _inherit = "hr.holidays"
    
    def _total_falta_dias(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            inicio = this.date_from.split('-')
            fin = this.date_to.split('-')
            dateinicio = date( int(inicio[0]), int(inicio[1]), int(inicio[2]) )
            datefin = date( int(fin[0]), int(fin[1]), int(fin[2]) )
            delta = datefin - dateinicio
            res[this.id] = delta.days + 1
        return res

    _columns = {
        #'assistance_lines': fields.one2many('gt.hr.assistance.absence', 'holidays_id', 'Detalle de Asistencia'),
        'contrato_id':fields.many2one('hr.contract','Contrato'),
        'total_dias': fields.function(_total_falta_dias, method=True, string="Total Dias", store=True, type="integer"), 
        'line_id':fields.many2one('hr.ie.line','Descuento'),
        'horas':fields.integer('Horas'),
        'tipo_rol':fields.many2one('hr.contract.type.type','Rol'),
        'tipo_relacion':fields.many2one('hr.contract.type','Relacion Laboral'),
        'code': fields.char('Numero',size=10),
        'date_from': fields.date('Fecha Desde'),
        'date_to': fields.date('Fecha Hasta'),
        'date_start' : fields.date('Fecha de inicio de la ausencia'),
        'tipo_vacaciones': fields.selection([('normal','Normales'),('extra','Adicionales')],'Descontar de', 
                                            help='Indicar de que tipo de vacaciones se descontara los dias indicados'),
        'state': fields.selection([('draft', 'Borrador'),
                                   ('confirm', 'Esperando Aprobación'),
                                   ('refuse', 'Rechazado'),
                                   ('validate1', 'Esperando Segunda Aprobación'),
                                   ('validate', 'Aprobado'),
                                   ('cancel', 'Cancelado')],'Estado', readonly=True),
    }
    
    _defaults = {
        'name':'Ausencia',
        'tipo_vacaciones':'normal'
    }
    

       # TODO: can be improved using resource calendar method
    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""

        DATETIME_FORMAT = "%Y-%m-%d"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day 
    
    def recalcula_descuento_falta(self, cr, uid, ids, context=None):
        contract_obj = self.pool.get('hr.contract')
        rule_obj = self.pool.get('hr.salary.rule')
        line_obj = self.pool.get('hr.ie.line')
        period_obj = self.pool.get('hr.work.period.line')
        if not context:
            context = {}
        for this in self.browse(cr, uid, ids):
            if this.line_id:
                line_obj.write(cr, uid, this.line_id.id,{'state':'draft',})
                line_obj.unlink(cr, uid, [this.line_id.id])
            #saca el contrato
            if this.contrato_id:
                contrato = this.contrato_id
            else:
                contract_ids = contract_obj.search(cr, uid, [('employee_id','=',this.employee_id.id),('activo','=',True)])
                if not contract_ids:
                    raise osv.except_osv('Error de usuario', 'No existe contrato activo para el funcionario')
                contrato = contract_obj.browse(cr, uid, contract_ids[0])
            monto = 0
            if contrato.type_id.name=='CODIGO TRABAJO':
                if this.total_dias==1:
                    if this.horas>0 and this.horas<4:
                        monto = (contrato.costo_hora)*(this.horas)
                    elif this.horas>=4 and this.horas<8:
                        monto = (contrato.costo_hora)*8
                    elif this.horas>=8:
                        monto = (contrato.costo_hora)*16
                    else:
                        raise osv.except_osv('Error de usuario', 'Numero horas no valido')
                elif this.total_dias==2:
                    monto = (contrato.costo_hora)*16
                else:
                    monto = 0
            else:
                monto = (contrato.costo_hora)*8*this.total_dias
            if monto>0:
                rule_ids = rule_obj.search(cr, uid, [('code','=','FALTAS')])
                if not rule_ids:
                    raise osv.except_osv('Error de configuracion', 'No existe rubro con codigo FALTAS, cree uno por favor')
                period_ids = period_obj.search(cr, uid, [('date_start','<=',this.date_from),('date_stop','>=',this.date_from)])
                if not period_ids:
                    raise osv.except_osv('Error de configuracion', 'No existe periodo para la fecha, cree uno por favor')
                line_id = line_obj.create(cr, uid,{                         
                                'name': contrato.employee_id.complete_name,
                                'employee_id': this.employee_id.id,
                                'date': this.date_from,
                                'valor': monto,
                                'categ_id': rule_ids[0],
                                'period_id': period_ids[0],
                                'state': 'pendiente',})
                self.write(cr, uid, ids, {'line_id':line_id,})

    def print_permiso(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        permiso = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [permiso.id],
                 'model': 'hr.holidays'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr.holidays',
            'model': 'hr.holidays',
            'datas': datas,
            'nodestroy': True,            
                }

    def onchange_sec_id(self, cr, uid, ids, status, context=None):
        warning = {}
        double_validation = False
        obj_holiday_status = self.pool.get('hr.holidays.status')
        if status:
            holiday_status = obj_holiday_status.browse(cr, uid, status, context=context)
            double_validation = holiday_status.double_validation
            if holiday_status.categ_id and holiday_status.categ_id.section_id and not holiday_status.categ_id.section_id.allow_unlink:
                warning = {
                    'title': "Warning for ",
                    'message': "You won\'t be able to cancel this leave request because the CRM Sales Team of the leave type disallows."
                }
        return {'warning': warning, 'value': {'double_validation': double_validation}}

    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        result = {}
        if date_to and date_from:
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value'] = {
                'number_of_days_temp': diff_day
            }
            return result
        result['value'] = {
            'number_of_days_temp': 0,
        }
        return result
    
    def create2(self, cr, uid, data, context=None):
        obj_holidays_period = self.pool.get("holidays.period")
        holiday_period_id = obj_holidays_period.create(self, cr, uid, {})
        user_id = super(gt_hr_holidays, self).create(cr, uid, data, context=context)

        # add shortcut unless 'noshortcut' is True in context
        if not(context and context.get('noshortcut', False)):
            data_obj = self.pool.get('ir.model.data')
            try:
                data_id = data_obj._get_id(cr, uid, 'hr', 'ir_ui_view_sc_employee')
                view_id  = data_obj.browse(cr, uid, data_id, context=context).res_id
                self.pool.get('ir.ui.view_sc').copy(cr, uid, view_id, default = {
                                            'user_id': user_id}, context=context)
            except:
                # Tolerate a missing shortcut. See product/product.py for similar code.
                logging.getLogger('orm').debug('Skipped meetings shortcut for user "%s"', data.get('name','<new'))

        return user_id
    
    def reducir_vacaciones(self, cr, uid, ids, context=None):
        total_dias = 0
        obj_period = self.pool.get('holidays.period')
        for registro in self.browse(cr, uid, ids, context):
            total_dias = abs(registro.number_of_days)
            if registro.type == "remove":
                aux_periodo = False
                for periodo in registro.employee_id.holidays_ids:
                    aux_periodo = periodo
                    if registro.tipo_vacaciones=='normal':
                        if periodo.days_normal > periodo.tomados_normal:
                            if total_dias > (periodo.days_normal - periodo.tomados_normal):
                                total_dias = total_dias - (periodo.days_normal - periodo.tomados_normal)
                                obj_period.write(cr, uid, periodo.id, {'tomados_normal':periodo.days_normal})
                            else:
                                obj_period.write(cr, uid, periodo.id, {'tomados_normal':periodo.tomados_normal+total_dias})
                                total_dias = 0
                                return True
                    if registro.tipo_vacaciones=='extra':
                        if periodo.days_extra > periodo.tomados_extra:
                            if total_dias > (periodo.days_extra - periodo.tomados_extra):
                                total_dias = total_dias - (periodo.days_extra - periodo.tomados_extra)
                                obj_period.write(cr, uid, periodo.id, {'tomados_extra':periodo.days_extra})
                            else:
                                obj_period.write(cr, uid, periodo.id, {'tomados_extra':periodo.tomados_extra+total_dias})
                                total_dias = 0
                                return True
                ultimo_id = 0
                if not registro.employee_id.holidays_ids:
                    ultimo_id = obj_period.create(cr, uid, {'name':'Carga Inicial',
                                                            'date_start': registro.employee_id.contract_id.date_start,
                                                            'date_stop': registro.employee_id.contract_id.date_start,}, context)
                else:
                    ultimo_id = aux_periodo.id
                if total_dias>0:
                    periodo = obj_period.browse(cr, uid, ultimo_id, context)
                    if registro.tipo_vacaciones=='normal':
                        obj_period.write(cr, uid, ultimo_id, {'tomados_normal':periodo.tomados_normal + total_dias})
                    if registro.tipo_vacaciones=='extra':
                        obj_period.write(cr, uid, ultimo_id, {'tomados_extra':periodo.tomados_extra + total_dias})
                    return True
        return False
    
    def holidays_confirm(self, cr, uid, ids, context=None):
        contract_obj = self.pool.get('hr.contract')
        self.check_holidays(cr, uid, ids, context=context)
        #get numero
        obj_sequence = self.pool.get('ir.sequence')
        aux_code = obj_sequence.get(cr, uid, 'hr.holidays')
        #busco el contrato activo y le agrego al documento el tipo de rol
        for this in self.browse(cr, uid, ids):
            contract_ids = contract_obj.search(cr, uid, [('employee_id','=',this.employee_id.id),('activo','=',True)])
            if not contract_ids:
                raise osv.except_osv('Error de usuario', 'No existe contrato activo para el funcionario')
            contrato = contract_obj.browse(cr, uid, contract_ids[0])
        return self.write(cr, uid, ids, {'state':'confirm','code':aux_code,'tipo_rol':contrato.subtype_id.id,
                                         'tipo_relacion':contrato.type_id.id,'contrato_id':contrato.id})

    def holidays_validate2(self, cr, uid, ids, context=None):
        self.check_holidays(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate'})
        data_holiday = self.browse(cr, uid, ids)
        holiday_ids = []
        for record in data_holiday:
            if record.holiday_status_id.double_validation:
                holiday_ids.append(record.id)
            if record.holiday_type == 'employee' and record.type == 'remove':
                meeting_obj = self.pool.get('crm.meeting')
                vals = {
                    'name': record.name,
                    #'categ_id': record.holiday_status_id.categ_id.id,
                    'duration': record.number_of_days_temp * 8,
                    'description': record.notes,
                    'user_id': record.user_id.id,
                    'date': record.date_from,
                    'end_date': record.date_to,
                    'date_deadline': record.date_to,
                }
                #case_id = meeting_obj.create(cr, uid, vals)
                self._create_resource_leave(cr, uid, [record], context=context)
                #self.write(cr, uid, ids, {'case_id': case_id})
            elif record.holiday_type == 'category':
                emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [record.category_id.id])])
                leave_ids = []
                for emp in obj_emp.browse(cr, uid, emp_ids):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=None))
                wf_service = netsvc.LocalService("workflow")
                for leave_id in leave_ids:
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        if holiday_ids:
            self.write(cr, uid, holiday_ids, {'manager_id2': manager})
        #reduccion de vacaciones de holidays.period
        self.reducir_vacaciones(cr, uid, ids, context)
        return True
    
    def check_holidays(self, cr, uid, ids, context=None):
        return True

    def _cantidad_maxima(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.holiday_status_id.max == 0:
            return True
        else:
            if obj.holiday_status_id.max >= obj.number_of_days:
                return True
            else:
                return False
        return True
    
    _constraints = [
                    (_cantidad_maxima, 'No puede superar el límite máximo de días por este motivo de ausencia', ['holiday_status_id','number_of_days']),
                    ]
    
gt_hr_holidays()

class gt_doc_holidays(osv.osv):
    _name = 'hr.doc.holidays'
    
    def _cargar_departamento_empleado(self, cr, uid, context=None):
        usuario_id = self.pool.get('res.users').search(cr, uid, [('id','=',uid)])
        if usuario_id:
            usuario = self.pool.get('res.users').browse(cr, uid, usuario_id[0])
            return usuario.context_department_id.id
        return False
    
    _columns = {
                #'name': fields.char('Descripción', size=50, required=True),
                'contract_id': fields.many2one('hr.contract','Empleado', required=True),
                'department_id': fields.related('contract_id', 'department_id', type='many2one', relation='hr.department', string='Departamento', store=True),
                'tipo_id': fields.many2one('hr.holidays.status', 'Tipo de Ausencia', required=True),
                'date_start' : fields.datetime('Inicio de la ausencia', required=True),
                'date_stop' : fields.datetime('Fin de la ausencia', required=True),
                'tipo_vacaciones': fields.selection([('normal','Normales'),('extra','Adicionales')],'Descontar de vacaciones?', help='Indicar de que tipo de vacaciones se descontara los dias indicados, en el caso que la ausencia se cargue a vacaciones'),
                'state': fields.selection([('draft', 'Borrador'),
                                           ('confirm', 'Esperando Aprobación'),
                                           ('validate1', 'Esperando Segunda Aprobación'),
                                           ('validate', 'Aprobado'),
                                           ('refuse', 'Anulado'),
                                           ('cancel', 'Cancelado')],'Estado', readonly=True),
                'holiday_id': fields.many2one('hr.holidays','Registro de Ausencia'),
                'notes': fields.text('Razones'),
                }
    
    _defaults = {
                 'department_id': _cargar_departamento_empleado,
                 'state':'draft',
                 }
    
    def confirm(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'confirm'})
    
    def aprobar_jefe(self, cr, uid, ids, context={}):
        for registro in self.browse(cr, uid, ids, context):
            if registro.double_validation:
                return self.write(cr, uid, ids, {'state':'validate1'})
            else:
                return self.write(cr, uid, ids, {'state':'validate'})
        return False
    
gt_doc_holidays()

class certificadoInstitute(osv.Model):
    _name = 'certificado.institute'
    _columns = dict(
        name = fields.char('Nombre',size=256,required=True),
    )
certificadoInstitute()

class certificadoPermiso(osv.Model):
    _name = 'certificado.permiso'
    _description = 'Certificados Permisos'

    def unlink(self, cr, uid, ids, *args, **kwargs):
        raise osv.except_osv('Error de usuario', 'No puede eliminar el registro')

    def _total_permiso(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            aux = this.hora_fin - this.hora_inicio
            res[this.id] = float(aux)
        return res

    def _total_permiso_dias(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            if this.tipo=='Dias':
                inicio = this.date.split('-')
                fin = this.date_end.split('-')
                dateinicio = date( int(inicio[0]), int(inicio[1]), int(inicio[2]) )
                datefin = date( int(fin[0]), int(fin[1]), int(fin[2]) )
                delta = datefin - dateinicio
                res[this.id] = delta.days + 1
        return res
 
    _columns = dict(
        tipo_contrato_id = fields.many2one('hr.contract.type.type','Tipo Contrato'),
        create_user_id = fields.many2one('res.users','Creado por'),
        institute_id = fields.many2one('certificado.institute','Instituto',required=True),
        total_dias = fields.function(_total_permiso_dias, method=True, string="Total Dias", store=True, type="integer"), 
        total_horas = fields.function(_total_permiso, method=True, string="Total Horas", store=True, type="float"), 
        employee_id = fields.many2one('hr.employee','Empleado',required=True),
        name = fields.char('Descripcion',size=64,required=True),
        tipo = fields.selection([('Dias','Dias'),('Horas','Horas')],'Tipo Permiso'),
        hora_inicio = fields.float('Hora Desde'),
        hora_fin = fields.float('Hora Hasta'),
        date = fields.date('Desde'),
        date_end = fields.date('Hasta'),
        state = fields.selection([('Borrador','Borrador'),('Autorizado','Autorizado'),('Ejecutado','Ejecutado'),('Anulado','Anulado')],'Estado'),
    )

    def return_draftpc(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0],{'state':'Borrador'})
        return True

    def anulaCert(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0],{'state':'Anulado'})
        return True
    
    def autorizaJefeCert(self, cr, uid, ids, context=None):
        contract_obj = self.pool.get('hr.contract')
        for this in self.browse(cr, uid, ids):
            contract_ids = contract_obj.search(cr, uid, [('activo','=',True),('employee_id','=',this.employee_id.id)])
            if not contract_ids:
                contract_ids = contract_obj.search(cr, uid, [('employee_id','=',this.employee_id.id)])
            contract = contract_obj.browse(cr, uid, contract_ids[0])
        self.write(cr, uid, ids[0],{'state':'Autorizado','tipo_contrato_id':contract.subtype_id.id})
        return True

    def draft_phora_ejecutado_cert(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        for this in self.browse(cr, uid, ids):
            if uid!=user.context_department_id.coordinador_id.user_id.id:
                raise osv.except_osv(('Error de usuario !'), ('Usted no es usuario autorizador'))
            if this.tipo=='Horas':
                if this.hora_fin<=0 or this.hora_inicio<=0:
                    raise osv.except_osv(('Error de usuario !'), ('La horas deben ser mayor a cero'))
                if this.hora_fin<this.hora_inicio:
                    raise osv.except_osv(('Error de usuario !'), ('La hora final debe mayor a la inicial'))
        self.write(cr, uid, ids[0],{'state':'Ejecutado'})
        return True

    def _get_uid(self, cr, uid, context=None):
        return uid

    _defaults = dict(
        state = 'Borrador',
        create_user_id = _get_uid,
    )    
certificadoPermiso()

class descuentaHoly(osv.Model):
    _name = 'descuenta.holy'

    def _get_state(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for this in self.browse(cr, uid, ids):
            if this.holi_id:
                aux_text = this.holi_id.state
                res[this.id] = aux_text
        return res

    _columns = dict(
        p_id = fields.many2one('permiso.hora','Permiso'),
        autorizado_por = fields.related('p_id','jefe_id',type='many2one',relation='hr.employee',string="Jefe Autoriza",store=True),
        state = fields.selection([('Proceso','Proceso'),('Liquidado','Liquidado'),('Anulado','Anulado')],'Estado'),
        date = fields.related('p_id','date_permiso',type='date',string="Fecha Solicitud",store=True),
        date_from = fields.related('p_id','date',type='date',string="Fecha Desde",store=True),
        date_end = fields.related('p_id','date_end',type='date',string="Fecha Hasta",store=True),
        hora_inicio = fields.related('p_id','hora_inicio',type='float',string="Hora Desde",store=True),
        hora_fin = fields.related('p_id','hora_fin',type='float',string="Hora Hasta",store=True),
        code = fields.related('p_id','code',type='char',string="Codigo Documento Permiso",size=10,store=True),
        desc = fields.related('p_id','name',type='char',string="Descripcion",size=128,store=True),
        holi_id = fields.many2one('holidays.period','Periodo'),
        dias = fields.integer('Dias Descuento'),
    )

    def _checkDiasMayor(self, cr, uid, ids):
        #OJO mover al compute sino no corre el duplicar
        band = True
        for obj in self.browse(cr, uid, ids):
            if obj.dias<=0:
                band = False
        return band

    _constraints = [
        (_checkDiasMayor,
         ustr('Los dias deben ser mayor a cero.'),['', 'Dias']),
    ]
descuentaHoly()

class permisoHora(osv.Model):
    _name = 'permiso.hora'
    _order = 'code_int desc'

    def onchange_aprobado_por(self, cr, uid, ids, aprobado_por, context=None):
        user_obj = self.pool.get('res.users')
        usuario = user_obj.browse(cr, uid, uid)
        if uid!=usuario.context_department_id.manager_id.user_id.id:
            return {'value':{'aprobado_por':False}}
        else:
            return {'value':{'aprobado_por':True}}
            
    def create_(self, cr, uid, vals, context=None):
        emp_obj = self.pool.get('hr.employee')
        empleado = emp_obj.browse(cr, uid, vals['employee_id'])
        aux = empleado.total_normal
        vals['saldo'] = aux
        return super(permisoHora, self).create(cr, uid, vals, context=None)            

    def unlink(self, cr, uid, ids, *args, **kwargs):
        for this in self.browse(cr, uid, ids):
            if this.code!='/':
                raise osv.except_osv('Error de usuario', 'No puede eliminar el registro ya numerados')
            else:
                if this.state!='Borrador':
                    raise osv.except_osv('Error de usuario', 'No puede eliminar el registro')
                else:
                    return super(permisoHora, self).unlink(cr, uid, ids , context=None)

    def _total_permiso(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            aux = this.hora_fin - this.hora_inicio
            res[this.id] = float(aux)
        return res

    def _code_int(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            if this.code!='/':
                aux = int(this.code)
                res[this.id] = aux
        return res


    def _total_permiso_dias(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            if this.tipo=='Dias':
                inicio = this.date.split('-')
                fin = this.date_end.split('-')
                dateinicio = date( int(inicio[0]), int(inicio[1]), int(inicio[2]) )
                datefin = date( int(fin[0]), int(fin[1]), int(fin[2]) )
                delta = datefin - dateinicio
                res[this.id] = delta.days + 1
        return res
 
    def _total_permiso_cargo(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        permiso_obj = self.pool.get('permiso.hora')
        aux = 0
        for this in self.browse(cr, uid, ids):
            if this.saldo_id:
                permisos_ids = permiso_obj.search(cr, uid, [('saldo_id','=',this.saldo_id.id),('id','!=',this.id)])
                if permisos_ids:
                    for permiso_id in permisos_ids:
                        permiso = permiso_obj.browse(cr, uid, permiso_id)
                        aux += permiso.total_dias
        res[this.id] = aux
        return res

    def onchange_empholy(self, cr, uid, ids, employee_id, context=None):
        emp_obj = self.pool.get('hr.employee')
        empleado = emp_obj.browse(cr, uid, employee_id)
        return {'value':{'saldo':empleado.total_normal}}

    def onchange_dateper(self, cr, uid, ids, date, context=None):
        if date!=time.strftime('%Y-%m-%d'):
            raise osv.except_osv(('Error de usuario !'), ('No puede la fecha ser diferente'))

    _columns = dict(
        tipo_contrato_id = fields.many2one('hr.contract.type.type','Tipo Contrato'),
        liquidado = fields.boolean('Liquidado vacaciones'),
        line_descuenta_ids = fields.one2many('descuenta.holy','p_id','Detalle Descuentos'),
        aprobado_por = fields.boolean('Apobado Direccion TTHH?'),
#        usuario_autoriza = fields.related('jefe_id','user_id',type='many2one',relation='res.users',string="Usuario Autoriza",store=True),
        usuario_autoriza = fields.many2one('res.users','Usuario Autoriza'),
        saldo = fields.integer('Dias Disponibles'),
        jefe_id = fields.many2one('hr.employee','Jefe Autoriza'),
        date_permiso = fields.date('Fecha Solicitud'),
        create_user_id = fields.many2one('res.users','Creado por'),
        total_cargo = fields.function(_total_permiso_cargo, method=True, string="Total Permiso Cargo", store=True, type="float"), 
        tipo2 = fields.selection([('VACACIONES','VACACIONES'),('LICENCIA','LICENCIA'),('LICENCIASIN','LICENCIA SIN SUELDO'),
                                  ('PERMISO','PERMISO'),('ENFERMEDAD ACCIDENTE','ENFERMEDAD ACCIDENTE'),
                                  ('COMPENSACION','COMPENSACION'),('CALAMIDAD DOMESTICA','CALAMIDAD DOMESTICA'),('PRESENTAR CERTIFICADO','PRESENTAR CERTIFICADO')
                                  ,('OTROS','OTROS')],'Tipo Solicitud'),
        tipo = fields.selection([('Dias','Dias'),('Horas','Horas')],'Tipo Permiso'),
        descuenta = fields.boolean('Cargo Vacaciones'),
        saldo_id = fields.many2one('holidays.period','Saldo'),
        code = fields.char('Numero',size=10),
        total_horas = fields.function(_total_permiso, method=True, string="Total Horas", store=True, type="float"), 
        code_int = fields.function(_code_int, method=True, string="Codigo", store=True, type="integer"), 
        total_dias = fields.function(_total_permiso_dias, method=True, string="Total Dias", store=True, type="integer"), 
        employee_id = fields.many2one('hr.employee','Empleado',required=True),
        name = fields.char('Descripcion',size=128,required=True),
        date = fields.date('Dia desde',required=True),
        date_end = fields.date('Dia Hasta'),
        hora_inicio = fields.float('Hora Desde'),
        hora_fin = fields.float('Hora Hasta'),
        state = fields.selection([('Borrador','Borrador'),('Solicitado','Solicitado'),('Autorizado','Autorizado'),
                                  ('Ejecutado','Ejecutado'),('Liquidado','Liquidado'),('Anulado','Anulado')],'Estado'),
        )

    def solicitaPermisoHoli(self, cr, uid, ids, context=None):
        #validacion limon
        user_obj = self.pool.get('res.users')
        aux_date = time.strftime('%Y-%m-%d')
        contract_obj = self.pool.get('hr.contract')
        for this in self.browse(cr, uid, ids):
            if not this.create_user_id.id==this.employee_id.user_id.id:
                raise osv.except_osv('Error de usuario', 'El empleado seleccionado no corresponde con el usuario')
            contract_ids = contract_obj.search(cr, uid, [('activo','=',True),('employee_id','=',this.employee_id.id)])
            if not contract_ids:
                contract_ids = contract_obj.search(cr, uid, [('employee_id','=',this.employee_id.id)])
            contract = contract_obj.browse(cr, uid, contract_ids[0])
#            if this.date_permiso!=aux_date:
#                raise osv.except_osv('Error de usuario', 'La fecha debe ser igual a la actual')
            user_ids = user_obj.search(cr, uid,[('employee_id','=',this.jefe_id.id)])
            if not user_ids:
                raise osv.except_osv('Error de configuracion', 'El jefe seleccionado no tiene usuario asociado')
            if this.code=='/':
                obj_sequence = self.pool.get('ir.sequence')
                aux_code = obj_sequence.get(cr, uid, 'hr.holidays')
                self.write(cr, uid, ids[0],{'state':'Solicitado','code':aux_code,'usuario_autoriza':user_ids[0],'tipo_contrato_id':contract.subtype_id.id})
            else:
                self.write(cr, uid, ids[0],{'state':'Solicitado','usuario_autoriza':user_ids[0],'tipo_contrato_id':contract.subtype_id.id})
        return True

    def autorizaJefeHoli(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        for this in self.browse(cr, uid, ids):
            if this.tipo2=='VACACIONES':
                user = user_obj.browse(cr, uid, uid)
                #if this.usuario_autoriza:
                #    if uid!=this.usuario_autoriza.id:
                #        raise osv.except_osv(('Error de usuario !'), ('Usted no es usuario autorizador'))
                #else:
                #    if user.employee_id.id!=this.jefe_id.id:
                #        raise osv.except_osv(('Error de usuario !'), ('Usted no es usuario autorizador'))
        self.write(cr, uid, ids[0],{'state':'Autorizado'})
        return True

    def returnDraftPhora(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0],{'state':'Borrador'})
        return True

    def returnLiquidadoAutorizado(self, cr, uid, ids, context=None):
        period_obj = self.pool.get('holidays.period')
        holy_obj = self.pool.get('descuenta.holy')
        for this in self.browse(cr, uid,ids):
            for line in this.line_descuenta_ids:
                holy_obj.write(cr, uid, line.id,{'state':'Proceso',})
                valor = line.holi_id.tomados_normal - line.dias
                period_obj.write(cr, uid, line.holi_id.id,{
                    'tomados_normal':valor,
                })
                
        self.write(cr, uid, ids[0],{'state':'Autorizado'})
        return True

    def anulaPermiso(self, cr, uid, ids, context=None):
        ##devolver los dias
        period_obj = self.pool.get('holidays.period')
        holy_obj = self.pool.get('descuenta.holy')
        for this in self.browse(cr, uid,ids):
            if this.state not in ('Autorizado','Ejecutado','Liquidado'):
                for line in this.line_descuenta_ids:
                    holy_obj.write(cr, uid, line.id,{'state':'Anulado',})
                self.write(cr, uid, ids[0],{'state':'Anulado'})
            else:
                raise osv.except_osv(('Error de usuario !'), ('No puede anular permisos'))
        return True

    def returnSolicitaDraft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids[0],{'state':'Borrador'})
        return True

    def returnAutorizadoDraft(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if uid==this.create_user_id.id:
                raise osv.except_osv(('Error de usuario !'), ('El mismo usuario no puede regresar'))
            else:
                self.write(cr, uid, ids[0],{'state':'Borrador'})
        return True
    
    def phora_liquidado(self, cr, uid, ids, context=None):
        dias_obj= self.pool.get('holidays.period')
        holy_obj = self.pool.get('descuenta.holy')
        for this in self.browse(cr, uid, ids):
            if this.tipo=='Horas':
                if this.hora_fin<=0 or this.hora_inicio<=0:
                    raise osv.except_osv(('Error de usuario !'), ('Las horas deben ser mayor a cero'))
                if this.hora_fin<this.hora_inicio:
                    raise osv.except_osv(('Error de usuario !'), ('La hora final debe mayor a la inicial'))
            if this.descuenta:
                if this.line_descuenta_ids:
                    aux_total_descuenta = 0
                    for line in this.line_descuenta_ids:
                        holy_obj.write(cr, uid, line.id,{'state':'Liquidado',})
                        aux_total_descuenta += line.dias
                    if aux_total_descuenta!=this.total_dias:
                        raise osv.except_osv(('Error de usuario !'), ('La suma de descuentos debe ser igual al total de dias solicitados'))
                    for line in this.line_descuenta_ids:
                        aux_tomados = line.holi_id.tomados_normal
                        aux_saldo  = line.holi_id.days_normal - line.holi_id.tomados_normal
                        if line.dias<=aux_saldo:
                            numero_dias = aux_tomados + line.dias
                            dias_obj.write(cr, uid, line.holi_id.id,{'tomados_normal':numero_dias})
                        else:
                            raise osv.except_osv(('Error de usuario !'), ('Verifique que los dias a descontar sean menor o igual a los saldos en cada periodo'))
                else:
                    raise osv.except_osv(('Error de usuario !'), ('Para liquidar con cargo a vacaciones debe seleccionar periodos a descontar'))
            self.write(cr, uid, ids[0],{'state':'Liquidado'})
        return True

    def phora_liquidado2(self, cr, uid, ids, context=None):
        dias_obj= self.pool.get('holidays.period')
        for this in self.browse(cr, uid, ids):
            if this.tipo=='Horas':
                if this.hora_fin<=0 or this.hora_inicio<=0:
                    raise osv.except_osv(('Error de usuario !'), ('Las horas deben ser mayor a cero'))
                if this.hora_fin<this.hora_inicio:
                    raise osv.except_osv(('Error de usuario !'), ('La hora final debe mayor a la inicial'))
            if this.descuenta:
                numero_dias = 0
                if this.saldo_id:
                    aux_tomados = this.saldo_id.tomados_normal
                    if this.saldo_id.days_normal>0:
                        aux_saldo  = this.saldo_id.days_normal - this.saldo_id.tomados_normal
                        if not aux_saldo>=0:
                            raise osv.except_osv(('Error de usuario !'), ('No tiene numero suficientes de dias disponibles'))
                    else:
                        raise osv.except_osv(('Error de usuario !'), ('No tiene numero suficientes de dias disponibles'))
                    #validar disponibiliad de dias
                    if not aux_saldo>=this.total_dias:
                        #debe registrar lineas de cada periodo con dias y descontar de cada uno
                        raise osv.except_osv(('Error de usuario !'), ('No tiene numero suficientes de dias disponibles'))
                    numero_dias = aux_tomados + this.total_dias
                dias_obj.write(cr, uid, this.saldo_id.id,{'tomados_normal':numero_dias})
            self.write(cr, uid, ids[0],{'state':'Liquidado'})
        return True


    def draft_phora_ejecutado(self, cr, uid, ids, context=None):
        dias_obj= self.pool.get('holidays.period')
        for this in self.browse(cr, uid, ids):
#            if not this.aprobado_por:
#                raise osv.except_osv(('Error de usuario !'), ('No puede ejecutar si no esta aprobado'))
            if this.tipo=='Horas':
                if this.hora_fin<=0 or this.hora_inicio<=0:
                    raise osv.except_osv(('Error de usuario !'), ('Las horas deben ser mayor a cero'))
                if this.hora_fin<this.hora_inicio:
                    raise osv.except_osv(('Error de usuario !'), ('La hora final debe mayor a la inicial'))
            if this.code=='/':
                obj_sequence = self.pool.get('ir.sequence')
                aux_code = obj_sequence.get(cr, uid, 'hr.holidays')
                self.write(cr, uid, ids[0],{'state':'Ejecutado','code':aux_code})
            else:
                self.write(cr, uid, ids[0],{'state':'Ejecutado'})
        return True

    def _get_uid(self, cr, uid, context=None):
        return uid


    def _checkHoliDate(self, cr, uid, ids):
        #OJO mover al compute sino no corre el duplicar
        return True
        band = True
        for this in self.browse(cr, uid, ids):
            aux_date = time.strftime('%Y-%m-%d')
            if this.date_permiso!=aux_date:
                band = False
                raise osv.except_osv('Error de usuario', 'La fecha debe ser igual a la actual')
        return band

    def _get_employee(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if user.employee_id:
            return user.employee_id.id

#    _constraints = [
#        (_checkHoliDate,
#         ustr('La fecha debe ser la actual.'),[ustr('Fecha'), 'Fecha'])
#        ]

    _defaults = dict(
        employee_id = _get_employee,
        code = '/',
        date_permiso = time.strftime('%Y-%m-%d'),
        state = 'Borrador',
        tipo2 = 'Permiso',
        create_user_id = _get_uid,
    )
permisoHora()

class repphLine(osv.TransientModel):
    _name = 'repph.line'
    _columns = dict(
        re_id = fields.many2one('repph','Rep'),
        e_id = fields.many2one('hr.employee','Funcionario'),
        tph = fields.integer('Total Permiso Hora'),
        horas = fields.float('Horas'),
        tpd = fields.integer('Total Permiso Dias'),
        dias = fields.float('Dias'),
    )
repphLine()
class repPh(osv.TransientModel):
    _name = 'repph'
    _columns = dict(
        date_s = fields.date('Desde'),
        date_e = fields.date('Hasta'),
        tipo_c = fields.many2one('hr.contract.type.type','Tipo Contrato'),
        line_ids = fields.one2many('repph.line','re_id','Detalle'),
    )

    def compute_repph(self, cr, uid, ids, context):
        line_obj = self.pool.get('repph.line')
        for this in self.browse(cr, uid, ids):
            print "VELE"
        return True

repPh()
