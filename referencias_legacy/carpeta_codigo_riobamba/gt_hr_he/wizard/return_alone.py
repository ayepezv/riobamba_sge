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

class returnAlone(osv.TransientModel):

    _name = "return.alone"

    _columns = dict(
        name = fields.char('Observaciones', size=256,required=True),
        )

    def alone_return(self, cr, uid, ids, context=None):
        active_id = context['active_id']
        alone_obj = self.pool.get('hr.he.register.alone')
        alone = alone_obj.browse(cr, uid, active_id)
        this = self.browse(cr, uid, ids[0])
        obs = this.name
        alone_obj.write(cr, uid, alone.id,{'observation':obs,
                                           'revert':True,
                                           'state':'draft'})
        alone_obj._generate_log(cr, uid, active_id,'<-- Borrador')
#        task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
#                                                                     'other_action' : str_2 ,
#                                                                     'description': 'Servidor: ' + req.solicitant_id.name + ' ' + str(req.solicitant_id.employee_lastname),
#                                                                     'department': req.department_id.id,
#                                                                     'employee_id' : req.solicitant_id.id,
#                                                                     'job_id': req.solicitant_id.job_id.id,
#                                                                     'user_id': uid,
#                                                                     'expedient_id':req.sgd_id.id,
#                                                                     'state': 'done',
#                                                                     }, context=context)
        return {'type': 'ir.actions.act_window_close'}

returnAlone()
