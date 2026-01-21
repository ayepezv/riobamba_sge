import time
from report import report_sxw
import pooler

class ReportProgressBar(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportProgressBar, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_scope': self.get_scope,
            'get_time': self.get_time,
            'get_money': self.get_money
        })

    def get_scope(self, obj):
        progress_scope = 0
        progress_scope = sum([kpi.weight*kpi.progress for kpi in obj.pointer_detail_ids]) / 100
        return progress_scope

    def get_time(self, obj):
        progress_time = 0
        progress_time = sum([task.weight*task.progress_time for task in obj.tasks]) / 100.00
        return progress_time

    def get_money(self, obj):
        progress_money = 0
        progress_money = self.pool.get('project.project').get_progress_money(self.cr, self.uid, obj)
        return progress_money

report_sxw.report_sxw('report.project_bars_general',
                       'project.project', 
                       'addons/gt_project_project/report/project_budget_plan.mako',
                       parser=ReportProgressBar, header=True)
