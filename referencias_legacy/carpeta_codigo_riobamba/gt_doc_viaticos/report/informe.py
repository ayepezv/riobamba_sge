# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################
import math
import datetime
from report import report_sxw
from tools import ustr

class viatico_sol(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(viatico_sol, self).__init__(cr, uid, name, context)
        self.localcontext.update({
		'actualizar_fecha': self.actualizar_fecha,
                })


    def actualizar_fecha(self, fecha):
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=5)
        return fecha
        
report_sxw.report_sxw('report.viatico_sol', 'viaticos.solicitud', 'gt_doc_viaticos/report/solicitud.mako', parser=viatico_sol, header=True)

class viatico_inf(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(viatico_inf, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_fecha': self.get_fecha,
            'get_hora': self.get_hora,
            'get_hora_inicio': self.get_hora_inicio,
            'float_time_convert': self.float_time_convert,
            'actualizar_fecha': self.actualizar_fecha,
        })

    def float_time_convert(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        aux = (factor * int(math.floor(val)), int(round((val % 1) * 60)))
        aux_return = str(aux[0])+':'+str(aux[1])
        return aux_return

    def get_fecha(self, fecha):
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=5)
        aux = fecha.strftime('%d-%m-%Y')
        return aux

    def get_hora(self, fecha):
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=5)
        aux = fecha.strftime('%H:%M')
        return aux

    def get_hora_inicio(self, hora):
        return hora

    def actualizar_fecha(self, fecha):
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=5)
        return fecha
        
report_sxw.report_sxw('report.viatico_inf', 'viaticos.solicitud', 'gt_doc_viaticos/report/informe.mako', parser=viatico_inf, header=True)

