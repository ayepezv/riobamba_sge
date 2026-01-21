import time
from report import report_sxw

class ReportVial(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportVial, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'process':self.process,
            'get_value': self.get_value,
            'get_before': self.get_before,
            'convert_date': self.convert_date
        })

    def convert_date(self, date):
        return getattr(date,'val')        

    def get_before(self, kpi_id, project_id):
        """
        Devuelve ultimo valor de avance de indicador
        """
        work_obj = self.pool.get('project.kpi.work')
        value = work_obj.get_before(self.cr, self.uid, kpi_id, project_id)
        return value    

    def get_value(self, kpi_id, project_id):
        """
        Devuelve ultimo valor de avance de indicador
        """
        work_obj = self.pool.get('project.kpi.work')
        value = work_obj.get_last(self.cr, self.uid, kpi_id, project_id)
        return value

    def process(self, objects, data):
        """
        Lista de objetos a ser procesados
        {'program_id': {projects: {canton: {projs: []} } } }
        """
        data = []
        data2 = {}
        for project in objects:
            program = project.build_program_id
            if not data2.get(program.id):
                data2.update({program.id: {'program_name': program.name, 'projects': {} } })
            if not data2[program.id]['projects'].get(project.canton_id.id):
                data2[program.id]['projects'].update({project.canton_id.id: {'projs': [], 'canton': project.canton_id.name} })
            data2[program.id]['projects'][project.canton_id.id]['projs'].append(project)
        for k, v in data2.items():
            v['projects'] = [v1 for k1,v1 in v['projects'].items()]
            data.append(v)            
        return data

report_sxw.report_sxw('report.project_infvial1_report',
                       'project.project', 
                       'addons/gt_project_project/report/project_report_infvial.mako',
                       parser=ReportVial, header=True)


class ReportVialSemanal(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportVialSemanal, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'process':self.process,
            'get_value': self.get_value,
            'get_before': self.get_before,
            'convert_date': self.convert_date,
            'group_kpis': self.group_kpis
        })

    def group_kpis(self, projects):
        """
        Agrupa los indicadores de los proyectos por programa
        y saca los totales
        """
        kpis = []
        data = {}
        lista = []
        for p in projects:
            kpis += [kpi for kpi in p.pointer_detail_ids if kpi.kpi_id.to_report]
        for k in kpis:
            if not data.get(k.id):
                data.update({k.id: {'valor': 0, 'name': k.kpi_id.name} })
            data[k.id]['valor'] += k.progress
        for k, v in data.items():
            lista.append(v)
        return lista

    def convert_date(self, date):
        return getattr(date,'val')        

    def get_before(self, kpi_id, project_id):
        """
        Devuelve ultimo valor de avance de indicador
        """
        work_obj = self.pool.get('project.kpi.work')
        value = work_obj.get_before(self.cr, self.uid, kpi_id, project_id)
        return value    

    def get_value(self, kpi_id, project_id):
        """
        Devuelve ultimo valor de avance de indicador
        """
        work_obj = self.pool.get('project.kpi.work')
        value = work_obj.get_last(self.cr, self.uid, kpi_id, project_id)
        return value

    def process(self, objects, data):
        """
        Lista de objetos a ser procesados
        [{'program_id': {projects: [] }, 'program_id2': {'projects:' []} }]
        """
        data = []
        data2 = {}
        for project in objects:
            program = project.build_program_id
            if not data2.get(program.id):
                data2.update({program.id: {'program_name': program.name, 'projects': [], 'total': 0 } })
            data2[program.id]['projects'].append(project)
        for k, v in data2.items():
            data.append(v)            
        return data

report_sxw.report_sxw('report.project_infvial2_report',
                       'project.project', 
                       'addons/gt_project_project/report/project_report_infvial_semanal.mako',
                       parser=ReportVialSemanal, header=True)    


