import time
from report import report_sxw
import pooler

class ProjectReportKpi(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ProjectReportKpi, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_months': self.get_months
        })

    def get_months(self, kpi):
        work_obj = pooler.get_pool(self.cr.dbname).get('project.kpi.work')
        data = []
        executed = 0
        for plan in kpi.plan_ids:
            stop = str(plan.period_id.date_stop)
            if len(stop.split('/')) == 3:
                f = stop.split('/')
                f.reverse()
                stop = '-'.join(f)
            domain = [('project_id','=',kpi.project_id.id),('detail_id','=',kpi.id),('date','<=',stop)]
            res = work_obj.search(self.cr, self.uid, domain, order='date desc,exec_done desc',limit=1)
            if res:                
                executed = work_obj.browse(self.cr, self.uid, res[0]).exec_done
            data.append({'planned': plan.planned, 'executed': executed})
        return data

report_sxw.report_sxw('report.project_kpi_report',
                      'project.project', 
                      'addons/gt_project_project/report/project_budget_plan.mako',
                      parser=ProjectReportKpi, header=True)    
