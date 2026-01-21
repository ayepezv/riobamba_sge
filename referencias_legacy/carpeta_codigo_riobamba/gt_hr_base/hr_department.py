# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
#
##############################################################################

__author__ = 'Mario Chogllo'

import time
import logging
from tools import ustr

from osv import osv, fields


class HrDepartment(osv.Model):

    _inherit = 'hr.department'

    _columns = dict(
        is_direccion = fields.boolean('Es Direccion'),
        sequence = fields.char('Código', size=8, required=True),
        coordinador_id = fields.many2one('hr.employee','Jefe'),
        direccion_id = fields.many2one('hr.department','Direccion'),
        program_id = fields.many2one('project.program','Programa'),
    )

    def unlink(self, cr, uid, ids, *args, **kwargs):
        employee_obj = self.pool.get('hr.employee')
        lista_emp = []
        for departamento in self.browse(cr, uid, ids):
            employee_ids = employee_obj.search(cr, uid, [('department_id','=',departamento.id)])
            if employee_ids:
                for employee_id in employee_ids:
                    empleado = employee_obj.browse(cr, uid, employee_id)
                    lista_emp.append(empleado.complete_name)
            if lista_emp:
                str_empleados = ''
                for emp in lista_emp:
                    str_empleados += emp + ' - '  
                raise osv.except_osv(('Operacion no permitida !'), ('El departamento esta relacionado en los empleados %s ') % (str_empleados))
        return super(HrDepartment, self).unlink(cr, uid, ids, *args, **kwargs)

    def name_get(self, cr, uid, ids, context=None):
        """
        Contructor de texto cuando el objeto se representa
        en un campo many2one
        """
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            if r.sequence:
                name_aux = r.sequence + ' ' + r.name
            else:
                name_aux = r.name
            res.append((r.id, name_aux))
        return res

    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
        ids = []
        ids_cedula = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        ids = list(set(ids + ids_cedula))
        if name:
            ids_name = self.search(cr, uid, [('sequence', operator, name)] + args, limit=limit, context=context)
            ids = list(set(ids + ids_name))
        return self.name_get(cr, uid, ids, context=context)

