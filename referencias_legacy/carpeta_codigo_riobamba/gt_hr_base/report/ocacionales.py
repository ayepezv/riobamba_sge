# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
import time
from report import report_sxw
from osv import fields, osv
from gt_tool import XLSWriter
import re

class ocacionales(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ocacionales, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_actividades': self.get_actividades,
        })

    def get_actividades(self, this):
        actividades = []
        ocupacional_obj = self.pool.get('grupo.ocupacional.line')
        ocupacional_ids = ocupacional_obj.search(self.cr, self.uid, [('ocupacional_id','=',this.ocupational_id.id),('job_id','=',this.employee_id.job_id.id)])
        if ocupacional_ids:
            ocupacional = ocupacional_obj.browse(self.cr, self.uid, ocupacional_ids[0])
            for line in ocupacional.line_ids:
                actividades.append(line.name)
        return actividades

report_sxw.report_sxw('report.ocacionales',
                       'hr.contract', 
                       'addons/gt_hr_base/report/ocacionales.mako',
                       parser=ocacionales,
                       header=False)

