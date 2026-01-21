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

class doc_expedient_draft(osv.osv_memory):
    _name = 'doc_expedient.draft'
    
    def get_expedient(self, cr, uid, context=None):
        return context.get('active_id',False)
    
    def draft_expedient(self, cr, uid, ids, context=None):
        obj_doc_expedient = self.pool.get('doc_expedient.expedient')
        exp_id = context.get('active_id', False)
        expediente = obj_doc_expedient.browse(cr, uid, exp_id)
        for wizard in self.browse(cr, uid, ids, context=None):
            obj_doc_expedient.write(cr, uid, exp_id, {'name':wizard.name,
                                                      'resumen':wizard.resumen,
                                                      'user_id':wizard.user_id.id,
                                                      'state':'draft'})
            
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_delete(uid, 'doc_expedient.expedient', expediente.id, cr)
            wf_service.trg_create(uid, 'doc_expedient.expedient', expediente.id, cr)
            
        #result = mod_obj.get_object_reference(cr, uid, 'gt_doc_expedient', 'action_doc_expedient_task_form1')
        #id = result and result[1] or False
        #result = act_obj.read(cr, uid, [id], context=context)[0]
        #result['context']="{'search_op':'complex'}"
        
        #result['context']="{'search_op':'complex', 'search_default_expendient_id':%s}"%obj.id
        #return {'type':'ir.actions.act_window_close'}
        return {'name':'Trámites Descartados',
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'doc_expedient.expedient',
                    #'res_id': message_id,
                    'type': 'ir.actions.act_window',
                    'domain': [('state','=','removed')],
                    #'view_id': '',
                    #'target': 'new',
                    }
        
    _columns = dict(
        name = fields.char('Asunto', size=128, required=True),
        resumen = fields.text('Resumen', required=True),
        user_id = fields.many2one('res.users', 'Responsable del Trámite', select=1, required=True),
        expedient_id = fields.many2one('doc_expedient.expedient','Trámite'),
    )
    _defaults = {'expedient_id':get_expedient}
                     
doc_expedient_draft()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
