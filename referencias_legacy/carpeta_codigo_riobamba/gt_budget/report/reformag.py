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
from tools import ustr
import operator

class mass_reformg(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(mass_reformg, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })

report_sxw.report_sxw('report.mass_reformg',
                       'mass.reform', 
                       'addons/gt_budget/report/reformag.mako',
                       parser=mass_reformg,
                       header=True)

