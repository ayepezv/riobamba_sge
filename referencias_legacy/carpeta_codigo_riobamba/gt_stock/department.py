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

from osv import osv, fields

class departmentLocation(osv.Model):
    _inherit = 'hr.department'
    _columns = dict(
        bool_location = fields.boolean('Activar como ubicación'),
        location_id = fields.many2one('stock.location','Ubicación Relacionada'),
        )

    def create(self, cr, uid, vals, context=None):
        location_obj = self.pool.get('stock.location')
        if vals.has_key('bool_location'):
          if vals['bool_location']:
            location_id = location_obj.create(cr, uid, {
                    'name':vals['name'],
                    'usage':'customer',
                    })
            vals['location_id']=location_id
        department_id = super(departmentLocation, self).create(cr, uid, vals, context=None)
        return department_id

departmentLocation
