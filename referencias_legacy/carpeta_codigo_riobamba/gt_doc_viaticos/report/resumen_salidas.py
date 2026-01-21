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

from datetime import datetime
from report import report_sxw

class resumen_salidas(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(resumen_salidas, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                                  'rango_inicio': self.rango_inicio,
                                  'rango_fin': self.rango_fin,
                })
        
    def rango_inicio(self, data):
        print data
        print "inicio"
        return 'inicio'
    
    def rango_fin(self):
        return 'fin'
        
report_sxw.report_sxw('report.resumen_salidas', 'salidas.solicitud', 'gt_doc_viaticos/report/resumen_salidas.rml', parser=resumen_salidas, header=False)

