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

__author__ = 'Cristian Salamea'

import time
import logging

from osv import osv, fields

class hr_department_nivel(osv.osv):

    _name = 'hr.department.level'

    _columns = dict(
        name = fields.char('Nombre de nivel', size=50, required=True),
        )
hr_department_nivel()


class HrDepartment(osv.Model):

    _inherit = 'hr.department'
    _order = 'sequence asc'

    _columns = dict(
        name = fields.char('Nombre de Departamento', size=100, required=True),
        sequence = fields.char('Código', size=8, required=True),
        active = fields.boolean('Activo'),
        email= fields.text('Email'),
        )

    _defaults = dict(
        active = True,
        )

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se representa
        en un campo many2one
        """
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            res.append((r.id, r.name))
        return res



