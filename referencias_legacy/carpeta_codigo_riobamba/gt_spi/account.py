# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-now Gnuthink Software Labs Co. Ltd. (<http://www.gnuthink.com>).
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

from time import strftime, strptime

from osv import osv, fields

class spiAccountMove(osv.Model):
    _inherit = 'account.move'
    _columns = dict(
        state = fields.selection([('draft','Unposted'), ('posted','Posted'),('payprocess','En proceso pago'),('pagado','Pagado'),('anulado','Anulado')], 
                                 'State', required=True, readonly=True)
     )
spiAccountMove()
