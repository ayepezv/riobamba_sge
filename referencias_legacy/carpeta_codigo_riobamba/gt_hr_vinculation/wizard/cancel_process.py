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

class cancelProcessSol(osv.TransientModel):

    _name = "cancel.process.sol"

    _columns = dict(
        name = fields.char('Observaciones', size=256,required=True),
        )

    def cancel_process(self, cr, uid, ids, context=None):
        active_id = context['active_id']
        req_obj = self.pool.get('hr.sol.personal')
        req = req_obj.browse(cr, uid, active_id)
        this = self.browse(cr, uid, ids[0])
        obs = this.name
        req_obj.write(cr, uid, req.id,{
                                       'state':'Anulado',
                                       })
        return {'type': 'ir.actions.act_window_close'}

cancelProcessSol()
