# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv

class res_employee(osv.Model):
    _name = 'event.employee'
    _order='date_begin asc'
        
    _columns = dict(
        employee_id = fields.many2one('hr.employee','Empleado',required=True),
        event_id = fields.many2one('agenda.agenda','Evento',required=True),
        date_begin = fields.datetime('Fecha Incio', required=True),
        date_end = fields.datetime('Fecha Fin', required=True),
        state=fields.related('event_id', 'state',  type='selection', selection=[
            ('draft', 'Creado'),
            ('confirm', 'Confirmado')], 
            string='Estado', 
            readonly=True ,store=False),        
        type=fields.related('event_id', 'type',  type='many2one', relation='agenda.type',  
            string='Tipo', 
            readonly=True ,store=False),        
        user_id=fields.related('event_id', 'user_id',  type='many2one', relation='res.users',  
            string='Creado por', 
            readonly=True ,store=False),
        descripcion=fields.related('event_id', 'note',  type='text',   
            string='Descripción', 
            readonly=True ,store=False),   
        email=fields.related('employee_id', 'email',  type='char',   
            string='Email Personal', 
            readonly=True ,store=False),       
        work_email=fields.related('employee_id', 'work_email',  type='char',   
            string='Email Trabajo', 
            readonly=True ,store=False),
        department_id=fields.related('employee_id', 'department_id',  type='many2one', relation='hr.department',  
            string='Departamento', 
            readonly=True ,store=False),
        job_id=fields.related('employee_id', 'job_id',  type='many2one', relation='hr.job',  
            string='Cargo', 
            readonly=True ,store=False),
        email_personal=fields.boolean('Enviar Email Personal'),                 
        )
    
    _sql_constraints = [
      ('name', 'UNIQUE (event_id,employee_id)', 'Empleado(s) repetido(s) para el evento')
   ]
        
res_employee()

class res_partner(osv.osv):
    _inherit = 'hr.employee'
    _columns = {        
        'event_ids_agenda': fields.one2many('event.employee','employee_id', readonly=True),  
        'email_personal':fields.boolean('Email Personal'),  
            
    }

res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
