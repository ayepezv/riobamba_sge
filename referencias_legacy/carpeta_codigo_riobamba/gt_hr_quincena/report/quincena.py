# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
from report import report_sxw
from osv import fields, osv
import time
class quincena_tipo(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(quincena_tipo, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_tipo_rol':self.get_tipo_rol,
            'get_lines':self.get_lines,
        })

    def get_lines(self,o):
        tipo_obj = self.pool.get('hr.contract.type.type')
        tipo_ids= tipo_obj.search(self.cr, self.uid, [])
        return tipo_ids

    def get_tipo_rol(self,o):
        tipo_obj = self.pool.get('hr.contract.type.type')
        tipo_ids= tipo_obj.search(self.cr, self.uid, [])
        return tipo_ids
        
report_sxw.report_sxw('report.quincena_tipo',
                       'hr.quincena', 
                       'addons/gt_hr_quincena/report/quincena_tipo.mako',
                       parser=quincena_tipo,
                       header=True)

