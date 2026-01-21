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
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

class vehicle_km_start(osv.osv_memory):
    _name = "vehicle.km.start"
    _description = "Seteo Kilometraje"
    
    _columns = dict(
        km = fields.integer('Kilometraje Inicial'),
        )

    def do_start_km(self, cr, uid, ids, context):
        vehicle_obj = self.pool.get('vehicle.vehicle')
        vals = {}
        for wizard in self.browse(cr, uid, ids[0], context=context):
            #Quantiny must be Positive
            if wizard.km <= 0:
                raise osv.except_osv(('Advertencia!'), ('Por favor ingrese valores positivos en el kilometraje!'))
            #vehicle_obj.write(cr, uid, context['active_id'],{
            #        'km':wizard.km,
            #        })
            vals['km']=wizard.km
        return super(vehicleVehicle, self).create(cr, uid, vals, context=None)
        #return {'type': 'ir.acctions.act_window_close'}
