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

class relateInvoiceAsset(osv.TransientModel):

    _name = "relate.invoice.asset"

    _columns = dict(
        partner_id = fields.many2one('res.partner','Contratista'),
#        contract_id = fields.many2one('doc_contract.contract','Contrato',required=True),
#        name = fields.char('Observaciones', size=256,required=True),
        asset_ids = fields.many2many('account.asset.asset','inv_id','ass_id','inv_asse_rel','Activos'),
        )

    def relate_invoice_asset(self, cr, uid, ids, context=None):
        active_id = context['active_ids'][0]
        for obj in self.browse(cr, uid, ids, context):
            for obj_asset in obj.asset_ids:
                self.pool.get('account.asset.asset').write(cr, uid, [obj_asset.id], {'invoice_id':active_id}, context)
        return {'type': 'ir.actions.act_window_close'}

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False

        res = super(relateInvoiceAsset, self).default_get(cr, uid, fields, context=context)
        invoice_id = self.pool.get('account.invoice').browse(cr, uid, record_id, context=context)
#        if 'invoice_id' in fields:
        res.update({'partner_id':invoice_id.partner_id.id})
        return res

 #   def _get_partner(self, cr, uid, ids, context=None):
 #       import pdb
 #       pdb.set_trace()
 #       for this in self.browse(cr, uid, ids):
 #           print "VELE"
 #       active_id = context['active_ids'][0]
 #       invoice_obj = self.pool.get('account.invoice')
 #       invoice = invoice_obj.browse(cr, uid, active_id)
 #       return invoice.partner_id.id
#
    _defaults = dict(
#        partner_id = _get_partner,
        )


relateInvoiceAsset()
