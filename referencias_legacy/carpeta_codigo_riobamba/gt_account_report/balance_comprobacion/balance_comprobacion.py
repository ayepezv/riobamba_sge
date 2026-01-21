# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2013 Consultoria YarosLab (<http://www.yaroslab.com> - info@yaroslab.com).
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

from osv import fields, osv
import time
from datetime import datetime
from openerp.tools.translate import _

class balance_comprobacion(osv.osv):
    _name = "balance.comprobacion"
    _description = "Balance de comprobacion"

    def _get_years(self, cursor, user_id, context=None):
        years = []
        year_now = datetime.now().year
        for x in range(15):
            years.append((str(year_now - x), str(year_now - x)))
        return years

    _columns = {
        'anio': fields.selection(_get_years, 'Año', required=True),
    }

    def report_banlace_comprobacion(self, cr, uid, ids, context={}):
        print "report_banlace_comprobacion: ids %s, context %s" % (ids, context)

        datas = {'ids': context.get('active_ids', [])}
        anio = self.read(cr, uid, ids, ['anio'], context=context)
        anio = anio and anio[0] or {}
        datas['form'] = dict(anio.items())
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'BalanceComprobacion',
            'datas': datas,
        }

balance_comprobacion()
