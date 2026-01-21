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
class hrVinculationExp(osv.osv):
    _inherit='hr.vinculation'

    _columns = dict(
        tramite_id = fields.many2one('doc_expedient.expedient','Trámite'),
 	)
      
    def vinc_verificar(self, cr, uid, ids, context=None):
        vinc_obj = self.pool.get('hr.vinculation')
        for this in self.browse(cr, uid, ids):
            if not this.doc_verificacion or not this.name_doc_verificacion:
                raise osv.except_osv('Error en el proceso','Debe agregar el documento de verificación para iniciar el proceso')
            if not this.tramite_id:
                expedient_id= self.pool.get('doc_expedient.expedient').create(cr, uid,{'name': ustr('Proceso de contratación: ') + this.name,
                                                                                       'state': 'draft',
                                                                                       'ubication':'internal',
                                                                                       'user_id': this.create_id.id,
                                                                                       'resumen': this.note}, context=context)
                task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : ustr('Proceso de contratación: ') + this.name,
                                                                             'description': 'Verificado la disponibilidad de cargo.',
                                                                             'assigned_user_id': this.create_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id': expedient_id,
                                                                             'state': 'done',
                                                                             }, context=context)
                self.pool.get('doc_expedient.expedient').action_draft_created(cr, uid, [expedient_id], context=context)
                self.write(cr, uid, this.id, {'tramite_id':expedient_id}, context=context)
            else:
                expedient_id = this.tramite_id.id
                task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : ustr('Proceso de contratación: ') + this.name,
                                                                             'description': 'Verificado la disponibilidad de cargo.',
                                                                             'assigned_user_id': this.create_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id': this.tramite_id.id,
                                                                             'state': 'done',
                                                                             }, context=context)
            vinc_obj.write(cr, uid, this.id,{'state':'verificado'})
        return True
    
    def vinc_autorizar(self, cr, uid, ids, context=None):
        vinc_obj = self.pool.get('hr.vinculation')
        solicitud_obj = self.pool.get('hr.sol.personal')
        for this in self.browse(cr, uid, ids):
            if not this.doc_aut_seleccion or not this.name_doc_aut_seleccion:
                raise osv.except_osv('Error en el proceso','Debe agregar el documento de autorización para iniciar el proceso')
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : ustr('Proceso de contratación: ') + this.name,
                                                                             'description': 'Autorizado el proceso de selección y contratación.',
                                                                             'assigned_user_id': this.create_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id': this.tramite_id.id,
                                                                             'state': 'done',
                                                                             }, context=context)
            solicitud_obj.write(cr, uid, this.solicitud_id.id,{'state':'en_proceso'})
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
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : ustr('Proceso de contratación: ') + this.name,
                                                                             'description': 'Proceso de selección y contratación finalizado.',
                                                                             'assigned_user_id': this.create_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id': this.tramite_id.id,
                                                                             'state': 'done',
                                                                             }, context=context)
            vinc_obj.write(cr, uid, this.id,{'state':'seleccionado',})
        return True

    def vinc_autorizar_contratar(self, cr, uid, ids, context=None):
        vinc_obj = self.pool.get('hr.vinculation')
        for this in self.browse(cr, uid, ids):
            if not this.doc_contratacion or not this.name_doc_contratacion:
                raise osv.except_osv('Error en el proceso','Debe agregar el documento de autorización de contratación de personal')
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : ustr('Proceso de contratación: ') + this.name,
                                                                             'description': 'Autorizada la contratación.',
                                                                             'assigned_user_id': this.create_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id': this.tramite_id.id,
                                                                             'state': 'done',
                                                                             }, context=context)
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
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : ustr('Proceso de contratación: ') + this.name,
                                                                             'description': 'Se procede a la contratación.',
                                                                             'assigned_user_id': this.create_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id': this.tramite_id.id,
                                                                             'state': 'done',
                                                                             }, context=context)
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
            self.pool.get('hr.sol.personal').write(cr, uid, this.solicitud_id.id,{'state':'en_proceso'})
            vinc_obj.write(cr, uid, this.id,{'state':'contratado',})
        return True


    def vinc_anular(self, cr, uid, ids, context=None):
        vinc_obj = self.pool.get('hr.vinculation')
        for this in self.browse(cr, uid, ids):
            vinc_obj.write(cr, uid, this.id, {'state':'anulado'})
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : ustr('Proceso de contratación: ') + this.name,
                                                                             'description': 'ANULADO.',
                                                                             'assigned_user_id': this.create_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id': this.tramite_id.id,
                                                                             'state': 'done',
                                                                             }, context=context)
            self.pool.get('hr.sol.personal').write(cr, uid, this.solicitud_id.id,{'state':'anulado'})
        return True

hrVinculationExp()

