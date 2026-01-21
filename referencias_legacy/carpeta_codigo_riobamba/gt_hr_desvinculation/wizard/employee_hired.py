# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

class hiredEmployee(osv.osv_memory):
    _name = 'hired.employee.ec'
    _description = 'Crea Empleado y Contrato'

    _columns = dict(
        wage = fields.float('Sueldo', required=True),
        type_id = fields.many2one('hr.contract.type','Tipo', required=True),
        date_start = fields.date('Fecha Inicio', required=True),
        )

    def vinculate(self, cr, uid,ids, context=None):
        """
        @param self: El objeto
        @param cr: cursor de la base de datos,
        @param uid: el ID del usuario actual,
        @param ids: Lista de IDS
        @param *args: Valor de la tupla
        """
        if context is None:
            context = {}
        objeto = self.browse(cr, uid, ids[0])
        return self.pool.get('hr.applicant').vinculate_employee(cr, uid,context.get('active_ids', []),objeto)

hiredEmployee()


