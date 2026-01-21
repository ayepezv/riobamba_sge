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

import datetime
from report import report_sxw
from tools import ustr

class viatico_informe(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(viatico_informe, self).__init__(cr, uid, name, context)
        self.localcontext.update({
		'actualizar_fecha': self.actualizar_fecha,
                })


    def actualizar_fecha(self, fecha):
        #import pdb
        #pdb.set_trace()
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=5)
        return fecha
        
report_sxw.report_sxw('report.viatico_informe', 'viaticos.solicitud', 'gt_doc_viaticos/report/viatico_informe.rml', parser=viatico_informe, header=True)

