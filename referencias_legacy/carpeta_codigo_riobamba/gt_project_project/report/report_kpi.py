import time
from report import report_sxw
from osv import osv

class ProjectReportKpi(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ProjectReportKpi, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'generate_plan': self.generate_plan,
            'generate_execution': self.generate_execution,
            'get_subtitle': self.get_subtitle,
        })

    def get_subtitle(self, kpi):
        return kpi.kpi_id.name
        
    def generate_execution(self, kpi):
        range_exec = [[0, 0]]
        for work in kpi.work_ids:
            t = time.strptime(work.date, '%Y-%m-%d')
            range_exec.append([t.tm_mon, work.exec_done])
        res = str(range_exec)
        return res

    def generate_plan(self, kpi):
        range_plan = [[0,0]]
        for plan in kpi.plan_ids:
            t = time.strptime(plan.period_id.date_start, '%Y-%m-%d')
            range_plan.append([t.tm_mon, plan.planned])
        res = str(range_plan)
        return res
        
report_sxw.report_sxw('report.project_report_kpi',
                       'project.project', 
                       'addons/gt_project_project/report/project_report_kpi.mako',
                       parser=ProjectReportKpi)
