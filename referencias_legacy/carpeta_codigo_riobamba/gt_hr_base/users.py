# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import osv, fields

class gpa_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
                'name': fields.char('Nombre de Usuario', size=128, required=True, select=True, help="Nombre real del usuario, usado para búsquedas y listados"),
                'job_id': fields.many2one('hr.job', 'Puesto de Trabajo'),
                'employee_id': fields.many2one('hr.employee', 'Servidor'),
                }
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = ""
            if record.employee_id:
                name = record.employee_id.complete_name
                if record.job_id:
                    name += ' - ' + record.job_id.name
            else:
                name = record.login
            res.append((record.id, name))
        return res

    def onchange_department(self, cr, uid, ids, context={}):
        return {'value':{'job_id': False}}
    
    def onchange_usuario(self, cr, uid, ids, job_id, employee_id, login, context={}):
        if ids: 
            if ids[0] == 1:
                return {'value':{'name':'Administrador'}}
        obj_job = self.pool.get('hr.job')
        obj_employee = self.pool.get('hr.employee')
        nombre_empleado = nombre_cargo = ""
        if employee_id:
            employee = obj_employee.browse(cr, uid, employee_id, context)
            nombre_empleado = employee.complete_name
        if job_id:
            job = obj_job.browse(cr, uid, job_id, context)
            nombre_cargo = job.name
        if login and (not job_id) and (not employee_id):
            return {'value':{'name': login}}
        return {'value':{'name': (nombre_cargo + ' - ' + nombre_empleado),}}
    
    def onchange_login(self, cr, uid, ids, job_id, employee_id, login, context={}):
        if login and (not job_id) and (not employee_id):
            return {'value':{'name': login}}
        
    def create(self, cr, uid, vals, context=None):
        result = super(gpa_users, self).create(cr, uid, vals, context=context)
        if vals.get('employee_id',False):
            obj_employee = self.pool.get('hr.employee')
            obj_employee.write(cr, uid, [vals['employee_id']], {'user_id':result}, context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        user_obj = self.pool.get('res.users')
        obj_employee = self.pool.get('hr.employee')
        result = super(gpa_users, self).write(cr, uid, ids, vals, context=context)
        if vals.has_key('employee_id'):
            for usuario in self.browse(cr, uid, ids, context):
                if usuario.employee_id:
                    obj_employee.write(cr, uid, [vals['employee_id']], {'user_id':usuario.id}, context)
        return result
    
gpa_users()
