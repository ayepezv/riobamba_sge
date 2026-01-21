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
    
class hrSolicitudPersonalExp(osv.Model):
    _inherit = 'hr.sol.personal'

    def sol_in_progress(self, cr, uid, ids, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        emp_obj = self.pool.get('hr.employee')
        self.write(cr, uid, ids, {'state': 'solicitado',
                                  'name': obj_sequence.get(cr, uid, 'hr.vinculation')} ,context=context)
        vinc_obj = self.pool.get('hr.vinculation')
        for this in self.browse(cr, uid, ids):
            expedient_id = False;
            if not this.tramite_id:
                expedient_id= self.pool.get('doc_expedient.expedient').create(cr, uid,{'name': ustr('Proceso de contratación: ') + this.name,
                                                                                       'state': 'draft',
                                                                                       'ubication':'internal',
                                                                                       'user_id': this.solicitant_id.id,
                                                                                       'resumen': this.note}, context=context)
                task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                             'other_action' : ustr('Proceso de contratación: ') + this.name,
                                                                             'description': 'Solicitado por: ' + this.solicitant_id.name,
                                                                             'assigned_user_id': this.solicitant_id.id,
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
                                                                             'description': 'Solicitado por: ' + this.solicitant_id.name,
                                                                             'assigned_user_id': this.solicitant_id.id,
                                                                             'user_id': uid,
                                                                             'expedient_id': this.tramite_id.id,
                                                                             'state': 'done',
                                                                             }, context=context)
            vinc_obj.create(cr, uid, {'solicitud_id':this.id,
                                      'solicitant_id':this.solicitant_id.employee_id.id,
                                      'create_id':this.solicitant_id.id,
                                      'date_start':this.solicitant_id.id,
                                      'tramite_id':expedient_id,
                                      'name':this.name,
                                      'job_id':this.job_id.id,
                                      'department_id':this.department_id.id,
                                      'number':this.number,
                                      'has_sol':True,
                                      })
            
        return True
    

    _columns = dict(
        tramite_id = fields.many2one('doc_expedient.expedient','Trámite'),
        )

hrSolicitudPersonalExp()
