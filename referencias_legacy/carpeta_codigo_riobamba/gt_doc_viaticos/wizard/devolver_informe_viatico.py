# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from osv import fields, osv
from time import strftime
from tools import ustr

class viatico_devolver_informe(osv.osv_memory):

   _name ='viatico.devolver.informe'
   _columns = {
        'viatico_id': fields.many2one('viaticos.solicitud', 'Viatico', readonly=True),
        'state': fields.related('viatico_id', 'state', type="selection", selection=[('draft','Borrador'),('solicitud1','Solicitado'),('solicitud2','Aprobado Jefe Superior'),('solicitud3','Aprobado Prefectura / Ingresar Informe'),('informe1','Informe ingresado'),('informe2','Informe aprobado Jefe superior'),('done','Aprobado TTHH'),('end','Finalizado'),('cancel','Rechazado'),('anulado','Anulado')], string="Estado"),
        'descripcion' : fields.char('Descripcion', size=128, required="1"),
        }

   def get_viatico(self, cr, uid, context={}):
      return context.get('active_id')
  
   def get_viatico_state(self, cr, uid, context={}):
       obj_viatico = self.pool.get('viaticos.solicitud')
       viatico = obj_viatico.browse(cr, uid, context.get('active_id'), context)
       return viatico.state
  

   def devolver_informe_viatico(self, cr, uid, ids, context={}):
      log_obj=self.pool.get('viaticos.log')
      usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
      viatico_obj=self.pool.get('viaticos.solicitud')
      for obj in self.browse(cr, uid, ids):
         log_obj.create(cr, uid, {
                                  'name': 'INFORME DEVUELTO: ' + obj.descripcion,
                                  'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                                  'viatico_id': obj.viatico_id.id,
                                  'user_id': uid,
                                  })
         task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                                  'other_action' : str('INFORME DEVUELTO') ,
                                                                                  'description': 'Informe devuelto por: ' + ustr(usuario.name),
                                                                                  #'department': obj.viatico_id.employee_id.department_id.id,
                                                                                  'assigned_user_id' : obj.viatico_id.employee_id.user_id.id,
                                                                                  'job_id': obj.viatico_id.employee_id.user_id.job_id.id,
                                                                                  'user_id': uid,
                                                                                  'expedient_id':obj.viatico_id.expedient_id.id,
                                                                                  'state': 'done',
                                                                                  }, context=context)
         viatico_obj.write(cr, uid, [obj.viatico_id.id], {'state': 'solicitud3'})
      return {'type':'ir.actions.act_window_close' }
  
   def rechazar_solicitud_viatico(self, cr, uid, ids, context={}):
      log_obj=self.pool.get('viaticos.log')
      usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
      viatico_obj=self.pool.get('viaticos.solicitud')
      for obj in self.browse(cr, uid, ids):
         log_obj.create(cr, uid, {
                                  'name': 'SOLICITUD RECHAZADA: ' + obj.descripcion,
                                  'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                                  'viatico_id': obj.viatico_id.id,
                                  'user_id': uid,
                                  })
         task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                                  'other_action' : str('SOLICITUD RECHAZADA') ,
                                                                                  'description': 'Solicitud Rechazada por: ' + ustr(usuario.name),
                                                                                  #'department': obj.viatico_id.employee_id.department_id.id,
                                                                                  'assigned_user_id' : obj.viatico_id.employee_id.user_id.id,
                                                                                  'job_id': obj.viatico_id.employee_id.user_id.job_id.id,
                                                                                  'user_id': uid,
                                                                                  'expedient_id':obj.viatico_id.expedient_id.id,
                                                                                  'state': 'done',
                                                                                  }, context=context)
         viatico_obj.write(cr, uid, [obj.viatico_id.id], {'state': 'cancel'})
      return {'type':'ir.actions.act_window_close' }
      
   _defaults = {
                'viatico_id': get_viatico,
                'state': get_viatico_state
                }

viatico_devolver_informe()


