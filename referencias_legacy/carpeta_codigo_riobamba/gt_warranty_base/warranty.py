# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Gnuthink Software Labs Cia. Ltda.
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

class WarrantyType(osv.osv):
    _name = 'warranty.type'
    _description = 'Warranty Types'

    _columns = {
        'name': fields.char('Nombre', size=32),
        'amount': fields.float('Monto Base', help="Monto base para aplicar este tipo."),
        'inclusive': fields.boolean('Incluyente', help="Considera más de una garantía."),
        'advance': fields.boolean('Anticipo ?'),
        }
WarrantyType()


class ResCompany(osv.Model):
    _inherit = 'res.company'

    _columns = {
        'warranty_days_due': fields.integer('Días Garantías'),
        }

    _defaults = {
        'warranty_days_due': 15,
        }
