import time
from report import report_sxw
import pooler

class ReportComplianceBar(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportComplianceBar, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_scope': self.get_scope,
            'get_time': self.get_time,
            'get_money': self.get_money
        })

    def get_scope(self, obj):
        com_kpi = sum([kpi.weight*kpi.compliance for kpi in obj.pointer_detail_ids]) / 100        
        return com_kpi>0 and com_kpi or 0

    def get_time(self, obj):
        total_ct = 0
        tpesos = 0
        today = time.strftime('%Y-%m-%d')
        for task in obj.tasks:
            if task.date_start < today:
                total_ct += task.weight*task.tcompliance
            tpesos += task.weight
        com_tasks = total_ct / tpesos
        return com_tasks>0 and com_tasks or 0

    def get_money(self, obj):
        total_budget = 0
        tpbudget = 0
        for task in obj.tasks:
            if task.bcompliance == 0 and task.progress_money2 == 0:
                continue
            total_budget += task.weight * task.bcompliance
            tpbudget += task.weight
        if tpbudget <= 0:
            tpbudget = 1
        com_budget = total_budget / tpbudget
        return com_budget>0 and com_budget or 0

report_sxw.report_sxw('report.project_compliance_report',
                       'project.project', 
                       'addons/gt_project_project/report/project_compliance_report.mako',
                       parser=ReportComplianceBar, header=True)
