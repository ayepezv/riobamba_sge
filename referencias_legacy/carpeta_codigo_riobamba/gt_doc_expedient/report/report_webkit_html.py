import time
from report import report_sxw
from osv import osv
import pdb

class report_doc_expedient_external(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_doc_expedient_external, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
      
report_sxw.report_sxw('report.report_doc_expedient_external',
                       'doc_expedient.expedient', 
                       'addons/gt_doc_expedient/report/report_doc_expedient_external.mako',
                       parser=report_doc_expedient_external,
                       header=True)


class report_doc_expedient(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_doc_expedient, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
      
report_sxw.report_sxw('report.report_doc_expedient',
                       'doc_expedient.expedient', 
                       'addons/gt_doc_expedient/report/report_doc_expedient.mako',
                       parser=report_doc_expedient,
                       header=True)

class report_doc_expedient_consult(report_sxw.rml_parse):
    
    def get_tasks_expedient(self, objects):
        for o in objects:
            obj_task = self.pool.get('doc_expedient.task')
            tasks_ids = obj_task.search(self.cr, self.uid, [('expedient_id','=',o.id)])
            objs = []
            for o in obj_task.browse(self.cr, self.uid, tasks_ids):
                objs.append(o)
            return objs
            

    def __init__(self, cr, uid, name, context):
        super(report_doc_expedient_consult, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_tasks_expedient': self.get_tasks_expedient,
        })
      
report_sxw.report_sxw('report.report_doc_expedient_consult',
                       'doc_expedient.expedient', 
                       'addons/gt_doc_expedient/report/report_doc_expedient_consult.mako',
                       parser=report_doc_expedient_consult,
                       header=True)



class report_doc_task(report_sxw.rml_parse):
    
    def get_department_ids(self):
        obj_department = self.pool.get('hr.department')
        ids_department = obj_department.search(self.cr, self.uid, [])
        return obj_department.browse(self.cr, self.uid, ids_department)

    def get_tareas_empleado(self, objects):
        values=[]
        datos=[]
        totales=[]
        total=0
        obj_department = self.pool.get('hr.department')
        ids_department = obj_department.search(self.cr, self.uid, [])
        for departamento in ids_department:
            
            for o in objects:
                bandera = False
                if o.department.id == departamento:
                    for fila in datos:
                        if fila[0] == o.employee_id.id and fila[2] == o.department.id and o.state == 'progress':
                            fila[4] += 1
                            total+=1
                            bandera = True
                    if bandera == False and o.state == 'progress':
                        #values.append([o.department.id,o.department.name,o.employee_id.id,1,o.employee_id.employee_lastname +' '+ o.employee_id.name,''])
                        datos.append([o.employee_id.id,o.employee_id.employee_lastname +' '+ o.employee_id.name,o.department.id,o.department.name,1])
                        total+=1
                             
        #datos.append([0,' ',0,'TOTAL',total])
        datos.sort(lambda x,y:cmp(x[1], y[1]))
        return datos
    
    
    def get_total_tareas(self, objects):
        datos=[]
        total=0
        obj_department = self.pool.get('hr.department')
        ids_department = obj_department.search(self.cr, self.uid, [])
        for departamento in ids_department:
            
            for o in objects:
                bandera = False
                if o.department.id == departamento:
                    for fila in datos:
                        if fila[0] == o.employee_id.id and fila[2] == o.department.id and o.state == 'progress':
                            fila[4] += 1
                            total+=1
                            bandera = True
                    if bandera == False and o.state == 'progress':
                        #values.append([o.department.id,o.department.name,o.employee_id.id,1,o.employee_id.employee_lastname +' '+ o.employee_id.name,''])
                        #datos.append([o.employee_id.id,o.employee_id.employee_lastname +' '+ o.employee_id.name,o.department.id,o.department.name,1])
                        total+=1
                             
        datos.append([' ','TOTAL',total])
        #datos.sort(lambda x,y:cmp(x[1], y[1]))
        return datos
    
    
 

  
    def __init__(self, cr, uid, name, context):
        super(report_doc_task, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_department_ids': self.get_department_ids,
            'get_tareas_empleado': self.get_tareas_empleado,
            'get_total_tareas': self.get_total_tareas,
            
        })
      
report_sxw.report_sxw('report.report_doc_task',
                       'doc_expedient.task', 
                       'addons/gt_doc_expedient/report/report_doc_task.mako',
                       parser=report_doc_task,
                       header=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
