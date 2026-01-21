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

class doc_expedient_import(osv.osv_memory):
    _name = 'doc_expedient.import'
    
    
    def expedient_import(self, cr, uid, ids, context=None):
        obj_doc_expedient = self.pool.get('doc_expedient.expedient')
        exp_id = context.get('active_id', False)
        expediente = self.pool.get('doc_expedient.expedient').browse(cr, uid, exp_id)
        for wizard in self.browse(cr, uid, ids, context=None):
            if not (wizard.notes):
                raise osv.except_osv('Mensaje de Advertencia !', 'Por favor ingrese una justificación...')
            if not (expediente.user_id.id == uid):
                raise osv.except_osv('Mensaje de Advertencia !', 'El usuario no puede anular el Tramite...')     
            obj_doc_expedient.write(cr, uid, exp_id, {'justification':wizard.notes})
            #pdb.set_trace()
            
            wf_service = netsvc.LocalService("workflow")
            #wf_service.trg_delete(uid, 'doc_expedient.expedient', expediente.id, cr)
            #wf_service.trg_create(uid, 'doc_expedient.expedient', expediente.id, cr)
            
            if expediente.state == 'draft':
                wf_service.trg_validate(uid, 'doc_expedient.expedient', wizard.expediente.id, 'wkf_draft_cancelled', cr)
                
            elif expediente.state == 'created':
                #wf_service.trg_validate(uid, 'doc_expedient.expedient', wizard.expediente.id, 'wkf_created_cancelled', cr)
                obj_doc_expedient.action_created_cancelled(cr, uid, [expediente.id])
        return {'type':'ir.actions.act_window_close'}
        
    _columns = dict(
        notes = fields.text('Justificación'),
        expediente = fields.many2one('doc_expedient.expedient'),
    )
    #_defaults = {'expediente':get_expedient}
                     
doc_expedient_import()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
