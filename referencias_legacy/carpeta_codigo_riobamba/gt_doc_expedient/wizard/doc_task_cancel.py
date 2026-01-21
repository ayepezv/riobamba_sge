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

from lxml import etree
from osv import fields, osv
from tools.translate import _
import netsvc
import pdb

class doc_task_cancel(osv.osv_memory):
    _name = 'doc_task.cancel'
    
    def get_task(self, cr, uid, context=None):
        return context.get('active_id',False)
    
    def cancel_task(self, cr, uid, ids, context=None):
        obj_doc_task = self.pool.get('doc_expedient.task')
        task_id = context.get('active_id', False)
        task = self.pool.get('doc_expedient.task').browse(cr, uid, task_id)
        for wizard in self.browse(cr, uid, ids, context=None):
            if not (wizard.notes):
                raise osv.except_osv('Mensaje de Advertencia !', 'Por favor ingrese una justificación...')
            if (task.assigned_user_id.id != uid) and (task.user_id.id != uid):
                raise osv.except_osv('Mensaje de Advertencia !', 'El usuario no puede anular la Tarea...')
            if (task.user_id.id == uid and task.assigned_user_id.id != uid and task.included == True):
                raise osv.except_osv('Mensaje de Advertencia !', 'No puede realizar esta accion, La tarea esta siendo ejecutada')
            obj_doc_task.write(cr, uid, task_id, {'justification':wizard.notes})
            obj_doc_task.task_done_cancelled(cr, uid, [task_id], context)
        return {'type':'ir.actions.act_window_close'}
        
    _columns = dict(
        notes = fields.text('Justificación'),
        tarea = fields.many2one('doc_expedient.task'),
    )
    _defaults = {'tarea':get_task}
                     
doc_task_cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
