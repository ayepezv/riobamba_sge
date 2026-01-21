# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-now Gnuthink Software Labs Co. Ltd. (<http://www.gnuthink.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools import ustr
from gt_tool import tool
from datetime import date, datetime, timedelta
import time

class personalRef(osv.Model):
    _name = 'personal.ref'
    _columns = dict(
        name = fields.char('Nombre',size=256,required=True),
        lugar_trabajo = fields.char('Lugar de trabajo',size=64,required=True),
        telf1 = fields.char('Telf. Conv',size=10,required=True),
        telf2 = fields.char('Telf. Cel',size=10,required=True),
        app_id = fields.many2one('hr.applicant','Candidato',required=True),
        )

personalRef()

class employeeApplicant(osv.osv):
    _inherit = 'hr.employee'
    _columns = dict(
        applicant_id = fields.many2one('hr.applicant','Prospecto'),
        )
employeeApplicant()

class contractApplicant(osv.osv):
    _inherit = 'hr.contract'
    _columns = dict(
        applicant_id = fields.many2one('hr.applicant','Prospecto'),
        )
contractApplicant()

class aplicantVinculation(osv.Model):
    _name = 'applicant.vinculation'
    _columns = dict(
        applicant_id = fields.many2one('hr.applicant','Candidato',required=True),
        value = fields.float('Calificación Global',required=True),
        job_id = fields.many2one('hr.job','Puesto Trabajo'),
        select = fields.boolean('Seleccionado'),
        vinculation_id = fields.many2one('hr.vinculation','Contratación'),
        )

aplicantVinculation

class hrVinculation(osv.osv):
    _name='hr.vinculation'
    _order = 'name desc'
    
    _STATE = [('start','Iniciado'),('verificado','Verificado'),('autorizado','Autorizado'),
              ('seleccionado','Seleccionado'),('autorizadoc','Autorizado/Contratar'),
              ('contratado','Contratado'),('anulado','Anulado')]

    _columns = dict(
        has_sol = fields.boolean('Tiene sol'),
        solicitant_id = fields.many2one('hr.employee','Persona que solicita',required=True),
        create_id = fields.many2one('res.users','Creado por',required=True),
        name = fields.char('Referencia',size=32,readonly=True),
        state = fields.selection(_STATE,'Estado',readonly=True),
        date_create = fields.datetime('Fecha hora creación'),
        date = fields.datetime('Fecha Vinculacion',help="Fecha en la que se aprobó el proceso y se vincula al empleado"),
        job_id = fields.many2one('hr.job','Puesto de trabajo',required=True),
        number = fields.integer('Cantidad'),
        wage = fields.float('Sueldo Sugerido'),
        type_id = fields.many2one('hr.contract.type','Tipo de relación laboral'),
        subtype_id = fields.many2one('hr.contract.type.type','Tipo de contrato'),
        work_id = fields.many2one('resource.calendar','Horario de trabajo'),
        department_id = fields.many2one('hr.department','Unidad Requirente',required=True),
        candidatos_ids = fields.one2many('applicant.vinculation','vinculation_id','Candidatos'),
        name_doc_solicitud = fields.char('Nombre doc. Solicitud', size=50),
        name_doc_verificacion = fields.char('Nombre doc. Verificación', size=50),
        name_doc_aut_seleccion = fields.char('Nombre doc. Autorización Selección', size=50),
        name_doc_seleccion = fields.char('Nombre doc. selección', size=50),
        name_doc_contratacion = fields.char('Nombre doc. Autorización Contratación', size=50),
        name_doc_contrato = fields.char('Nombre doc. Contrato', size=50),
        doc_solicitud = fields.binary('Doc. Solicitud'),
        doc_verificacion = fields.binary('Doc. Verificación'),
        doc_aut_seleccion = fields.binary('Doc. Autorización Selección'),
        doc_seleccion = fields.binary('Doc. Selección'),
        doc_contratacion = fields.binary('Doc. Autorización Contratación'),
        doc_contrato = fields.binary('Doc. Contrato'),
	)
    
    
    def vinc_verificar(self, cr, uid, ids, context=None):
        vinc_obj = self.pool.get('hr.vinculation')
        for this in self.browse(cr, uid, ids):
            if not this.doc_verificacion or not this.name_doc_verificacion:
                raise osv.except_osv('Error en el proceso','Debe agregar el documento de verificación para iniciar el proceso')
            vinc_obj.write(cr, uid, this.id,{'state':'verificado'})
        return True
    
    def vinc_autorizar(self, cr, uid, ids, context=None):
        vinc_obj = self.pool.get('hr.vinculation')
        solicitud_obj = self.pool.get('hr.sol.personal')
        for this in self.browse(cr, uid, ids):
            if not this.doc_aut_seleccion or not this.name_doc_aut_seleccion:
                raise osv.except_osv('Error en el proceso','Debe agregar el documento de autorización para iniciar el proceso')
            vinc_obj.write(cr, uid, this.id,{'state':'autorizado'})
        return True

    def vinc_seleccionar(self, cr, uid, ids, context=None):
        vinc_obj = self.pool.get('hr.vinculation')
        for this in self.browse(cr, uid, ids):
            aux = 0
            if not this.doc_seleccion or not this.name_doc_seleccion:
                raise osv.except_osv('Error en el proceso','Debe agregar el documento del proceso de selección de personal')
            for line in this.candidatos_ids:
                if line.select:
                    aux += 1
            if aux <= 0:
                raise osv.except_osv(('Error'),('Debe seleccionar por lo menos un candidato'))
            vinc_obj.write(cr, uid, this.id,{'state':'seleccionado',})
        return True

    def vinc_autorizar_contratar(self, cr, uid, ids, context=None):
        vinc_obj = self.pool.get('hr.vinculation')
        for this in self.browse(cr, uid, ids):
            if not this.doc_contratacion or not this.name_doc_contratacion:
                raise osv.except_osv('Error en el proceso','Debe agregar el documento de autorización de contratación de personal')
            vinc_obj.write(cr, uid, this.id,{'state':'autorizadoc',})
        return True

    def vinc_contratar(self, cr, uid, ids, context=None):
        vinc_obj = self.pool.get('hr.vinculation')
        emp_obj = self.pool.get('hr.employee')
        last_obj = self.pool.get('hr.last.work')
        title_obj = self.pool.get('hr.employee.title')
        curse_obj = self.pool.get('hr.employee.course')
        contract_obj = self.pool.get('hr.contract')
        vinc_obj = self.pool.get('hr.vinculation')
        user_obj = self.pool.get('res.users')
        job_obj = self.pool.get('hr.job')
        for this in self.browse(cr, uid, ids):
            if not this.doc_contrato or not this.name_doc_contrato:
                raise osv.except_osv('Error en el proceso','Debe agregar el documento del contrato')
            if not this.type_id or not this.subtype_id or not this.work_id:
                raise osv.except_osv('Error en el proceso','Debe agregar el tipo de relación laboral, contrato, y horario para generar la información relacionada al servidor')
            for employee_line in this.candidatos_ids:
                    if employee_line.select:
                        job_obj.write(cr, uid, employee_line.job_id.id,{
                                'autorizado':False,
                                })
                        aplicante = employee_line.applicant_id
                        disc_detail = ""
                        if aplicante.discapacitado:
                            disc_detail = aplicante.tipo_discapacidad
                        emp_id = emp_obj.create(cr, uid, {
                                'employee_first_name':aplicante.employee_first_name,
                                'employee_second_name':aplicante.employee_second_name,
                                'employee_first_lastname':aplicante.employee_first_lastname,
                                'employee_second_lastname':aplicante.employee_second_lastname,
                                'birthday':aplicante.fec_nac,
                                'name':aplicante.id_number,
                                'id_type':aplicante.id_type,
                                'department_id':this.department_id.id,
                                'gender':aplicante.gender,
                                'marital_id':aplicante.marital_id.id,
                                'blood_type':aplicante.blood_type,
                                'discapacitado':aplicante.discapacitado,
                                'country_id':aplicante.country_id.id,
                                'state_id':aplicante.state_id.id,
                                'canton_id':aplicante.canton_id.id,
                                'city':aplicante.city.id,
                                'job_id':this.job_id.id,
                                'address':aplicante.address,
                                'house_phone':aplicante.partner_phone,
                                'tipo_discapacidad':disc_detail,
                                })
                        grupo_id = False
                        if this.job_id.grupo_id:
                            grupo_id = this.job_id.grupo_id.id
                        contract_id = contract_obj.create(cr, uid,{
                                'name':aplicante.id_number,
                                'employee_id':emp_id,
                                'date_start':time.strftime('%Y-%m-%d'),
                                'job_id':this.job_id.id,
                                'type_id':this.type_id.id,
                                'subtype_id':this.subtype_id.id,
                                'wage':this.wage,
                                'work_id': this.work_id.id,
                                'department_id':this.department_id.id,
                                'ocupational_id':grupo_id,
                                'active':True,
                                })
                        if aplicante.last_work:
                            for l in aplicante.last_work:
                                last_obj.write(cr, uid, l.id, {'employee_id':emp_id,})
                        if aplicante.academic_ids:
                            for l in aplicante.academic_ids:
                                title_obj.write(cr, uid, l.id, {'employee_id':emp_id,})
                        if aplicante.course_ids:
                            for l in aplicante.course_ids:
                                curse_obj.write(cr, uid, l.id, {'employee_id':emp_id,})
#            if this.solicitud_id:
#                self.pool.get('hr.sol.personal').write(cr, uid, this.solicitud_id.id,{'state':'en_proceso'})
            vinc_obj.write(cr, uid, this.id,{'state':'contratado',})
        return True


    def vinc_anular(self, cr, uid, ids, context=None):
        vinc_obj = self.pool.get('hr.vinculation')
        for this in self.browse(cr, uid, ids):
            vinc_obj.write(cr, uid, this.id, {'state':'anulado'})
            self.pool.get('hr.sol.personal').write(cr, uid, this.solicitud_id.id,{'state':'anulado'})
        return True

    def _get_uid(self, cr, uid, ids, context=None):
        return uid

    def _get_employee(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        emp_ids = user.employee_id.id
        if emp_ids:
            return emp_ids
        else:
            raise osv.except_osv(('Error de usuario!'),('No existe empleado definido para el usuario responsable del proceso'))
            return False

    def _check_lines(self, cr, uid, ids):
        result = True
        for obj in self.browse(cr, uid, ids):
            if not obj.candidatos_ids:
                raise osv.except_osv(('Error de usuario!'),('Debe por lo menos registrar un candidato al cargo solicitado'))
                result = False
        return result

    _defaults = dict(
        date_create = time.strftime('%Y-%m-%d'),
        state = 'start',
        create_id = _get_uid,
#        solicitant_id = _get_employee,
        )
    
hrVinculation()


class empTitle(osv.osv):
    _inherit = 'hr.employee.title'
    _columns = dict(
        applicant_id = fields.many2one('hr.applicant','Candidato'),
        )
empTitle()

class empCourse(osv.osv):
    _inherit = 'hr.employee.course'
    _columns = dict(
        applicant_id = fields.many2one('hr.applicant','Candidato'),
        )
empTitle()

class hrApplicant(osv.osv):
    _inherit = 'hr.applicant'

    _TIPOID = [('c','Cedula'),('p','Pasaporte')]

    def case_close(self, cr, uid, ids, *args):
        res = super(hrApplicant, self).case_close(cr, uid, ids, *args)
        for (id, name) in self.name_get(cr, uid, ids):
            message = ("El aspirante '%s' fue vinculado satisfactoriamante. Verifique el formulario del empleado, asi como tambien el contrato generado") % name
            self.log(cr, uid, id, ustr(message))
        return res

    def vinculate_employee(self, cr, uid, ids, objeto,*args):
        hr_employee = self.pool.get('hr.employee')
        hr_contract = self.pool.get('hr.contract')
        model_data = self.pool.get('ir.model.data')
        vinculation_obj = self.pool.get('hr.vinculation')
        act_window = self.pool.get('ir.actions.act_window')
        emp_id = False
        for applicant in self.browse(cr, uid, ids):
            address_id = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
            if applicant.job_id:
                applicant.job_id.write({'no_of_recruitment': applicant.job_id.no_of_recruitment - 1})
                emp_id = hr_employee.create(cr,uid,{
                        'employee_first_name':applicant.employee_first_name,
                        'employee_second_name':applicant.employee_second_name,
                        'employee_first_lastname':applicant.employee_first_lastname,
                        'employee_second_lastname':applicant.employee_second_lastname,
                        'name' : applicant.id_number,
                        'id_type' : applicant.id_type,
                        'job_id': applicant.job_id.id,
                        'department_id': applicant.department_id.id,
                        'applicant_id' : applicant.id,
                        })
                if emp_id:
                    date_start = objeto.date_start
                    contract_id = hr_contract.create(cr,uid,{
                            #'name': hr_contract.pool.get('ir.sequence').get(cr, uid, 'hr.contract'),
                            'name': 'REGISTRO DE CONTRATO',
                            'active': True,
                            'employee_id': emp_id,
                            'job_id': applicant.job_id.id,
                            'wage': objeto.wage,
                            'type_id': objeto.type_id.id,
                            'date_start': date_start,
                            'trial_date_start': date_start,
                            'applicant_id' : applicant.id,
                            #'state' : 'prueba',
                            'trial_date_end':(datetime.strptime(date_start,'%Y-%m-%d')+timedelta(days=89)).strftime('%Y-%m-%d'),
                            })
                    vinculation_id = vinculation_obj.create(cr, uid, {
                            'name':'Vinc. '+ applicant.complete_name,
                            'contract_id' : contract_id,
                            'employee_id' : emp_id,
                            'date' : strftime('%Y-%m-%d'),
                            'job_id': applicant.job_id.id,
                            'wage_sugested' : applicant.salary_expected,
                            'wage' : objeto.wage,
                            'applicant_id' : applicant.id,
                            })
                self.case_close(cr, uid, [applicant.id], *args)
            else:
                raise osv.except_osv(('Advertencia!'),('Debe definir un puesto de trabajo para el aspirante.'))

        action_model, action_id = model_data.get_object_reference(cr, uid, 'hr', 'open_view_employee_list')
        dict_act_window = act_window.read(cr, uid, action_id, [])
        if emp_id:
            dict_act_window['res_id'] = emp_id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window

    def _check_identificador(self, cr, uid, ids):
        for employee in self.browse(cr, uid, ids):
            if employee.id_type=='c':
                return tool._check_cedula(employee.id_number)
            else:
                return True

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
                name = record.complete_name
            res.append((record.id, name))
        return res
    
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        ids = []
        ids_cedula = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_cedula))
        if name:
            #ids_first_lastname = self.search(cr, uid, [('employee_first_lastname', operator, name)] + args, limit=limit, context=context)
            #ids_second_lastname = self.search(cr, uid, [('employee_second_lastname', operator, name)] + args, limit=limit, context=context)
            #ids_first_name = self.search(cr, uid, [('employee_first_name', operator, name)] + args, limit=limit, context=context)
            #ids_second_name = self.search(cr, uid, [('employee_second_name', operator, name)] + args, limit=limit, context=context)
            #ids = list(set(ids + ids_first_lastname))
            #ids = list(set(ids + ids_second_lastname))
            #ids = list(set(ids + ids_first_name))
            #ids = list(set(ids + ids_second_name))
            ids_name = self.search(cr, uid, [('complete_name', operator, name)] + args, limit=limit, context=context)
            ids = list(set(ids + ids_name))
        return self.name_get(cr, uid, ids, context=context)

    _BLOOD = [('on','O-'),('op','O+'),('an','A-'),('ap','A+'),
              ('bn','B-'),('bp','B+'),('abn','AB-'),('abp','AB+')]

    _columns = dict(
        fec_nac = fields.date('Fec. Nacimiento'),
        complete_name = fields.function(_complete_name, method=True, string="Nombre Completo", store=True, type="char", size=120),
        name = fields.function(_complete_name, method=True, string="Nombre Completo", store=True, type="char", size=120), 
        employee_first_name = fields.char('Primer Nombre', size=30,required=True),
        employee_second_name = fields.char('Segundo Nombre', size=30,required=True),
        employee_first_lastname = fields.char('Primer Apellido', size=30,required=True),
        employee_second_lastname = fields.char('Segundo Apellido', size=30,required=True),
        ref_ids = fields.one2many('personal.ref','app_id','Referencias Personales'),
        aplication_date = fields.date('Fecha de aplicación',required=True),
        gender = fields.selection([('male', 'Hombre'),('female', 'Mujer')], 'Sexo'),
        marital_id = fields.many2one('hr.marital.status', 'Estado Civil'),
        country_id =  fields.many2one('res.country', 'Pais'),
        blood_type =  fields.selection(_BLOOD,'Tipo Sangre'),
        state_id = fields.many2one('res.country.state','Provincia'),
        canton_id = fields.many2one('res.country.state.canton','Canton'),
        city = fields.many2one('res.country.state.city','Ciudad'),
        discapacitado = fields.boolean('Discapacitado',help="Marque este campo, si el empleado tiene alguna limitación para llevar a cabo ciertas actividades provocadas por una deficiencia física o mental"),
        tipo_discapacidad = fields.char('Tipo Discapacidad',size=64),
        address = fields.char('Direccion',size=256),
        academic_ids = fields.one2many('hr.employee.title','applicant_id','Datos Titulos'),
        course_ids  = fields.one2many('hr.employee.course','applicant_id','Datos Cursos'),
        #idioma_ids  = fields.one2many('hr.employee.idioma','employee_id','Datos Cursos'),
        salud_state = fields.selection([('Bueno','Bueno'),('Regular','Regular'),('Malo','Malo')],'Estado de salud',
                                       help="Como considera su estado de salud"),
        cronic = fields.boolean('Enfermedad Crónica',help="Si padece alguna enfermedad crónica"),
        state = fields.selection([('new','Nuevo'),('contratado','Contratado')],'Estado',readonly=True),
#        last_name = fields.char('Apellidos',size=128,required=True),
#        partner_name = fields.char('Nombres',size=128,required=True),
        id_number = fields.char('ID', size=10, help="Es el numero de identificador, debe ser único", required=True),
        id_type = fields.selection(_TIPOID, "Tipo ID",
                                   help="Es el tipo de identificador"),
        last_work = fields.one2many('hr.last.work','applicant_id','Experiecia Laboral'),
	)

    _constraints = [
        (_check_identificador,'El identificador es invalido, por favor verifique',['id_number']),
        ]

    _sql_constraints = [
        ('unique_cedula_emp','unique(id_number,id_type)','Solo puede tener un mismo número de identificador por empleado.')
        ]

    _defaults = dict(
        id_type = 'p',
        state = 'new',
        aplication_date = time.strftime("%Y-%m-%d"),
        blood_type = 'op',
        )
	
hrApplicant()

