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

class doc_covenant_cancel(osv.osv_memory):
    _name = 'doc_covenant.cancel'
    
    def get_convenio(self, cr, uid, context=None):
        return context.get('active_id',False)
    
    def cancel_covenant(self, cr, uid, ids, context=None):
        obj_historial = self.pool.get('doc.covenant.historial')
        obj_doc_covenant = self.pool.get('doc_covenant.covenant')
        for wizard in self.browse(cr, uid, ids, context=None):
            if not (wizard.notes):
                raise osv.except_osv('Mensaje de Advertencia !', 'Por favor ingrese una justificación...')
            obj_doc_covenant.write(cr, uid, [wizard.convenio.id], {'justification':wizard.notes,
                                                                   'state':'cancelled'})
            obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                           'usuario':uid,
                                           'name':'Convenio Anulado',
                                           'covenant_id':wizard.convenio.id})
        return {'type':'ir.actions.act_window_close'}
        
    _columns = dict(
        notes = fields.text('Justificación'),
        convenio = fields.many2one('doc_covenant.covenant'),
    )
    _defaults = {'convenio':get_convenio}
                     
doc_covenant_cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
