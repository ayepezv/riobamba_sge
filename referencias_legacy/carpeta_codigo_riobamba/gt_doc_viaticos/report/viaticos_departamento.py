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

class viaticos_departamento(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(viaticos_departamento, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'agrupar_departamento': self.agrupar_departamento,
		'actualizar_fecha': self.actualizar_fecha,
                })
        
    def agrupar_departamento(self, objects):
        res = []
        for objeto in objects:
            if objeto.state== 'done' or objeto.state == 'end':
                bandera = False
                for resultado in res:
                    if objeto.department_id.id == resultado[0]:
                        resultado[2] = resultado[2] + objeto.total_informe
                        resultado[3].append(objeto)
                        bandera = True
                if bandera == False:
                    #id departamento, nombre departamento, total, [registros]
                    res.append([objeto.department_id.id,objeto.department_id.name, objeto.total_informe, [objeto]])
        return res

    def actualizar_fecha(self, fecha):
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=5)
        return fecha
        
report_sxw.report_sxw('report.viaticos_departamento', 'viaticos.solicitud', 'gt_doc_viaticos/report/viaticos_departamento.rml', parser=viaticos_departamento, header=True)

