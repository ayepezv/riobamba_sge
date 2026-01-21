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
import time

class doc_contract_cancel_inherit(osv.osv_memory):
    _inherit = 'doc_contract.cancel'
    
    def cancel_contract(self, cr, uid, ids, context=None):
        obj_historial = self.pool.get('doc.contract.historial')
        obj_doc_contract = self.pool.get('doc_contract.contract')
        log_obj = self.pool.get('log.state.change')
        for wizard in self.browse(cr, uid, ids, context=None):
            if not (wizard.notes):
                raise osv.except_osv('Mensaje de Advertencia !', 'Por favor ingrese una justificación...')
            obj_doc_contract.write(cr, uid, [wizard.contrato.id], {'justification':wizard.notes,
                                                                   'state':'cancelled'})
            obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                           'usuario':uid,
                                           'name':'Contrato Anulado',
                                           'contract_id':wizard.contrato.id})
        return {'type':'ir.actions.act_window_close'}
        
doc_contract_cancel_inherit()

