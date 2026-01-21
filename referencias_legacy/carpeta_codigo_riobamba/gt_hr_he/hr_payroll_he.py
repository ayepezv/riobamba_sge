#-*- coding:utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

import time
from datetime import date, datetime, timedelta
import netsvc
from osv import fields, osv
from tools import config
from tools.translate import _
import decimal_precision as dp

class heConfig(osv.Model):
    _name = 'he.config'
    _order = 'contract_type desc'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.name + " - " + record.contract_type.name
            res.append((record.id, name))
        return res

    _columns = dict(
        name = fields.selection([('Suplementaria','Suplementaria'),('Extraordinaria','Extraordinaria')],'Tipo Hora',required=True),
        contract_type = fields.many2one('hr.contract.type','Tipo Contrato',required=True),
        coef = fields.float('Coeficiente',required=True),
        rule_id = fields.many2one('hr.salary.rule','Regla Salarial',required=True),
        )

heConfig()

##INDIVIDUAL HE REGISTER
class hrHeRegisterAloneLine(osv.Model):
    _name = 'hr.he.register.alone.line'

    def create(self, cr, uid, vals, context=None):
        result = True
        period_obj = self.pool.get('hr.work.period')
        fest_obj = self.pool.get('hr.calendar.line')
        line_obj = self.pool.get('hr.he.register.alone.line')
        alone_obj = self.pool.get('hr.he.register.alone')
        return super(hrHeRegisterAloneLine, self).create(cr, uid, vals, context=None)
    
    def _calcular_usd(self, cr, uid, ids, field_name, arg, context=None):    
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            costo_hora = line.registro_id.contract_id.costo_hora
            aux = (costo_hora * line.h_25 * 1.25) + (costo_hora * line.h_60 * 1.6) + (costo_hora * line.h_50 * 1.5) + (costo_hora * line.h_100 * 2)  
            res[line.id] = aux
        return res

    def calcular_hora(self, cr, uid, ids, field_name, arg, context=None):
        #CALCULA LAS HORAS EXTRA EN NUMERO
        
         res = {}
         for line in self.browse(cr, uid, ids, context=context):
            result = True           
            period_obj = self.pool.get('hr.work.period')
            fest_obj = self.pool.get('hr.calendar.line')
            line_obj = self.pool.get('hr.he.register.alone.line')
            alone_obj = self.pool.get('hr.he.register.alone')
            period_ids = period_obj.search(cr ,uid, [('active','=',True)],limit=1)
            if not period_ids:
                raise osv.except_osv(('Error de configuración'), 
                                     ('No existe tabla de periodo definida activa, por favor configure una'))
            periodo = period_obj.browse(cr, uid, period_ids[0])            
            parent =line.registro_id.id
            periodo1 = line.registro_id.period_id
            fecha = line.name
            if hora_desde>hora_hasta:
                raise osv.except_osv(('Error de usuario'), ('La hora inicio no puede ser menor a la final'))               
            #busco primero si es feriado no importa las horas
            fest_ids = fest_obj.search(cr, uid, [('date','=',line.name)])
            if fest_ids:
                line.festivo = True
            if hora_desde >= periodo.hour_start_ext and hora_hasta <= periodo.hour_start_ext: 
                line.festivo = True
            if not fest_ids:
                #no es festivo entonces debe estar fuera del horario normal
                if (hora_desde > periodo.hour_start and hora_hasta < periodo.hour_end):
                  
                    result = False
                if (hora_desde > periodo.hour_start and hora_desde < periodo.hour_end):
                    result = False
                    
                if (hora_hasta > periodo.hour_start and hora_hasta < periodo.hour_end):
                    result = False
                 
                if (hora_desde > periodo.hour_start_aft and hora_hasta < periodo.hour_end_aft):
                    result = False
                    
                if (hora_desde > periodo.hour_start_aft and hora_desde < periodo.hour_end_aft):
                    result = False
                    
                if (hora_hasta > periodo.hour_start_aft and hora_hasta < periodo.hour_end_aft):
                    result = False
                              
            if result == False:
                raise osv.except_osv(('Error de usuario'), ('No puede registrar horas que estan dentro del horario normal de labores'))
            else:
                res[line.id] = hora_hasta-hora_desde
            return res

    def _compute_he_usd_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            costo_hora = this.registro_id.contract_id.costo_hora
            res[this.id] = {
                'usd_25': 0.0,
                'usd_50': 0.0,
                'usd_60': 0.0,
                'usd_100': 0.0,
            }
            aux25 = aux50 = aux60 = aux100 = 0
            aux25 = (this.h_25 * 1.25 * costo_hora)
            aux50 = (this.h_50 * 1.50 * costo_hora)
            aux60 = (this.h_60 * 1.60 * costo_hora)
            aux100 = (this.h_100 * 2 * costo_hora)
        res[this.id]['usd_25']= aux25
        res[this.id]['usd_50']= aux50
        res[this.id]['usd_60']= aux60
        res[this.id]['usd_100']= aux100
        return res


    _columns = dict(
        name = fields.date('Fecha'),
#        hora_desde = fields.float('Hora desde',required=True),
#        hora_hasta = fields.float('Hora hasta',required=True),
        h_25 = fields.float('Horas 25%'),
        h_50 = fields.float('Horas 50%'),
        h_60 = fields.float('Horas 60%'),
        h_100 = fields.float('Horas 100%'),
        usd_25 = fields.function(_compute_he_usd_line,type="float",string='USD 25%',multi="valoresline",store=True),
        usd_50 = fields.function(_compute_he_usd_line,type="float",string='USD 50%',multi="valoresline",store=True),
        usd_60 = fields.function(_compute_he_usd_line,type="float",string='USD 60%',multi="valoresline",store=True),
        usd_100 = fields.function(_compute_he_usd_line,type="float",string='USD 100%',multi="valoresline",store=True),
        total_usd = fields.function(_calcular_usd, type='float',
                                    store = True, string='Total USD'),
        #t_hora= fields.function(calcular_hora, type='float',
          #                                store = True, string='Total Horas'),
        festivo = fields.boolean('Extraordinarias'),
#        tipo_he = fields.many2one('he.config','Tipo Hora',required=True),
        actividad = fields.char('Actividades cumplidas',size=256),
        registro_id = fields.many2one('hr.he.register.alone','Detalle por Empleado', ondelete = 'cascade'),
        contract_id = fields.related('registro_id', 'contract_id', type='many2one', relation='hr.contract',
                                       string='Contrato', store=True),
        contract_type = fields.related('contract_id', 'type_id', type='many2one', relation='hr.contract.type',
                                       string='Tipo Contrato', store=True),
        )

hrHeRegisterAloneLine()

class logAlone(osv.Model):
    _name = 'alone.log'
    _order = 'date desc'
    _columns = dict(
        name = fields.many2one('res.users','Usuario'),
        date = fields.datetime('Fecha'),
        action = fields.char('Acción',size=64),
        desc = fields.char('Observación',size=256),
        alone_log_id = fields.many2one('hr.he.register.alone','Solicitud'),
        )

    _defaults=dict(
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        )
logAlone

class hrHeIeLine(osv.Model):
    _inherit = 'hr.ie.line'
    _columns = dict(
        registro_id = fields.many2one('hr.he.register.alone','Cabecera'),
        )
hrHeIeLine()

class hrHeRegisterAlone(osv.Model):
    _name = 'hr.he.register.alone'
    _order = 'date_create desc'

    def _generate_log(self, cr, uid, id, state, context=None ):
        alone_obj = self.pool.get('hr.he.register.alone')
        log_obj = self.pool.get('alone.log')
        alone=alone_obj.browse(cr, uid, id)
        log_obj.create(cr, uid, {
                'name':uid,
                'action':state,
                'alone_log_id':alone.id,
                'desc':alone.observation,
                'date':time.strftime('%Y-%m-%d %H:%M:%S')  
                })
        alone_obj.write(cr, uid, id, {
                'observation':'',
                })
        return True

    def unlink(self, cr, uid, id, context=None):
        raise osv.except_osv(('Error'), ('No puede eliminar el documento'))

    def create(self, cr, uid, vals, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        vals['name'] = obj_sequence.get(cr, uid, 'hr.he.register.alone')
        return super(hrHeRegisterAlone, self).create(cr, uid, vals, context=None)

    def _compute_he_usd(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            res[this.id] = {
                'total_25': 0.0,
                'total_50': 0.0,
                'total_60': 0.0,
                'total_100': 0.0,
            }
            aux25 = aux50 = aux60 = aux100 = 0
            for line in this.line_ids:
                aux25 += line.usd_25
                aux50 += line.usd_50
                aux60 += line.usd_60
                aux100 += line.usd_100
        res[this.id]['total_25']= aux25
        res[this.id]['total_50']= aux50
        res[this.id]['total_60']= aux60
        res[this.id]['total_100']= aux100
        return res

    def _compute_he_total(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                aux += line.total_usd
        res[this.id] = aux
        return res

    _columns = dict(
        date = fields.date('Fecha Aplicacion Rol'),
        costo_hora = fields.related('contract_id','costo_hora', type='float', 
                                    string='Costo Hora', store=True),
        detalle_ids = fields.one2many('hr.ie.line', 'registro_id', 'Detalle Total'),
        registro_d_id = fields.many2one('hr.he.register','Detalle por Empleado', ondelete = 'cascade'),
        date_create = fields.date('Fecha creación',readonly=True),
        total_25 = fields.function(_compute_he_usd,type="float",string='Total 25%',multi="valores"),
        total_50 = fields.function(_compute_he_usd,type="float",string='Total 50%',multi="valores"),
        total_60 = fields.function(_compute_he_usd,type="float",string='Total 60%',multi="valores"),
        total_100 = fields.function(_compute_he_usd,type="float",string='Total 100%',multi="valores"),
        total = fields.function(_compute_he_total,type="float",string='Total USD',store=True),
        contract_id = fields.many2one('hr.contract','Empleado',required=True),
        employee_id =fields.related('contract_id', 'employee_id', type='many2one', relation='hr.employee',
                                       string='Empleado', store=True),
        user_id =fields.related('employee_id', 'user_id', type='many2one', relation='res.users',
                                       string='Usuario', store=True),
        type_contract_id =fields.many2one('hr.contract.type','Tipo de contrato',readonly=True),        
        department_id = fields.related('contract_id', 'department_id', type='many2one', relation='hr.department',
                                       string='Departamento',store=True, readonly=True),
        name = fields.char('Código',size=10,readonly=True),
        state = fields.selection([('draft','Borrador'),('proceso','En proceso'),
                                  ('aprobado','Aprobado'),('cancel','Cancelado'),('done','Terminado')],
                                 'Estado', select=True, readonly=True),
        period_id = fields.many2one('hr.work.period.line','Periodo',required=True),
        line_ids = fields.one2many('hr.he.register.alone.line', 'registro_id', 'Detalle',
                                   states={'done':[('readonly',True)]}),
        revert = fields.boolean('Devuelto',readonly=True),
        observation = fields.char('Comentario',size=256,
                                  help="Coloque aquí su comentario referente al proceso de la solicitud de compra"),
        log_ids = fields.one2many('alone.log','alone_log_id','Solicitud',readonly=True),
        )

    def compute_he_alone(self, cr, uid, ids, context=None):
        # en este metodo se debe agrupar por tipo de hora y generar un solo line
        line_ie_obj = self.pool.get('hr.ie.line')
        rule_obj = self.pool.get('hr.salary.rule')
        for this in self.browse(cr, uid, ids):
            for anterior in this.detalle_ids:
                line_ie_obj.unlink(cr, uid, [anterior.id])
            aux = 0
            values = {}
            rule_25_id = rule_obj.search(cr, uid, [('code','=','HS')],limit=1)[0]
            values[rule_25_id] = this.total_25
            rule_50_id = rule_obj.search(cr, uid, [('code','=','HS')],limit=1)[0]
            values[rule_50_id] += this.total_50
            rule_60_id = rule_obj.search(cr, uid, [('code','=','HS')],limit=1)[0]
            values[rule_60_id] += this.total_60
            rule_100_id = rule_obj.search(cr, uid, [('code','=','HS')],limit=1)[0]
            values[rule_100_id] += this.total_100
            for val in values:
                if values[val] > 0:
                    line_ie_obj.create(cr, uid, {
                        'name':this.contract_id.employee_id.complete_name,
                        'employee_id':this.contract_id.employee_id.id,
                        'date':this.date,
                        'valor':values[val],
                        'categ_id':val,
                        'state':'pendiente',
                        'period_id':this.period_id.id,
                        'registro_id':this.id,
                        })
        return True

    def he_alone_aprobado_terminado(self, cr, uid, ids, context=None):
        self.compute_he_alone(cr, uid, ids, context)
        self.write(cr, uid, ids[0],{'state':'done'})
        self._generate_log(cr, uid, ids[0],'Terminado')
        return True

    def he_alone_process_aprobado(self, cr, uid, ids, context=None):
 #       self.compute_he_alone(cr, uid, ids, context)
        self.write(cr, uid, ids[0],{'state':'aprobado'})
        self._generate_log(cr, uid, ids[0],'Aprobado')
        return True

    def he_alone_draft_process(self, cr, uid, ids, context=None):
        #llamar al calcular
        #self.compute_he_alone(cr, uid, ids, context)
        for this in self.browse(cr, uid, ids):
            if not this.line_ids:
                raise osv.except_osv(('Error de usuario'), ('Debe registrar por lo menos una linea de detalle'))
            self.write(cr, uid, this.id,{'state':'proceso'})
            self._generate_log(cr, uid, this.id,'En proceso')
        return True

    def _get_contract(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        emp_ids = emp_obj.search(cr, uid, [('user_id','=',uid)],limit=1)
        if emp_ids:
            contract_ids = contract_obj.search(cr, uid, [('employee_id','=',emp_ids[0])],limit=1)
            if contract_ids:
                return contract_ids[0]
            else:
                return False
                #raise osv.except_osv(('Error de usuario'), ('No existe contrato activo para el empleado'))
        else:
            return False
            #raise osv.except_osv(('Error de usuario'), ('No existe empleado relacionado al usuario que registra'))

    def _get_department(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        return user.context_department_id.id

    def _get_type_contract(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        emp_ids = emp_obj.search(cr, uid, [('user_id','=',uid)],limit=1)
        if emp_ids:
            contract_ids = contract_obj.search(cr, uid, [('employee_id','=',emp_ids[0])],limit=1)
            if contract_ids:
                for obj_contract in self.pool.get('hr.contract').browse(cr, uid, [contract_ids[0]], context=None):                
                    return obj_contract.type_id.id
            else:
                return False
                #raise osv.except_osv(('Error de usuario'), ('No existe contrato activo para el empleado'))
        else:
            return False
            #raise osv.except_osv(('Error de usuario'), ('No existe empleado relacionado al usuario que registra'))    

    _defaults = dict(
        state = 'draft',
        contract_id = _get_contract,
        department_id = _get_department,
        type_contract_id = _get_type_contract,
        date_create = time.strftime('%Y-%m-%d'),
        )

hrHeRegisterAlone()

##PERIOD HOURS REGISTER -- consolidado

class hrHeRegister(osv.osv):
    _name = "hr.he.register"
    _description = "Registro de Horas Extra"
    
    def unlink(self, cr, uid, ids, *args, **kwargs):
        for reg in self.browse(cr, uid, ids):
            if reg.state=='done':
                raise osv.except_osv(('Operación no permitida !'), ('No puede eliminar registros validados'))
        return super(hrHeRegister, self).unlink(cr, uid, ids, *args, **kwargs)    

    def wkf_draft(self, cr, uid, id):
        self.write(cr, uid, id,{'state':'draft'})
        return True

    def he_draft_validar(self, cr, uid, id, context=None):
        aux_name = ""
        for this in self.browse(cr, uid, id):
            #name = "Resumen Horas Extras " + this. 
            if this.line_ids:
                self.write(cr, uid, id,{'state':'validate'})
            else:
                raise osv.except_osv(('Operación no permitida !'), ('No existen horas extras en este periodo'))      
        return True

    def he_validar_cancelar(self, cr, uid, id, context=None):
        self.write(cr, uid, id,{'state':'cancel'})
        return True

    def he_validar_terminar(self, cr, uid, ids, context=None):
        line_ie_obj = self.pool.get('hr.ie.line')
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                for ie_line in line.detalle_ids:
                    line_ie_obj.write(cr, uid, ie_line.id,{
                            'state':'pendiente',
                            })
        self.write(cr, uid, ids,{'state':'done'})
        
    def cargar_empleados(self, cr, uid, ids, context=None):
        obj = self.pool.get('hr.he.register')
        line_obj = self.pool.get('hr.he.register.alone')
        for this in self.browse(cr, uid, ids):
            detail_ids = line_obj.search(cr, uid, [('period_id','=',this.period_id.id),('state','in',('done','proceso'))])
            if detail_ids:
                for detail in detail_ids:
                    line_obj.write(cr, uid, detail,{
                            'registro_d_id':this.id,
                            })
            else:
                raise osv.except_osv(('Error de usuario'), ('No existen registros de horas extras en este periodo'))
        return True    
                    
    _columns = dict(
        name = fields.char('Descripcion', size=35, readonly=True),
        state = fields.selection([('draft','Borrador'),('validate','Validado'),('cancel','Cancelado'),('done','Terminado')],
                                 'Estado', select=True, readonly=True),
        department_id = fields.many2one('hr.department', 'Departamento', ondelete = 'cascade',
                                        help="Si selecciona un departamento se listarán solo los empleados correspondientes a este",
                                        states={'done':[('readonly',True)]}),
        period_id = fields.many2one('hr.work.period.line','Periodo',
                                    states={'done':[('readonly',True)]}),
        line_ids = fields.one2many('hr.he.register.alone', 'registro_d_id', 'Detalle',
                                   states={'done':[('readonly',True)]}),
        )
    
    _defaults = dict(
        state = 'draft',
        name = 'Registro HE'
        )
    
    #_sql_constraints = [
    #    ('month_week', 'unique(period_id,week_id)',
    #     'Solo puede sacar un Resumen de Horas quincenal'),
    #    ('week_one', 'unique(week_id,is_one)',
    #     'Solo puede haber una quincena inicial en el mes'),
    #    ]
    
hrHeRegister()

class hrHeRegisterLine(osv.osv):
    _name = "hr.he.register.line"
    _description = "Detalle de horas por empleado"
    _order = "employee_name"

    _columns = dict(
        name = fields.char('Descripcion', size=12),
#        registro_id = fields.many2one('hr.he.register','Detalle por Empleado', ondelete = 'cascade'),
        employee_id = fields.many2one('hr.employee', 'Empleado', ondelete = 'cascade'),
        employee_name = fields.char('EMPLEADO',size=256),
        period_id = fields.many2one('hr.work.period.line','Periodo',
                                    states={'validate':[('readonly',True)]}),
        wage = fields.float('Salario'),
        costo_hora = fields.float('Costo Hora', digits_compute=dp.get_precision('Extras')),
        hora_100 = fields.float('01', required=True),
        hora_125 = fields.float('25%'),
        hora_150 = fields.float('50%'),
        hora_200 = fields.float('100%'),
        hora_125_ = fields.float('JNoct.'),
        hora_150_ = fields.float('50%'),
        hora_200_ = fields.float('100%'),
        total = fields.float('TOTAL $'),
        )

    _defaults = dict(
        hora_100 = 80,
        )

hrHeRegisterLine()
