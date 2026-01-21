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
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

class hr_employee_exec(osv.Model):
    _name = "hr.employee.exec"
    _description="Listado de Empleados"
    
    def do_exec(self, cr, uid, ids, context=None):
        emp_pool = self.pool.get('hr.employee')
        agenda_obj = self.pool.get('agenda.agenda')  
        event_obj = self.pool.get('event.employee')       
        event_id = agenda_obj.browse(cr, uid, context['active_ids'][0])        
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]    
        for line in data['employee_idse']:
            event_obj.create(cr, uid, {'employee_id':line,
                                       'event_id': event_id.id,  
                                       'date_begin': event_id.date_begin,
                                       'date_end': event_id.date_end})
        return {'type': 'ir.actions.act_window_close'}
    
    
    _columns = dict(        
        employee_idse =fields.many2many('hr.employee', 'employee_event_relacion','event_id','emp_id','Asistentes',required=True),
        event_id = fields.many2one('agenda.agenda', 'Evento ID'),
        )

hr_employee_exec()    


    
