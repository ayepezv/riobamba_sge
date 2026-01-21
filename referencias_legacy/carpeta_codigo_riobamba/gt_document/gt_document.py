# -*- coding: utf-8 -*-
##############################################################################
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

from osv import osv
from osv import fields

class Doc_Ir_Attachment(osv.osv):
    _inherit = 'ir.attachment'

    def unlink(self, cr, uid, ids, *args, **kwargs):
        for doc in self.browse(cr, uid, ids):
            if doc.create_uid.id != uid:
                raise osv.except_osv(('Operación no Permitida  !'), ('No puede eliminar el documento del sistema.'))
        return super(Doc_Ir_Attachment, self).unlink(cr, uid, ids, *args, **kwargs)

#    def create(self, cr, uid, vals, context=None):
#        if vals['datas']:
#            adjunto= vals['datas']
#            vals['file_size'] = len(adjunto)
#            if len(adjunto)>14019368 or len(adjunto)== 0:
#                del vals['file_size']
#                raise osv.except_osv('Mensaje de Advertencia !', 'El Tamaño del adjunto no debe ser mayor a 10 MB')
#
#        res_id = super(Doc_Ir_Attachment, self).create(cr, uid, vals, context=context)
#        return res_id 	

Doc_Ir_Attachment()              
        

