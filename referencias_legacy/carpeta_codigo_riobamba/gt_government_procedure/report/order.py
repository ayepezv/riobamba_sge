# -*- coding: utf-8 -*-
##############################################################################
#    
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler
from gt_tool import amount_to_text_ec

class orderM(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(orderM, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time,
                                  'get_letras_po':self.get_letras_po,
                                  })

    def get_letras_po(self, valor):
        letra = amount_to_text_ec.amount_to_text_ec(valor)
        return letra

report_sxw.report_sxw('report.purchase.order.m','purchase.order','addons/gt_government_procedure/report/order.rml',parser=orderM,header=True)


