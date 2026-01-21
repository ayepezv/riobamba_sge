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

class salidas_pagadas(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(salidas_pagadas, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                                  'agrupar_departamento': self.agrupar_departamento,
                })
        
    def agrupar_departamento(self, objects):
        res = []
        for objeto in objects:
            if objeto.state == 'pagado':
                bandera = False
                for resultado in res:
                    if objeto.department_id.id == resultado[0] and objeto.period_id.id == resultado[2]:
                        resultado[4] = resultado[4] + objeto.valor
                        resultado[5].append(objeto)
                        bandera = True
                if bandera == False:
                    #id departamento, nombre departamento, id mes, mes, total, [registros]
                    res.append([objeto.department_id.id, objeto.department_id.name, objeto.period_id.id, objeto.period_id.name, objeto.valor, [objeto]])
        return res
        
report_sxw.report_sxw('report.salidas_pagadas', 'salidas.solicitud', 'gt_doc_viaticos/report/salidas_pagadas.rml', parser=salidas_pagadas, header=True)

