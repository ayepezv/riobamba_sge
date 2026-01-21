import time
from report import report_sxw
from osv import osv

class ProjectReportTasks(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ProjectReportTasks, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'browse_group': self.browse_group,
            'get_progress': self.get_progress
        })

    def browse_group(self, objects):
        """
        return: {'dept': 1, 'project_ids':[]}
        """
        data = []
        data2 = {}        
        project_obj = self.pool.get('project.project')
        for p in objects:
            if not data2.get(p.department_id.id):
                data2.update({p.department_id.id: {'project_ids':[], 'name': p.department_id.name }})
            data2[p.department_id.id]['project_ids'].append(p)
        for k,v in data2.items():
            data.append(v)
        return data

    def get_progress(self, project):
        total = 0
        w = 0
        for t in project.tasks:
            total += t.weight*t.progress_time
            w += t.weight
        total = total / w
        return total

    def generate_execution(self, task):
        range_exec = [[0, 0]]
        for work in task.executed_ids:
            t = time.strptime(work.date_done, '%Y-%m-%d %H:%M:%S')
            range_exec.append([t.tm_mon, work.executed])
        res = str(range_exec)
        return res

report_sxw.report_sxw('report.project_tasks_report',
                       'project.project', 
                       'addons/gt_project_project/report/project_report_tasks.mako',
                       parser=ProjectReportTasks)
