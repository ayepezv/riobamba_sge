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

from osv import fields, osv
import time
import datetime
from datetime import date
from osv.orm import browse_record, browse_null
from tools import ustr

class orderCancel(osv.osv_memory):
   _name = 'order.cancel'
   _description = "Anular Solicitud de Movilización"

   _columns = dict(
       # order_id = fields.many2one('movilization.order','Nº Órden'),
        descripcion = fields.text('Descripción de la Anulacíon'),
        )

   def mail_user_cancel(self, cr, uid, ids,  context=None):
        movilization_obj=self.pool.get('movilization.order')
        
        email_to_emp = []    
        group_id = self.pool.get('ir.model.data').search(cr, uid, [('name','=','group_vehicle_manager')])
        group_id = self.pool.get('ir.model.data').browse(cr, uid,group_id )
        rel= cr.execute('select * from res_groups_users_rel where gid='+str(group_id[0].res_id))            
        rel = cr.dictfetchall()      
        if rel:
            for rel_line in rel:                  
                empleado_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',rel_line['uid'])])
                if empleado_id:
                    empleado = self.pool.get('hr.employee').browse(cr, uid, empleado_id[0])
                    if empleado.department_id.email:
                        email_to_emp+=empleado.department_id.email.split(";")  
        for line in movilization_obj.browse(cr, uid, ids, context=context):    
            if line.responsable_id.work_email:
                email_to_emp = [line.responsable_id.work_email]                           
            if line.responsable_id.department_id.email:
                email_to_emp+=line.responsable_id.department_id.email.split(";")  
        email_to_emp=list(set(email_to_emp))
        if email_to_emp:
            subject_emp = 'ÓRDEN DE MOVILIZACIÓN Nº ' +str(line.ref) + ' ANULADA'             
            body_emp  = 'Responsable: '+ustr(line.responsable_id.complete_name)+"\n"
            body_emp += 'Departamento: '+line.department_id.name+"\n"+'Fecha/Hora Salida: '+str(line.movilization_date)+"\n"+'Fecha/Hora Retorno : '+str(line.return_date)+"\n"
            body_emp += 'Detalle de Actividades: '+line.desc+"\n"
            body_emp += 'Recorrido:\n'
            for routes in line.route_ids:                
                body_emp +='Ruta '+str(routes.sec)+':   '+routes.desde+'     '+routes.hasta+"\n"           
            body_emp += 'Detalle Anulacion: '+str(line.observaciones_anulado)
            if subject_emp or body_emp:                        
                mail_ids=self.pool.get('ir.mail_server').search(cr, uid, [], context = context)                
                for mails_obj in self.pool.get('ir.mail_server').browse(cr, uid, mail_ids, context):
                    if mails_obj.smtp_user:
                        mail_name= mails_obj.smtp_user            
                    if mail_name: 
                        ir_mail_server = self.pool.get('ir.mail_server')                        
                        msg = ir_mail_server.build_email(email_from=mail_name , email_to=email_to_emp, subject= subject_emp, body=body_emp,)                        
                        ir_mail_server.send_email(cr, uid, msg, context=context)
        return True
   
   def order_cancel(self, cr, uid, ids, context):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')       
        active_id = context['active_id']
        order_obj = self.pool.get('movilization.order')                
        order = order_obj.browse(cr, uid, active_id)        
        for this in self.browse(cr, uid, ids):
            order_obj.write(cr, uid, order.id,{'observaciones_anulado' : this.descripcion,'state' : 'anulado'},context,)
            #self.mail_user_cancel(cr, uid, [order.id])              
        result = mod_obj.get_object_reference(cr, uid, 'gt_vehicle', context['view_id'])
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context={})[0]            
        return result
    


orderCancel()


