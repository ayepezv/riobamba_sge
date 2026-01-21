2# -*- coding: utf-8 -*-
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

class relateInvoiceConv(osv.TransientModel):

    _name = "relate.invoice.covenant"

    _columns = dict(
#        partner_id = fields.many2one('res.partner','Beneficiario'),
        covenant_id = fields.many2one('doc_covenant.covenant','Convenio',required=True),
#        name = fields.char('Observaciones', size=256,required=True),
        )

    def relate_invoice_covenant(self, cr, uid, ids, context=None):
        active_id = context['active_ids'][0]
        invoice_obj = self.pool.get('account.invoice')
        covenant_obj = self.pool.get('doc_covenant.covenant')
        this = self.browse(cr, uid, ids[0])
        covenant_id = this.covenant_id.id
        #validar los montos
        covenant = covenant_obj.browse(cr, uid, covenant_id)
        invoice = invoice_obj.browse(cr, uid, active_id)
        amount_invoice = 0
        for invoice in covenant.invoice_ids:
            amount_invoice += invoice.amount_vat_cero+invoice.amount_vat
#        if (amount_invoice + invoice.amount_vat_cero+invoice.amount_vat) > contract.amount:
#            raise osv.except_osv(('Error de usuario'), ('El monto total de las facturas no puede sobrepasar el monto del contrato'))
        sql = "insert into inv_cov_rel (c_id,inv_id) values(%s,%s)" % (active_id,covenant_id)
        cr.execute(sql)
        return {'type': 'ir.actions.act_window_close'}

relateInvoiceConv()
