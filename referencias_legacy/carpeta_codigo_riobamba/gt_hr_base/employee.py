# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
import time
from time import strftime, strptime
from osv import osv, fields
from gt_tool import tool
from datetime import date, datetime

class resPartnerEmp(osv.Model):
    _inherit = 'res.partner'
    
    def _emp_name(self, cr, uid, ids, field_name, arg, context):
        employee_obj = self.pool.get('hr.employee')
        res = {}
        for partner in self.browse(cr, uid, ids):
            aux_name = ""
            employee_ids = employee_obj.search(cr, uid, [('name','=',partner.ced_ruc)],limit=1)
            if employee_ids:
                employee = employee_obj.browse(cr, uid, employee_ids[0])
                aux_name = employee.complete_name
            res[partner.id] = aux_name
        return res

    _columns = dict(
        name_empleado = fields.function(_emp_name, method=True, string="Empleado Nombre", store=True, type="char",size=256), 
    )
resPartnerEmp()
class hrAccionPersonal(osv.Model):
    _name = 'hr.accion.personal'
    _description = 'Accion de personal'

    def get_nivel_contrato(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = line.contract_id.nivel_contrato.name
        return res

    _columns = dict(
        alcalde_e = fields.many2one('hr.employee','Alcalde Encargado'),
        subrog_alcalde = fields.boolean('Alcalde subrogado'),
        talento_e = fields.many2one('hr.employee','Director Encargado'),
        subrog_talento = fields.boolean('Director subrogado'),
        si_actual = fields.boolean('Oculta Actual'),
        si_nueva = fields.boolean('Oculta Propuesta'),
        crea_uid = fields.many2one('res.users','Creado por'),
        desc = fields.text('ANTECEDENTES'),
        desc1 = fields.text('EXPLICACION'),
        state = fields.selection([('Borrador','Borrador'),('Ejecutado','Ejecutado'),('Anulado','Anulado')],'Estado'),
        name = fields.char('Numero',size=15),
        date = fields.date('Feha'),
        contract_id = fields.many2one('hr.contract','Empleado',required=True,  domain=[('activo', '=', True)]),
        # nivel_contrato = fields.related('contract_id', 'nivel_contrato'),
        nivel_contrato = fields.function(get_nivel_contrato, method=True, string='Nivel', type='char'),
        # nivel_contrato = fields.function(get_nivel_contrato,type='many2one', relation='hr.contract.nivel',string='Nivel'),
        tipo = fields.selection([('Ingreso','Ingreso'),('Nombramiento','Nombramiento'),('Nombramiento Periodo Fijo','Nombramiento Periodo Fijo'),('Libre Nombramiento o Remocion','Libre Nombramiento o Remocion'),
                                 ('Nombramiento Provisional','Nombramiento Provisional'),('Ascenso','Ascenso'),('Actualizacion','Actualizacion',),
                                 ('Encargo','Encargo'),('Vacaciones','Vacaciones'),('Traslado','Traslado'),('Traspaso','Traspaso'),
                                 ('Cambio Administrativo','Cambio Administrativo'),('Remocion','Remocion'),('Comision Servicios','Comision Servicios'),
                                 ('Licencia','Licencia'),('Sancion Disciplinaria','Sancion Disciplinaria'),('Reclasificacion','Reclasificacion'),
                                 ('Ubicacion','Unicacion'),('Reintegro','Reintegro'),('Jubilacion','Jubilacion'),('Renuncia','Renuncia'),
                                 ('Subrogacion','Subrogacion'),('Otro','Otro')],'Tipo',),
        date_from = fields.date('Rige A partir de:'),
        direccion_id = fields.many2one('hr.department','Direccion'),
        department_id = fields.many2one('hr.department','Departamento'),
        cargo_id = fields.many2one('hr.job','Cargo'),
        nivel_id = fields.many2one('grupo.ocupacional','Grupo Ocupacional'),
        nivel_contrato_id = fields.many2one('hr.contract.nivel','Nivel'),
        lugar = fields.char('Lugar de trabajo',size=64),
        rmu = fields.float('Remuneracion Unificada'),
#        budget_id = fields.many2one('budget.item','Partida'),
        budget_id = fields.char('Partida',size=32),
        direccion_id2 = fields.many2one('hr.department','Direccion'),
        department_id2 = fields.many2one('hr.department','Departamento'),
        cargo_id2 = fields.many2one('hr.job','Cargo'),
        nivel_id2 = fields.many2one('grupo.ocupacional','Grupo Ocupacional'),
        nivel_contrato_id2 = fields.many2one('hr.contract.nivel','Nivel'),
        lugar2 = fields.char('Lugar de trabajo',size=64),
        rmu2 = fields.float('Remuneracion Unificada'),
#        budget_id2 = fields.many2one('budget.item','Partida'),
        budget_id2 = fields.char('Partida',size=32),
    )

    def onchange_contract_accionp(self, cr, uid, ids, contract_id):
        contract_obj = self.pool.get('hr.contract')
        result = {}
        if not contract_id:
            return {'value':result}
        contrato = contract_obj.browse(cr, uid, contract_id)
        result['nivel_contrato']=contrato.nivel_contrato.name
        result['department_id']=contrato.employee_id.department_id.id
        result['direccion_id']=contrato.employee_id.department_id.direccion_id.id
        result['cargo_id']=contrato.employee_id.job_id.id
        result['nivel_id']=contrato.ocupational_id.id
        result['rmu']=contrato.wage
        if contrato.budget_ind:
            result['budget_id']=contrato.budget_ind
        else:
            result['budget_id']=contrato.budget_id.code
        #nuevo
        result['department_id2']=contrato.employee_id.department_id.id
        result['direccion_id2']=contrato.employee_id.department_id.direccion_id.id
        result['cargo_id2']=contrato.employee_id.job_id.id
        result['nivel_id2']=contrato.ocupational_id.id
        result['rmu2']=contrato.wage
        if contrato.budget_ind:
            result['budget_id2']=contrato.budget_ind
        else:
            result['budget_id2']=contrato.budget_id.code
        return {'value':result}

    def accionPersonalAnular(self, cr, uid, ids, context):
        self.write(cr, uid, ids,{
            'state':'Anulado',
        })
        return True

    def accionPersonalEjecutar(self, cr, uid, ids, context):
        accion_obj = self.pool.get('hr.accion.personal')
        for this in self.browse(cr, uid, ids):
            obj_sequence = self.pool.get('ir.sequence')
            aux_name = obj_sequence.get(cr, uid, 'hr.accion.personal')
            accion_obj.write(cr, uid, this.id,{
                'state':'Ejecutado',
                'name':aux_name,
            })
        return True

    def _get_uid(self, cr, uid, ids, context=None):
        return uid

    _defaults = dict(
        state = 'Borrador',
        date = time.strftime('%Y-%m-%d'),
        crea_uid = _get_uid,
        
    )
hrAccionPersonal()

class hrLastJob(osv.Model):
    _name = 'hr.last.job'
    _columns = dict(
        name = fields.char('Nombre Cargo',size=32,required=True)
        )
hrLastJob()    

class hrLastWork(osv.Model):
    _name = 'hr.last.work'
    _columns = dict(
        name = fields.char('Empresa',size=32,required=True),
        cargo_id = fields.many2one('hr.last.job','Cargo Ocupado',required=True),
        date_start = fields.date('Fecha Ingreso'),
        date_end = fields.date('Fecha Salida'),
        partner_type = fields.selection([('Privada','Privada'),('Publica','Pública')],'Tipo Empresa',required=True),
        applicant_id = fields.many2one('hr.applicant','Candidato'),
        employee_id = fields.many2one('hr.employee','Empleado'),
        )

    defaults = dict(
        partner_type = 'Privada',
        )

hrLastWork()

class hr_novedad(osv.osv):
    _name = 'hr.novedad'
    
    _columns = {
                'name': fields.selection([('funcion_judicial','Funcion Judicial'),
                                          ('pension_alimentos','Pension de alimentos')],'Descripcion', required=True),
                'family_id': fields.many2one('hr.family.item', 'Familiar', required=True),
                #'type': fields.many2one('hr.salary.rule.category', 'Categoria salarial'),
                'value': fields.float('Valor', required=True),
                }
    
hr_novedad()

## #PROJECTION LINE

class hrAnualProjection(osv.osv):
    _name = 'hr.anual.projection'
    _description='Proyeccion Anual'

    def _compute_all(self, cr, uid, id, name, args, context):
        sum=0
        result={}
        for anual in self.browse(cr, uid, id):
            sum=0
            for line in anual.line_ids:
                sum+=line.value
            result[anual.id]=sum
        return result

    _columns = dict(
                    name = fields.char('Descripción',size=128),
                    fy_id = fields.many2one('hr.work.period','Año Laboral'),
                    total = fields.function(_compute_all, method=True, string='Total', type='float'),
                    line_ids = fields.one2many('hr.projection.line','pl_id','Lineas Proyección'),
                    employee_id = fields.many2one('hr.employee','Empleado'),
                    )

hrAnualProjection()

class hrContractProjection(osv.osv):

    _name = 'hr.contract.projection'
    _descripcion = "Proyecciones Imp. a la Renta"
    
    _columns = dict(
        code = fields.char('Código',size=8),
        name = fields.char('Nombre',  size=32),
        description = fields.text('Descripción'),
        )

hrContractProjection()

class hrProjectionLine(osv.osv):
    
    _name='hr.projection.line'
    _columns = dict(
        #name = fields.char('Desc.',size=8),
        projection_id = fields.many2one('hr.deduction','Deducción'),
        value = fields.float('Valor'),
        pl_id = fields.many2one('hr.anual.projection', 'Año'),
        )

hrProjectionLine()

class hrAnualRentTax(osv.osv):
    _name='hr.anual.rent.tax'

    _columns = dict(
        name = fields.char('Descripción',size=128),
        fy_id = fields.many2one('hr.work.period','Año Laboral'),
        #start_computed = fields.float('A pagar inicial anual'),
        #mensual = fields.float('Mensual Aprox.'),
        #end_computed = fields.float('Pagado anual real'),    
        line_ids = fields.one2many('hr.rent.tax','tl_id','Impuesto Renta'),
        employee_id = fields.many2one('hr.employee','Empleado'),
        )
    
hrAnualRentTax()

class hrRentTax(osv.osv):
    _name = 'hr.rent.tax'
    _columns = dict(
        #name = fields.char('Descripcion',size=32),
        period_id = fields.many2one('hr.work.period.line','Periodo'),
        apt_proy = fields.float('Aportables y proyectables'),
        apt_noproy = fields.float('Aportables no proyectables'),
        noapt_proy = fields.float('No aportable proyectable'),
        noapt_noproy = fields.float('No aportable no proyectable'),
        valor = fields.float('Valor retenido'),
        tl_id = fields.many2one('hr.anual.rent.tax','Año'),
        )
    
    _defaults = {
                 'apt_proy': 0,
                 'apt_noproy': 0,
                 'noapt_proy': 0,
                 'noapt_noproy': 0,
                 'valor': 0,
                 }
hrRentTax()

class hrFamilyItem(osv.osv):
    _name = 'hr.family.item'
    _description = 'Cargas/Miembros de la familia'
    _order = 'name desc'
    

    def onchange_birth(self, cr, uid, ids, birth):
        v={}
        result={}
        if birth:
            fecha_n = datetime.strptime(birth, "%Y-%m-%d")
            if fecha_n <= datetime.today():
                today = datetime.today().strftime("%Y-%m-%d")
                now = today.split('-')
                birth = birth.split('-')
                datenow = date( int(now[0]), int(now[1]), int(now[2]) )
                datebirth = date( int(birth[0]), int(birth[1]), int(birth[2]) )
                delta = datenow - datebirth
                age = delta.days/365
                v['age']=int(age)
                return {'value' : v}
            else:
                result['value']={'birth':""}
                result['warning']={'title' : 'Error de Usuario', 
                                   'message':'La fecha de nacimiento no puede ser mayor a la actual'}
        return result
    
    _RELATION = [('hb_wife','Esposo (a)'), ('son', 'Hijo (a)'),
                 ('padre','Padre'),('madre','Madre'),
                 ('tio','Tio'),('hermano','Hermano'),
                 ('sobrino','Sobrino'),('ulibre','Unión Libre'),
                 ('entenado','Otro')]
            
    _columns = dict(
        estudiante = fields.boolean('Estudiante??'),
        name = fields.char('Nombre Completo', size=50, required=True),
        sex = fields.selection([('h','Hombre'),('m','Mujer')],'Sexo'),
        #age = fields.integer('Edad'),
        carga_justificada = fields.boolean('Es una carga justificada?', help="Activar esta casilla si la carga familiar se encuentra justificada"),
        birth = fields.date('Fecha de Nacimiento'),
        relationship = fields.selection(_RELATION,'Parentezco'),
        disabled = fields.boolean('Discapacitado?', help="Marque este campo si la carga familiar es discapacitado"),
        employee_id =  fields.many2one('hr.employee', 'Empleado'),
        #novedad_ids = fields.one2many('hr.novedad', 'family_id', 'Rubros Fijos'),
        recibe_pension = fields.selection([('pension_alimentos','Pension de Alimentos'),('funcion_judicial','Funcion Judicial')],'Recibe pension?', help='Activar este campo en caso que esta carga familiar reciba una pension de alimentos, y elija el tipo de descuento'),
        valor_pension = fields.float('Valor',help='Valor a cobrar por la pension'),
        cuenta_pension = fields.many2one('res.partner.bank','Cuenta Bancaria', help='Cuenta bancaria en la cual se debe realizar el deposito por la pension')
        )
    
    _defaults = dict(
        #age = 0,
        )

    
hrFamilyItem()

class hrEmployeeCourse(osv.osv):
    _name = 'hr.employee.course'
    _description = 'Cursos Empleado'
    _MODALITY = [('v','Virtual'),('d','Distancia'),('p','Presencial'),
                 ('s','Semipresencial'),('o','Otros')]
    _columns = dict(
        name = fields.char('Tema',size=128,required=True),
        hours =  fields.integer('Numero de horas'),
        modality = fields.selection(_MODALITY,'Modalidad'),
        institute = fields.char('Institucion',size=32),
        employee_id = fields.many2one('hr.employee', 'Empleado'),
        tipo = fields.selection([('aprobacion','de aprobacion'),('asistencia','de asistencia')],'Tipo de Curso'),
        )
hrEmployeeCourse()

class title(osv.osv):
    _name = 'title'
    _description = 'Titulos Academicos'
    _order = 'name desc'
    _columns = dict(
        name = fields.char('Título', size=64),
        )
title()

class hrEmployeeTitle(osv.osv):   
    _name= 'hr.employee.title'
    _description = 'Titulos Empleado'
    _order = 'name desc,nivel desc'
    _LEVEL = [('art','Artesano'),('bas','Básica'),('bach','Bachillerato'),
              ('sup','Superior Técnico'),('egr','Egresado'),
              ('tercer','Tercer Nivel'),('cuarto','Cuarto Nivel')]
    _columns = dict(
        name = fields.many2one('title','Título',required="1"),
        institute = fields.char('Universidad', size=128),
        nivel = fields.selection(_LEVEL,'Nivel'),
        codigo = fields.char('Codigo SENESCYT', size=50),
        employee_id = fields.many2one('hr.employee', 'Empleado'),
        )
    
hrEmployeeTitle()

class hrEmployeeType(osv.osv):
    _name = 'employee.type'
    _columns = dict(
        name = fields.char('Tipo', size = 16)
        )
hrEmployeeType()

class hr_marital_status(osv.osv):
    _name = 'hr.marital.status'
    _columns = dict(
        name = fields.char('Estado Civil', size = 20)
        )
hr_marital_status()

class resource_resource_order(osv.osv):
    _inherit = 'resource.resource'
    _order = 'name asc'
    
    _defaults = {
                 'name': '0',
                 }
resource_resource_order()

class employeeJudicial(osv.Model):
    _name = 'employee.judicial'
    _columns = dict(
        is_supa = fields.boolean('Paga SUPA',help='Marque este campo si se paga por medio del sistema SUPA y no en cuenta individual'),
        emp_id = fields.many2one('hr.employee','Funcionario'),
        partner_id = fields.many2one('res.partner','Beneficiario',required=True),
        monto = fields.float('Monto',required=True),
        activo = fields.boolean('Descuento Activo'),
    )
    _defaults = dict(
        activo = True,
    )
employeeJudicial()

class employeeSancion(osv.Model):
    _name = 'employee.sancion'
    _columns = dict(
        employee_id = fields.many2one('hr.employee','Funcionario'),
        name = fields.many2one('hr.work.period','Periodo'),
        department_id = fields.many2one('hr.department','Departamento'),
        cargo_id = fields.many2one('hr.job','Cargo'),
        contract_id = fields.many2one('hr.contract','Contrato'),
        fecha_ingreso = fields.date('Fecha Ingreso'),
        verbal = fields.char('Verbal 1',size=256),
        verbal2 = fields.char('Verbal 2',size=256),
        escrita = fields.char('Escrita 1',size=256),
        escrita2 = fields.char('Escrita 2',size=256),
        pecuniaria = fields.char('Pecuniaria',size=256),
        visto_bueno = fields.char('Visto Bueno',size=256),
        destitucion = fields.char('Destitucion',size=256),
    )
employeeSancion()
class hrEmployee(osv.osv):
    _inherit = 'hr.employee'
    _order = 'complete_name asc'
    
    _TIPOID = [('c','Cedula'),('p','Pasaporte')]
    _BLOOD = [('on','O-'),('op','O+'),('an','A-'),('ap','A+'),
              ('bn','B-'),('bp','B+'),('abn','AB-'),('abp','AB+')]

    def write(self, cr, uid, ids, vals, context=None):
        partner_obj = self.pool.get('res.partner')
        user_obj = self.pool.get('res.users')
        identificadores = []
        for this in self.browse(cr, uid, ids):
            if vals.has_key('email'):
                aux_email = vals['email']
                aux_ced = this.name
                aux_ruc = this.name+'001'
                identificadores.append(aux_ced)
                identificadores.append(aux_ruc)
                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','in',identificadores)])
                if partner_ids:
                    for partner_id in partner_ids:
                        partner_obj.write(cr, uid, partner_id,{
                            'email':aux_email,
                        })
                    partner = partner_obj.browse(cr, uid, partner_id)
            if vals.has_key('department_id'):
                if this.user_id:
                    user_obj.write(cr, uid, this.user_id.id,{
                        'context_department_id':vals['department_id'],
                    })
            if vals.has_key('job_id'):
                if this.user_id:
                    user_obj.write(cr, uid, this.user_id.id,{
                        'job_id':vals['job_id'],
                    })
        return super(hrEmployee, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',vals['name'])])
        bank_obj = self.pool.get('res.partner.bank')
        b_obj = self.pool.get('res.bank')
        if len(partner_ids)>0:
            bank_ids = bank_obj.search(cr, uid, [('partner_id','=',partner_ids[0])])
            if len(bank_ids)>0:
                print "hay"
#               vals['bank_account_id']=bank_ids[0]
        else:
            banko_ids = b_obj.search(cr, uid, [])
            name_aux = vals['employee_first_lastname'] + ' ' + vals['employee_first_name']
            partner_id = partner_obj.create(cr, uid, {
                'ced_ruc':vals['name'],
                'type_ced_ruc':'cedula',
                'tipo_persona':'6',
                'name':name_aux,
                'direccion':vals['address'],
                'telefono':vals['house_phone'],
            })
#            bank_id = bank_obj.create(cr, uid, {
#                'partner_id':partner_id,
#                'type_cta':'aho',
#                'bank':banko_ids[0],
#                'acc_number':'0000000',
#            })
#x            vals['bank_account_id'] = bank_id
        return super(hrEmployee, self).create(cr, uid, vals, context=None) 
    
    def limpiar_puesto(self, cr, uid, ids, context={}):
        return {'value':{'job_id': False}}
    
    def _get_latest_contract(self, cr, uid, ids, field_name, args, context=None):
        #PROCESO REDEFINIDO DEL MODULO HR.CONTRACT
        res = {}
        obj_contract = self.pool.get('hr.contract')
        for emp in self.browse(cr, uid, ids, context=context):
            contract_ids = obj_contract.search(cr, uid, [('employee_id','=',emp.id),('active','=',True)], order='date_start', context=context)
            if contract_ids:
                res[emp.id] = contract_ids[-1:][0]
            else:
                res[emp.id] = False
        return res

    def _compute_age(self, cr, uid, ids, field_name, arg, context):
        v={}
        result = {}
        for this in self.browse(cr, uid, ids):
            result[this.id] = ""
            birth=this.birthday
            if birth:
                fecha_n = datetime.strptime(birth, "%Y-%m-%d")
                if fecha_n <= datetime.today():
                    today = datetime.today().strftime("%Y-%m-%d")
                    now = today.split('-')
                    birth = birth.split('-')
                    datenow = date( int(now[0]), int(now[1]), int(now[2]) )
                    datebirth = date( int(birth[0]), int(birth[1]), int(birth[2]) )
                    delta = datenow - datebirth
                    age = delta.days/365
                    result[this.id] = age
        return result

    def _compute_hijos18(self, cr, uid, ids, field_name, arg, context):
        for employee in self.browse(cr, uid, ids):
            aux = 0
            for family in employee.family_item_ids:
                if family.age<=18 or family.disabled:
                    aux += 1
        return {employee.id:aux}
    
    def onchange_provincia(self, cr, uid, ids, context={}):
        return {'value':{'canton_id':False,
                         'parish_id':False}}
        
    def onchange_canton(self, cr, uid, ids, context={}):
        return {'value':{'parish_id':False}}
    
    def _acc_anticipo(self, cr, uid, ids, field_name, arg, context):
        partner_obj = self.pool.get('res.partner')
        res = {}
        for employee in self.browse(cr, uid, ids):
            aux_acc = ""
            partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',employee.name)],limit=1)
            if partner_ids:
                partner = partner_obj.browse(cr, uid, partner_ids[0])
                if partner.anticipo_id:
                    partner = partner_obj.browse(cr, uid, partner_ids[0])
                    aux_acc = partner.anticipo_id.code + ' - ' + partner.anticipo_id.name
            else:
                aux_acc = "No Definido en proveedor"
            res[employee.id] = aux_acc
        return res

    def _complete_name(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for employee in self.browse(cr, uid, ids):
            name = ""
            if employee.employee_first_lastname:
                name = name + employee.employee_first_lastname
            if employee.employee_second_lastname:
                name = name + " " + employee.employee_second_lastname
            if employee.employee_first_name:
                name = name + " " + employee.employee_first_name
            if employee.employee_second_name:
                name = name + " " + employee.employee_second_name
            res[employee.id] = name
        return res
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = ""
            #if record.employee_first_lastname:
            #    name = name + record.employee_first_lastname
            #if record.employee_second_lastname:
            #    name = name + " " + record.employee_second_lastname
            #if record.employee_first_name:
            #    name = name + " " + record.employee_first_name
            #if record.employee_second_name:
            #    name = name + " " + record.employee_second_name
            if record.complete_name:
                name = record.name + " - " + record.complete_name
            res.append((record.id, name))
        return res
    
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        ids = []
        ids_cedula = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_cedula))
        if name:
            ids_name = self.search(cr, uid, [('complete_name', operator, name)] + args, limit=limit, context=context)
            ids = list(set(ids + ids_name))
        return self.name_get(cr, uid, ids, context=context)

    def _check_identificador(self, cr, uid, ids):
        for employee in self.browse(cr, uid, ids):
            if employee.id_type=='c':
                return tool._check_cedula(employee.name)
            else:
                return True

    def _check_identificador_unico(self, cr, uid, ids):
        employee_obj = self.pool.get('hr.employee')
        for employee in self.browse(cr, uid, ids):
            employee_ids = employee_obj.search(cr, uid, [('name','=',employee.name),('id','!=',employee.id)])
            if employee_ids:
                return False
        return True

    def _acc_bank(self, cr, uid, ids, field_name, arg, context):
        partner_obj = self.pool.get('res.partner')
        bank_obj = self.pool.get('res.partner.bank')
        res = {}
        for employee in self.browse(cr, uid, ids):
            partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',employee.name)],limit=1)
            if partner_ids:
                partner = partner_obj.browse(cr, uid, partner_ids[0])
                if partner.bank_ids:
                    banco_id = partner.bank_ids[0].id
                    res[employee.id] = banco_id
        return res

    _columns = dict(
        codigo_biometrico = fields.char('Codigo Reloj Biometrico',size=32),
        is_supa = fields.boolean('Paga SUPA',help='Marque este campo si se paga por medio del sistema SUPA y no en cuenta individual'),
        sancion_ids = fields.one2many('employee.sancion','employee_id','Sanciones'),
        judicial_ids = fields.one2many('employee.judicial','emp_id','Beneficiarios Judicial'),
        bank_account_id = fields.function(_acc_bank, method=True, string="Cuenta Anticipo", store=True, type="many2one", relation='res.partner.bank'), 
        anticipo_acc = fields.function(_acc_anticipo, method=True, string="Cuenta Anticipo", store=True, type="char", size=120), 
        complete_name = fields.function(_complete_name, method=True, string="Nombre Completo", store=True, type="char", size=120), 
        #employee_name = fields.char('Nombres', size=50, required=True),
        name = fields.char('Numero Cedula o Identificador', size=10, help="Es el numero de identificador, debe ser único", required=True),
        employee_first_name = fields.char('Nombres', size=128),
        employee_second_name = fields.char('Segundo Nombre', size=30),
        employee_first_lastname = fields.char('Apellidos', size=128),
        employee_second_lastname = fields.char('Segundo Apellido', size=30),
        #place_birth = fields.char('Lugar de nacimiento',size=32),
        personal_mail = fields.char('Mail Personal',size=32),
        #ci = fields.char('ID', size=10, help="Es el numero de identificador, debe ser único", required=True),
        id_type = fields.selection(_TIPOID, "Tipo ID",
                                     help="Es el tipo de identificador"),
        family_item_ids = fields.one2many('hr.family.item', 'employee_id', "Items Familia"),
        #children_18 =  fields.function(_compute_hijos18, method=True, string="Cargas Para Utilidad", 
        #                               store=True, type="integer"), 
        #type_id = fields.many2one('employee.type','Tipo',required=True),
        academic_ids = fields.one2many('hr.employee.title','employee_id','Datos Titulos'),
        course_ids  = fields.one2many('hr.employee.course','employee_id','Datos Cursos'),
        #experience_ids  = fields.one2many('hr.employee.course','employee_id','Datos Cursos'),
        #age = fields.function(_compute_age, method=True, string="Edad", store=True, type="integer"),
        country_id =  fields.many2one('res.country', 'Pais'),
        state_id = fields.many2one('res.country.state','Provincia'),
        canton_id = fields.many2one('res.country.state.canton','Canton'),
        parish_id = fields.many2one('res.country.state.parish','Parroquia'),
        #city = fields.many2one('res.country.state.city','Ciudad'),
        discapacitado = fields.boolean('Discapacitado',help="Marque este campo, si el empleado tiene alguna limitación para llevar a cabo ciertas actividades provocadas por una deficiencia física o mental"),
        tipo_discapacidad = fields.char('Tipo Discapacidad',size=64),
        porcentaje_discapacidad = fields.float('Porcentaje Discapacidad',size=64),
        id_conadis = fields.char('ID CONADIS',size=10,help="Codigo de identificación del CONADIS"),
        blood_type =  fields.selection(_BLOOD,'Tipo Sangre'),
        address = fields.char('Direccion',size=256),
        #house_number = fields.char('Num. de Casa', size=5),
        house_phone = fields.char('Telefono Convencional', size=15),
        marital_id = fields.many2one('hr.marital.status', 'Estado Civil'),
        email = fields.char('Email Personal', size=240),
        #ocupational_id = fields.many2one('grupo.ocupacional', 'Grupo Ocupacional'),
        contacto_emergencia = fields.char('En caso de emergencia llamar a', size=50),
        numero_emergencia = fields.char('Telefono del contacto', size=30),
        ppi = fields.integer('PPI'),
        receives_notifications = fields.boolean('Recibe notificaciones?', help="Activar el casillero si el empleado recibe notificaciones por correo electrónico"),
        #sup_id = fields.many2one('res.partner','Empresa Relacionada',required=True),
        #partner_id = fields.many2one('res.partner','Empresa Relacionada',required=True),
        state_system = fields.boolean('Presente'),
        projection_ids = fields.one2many('hr.anual.projection','employee_id','Proyecciones'),
        rent_tax_ids = fields.one2many('hr.anual.rent.tax','employee_id','Impuesto Renta'),
        last_work = fields.one2many('hr.last.work','employee_id','Experiencia Laboral'),
        )

    _constraints = [
        (_check_identificador,'El identificador es invalido, por favor verifique',['name']),
        (_check_identificador_unico,'El identificador es unico, por favor verifique',['name'])
        ]

    _sql_constraints = [
        ('unique_cedula_emp','unique(name)','Solo puede tener un mismo numero de identificador por empleado.')
        ]
    
    _defaults = dict(
        #children_18 = 0,
        id_type = 'c',
        name = '0',
        active = True,
        blood_type = 'op',
        state_system = False,
        )

hrEmployee()
