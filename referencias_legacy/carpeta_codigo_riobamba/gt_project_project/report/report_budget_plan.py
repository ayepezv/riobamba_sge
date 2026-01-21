import time
from report import report_sxw
import pooler

class ReportBudgetPlan(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportBudgetPlan, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'browse_group': self.browse_group,
            'get_total': self.get_total,
            'commited': self.commited
        })

    def commited(self, tasks):
        total = 0
        for t in tasks:
            total += sum([b.commited_amount for b in t.budget_planned_ids])
        return total

    def browse_group(self, objects):
        """
        return: [{'department_id':[p1,p2,p3,..,Pn]}]
        """
        project_obj = pooler.get_pool(self.cr.dbname).get('project.project')
        data = []
        data2 = {}
        for p in objects:
            if not data2.get(p.department_id.id):
                data2.update({p.department_id.id: {'project_ids':[],
                                                   'name': p.department_id.name,
                                                   'planned_amount':0,
                                                   'commited_amount': 0,
                                                   'avai_amount': 0  }})
            data2[p.department_id.id]['project_ids'].append(p)
            data2[p.department_id.id]['planned_amount'] += p.amount_budget
            data2[p.department_id.id]['commited_amount'] += self.commited(p.tasks)
            data2[p.department_id.id]['avai_amount'] += p.amount_budget - self.commited(p.tasks) 
        for k,v in data2.items():
            data.append(v)
        return data

    def get_total(self, objects):
        data = {'planned': 0, 'commited': 0, 'avai': 0}
        for p in objects:
            data['planned'] += p.amount_budget
            data['commited'] += self.commited(p.tasks)
            data['avai'] += p.amount_budget - self.commited(p.tasks)
        return data
        
report_sxw.report_sxw('report.project_budget_plan_report',
                       'project.project', 
                       'addons/gt_project_project/report/project_budget_plan.mako',
                       parser=ReportBudgetPlan, header=True)
