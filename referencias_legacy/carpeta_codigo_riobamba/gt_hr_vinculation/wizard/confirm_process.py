# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP SA (<http://openerp.com>).
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

import time
from osv import fields, osv

class confirmProcess(osv.TransientModel):

    _name = "confirm.process"

    _columns = dict(
        name = fields.many2one('hr.contract.type','Tipo de contrato',required=True),
        sub_id = fields.many2one('hr.contract.type.type','SubTipo',required=True),
        date = fields.date('Fecha Inicio Contrato',required=True),
        ocupational_id = fields.many2one('grupo.ocupacional','Grupo Ocupacional',required=True),
        wage = fields.float('Salario'),
        work_id = fields.many2one('resource.calendar','Horario Trabajo',required=True),
        )

    def confirm_process_contratation(self, cr, uid, ids, context=None):
        active_id = context['active_id']
        emp_obj = self.pool.get('hr.employee')
        last_obj = self.pool.get('hr.last.work')
        title_obj = self.pool.get('hr.employee.title')
        curse_obj = self.pool.get('hr.employee.course')
        contract_obj = self.pool.get('hr.contract')
        vinc_obj = self.pool.get('hr.vinculation')
        user_obj = self.pool.get('res.users')
        this = vinc_obj.browse(cr, uid, active_id)
        for this_ in self.browse(cr, uid, ids):
            if this.aprobado_prefecto:
                vinc_obj._create_task(cr, uid, this, this.tramite_id.id,'Contratado.. TR Finalizado')
                for employee_line in this.candidatos_ids:
                    if employee_line.select:
                        aplicante = employee_line.applicant_id
                        disc_detail = ""
                        if aplicante.discapacitado:
                            disc_detail = aplicante.tipo_discapacidad
                        str_login = aplicante.employee_first_name[0]+aplicante.employee_first_lastname
                        login = str_login.lower()
                        user_id = user_obj.create(cr, uid, {
                                'name':aplicante.complete_name,
                                'login':login,
                                'new_password':login,
                                'context_department_id':this.department_id.id,
                                })
                        emp_id = emp_obj.create(cr, uid, {
                                'user_id':user_id,
                                'employee_first_name':aplicante.employee_first_name,
                                'employee_second_name':aplicante.employee_second_name,
                                'employee_first_lastname':aplicante.employee_first_lastname,
                                'employee_second_lastname':aplicante.employee_second_lastname,
                                'name':aplicante.id_number,
                                'id_type':aplicante.id_type,
                                'department_id':this.department_id.id,
                                'gender':aplicante.gender,
                                'marital_id':aplicante.marital_id.id,
                                'blood_type':aplicante.blood_type,
                                'gender':aplicante.gender,
                                'discapacitado':aplicante.discapacitado,
                                'country_id':aplicante.country_id.id,
                                'state_id':aplicante.state_id.id,
                                'canton_id':aplicante.canton_id.id,
                                'city':aplicante.city.id,
                                'job_id':employee_line.job_id.id,
                                'address':aplicante.address,
                                'house_phone':aplicante.partner_phone,
                                'tipo_discapacidad':disc_detail,
                                'ocupational_id':this_.ocupational_id.id,
                                })
                        contract_id = contract_obj.create(cr, uid,{
                                'employee_id':emp_id,
                                'date_start':this_.date,
                                'job_id':employee_line.job_id.id,
                                'type_id':this_.name.id,
                                'subtype_id':this_.sub_id.id,
                                'wage':this_.wage, 
                                'department_id':this.department_id.id,
                                'ocupational_id':this_.ocupational_id.id,
                                'work_id':calendar_ids[0],
                                'active':True,
                                })
                        vals = {}
                        if aplicante.last_work:
                            for l in aplicante.last_work:
#                                vals = last_obj.copy_data(cr, uid, l.id)
#                                vals['applicant_id'] = 0
#                                vals['employee_id'] = emp_id
                                last_obj.write(cr, uid, l.id, {'employee_id':emp_id,})
                        if aplicante.academic_ids:
                            for l in aplicante.academic_ids:
#                                vals = title_obj.copy_data(cr, uid, l.id)
#                                vals['applicant_id'] = 0
 #                               vals['employee_id'] = emp_id
                                title_obj.write(cr, uid, l.id, {'employee_id':emp_id,})
                        if aplicante.course_ids:
                            for l in aplicante.course_ids:
#                                vals = curse_obj.copy_data(cr, uid, l.id)
#                                vals['applicant_id'] = 0
#                                vals['employee_id'] = emp_id
                                curse_obj.write(cr, uid, l.id, {'employee_id':emp_id,})
                vinc_obj.write(cr, uid, this.id, {'state':'aprobado',
                                                  'contract_id':contract_id,
                                                  'date':time.strftime('%Y-%m-%d')})
            else:
                raise osv.except_osv(('Error de usuario'), ('El proceso debe ser aprobado por el prefecto'))
        return {'type': 'ir.actions.act_window_close'}

confirmProcess()
