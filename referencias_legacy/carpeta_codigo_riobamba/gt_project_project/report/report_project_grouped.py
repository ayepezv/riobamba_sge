import time
from report import report_sxw

class ReportProjectByAxis(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportProjectByAxis, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'browse_group': self.browse_group,
            'convert_date': self.convert_date,
            'get_fy': self.get_fy
        })

    def get_fy(self):
        conf_obj = self.pool.get('project.configuration')
        res = conf_obj.search(self.cr, self.uid, [('active','=',True)])
        if not res:
            return '<th>Ninguno</th>'
        data = conf_obj.browse(self.cr, self.uid, res)[0]
        line = "<th>%s</th>" % data.fiscalyear_plan_id.name
        return line

    def convert_date(self, date):
        return getattr(date,'val')

    def browse_group(self, objects):
        """
        return: []
        """
        project_obj = self.pool.get('project.project')
        data = []
        data2 = {}
        objects.sort(key=lambda x: x.state)
        for p in objects:
            if not data2.get(p.axis_id.id):
                data2.update({p.axis_id.id: {'project_ids':[],
                                                   'name': p.axis_id.name,
                                                   'progress': 0, 'compliance': 0, 'count': 0 }})
            data2[p.axis_id.id]['project_ids'].append(p)
            data2[p.axis_id.id]['count'] += 1
        for k,v in data2.items():
            data.append(v)
        for d in data:
            d['progress'] = sum([p.activity_progress for p in d['project_ids']]) / len(d['project_ids'])
            d['compliance'] = sum([p.compliance for p in d['project_ids']]) / len(d['project_ids'])            
        return data

report_sxw.report_sxw('report.project_by_axis',
                       'project.project', 
                       'addons/gt_project_project/report/project_by_axis.mako',
                       parser=ReportProjectByAxis)


class ReportProjectByEstrategy(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportProjectByEstrategy, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'browse_group': self.browse_group,
            'convert_date': self.convert_date,
            'get_fy': self.get_fy
        })

    def get_fy(self):
        conf_obj = self.pool.get('project.configuration')
        res = conf_obj.search(self.cr, self.uid, [('active','=',True)])
        if not res:
            return '<th>Ninguno</th>'
        data = conf_obj.browse(self.cr, self.uid, res)[0]
        line = "<th>%s</th>" % data.fiscalyear_plan_id.name
        return line

    def convert_date(self, date):
        return getattr(date,'val')

    def browse_group(self, objects):
        """
        return: []
        """
        project_obj = self.pool.get('project.project')
        data = []
        data2 = {}
        objects.sort(key=lambda x: x.state)
        for p in objects:
            if not data2.get(p.estrategy_id.id):
                data2.update({p.estrategy_id.id: {'project_ids':[],
                                                   'name': p.estrategy_id.name,
                                                   'progress': 0, 'compliance': 0, 'count': 0 }})
            data2[p.estrategy_id.id]['project_ids'].append(p)
            data2[p.estrategy_id.id]['count'] += 1
        for k,v in data2.items():
            data.append(v)
        for d in data:
            d['progress'] = sum([p.activity_progress for p in d['project_ids']]) / len(d['project_ids'])
            d['compliance'] = sum([p.compliance for p in d['project_ids']]) / len(d['project_ids'])            
        return data

report_sxw.report_sxw('report.project_by_estrategy',
                       'project.project', 
                       'addons/gt_project_project/report/project_by_estrategy.mako',
                       parser=ReportProjectByEstrategy)


class ReportProjectByProgram(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportProjectByProgram, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'browse_group': self.browse_group,
            'convert_date': self.convert_date,
            'get_fy': self.get_fy
        })

    def get_fy(self):
        conf_obj = self.pool.get('project.configuration')
        res = conf_obj.search(self.cr, self.uid, [('active','=',True)])
        if not res:
            return '<th>Ninguno</th>'
        data = conf_obj.browse(self.cr, self.uid, res)[0]
        line = "<th>%s</th>" % data.fiscalyear_plan_id.name
        return line

    def convert_date(self, date):
        return getattr(date,'val')

    def browse_group(self, objects):
        """
        return: []
        """
        project_obj = self.pool.get('project.project')
        data = []
        data2 = {}
        objects.sort(key=lambda x: x.state)
        for p in objects:
            if not data2.get(p.program_id.id):
                data2.update({p.program_id.id: {'project_ids':[],
                                                   'name': p.program_id.name,
                                                   'progress': 0, 'compliance': 0, 'count': 0 }})
            data2[p.program_id.id]['project_ids'].append(p)
            data2[p.program_id.id]['count'] += 1
        for k,v in data2.items():
            data.append(v)
        for d in data:
            d['progress'] = sum([p.activity_progress for p in d['project_ids']]) / len(d['project_ids'])
            d['compliance'] = sum([p.compliance for p in d['project_ids']]) / len(d['project_ids'])            
        return data

report_sxw.report_sxw('report.project_by_program',
                       'project.project', 
                       'addons/gt_project_project/report/project_by_program.mako',
                       parser=ReportProjectByProgram)
