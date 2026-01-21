# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
import time
from time import strftime, strptime
import datetime
from datetime import date, datetime

from osv import osv, fields

import decimal_precision as dp
from gt_tool import amount_to_text_ec

class diasContratoLine(osv.TransientModel):
    _name = 'dias.contrato.line'
    _order = 'employee_name asc'
    _columns = dict(
        employee_name = fields.char('Funcionario',size=256),
        d_id = fields.many2one('dias.contrato','Dias'),
        contract_id = fields.many2one('hr.contract','Contrato Funcionario'),
        dias = fields.integer('Total Dias'),
    )
diasContratoLine

class diasContrato(osv.TransientModel):
    _name = 'dias.contrato'
    _columns = dict(
        opcion = fields.selection([('Activos','Activos'),('Todos','Todos')],'Contratos??'),
        fecha = fields.date('Fecha para calculo(Hasta)'),
        tipo_contrato = fields.many2one('hr.contract.type.type','Tipo Contrato'),
        line_ids = fields.one2many('dias.contrato.line','d_id','Detalle'),
    )

    def print_dias_contrato(self, cr, uid, ids,context):
        obj = self.pool.get('dias.contrato')
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        obj.compute_dias_contrato(cr, uid, ids, context)
        datas = {'ids': [report.id], 'model': 'report.dias.contrato'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'dias.contrato',
            'model': 'dias.contrato',
            'datas': datas,
            'nodestroy': True,                        
        }

    def compute_dias_contrato(self, cr, uid, ids,context):
        contract_obj = self.pool.get('hr.contract')
        line_obj = self.pool.get('dias.contrato.line')
        for this in self.browse(cr, uid, ids):
            line_ids_antes = line_obj.search(cr, uid, [('d_id','=',this.id)])
            if line_ids_antes:
                line_obj.unlink(cr, uid, line_ids_antes)
            if this.tipo_contrato:
                if this.opcion=='Activos':
                    contract_ids = contract_obj.search(cr, uid, [('subtype_id','=',this.tipo_contrato.id),('activo','=',True)])
                else:
                    contract_ids = contract_obj.search(cr, uid, [('subtype_id','=',this.tipo_contrato.id)])
            else:
                if this.opcion=='Activos':
                    contract_ids = contract_obj.search(cr, uid, [('activo','=',True)])
                else:
                    contract_ids = contract_obj.search(cr, uid, [])
            date = this.fecha
            if contract_ids:
                for contract_id in contract_ids:
                    dias = 0
                    contrato = contract_obj.browse(cr, uid, contract_id)
                    inicio = contrato.date_start.split('-')
                    if contrato.date_end and (time.strftime('%Y-%m-%d')>contrato.date_end):
                        fin = contrato.date_end.split('-')
                    else:
                        fin = time.strftime('%Y-%m-%d').split('-')
                    dateinicio = datetime( int(inicio[0]), int(inicio[1]), int(inicio[2]) )
                    datefin = datetime( int(fin[0]), int(fin[1]), int(fin[2]) )
                    delta = datefin - dateinicio
                    dias = delta.days + 1
                    line_obj.create(cr, uid, {
                        'd_id':this.id,
                        'contract_id':contrato.id,
#                        'dias':contrato.dias_contrato,
                        'dias':dias,
                        'employee_name':contrato.employee_id.complete_name,
                    })
                    contract_obj.write(cr, uid, contrato.id,{'dias_contrato':dias,})
        return True

    _defaults = dict(
        fecha = time.strftime('%Y-%m-%d'),
        opcion = 'Activos',
    )
    
diasContrato()

class hrHistWage(osv.osv):
    _name = 'hr.hist.wage'
    _description = 'Historial Salario'
    _order = 'name desc'
    
    _columns = dict(
        name = fields.date('Fecha Actualización'),
        wage = fields.float('Salario Anterior'),
        new_wage = fields.float('Salario Nuevo'),
        contract_wage_id = fields.many2one('hr.contract','Contrato'),
        )

hrHistWage()

class gt_hr_contract_type(osv.osv):
    _inherit = 'hr.contract.type'
    _columns = {
        'formula_normales': fields.text('Formula para dias normales'),
        'formula_adicionales': fields.text('Formula para dias adicionales'),
    }
    _defaults = {
        'formula_normales': '''# Available variables:
#----------------------
# employee: hr.employee object
# contract: hr.contract object
# date_time: date and time functions

# Note: returned value have to be set in the variable 'result'

result = 0''',
        'formula_adicionales': '''# Available variables:
#----------------------
# employee: hr.employee object
# contract: hr.contract object
# date_time: date and time functions

# Note: returned value have to be set in the variable 'result'

result = 0''',
    }
gt_hr_contract_type()

class hrContractTypeType(osv.osv):
    _name = 'hr.contract.type.type'
    _description = 'Tipo de contrato'
    _order = 'type_id asc, name asc'
    
    _columns = dict(
        account_id = fields.many2one('account.account','Cuenta Quincena'),
        name = fields.char('Tipo de contrato', size=32),
        type_id = fields.many2one('hr.contract.type','Tipo de relación laboral'),
        )

hrContractTypeType()

class hrHistJob(osv.osv):
    _name = 'hr.hist.job'
    _description = 'Historial Puestos Trabajo'
    _order = 'name desc'
    _columns = dict(
        name = fields.date('Desde'),
        date_end = fields.date('Hasta'),
        job_id = fields.many2one('hr.job','Cargo Anterior'),
        new_job = fields.many2one('hr.job','Cargo Nuevo'),
        contract_job_id = fields.many2one('hr.contract','Contrato'),
        )

hrHistJob()

class aportableLine(osv.Model):
    _name = 'aportable.line'
    _columns = dict(
        c_id= fields.many2one('hr.contract','Contrato',ondelete='cascade'),
        name = fields.char('Referencia Rol',size=32),
        period_id = fields.many2one('hr.work.period.line','Periodo'),
        derecho_fr = fields.boolean('Derecho FR'),
        cobro_fr = fields.boolean('Cobro FR Rol'),
        decimo_rol = fields.boolean('Cobro Decimos'),
    )
aportableLine()

class contratoNivel(osv.Model):
    _name = 'contrato.nivel'
    _columns = dict(
        name = fields.char('Nivel',size=16),
    )
contratoNivel()

class hr_account_configuration(osv.osv):
    _name = 'hr.account.configuration'

#    def unlink(self, cr, uid, ids, context=None):
#        raise osv.except_osv('Error', 'No pueden eliminar reglas comuniquese con el administrador')

    def _tipo_budget(self, cr, uid, ids, a, b, c):
        res = {}
        for this in self.browse(cr, uid, ids):
            res[this.id] = this.budget_id.code[0:1]
        return res

    _columns = {
        'rule_id': fields.many2one('hr.salary.rule', 'Rubro'),
        'project_id': fields.many2one('account.analytic.account', 'Centro de costo'),
        'pay_account_id': fields.many2one('account.account', 'Cuenta por Pagar'),
        'expense_account_id': fields.many2one('account.account', 'Cuenta de Gasto'),
        'budget_id':fields.many2one('budget.post','Partida',required=True),
        'tipo_budget':fields.function(_tipo_budget,string='Tipo Presupuesto',type="char",size=1,store=True),
    }

hr_account_configuration()

class hrContractBase(osv.osv):
    _inherit = 'hr.contract'
    _order = 'employee_name asc'

    def onchange_pcontract(self, cr, uid, ids, program_id):
        result = {}
        result['budget_id'] = ''
        return {'value': result}

    #def unlink(self, cr, uid, ids, *args, **kwargs):
    #    for contract in self.browse(cr, uid, ids):
    #        if contract.state!='draft':
    #            raise osv.except_osv(('Operación no permitida !'), ('Solo puede eliminar contratos en borrador '))
    #    return super(hrContractBase, self).unlink(cr, uid, ids, *args, **kwargs)

    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        ids = []
        ids_cedula = self.search(cr, uid, [('employee_name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_cedula))
        return self.name_get(cr, uid, ids, context=context)    

    def crear_proyecciones(self, cr, uid, ids, context={}):
        obj_empleado = self.pool.get('hr.employee')
        obj_period = self.pool.get('hr.work.period')
        obj_anual = self.pool.get('hr.anual.projection')
        ids_contratos = []
        time_actual = datetime.datetime.today()
        ids_contratos1 = self.search(cr, uid, [('date_start','<=',str(time_actual)),('date_end','>=',str(time_actual))])
        ids_contratos2 = self.search(cr, uid, [('date_start','<=',str(time_actual)),('date_end','=',False)])
        ids_contratos = ids_contratos1 + ids_contratos2
        period_id = obj_period.search(cr, uid, [('active','=',True)])
        period = obj_period.browse(cr, uid, period_id[0], context=context)
        for contrato in self.browse(cr, uid, ids_contratos, context=context):
            empleado = contrato.employee_id
            obj_anual.create(cr, uid, {'name':period.name, 'fy_id':period.id, 'employee_id': empleado.id})

    def _compute_tax(self, cr, uid, ids, field_name, arg, context):
        #calcula el impuesto a la renta para el anio
        result={}
        anual_obj=self.pool.get('hr.anual.rent.tax')
        project_obj=self.pool.get('hr.anual.projection')
        proj_line_obj=self.pool.get('hr.projection.line')
        for this in self.browse(cr, uid, ids):
            for year_line in this.rent_tax_ids:
                tabla_pool = self.pool.get('hr.base.retention')
                line_pool = self.pool.get('hr.base.retention.line')
                ing_grav=imp_sobre_excedente=imp_frac_basica=base=excedente=0
                gastos_personales=0
                result[year_line.id] = {
                    'start_computed':0,
                    'mensual':0,
                    }
                ing_grav = this.wage * 12
                ap_personal = ing_grav * 0.0935
                t_wiess = ing_grav - ap_personal
                #proyecciones para el periodo, el anual del empleado
                proj_ids=project_obj.search(cr, uid, [('fy_id','=',year_line.fy_id.id)])
                if proj_ids:
                    for proj_ in proj_ids:
                        proj=project_obj.browse(cr, uid, proj_)
                        for proj_line in proj.line_ids:
                            gastos_personales = gastos_personales + proj_line.value
                            base = t_wiess - gastos_personales
                            tabla_ids=tabla_pool.search(cr, uid, [('period_id','=',year_line.fy_id.id)])
                            if tabla_ids:
                                for tabla in tabla_ids:
                                    linea_ids=line_pool.search(cr, uid,[('retention_id','=',tabla),
                                                                        ('fraccion_basica','<',base),('exceso_hasta','>',base)])
                                    for linea_ in linea_ids:
                                        linea=line_pool.browse(cr, uid, linea_)
                                        excedente=base-linea.fraccion_basica
                                        imp_sobre_excedente=excedente*linea.percent/100
                                        imp_frac_basica=linea.frac_basica_tax
                                        imp_renta_anual=imp_sobre_excedente+imp_frac_basica
                                        imp_renta_mensual=imp_renta_anual/12
                                        anual_obj.write(cr, uid, year_line.id,{
                                                'start_computed':imp_renta_anual,
                                                'mensual':imp_renta_mensual
                                                })
                            else:
                                raise osv.except_osv(('Aviso !'), 'No existe tabla de retencion, Notifique al personal de sistemas de esta configuración')
                else:
                    gastos_personales = gastos_personales
                    base = t_wiess - gastos_personales
                    tabla_ids=tabla_pool.search(cr, uid, [('period_id','=',year_line.fy_id.id)])
                    if tabla_ids:
                        for tabla in tabla_ids:
                            linea_ids=line_pool.search(cr, uid,[('retention_id','=',tabla),
                                                                ('fraccion_basica','<',base),('exceso_hasta','>',base)])
                            for linea_ in linea_ids:
                                linea=line_pool.browse(cr, uid, linea_)
                                excedente=base-linea.fraccion_basica
                                imp_sobre_excedente=excedente*linea.percent/100
                                imp_frac_basica=linea.frac_basica_tax
                                imp_renta_anual=imp_sobre_excedente+imp_frac_basica
                                imp_renta_mensual=imp_renta_anual/12
                                anual_obj.write(cr, uid, year_line.id,{
                                        'start_computed':imp_renta_anual,
                                        'mensual':imp_renta_mensual
                                        })
                    else:
                        raise osv.except_osv(('Aviso !'), 'No existe tabla de retencion, Notifique al personal de sistemas de esta configuración')
        return result

    def _check_max_projection(self, cr, uid, ids):
        result=True
        tabla_obj=self.pool.get('hr.base.retention')
        tabla_line_obj=self.pool.get('hr.base.retention.line')
        for obj in self.browse(cr, uid, ids):
            for line in obj.projection_ids:
                for projection in line.line_ids:
                    tabla_ids=tabla_obj.search(cr, uid, [('period_id','=',line.fy_id.id)])
                    if tabla_ids:
                        for tabla_ in tabla_ids:
                            tabla=tabla_obj.browse(cr, uid, tabla_)
                            for tabla_line_max in tabla.projection_max_line:
                                if projection.projection_id.name==tabla_line_max.name.name:
                                    if projection.value>tabla_line_max.max_value:
                                        result=False
                    else:
                        raise osv.except_osv(('Aviso !'), 'No existe tabla de retencion para este año laboral, Notifique al personal de sistemas de esta configuración')
        return result

    def _check_combo(self, cr, uid, ids):
        result = False
        for obj in self.browse(cr, uid, ids):
            j = 0
            if obj.sindicalizado:
                j+=1
            if obj.sindicato_choferes:
                j+=1
            if obj.asociacion:
                j+=1
        if j<=1:
            result = True
        return result

    def _check_contract(self, cr, uid, ids):
        result = False
        for obj in self.browse(cr, uid, ids):
            #contratos = self.search(cr, uid, [('active','=',True),('employee_id','=',obj.employee_id.id)])
            #if len(contratos) <= 1:
                result = True
        return result

    def _compute_hour_cost(self,cr, uid, ids, field_name, arg, context):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = (obj.wage) / 240
        return res

    def tarea_actualizar_costo_hora(self, cr, uid, ids, context=None):
        #ids = self.browse(cr, uid, [], context)
        #for obj in self.browse(cr, uid, ids, context):
        #    self.write(cr, uid, obj.id, {'wage': obj.wage, 'hour_cost': (obj.wage) / 240.00000})
        obj_he = self.pool.get("hr.he.register.line")
        ids_he = obj_he.search(cr, uid, [])
        for obj in obj_he.browse(cr, uid, ids_he, context):
            obj_he.write(cr, uid, obj.id, {'costo_hora': obj.employee_id.contract_id.wage/240.00000})
        return True
    
    def _complete_name(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            if obj.employee_id.employee_lastname:
                res[obj.id] = obj.employee_id.employee_lastname + ' ' + obj.employee_id.name
            else:
                res[obj.id] = obj.employee_id.name
        return res

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            #if record.employee_id.employee_lastname and record.employee_id.name:
            #    name = '%s %s' % (record.employee_id.employee_lastname, record.employee_id.name)
                name = record.name + " - " + record.employee_id.complete_name 
                res.append((record.id, name))
        return res

    #def create(self, cr, uid, vals, context=None):
    #    if vals.get('name'):
    #        vals['name']=vals['name'].upper()
    #    else:
    #        vals['name']='CONTRATO EMPRESA'            
    #    return super(hrContractBase, self).create(cr, uid, vals, context=None)    

#    def write(self, cr, uid, ids, vals, context=None):
#        if vals.has_key('budget_id')
#        return super(hrContractBase, self).write(cr, uid, ids, vals, context=context)
    
    def _compute_continuidad(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.tiene_continuidad:
                res[line.id] = line.contrato_anterior.continuidad_desde
                #res[line.id] = line.date_start
            else:
                res[line.id] = line.date_start
        return res
    
    def onchange_employee(self, cr, uid, ids, employee_id, context={}):
        emp_obj = self.pool.get('hr.employee')
        empleado = emp_obj.browse(cr, uid, employee_id)
        vals = {}
        return {'value':{'department_id':empleado.department_id.id}}

    def load_basic(self, cr, uid, ids, context=None):
        pass

    def _get_depto(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            if this.employee_id.department_id.id:
                res[this.id] = this.employee_id.department_id.id
            else:
                raise osv.except_osv(('Error !'), ('El empleado no tiene asignado un departamento '))
        return res    

    _STATE_CONTRACT = [('draft','Borrador'),('prueba','Periodo Prueba'),('primer','Primer Año'),
                       ('segundo','Segundo Año'),('indefinido','Indefinido'),('terminado','Terminado')]
    
    #STORE_CONTINUIDAD = {'hr.contract': (lambda self, cr, uid, ids, c={}: ids,
    #                                          ['request_ids', 'reserved_amount', 'commited_amount', 'reforma_ids', 'reforma_to_ids'],
    #                                          10),
    #             'crossovered.budget.certificate.line': (_get_certificates,
    #                                                     ['amount','amount_certified','amount_compromised','budget_line_id','state'], 10),
    #             'crossovered.budget.reform': (_get_reforms,
    #                                           ['amount', 'type_transaction', 'state'], 10)}

    def _get_employee(self, cr, uid, ids, context=None):
        result = {}
        contract_obj = self.pool.get('hr.contract')
        contract_ids = contract_obj.search(cr, uid, [('employee_id','in', ids)])
        return contract_ids        
    
    def _total_dias_contrato(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            inicio = this.date_start.split('-')
            if this.date_end and (time.strftime('%Y-%m-%d')>this.date_end):
                fin = this.date_end.split('-')
            else:
                fin = time.strftime('%Y-%m-%d').split('-')
            dateinicio = date( int(inicio[0]), int(inicio[1]), int(inicio[2]) )
            datefin = date( int(fin[0]), int(fin[1]), int(fin[2]) )
            delta = datefin - dateinicio
            res[this.id] = delta.days + 1
        return res

    def _check_partida(self, cr, uid, ids):
        return True
        for obj in self.browse(cr, uid, ids):
            if obj.budget_id.program_id.id!=obj.program_id.id:
                raise osv.except_osv(('Error de usuario !'), ('La partida del contrato no pertenece al programa seleccionado'))

    def _check_numero(self, cr, uid, ids):
        return True
        result = True
        period_obj = self.pool.get('account.period')
        for obj in self.browse(cr, uid, ids):
            date_aux = obj.date_start
#            period_ids = period_obj.find(cr, uid, date_aux)
            period_ids = period_obj.search(cr, uid, [('date_start','<=',date_aux),('date_stop','>=',date_aux)])
            if period_ids:
                period = period_obj.browse(cr, uid, period_ids[0])
                contratos = self.search(cr, uid, [('name','=',obj.name),('id','!=',obj.id),('activo','=',True),
                                                  ('date_start','>=',period.date_start),('date_start','<=',period.date_stop)])
                if len(contratos) >= 1:
                    result = False
        return result

    VAR_STORE = {
                'hr.employee': (_get_employee, ['department_id'], 10),
            }
    
    def _wage_letras(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            letra = amount_to_text_ec.amount_to_text_ec(this.wage)
            res[this.id] = letra
        return res

    def _get_activo(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            if this.activo:
                res[this.id] = 'ACTIVO'
            else:
                res[this.id] = 'INACTIVO'
        return res

    _columns = dict(
        config_rubro_ids = fields.many2many('hr.account.configuration','c_co_id','c_id','co_id','Configuracion Rubros'),
        state = fields.function(_get_activo, string="Estado", store=True, type="char",size=10), 
        nivel_id = fields.many2one('contrato.nivel','Nivel'),
        financia_id = fields.many2one('budget.financiamiento','Financiamiento'),
        oficio = fields.char('Oficio Nro.',size=32),
        informe = fields.char('Informe Nro.',size=32),
        fecha_informe = fields.date('Fecha Informe'),
        letras = fields.function(_wage_letras, string="Sueldo", store=True, type="char",size=256), 
        porcentaje_anticipo = fields.integer('Porcentaje Primera Quincena'),
        dias_contrato = fields.function(_total_dias_contrato, string="Total Dias", store=True, type="integer"), 
        asociacion = fields.boolean('Asociado','Marque el campo si el funcionario pertenece a la asociacion'),
        date_asociacion = fields.date('Fecha Ingreso Asociacion'),
        sindicalizado = fields.boolean('Sindicalizado',help="Marque el campo si el funcionario pertenece al sindicato"),
        sindicato_choferes = fields.boolean('Sindicato Choferes',help="Marque el campo si el funcionario pertenece al sindicato choferes"),
        cedula = fields.related('employee_id', 'name', type="char", size=120, string="Cedula", store=True),
        aportable_ids = fields.one2many('aportable.line','c_id','Detalle Aportacion'),
        program_id = fields.many2one('project.program','Programa'),
        budget_id = fields.many2one('budget.item','Partida Presupuestaria'),
        budget_ind = fields.char('Partida Individual',size=64),
        #state = fields.selection(_STATE_CONTRACT,'Estatus del contrato'),
        costo_hora = fields.function(_compute_hour_cost, method=True,
                                    string="Costo Hora", store=True, type="float", digits_compute=dp.get_precision('Extras'), 
                                    help="Es el valor en dólares de la hora de trabajo, calculado automaticamente"),
        fondo_reserva = fields.boolean('Fondo reserva rol', 
                                       help="Activar si el empleado va a recibir los fondos de reserva en el rol (usar fondo_reserva en las formulas)"),
        decimo = fields.boolean('Decimos a rol', 
                                help="Activar si el empleado va a recibir los decimos en el rol (usar decimo en las formulas)"),
        decimo_opc = fields.selection([('Acumular','Acumular'),('Decimo 3','Decimo 3'),('Decimo 4','Decimo 4'),('Ambos','Ambos')],'Decimos A Rol'),
        extension_iess = fields.boolean('Extension de cobertura IESS', 
                                       help="Activar si el empleado ha solicitado la extension de cobertura familiar para el IESS (usar extension_iess en las formulas)"),
        #projection_ids = fields.one2many('hr.anual.projection','contract_id','Proyecciones'),
        #rent_tax_ids = fields.one2many('hr.anual.rent.tax','c_tr_id','Impuesto Renta'),
        activo = fields.boolean('Activo'),
        #date_start_2 = fields.date('Fecha inicio segundo año'),
        #date_end_2 = fields.date('Fecha fin segundo año'),
        wage_hist_ids = fields.one2many('hr.hist.wage','contract_wage_id','Historial Salario'),
        job_hist_ids = fields.one2many('hr.hist.job','contract_job_id','Historial Puestos Trabajo'),
        #basic_wage = fields.boolean('Percibe Básico', help="Marque esta casilla si el empleado percibe el Salario Basico"),
        #employee_name = fields.function(_complete_name, method=True,
        #                                string="Nombre del Empleado", store=True, 
        #                                type="char", size=128),
        employee_name = fields.related('employee_id', 'complete_name', type="char", size=120, string="Empleado", store=True),
        #out_type = fields.selection(_OUT_TYPE,'Tipo de Salida'),
        #memo = fields.text('Motivo Salida'),
        subtype_id = fields.many2one('hr.contract.type.type', 'Tipo de Contrato', required=True),
        dias_fr = fields.integer('Días Acumulan FR', help="Especifique aquí el número de días que el empleado laboró anteriormente y que son aplicables para el fondo de reserva (usar dias_fr en las formulas)"),
        derecho_fr = fields.boolean('Derecho Fondos Reserva'),
        fecha_legalizacion = fields.date('Fecha de legalización'),
        codigo = fields.char('Codigo MRL',size=20),
        department_id = fields.function(_get_depto, type='many2one', relation='hr.department',
                                             store=VAR_STORE, string='Departamento'),
        #related('employee_id', 'department_id', type='many2one', relation='hr.department', 
        #                               string="Departamento", store=True,readonly=True),
        ocupational_id = fields.many2one('grupo.ocupacional', 'Grupo Ocupacional'),
        nivel_contrato = fields.many2one('hr.contract.nivel','Nivel'),
        #budget_line_id = fields.many2one('crossovered.budget.lines','Partida Presupuestaria'),
        project_id = fields.many2one('project.project','Proyecto'),
        activity_id = fields.many2one('project.task','Actividad'),
        work_id = fields.many2one('resource.calendar', 'Horario de Trabajo', required=True),
        marc_employee = fields.boolean('Obligado a marcar'),
        tiene_continuidad = fields.boolean('Tiene continuidad?', help='Seleccione el casillero si el servidor tiene un Contrato/Accion de personal anterior que se considere continuidad'),
        #continuidad_desde = fields.date('Aplica continuidad desde', help='En caso de aplicar continuidad, este campo obtendra la fecha del primer contrato/accion de personal que se encuentre encadenado'),
        contrato_anterior = fields.many2one('hr.contract', 'Contrato/Accion de personal anterior'),
        continuidad_desde = fields.function(_compute_continuidad, method=True, store=True, type='date',
                                            string='Aplica continuidad desde', help='En caso de aplicar continuidad, este campo obtendra la fecha del primer contrato/accion de personal que se encuentre encadenado'),
        )

    _constraints = [
        (_check_partida,'La partida no corresponde al programa seleccionado',['budget_id']),
        (_check_contract,'Solo puede tener un contrato activo para un empleado',['employee_id','activo']),
        (_check_combo,'Solo puede marcar una opcion',['employee_id']),
        (_check_numero,'El numero debe ser unico por anio',['name']),
        #(_check_max_projection,'No puede sobrepasar los valore maximos q deducir por favor revise su proyeccion de gastos personales',['projection_ids']),
        ]
    
    _defaults = dict(
        decimo = 'Acumular',
        fondo_reserva = True,
        )
    
    def obtener_dias_fr(self, cr, uid, ids, contract_id, context={}):
        obj_contrato = self.pool.get('hr.contract')
        dias = 0
        if contract_id:
            contrato = obj_contrato.browse(cr, uid, contract_id, context)
            time_fecha1 = datetime.datetime.strptime(contrato.date_start, "%Y-%m-%d")
            time_fecha2 = datetime.datetime.strptime(contrato.date_end, "%Y-%m-%d")
            resultado = time_fecha2 - time_fecha1
            dias = resultado.days + contrato.dias_fr
        return {'value': {'dias_fr':dias}}
    
    def search_prueba(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        return super(hrContractBase, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

hrContractBase()

class hrContractNivel(osv.osv):
    _name = 'hr.contract.nivel'
    _columns = dict(
        name = fields.char('Nombre', size = 64)
    )

hrContractNivel()
