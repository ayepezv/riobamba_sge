import time
from report import report_sxw
from osv import osv
import pdb

class rol_individual_gpa(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rol_individual_gpa, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
      
report_sxw.report_sxw('report.rol_individual_gpa',
                       'hr.payslip', 
                       'addons/gt_hr_payroll_ec/report/rol_individual_gpa.mako',
                       parser=rol_individual_gpa,
                       header=False)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
