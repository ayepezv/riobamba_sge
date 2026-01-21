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
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
from osv import fields, osv
from tools import ustr
import base64


class event_type(osv.osv):
    """ Event Type """
    _name = 'agenda.type'
    _description ="Tipo de Eventos"
    _columns = {
        'name': fields.char('Tipo de Evento', size=64, required=True),
    }

event_type()
class ir_attachment_agenda(osv.osv):
   '''  
   Permite adjuntar archivos a informe
   ''' 
   _inherit = 'ir.attachment'
   _name='ir.attachment.agenda'
   _columns = {
       'document_id' : fields.many2one('agenda.agenda', 'Evento Relacionado'), 
       'is_old': fields.boolean('Confirma creación', size=64),
    }   
   
   _defaults = {       
        'is_old':False,      
    }


   def create(self, cr, uid, vals, context=None):
        """        
        Permite que lso documentos adjuntos se visualicen en SGP
        """    
        res=[]
        inform_id=int(vals['document_id']) 
        if inform_id:
            attach_ids = self.search(cr, uid, [('document_id','=',int(vals['document_id'])),])
            for obj_adjuntos in self.browse(cr, uid, attach_ids, context):
                if ustr(obj_adjuntos.name)==vals['name']:
                    raise osv.except_osv(('Error !'), (ustr('Está intentando cargar un archivo adjunto con una descripción que ya existe.')))
            for obj_inform in self.pool.get('agenda.agenda').browse(cr, uid, [inform_id], context):            
                vals['is_old']=True          
                added_id= self.pool.get('ir.attachment').create(cr, uid,{'name': vals['name'],
                                                                         'parent_id': vals['parent_id'],
                                                                         'datas_fname': vals['datas_fname'],
                                                                         'datas':vals['datas'],                                                        
                                                                         'parent_id': vals['parent_id'],
                                                                         }, context=context)                
                res = super(ir_attachment_agenda, self).create(cr, uid, vals, context=None)     
        return res   
         
ir_attachment_agenda()

class agenda_agenda(osv.Model):
    """Eventos"""
    _name = 'agenda.agenda'
    _description ="Agenda Institucional"
    _order='date_create desc'
        
    def fields_get(self, cr, uid, allfields=None, context=None):
        ret = super(agenda_agenda, self).fields_get(cr, uid,allfields=allfields, context=context)      
        if 'name' in ret:
            if context:                                         
                if 'user_loggin' in context:                
                    if context['user_loggin']==uid:                    
                        ret['name']['readonly'] = False
                        ret['place']['readonly'] = False
                        ret['user_id']['readonly'] = False
                        ret['type']['readonly'] = False
                        ret['date_begin']['readonly'] = False
                        ret['date_end']['readonly'] = False
                        ret['state']['readonly'] = False
                        ret['employee_ids']['readonly'] = False
                        ret['note']['readonly'] = False
                        ret['observaciones']['readonly'] = False
                        ret['documents_ids']['readonly'] = False     
                        ret['country_id']['readonly'] = False
                        ret['state_id']['readonly'] = False
                        ret['canton_id']['readonly'] = False
                        ret['parroquia_id']['readonly'] = False                
                    else:
                        ret['name']['readonly'] = True
                        ret['place']['readonly'] = True
                        ret['user_id']['readonly'] = True
                        ret['type']['readonly'] = True
                        ret['date_begin']['readonly'] = True
                        ret['date_end']['readonly'] = True
                        ret['state']['readonly'] = True
                        ret['employee_ids']['readonly'] = True
                        ret['note']['readonly'] = True
                        ret['observaciones']['readonly'] = True
                        ret['documents_ids']['readonly'] = True
                        ret['country_id']['readonly'] = True
                        ret['state_id']['readonly'] = True
                        ret['canton_id']['readonly'] = True
                        ret['parroquia_id']['readonly'] = True                
        return ret
    
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Error', 'No puede eliminar eventos')
        return False

    def mail_user_confirm(self, cr, uid, ids,  context=None):
        email_true=0
        for line_ids in self.browse(cr, uid, ids, context=context):     
            for employee in line_ids.empleados_ids:
                if employee.email_personal==True:
                    email_true=1
        email = self.browse(cr, uid, ids, context=context)[0].email        
        if email==True or email_true==1:
            email_to_emp = [] 
            for line in self.browse(cr, uid, ids, context=context):                   
                for employee in line.empleados_ids:
                    if employee.work_email:
                        if email==True:
                            email_to_emp+=[employee.work_email]
                    if employee.email_personal==True:
                        if employee.email:                        
                            email_to_emp+=[employee.email]            
            email_to_emp=list(set(email_to_emp))    
            for message in self.browse(cr, uid, ids, context=context):
                attachments = []
                for attach in message.documents_ids:
                    attachments.append((attach.datas_fname, base64.b64decode(attach.datas)))                          
            if email_to_emp:
                subject_emp = 'EVENTO CONFIRMADO: ' +str(line.name)
                body_emp = 'EVENTO:'+ustr(line.name)+"\n"+'FECHA INICIO: '+ustr(line.date_begin)+"\n"+'FECHA FIN: '+ustr(line.date_end)+"\n"+'LUGAR: '+ustr(line.country_id.name)+"-"+ustr(line.state_id.name)+"-"+ustr(line.canton_id.name)+"-"+ustr(line.parroquia_id.name)+"\n"+'DESCRIPCION: '+ustr(line.note)            
                if subject_emp or body_emp:                        
                    mail_ids=self.pool.get('ir.mail_server').search(cr, uid, [], context = context)                
                    for mails_obj in self.pool.get('ir.mail_server').browse(cr, uid, mail_ids, context):
                        if mails_obj.smtp_user:
                            mail_name= mails_obj.smtp_user            
                        if mail_name:                         
                            ir_mail_server = self.pool.get('ir.mail_server')                        
                            msg = ir_mail_server.build_email(email_from=mail_name , email_to=email_to_emp, subject= subject_emp, body=body_emp,attachments=attachments)
                            try:
                                ir_mail_server.send_email(cr, uid, msg, context=context)
                            except:
                                pass
                            
        return True
    
#    def mail_user_cancel(self, cr, uid, ids,  context=None):        
#        email_to_emp = [] 
#        for line in self.browse(cr, uid, ids, context=context):            
#            for employee in line.employee_ids:
#                if employee.department_id.email:
#                    email_to_emp+=employee.department_id.email.split(";") 
#        email_to_emp=list(set(email_to_emp))                             
#        if email_to_emp:
#            subject_emp = 'EVENTO CANCELADO: ' +str(line.name)
#            body_emp = 'EVENTO:'+str(line.name)+"\n"+'FECHA INICIO: '+str(line.date_begin)+"\n"+'FECHA FIN: '+str(line.date_end)+"\n"+'LUGAR: '+str(line.place)+"\n"+'DESCRIPCIÓN: '+str(line.note)            
#            if subject_emp or body_emp:                        
#                mail_ids=self.pool.get('ir.mail_server').search(cr, uid, [], context = context)                
#                for mails_obj in self.pool.get('ir.mail_server').browse(cr, uid, mail_ids, context):
#                    if mails_obj.smtp_user:
#                        mail_name= mails_obj.smtp_user            
#                    if mail_name:                     
#                        ir_mail_server = self.pool.get('ir.mail_server')                        
#                        msg = ir_mail_server.build_email(email_from=mail_name , email_to=email_to_emp, subject= subject_emp, body=body_emp,)                    
#                        try:
#                            ir_mail_server.send_email(cr, uid, msg, context=context)
#                        except:
#                            pass
#                        
#        return True
    
    def mail_user_alert(self, cr, uid, ids, vals, context=None):             
        email_to_emp =[] 
        body_emp = ""    
        pais=provincia=canton=parroquia=lugar=""
              
        for line in self.browse(cr, uid, ids, context=context):            
            for employee in line.employee_ids:
                if employee.department_id.email:
                    email_to_emp+=employee.department_id.email.split(";") 
        email_to_emp=list(set(email_to_emp))                               
        if email_to_emp:            
            subject_emp = 'ACTUALIZACIÓN DEL EVENTO:'+str(line.name)
            if 'name' in vals:
                body_emp+= 'SE HA MODIFICADO EL EVENTO: '+vals['name']+"\n"
            if 'date_begin' in vals:
                body_emp+= 'SE HA MODIFICADO LA FECHA INICIO: '+vals['date_begin']+"\n"
            if 'date_end' in vals:
                body_emp+= 'SE HA MODIFICADO LA FECHA FIN: '+vals['date_end']+"\n"
            if 'type' in vals:
                body_emp+= 'SE HA MODIFICADO EL TIPO DE EVENTO: '+vals['type']+"\n"
            if 'place' in vals or 'country_id' in vals or 'state_id' in vals or 'canton_id' in vals or 'parroquia_id' in vals :
                if 'country_id' in vals:                
                    pais = self.pool.get('res.country').browse(cr, uid, vals['country_id']).name
                if 'state_id' in vals:                    
                    provincia = self.pool.get('res.country.state').browse(cr, uid, vals['state_id']).name
                if 'canton_id' in vals:
                    canton = self.pool.get('res.country.state.canton').browse(cr, uid, vals['canton_id']).name                
                if 'parroquia_id' in vals:
                    parroquia = self.pool.get('res.country.state.parish').browse(cr, uid, vals['parroquia_id']).name                
                body_emp+= 'SE HA MODIFICADO: '+ustr(pais)+" "+ustr(provincia)+" "+ustr(canton)+" "+" "+ustr(parroquia)+"\n"
                if 'place' in vals: 
                    lugar=vals['place']
                    body_emp+="LUGAR: "+ustr(lugar)+"\n"
            if 'note' in vals:
                body_emp+= 'SE HA MODIFICADO LA DESCRIPCIÓN: '+vals['note']+"\n"
            if 'observaciones' in vals:
                body_emp+= 'SE HA MODIFICADO LAS OBSERVACIONES: '+vals['observaciones']+"\n"                                
            if subject_emp or body_emp:                        
                mail_ids=self.pool.get('ir.mail_server').search(cr, uid, [], context = context)                
                for mails_obj in self.pool.get('ir.mail_server').browse(cr, uid, mail_ids, context):
                    if mails_obj.smtp_user:
                        mail_name= mails_obj.smtp_user            
                    if mail_name: 
                        ir_mail_server = self.pool.get('ir.mail_server')                        
                        msg = ir_mail_server.build_email(email_from=mail_name , email_to=email_to_emp, subject= subject_emp, body=body_emp,)
                        try:
                            ir_mail_server.send_email(cr, uid, msg, context=context)
                        except:
                            pass
        return True
    
    
    def do_confirm(self, cr, uid, ids, context):   
        self.mail_user_confirm(cr, uid, ids)
        self._validar_tiempo_actual(cr, uid, ids,context={'val':'True'})        
        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

    def do_cancel(self, cr, uid, ids, context):       
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
    
    def button_confirm(self, cr, uid, ids, context):        
        mensaje=''        
        hr_employee_obj = self.pool.get('hr.employee')
        employee_event_obj = self.pool.get('event.employee')      
        event_emp_obj = self.pool.get('event.employee')
        message_obj=self.pool.get('agenda.confirm')
        message_line_obj=self.pool.get('events.line')
        message_id=message_obj.create(cr, uid, {'name': 'Confirmación Asistencia'})                 
        res = False        
        data_pool = self.pool.get('ir.model.data')
        for event in self.browse(cr, uid, ids, context=context):         
            for line in event.empleados_ids:               
                id_events=employee_event_obj.search(cr,uid,[('employee_id','=',line.employee_id.id)])   
                for events in employee_event_obj.browse(cr,uid,id_events):
                    hr_employee=hr_employee_obj.browse(cr,uid,line.employee_id.id)                    
                    if events.event_id.state in ['confirm']:                           
                        if event.date_begin> events.date_begin and event.date_begin<events.date_end:                                                                                
                            mensaje += ustr(hr_employee.complete_name)+' ya tiene el evento '+ str(events.event_id.name)+'\n'
                            message_line_obj.create(cr, uid, {'employee':ustr(hr_employee.complete_name),
                                                              'name': 'Funcionario con Reunión',  
                                                              'evento': str(events.event_id.name),                                                                                                              
                                                              'message_id':message_id})
        if mensaje!='':   
            return {
                    'name': 'Evento',
                    'context': context,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id': message_id,
                    'res_model': 'agenda.confirm',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'nodestroy': True
            }
        else:          
            self.mail_user_confirm(cr, uid, ids)    
            self._validar_tiempo_actual(cr, uid, ids,context={'val':'True'})        
            return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)

    def write(self, cr, uid, ids, vals, context):           
        ind=0           
        event_obj = self.pool.get('agenda.agenda')
        event_emp_obj = self.pool.get('event.employee')        
        events= event_emp_obj.search(cr,uid, [('event_id', '=', ids)])
        evento= event_obj.browse(cr,uid, ids)[0]                     
        if 'state' in vals:            
            if evento.user_id.id==uid:
                if vals['state']=='confirm':                                                                        
                        if evento.empleados_ids :     
                            vals['create']=False
                            return super(agenda_agenda, self).write(cr, uid, ids, vals, context=context)                                        
                        else:
                            raise osv.except_osv('Error', 'El evento debe tener al menos un asistente')
                if vals['state']=='cancel':
                    if str(datetime.now())< str(evento.date_begin):                                        
                        return super(agenda_agenda, self).write(cr, uid, ids, vals, context=context)
                    else:
                        raise osv.except_osv('Error', 'No puede suspender el evento')
                        
                                                    
            else:                    
                group_id = self.pool.get('ir.model.data').search(cr, uid, [('name','=','group_agenda_manager')])
                if group_id:
                    group_id = self.pool.get('ir.model.data').browse(cr, uid,group_id ) 
                    rel= cr.execute('select * from res_groups_users_rel where gid='+str(group_id[0].res_id))            
                    rel = cr.dictfetchall()      
                    if rel:
                        for rel_line in rel:
                            if rel_line['uid']!=1:                              
                                if rel_line['uid']==uid:                                                    
                                    return super(agenda_agenda, self).write(cr, uid, ids, vals, context=context)
                                else:
                                    raise osv.except_osv(('Error !'), (ustr('Ud. está intentando modificar un evento que no le pertenece o no tiene los permiso para hacerlo')))        
        else:
            if evento.user_id.id==uid:
                if evento.state=='draft':
                    if evento.create==True:                        
                            return super(agenda_agenda, self).write(cr, uid, ids, vals, context=context)
                    else:
                        if evento.empleados_ids :
                                vals['create']=False     
                                return super(agenda_agenda, self).write(cr, uid, ids, vals, context=context)                                        
                        else:
                                raise osv.except_osv('Error', 'El evento debe tener al menos un asistente')
                if evento.state=='confirm':      
                    return super(agenda_agenda, self).write(cr, uid, ids, vals, context=context)                    
            else:                    
                group_id = self.pool.get('ir.model.data').search(cr, uid, [('name','=','group_agenda_manager')])
                if group_id:
                    group_id = self.pool.get('ir.model.data').browse(cr, uid,group_id ) 
                    rel= cr.execute('select * from res_groups_users_rel where gid='+str(group_id[0].res_id))            
                    rel = cr.dictfetchall()      
                    if rel:
                        for rel_line in rel:
                            if rel_line['uid']!=1:                              
                                if rel_line['uid']==uid:                                                    
                                    return super(agenda_agenda, self).write(cr, uid, ids, vals, context=context)
                                else:
                                    raise osv.except_osv(('Error !'), (ustr('Ud. está intentando modificar un evento que no le pertenece o no tiene los permiso para hacerlo')))
                                                      
           
    def create(self, cr, uid, vals, context):                        
        id_reg=super(agenda_agenda, self).create(cr, uid, vals, context)           
        return id_reg
       
    
    def duration_event(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            duration=datetime.strptime(this.date_end, "%Y-%m-%d %H:%M:%S")-datetime.strptime(this.date_begin, "%Y-%m-%d %H:%M:%S")
            duration=str(duration)
        if duration.find("day"):
            res[this.id] = duration.replace("day", "día")
        else:
            if duration.find("days"):            
                res[this.id] = duration.replace("days", "días")
        return res
    
    def _get_default_country(self, cr, uid, context=None):
        id = self.pool.get('res.country').search(cr, uid, [('name','ilike','Ecuador')], context=context)   
        name= self.pool.get('res.country').browse(cr, uid, id, context=context)  
        return name[0].id
    
    def _get_default_state(self, cr, uid, context=None):
        id = self.pool.get('res.country.state').search(cr, uid, [('name','ilike','AZUAY')], context=context)   
        name= self.pool.get('res.country.state').browse(cr, uid, id, context=context)                            
        return name[0].id
    
    
    def onchange_country(self, cr, uid,ids, country_ids, context=None):   
        #on_change: carga el departamento  y el custodio actual del activo
        name= self.pool.get('res.country').browse(cr, uid, country_ids, context=context)        
        res = {'value': {}}
        if name.name!='Ecuador':            
            res['value'] = {'state_id': '',
                        'parroquia_id': '',
                        'id_country':False}
        if name.name=='Ecuador':
            res['value'] = {'id_country':True}            
        return res   
        
    
    def onchange_state_id(self, cr, uid, ids, context=None):   
        #on_change: carga el departamento  y el custodio actual del activo
        res = {'value': {}}
        if country_ids!=64:            
            res['value'] = {'parroquia_id': '',
                        'canton_id':''}      
        return res   
              
        
    def onchange_canton_id(self, cr, uid, ids, context=None):   
        #on_change: carga el departamento  y el custodio actual del activo
        res = {'value': {}}
        res['value'] = {'parroquia_id': '',
                        }      
        return res   
    
    def validar_tiempo(self, cr, uid, ids, fecha1,context=None):
        res_value = {}       
        if fecha1:
            time_fecha1 = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_date1 = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_fecha1 = time_fecha1.replace(second=00)
            res_value['date_begin']=str(time_fecha1)   
        return res_value
        
    def list_empleados(self, cr, uid, ids, context):              
        print "list empleados"
        context = dict(context, active_ids=ids, active_model=self._name)
        event_id = self.pool.get("hr.employee.exec").create(cr, uid, {}, context=context)
        return {
            'name':"Listado Empleados",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'hr.employee.exec',
            'res_id': event_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }    
    
    _columns = {
        'name': fields.char('Nombre Evento', size=64, required=True, ),
        'place': fields.char('Lugar', size=64, ),
        'user_id': fields.many2one('res.users', 'Creado por', readonly=False, required=True),    
        'type': fields.many2one('agenda.type', 'Tipo del Evento', required=True,readonly=False),
        'date_begin': fields.datetime('Fecha Inicio', required=True, help="Fecha Inicio del Evento" ),
        'date_create': fields.datetime('Fecha Creación', required=True, help="Fecha Creación del Evento",readonly=True),
        'date_end': fields.datetime('Fecha Fin', required=True, help="Fecha Fin del Evento"),
        'duration': fields.function(duration_event, string="Duración", type='char',store=True, readonly=False),        
        'state': fields.selection([
            ('draft', 'Creado'),
            ('confirm', 'Confirmado'),
            ('cancel', 'Suspendido')],
            'Estado', readonly=True, required=True),                           
        'note': fields.text('Descripción'),                    
        'observaciones': fields.text('Observaciones'),        
        'documents_ids' : fields.one2many('ir.attachment.agenda','document_id','Adjuntos',
                                                   ondelete='cascade',states={'confirm': [('readonly', True)]}),
        'empleados_ids' : fields.one2many('event.employee','event_id','Asistentes'),
        'country_id' :  fields.many2one('res.country', 'País'),
        'state_id' : fields.many2one('res.country.state','Provincia'),
        'canton_id' : fields.many2one('res.country.state.canton','Cantón'),
        #'city_id' : fields.many2one('res.country.state.city','Ciudad',states={'done': [('readonly', True)],'cancel': [('readonly', True)]}),
        'parroquia_id': fields.many2one('res.country.state.parish', 'Parroquia'),
        'email':fields.boolean('Enviar Email Asistentes'),
        'id_country': fields.boolean('Id Country'),
        'create': fields.boolean('Creado'),
            
    }

    _defaults = {
        'state': 'draft',
        'email': False,
        'user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
        'state_id': _get_default_state,
        'country_id': _get_default_country,
        'id_country': True,
        'create': True,
        'date_create' : time.strftime('%Y-%m-%d %H:%M:%S'),
       
    }

    def _check_closing_date(self, cr, uid, ids, context=None):
        for event in self.browse(cr, uid, ids, context=context):
            if event.date_end < event.date_begin:
                return False
        return True
        
    def _check_asistente(self, cr, uid, ids):        
        for obj in self.browse(cr, uid, ids):
            if obj.create==False: 
                if obj.empleados_ids:
                    result = True
                else:
                    result = False
            else:
                    result = True                
        return result  
    
    def _validar_tiempo_actual(self, cr, uid, ids,context):
        res_value = {}         
        if 'val' in context:            
            for event in self.browse(cr, uid, ids, context=context):                
                if event.date_begin:                        
                    if event.create==True:
                        if event.empleados_ids:
                            time_date1 = datetime.strptime(event.date_begin, "%Y-%m-%d %H:%M:%S")                                    
                            if str(time_date1)<=str(datetime.now()-timedelta(seconds=100)):                    
                                raise osv.except_osv(('Error !'), (ustr('La Fecha no puede ser menor a la actual')))
                            else:
                                return True
        else:
            return True
                    
                
#    def end_date(self, cr, uid, ids, fecha1,context=None):
#        res_value = {}        
#        if fecha1:
#            time_fecha1 = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
#            time_fecha1 = time_fecha1.replace(second=00)
#            time_fecha2 = time_fecha1+timedelta(minutes=15)            
#            res_value['date_begin']=str(time_fecha1)
#            res_value['date_end']=str(time_fecha2)                                  
#        return {'value':res_value}
                
    _constraints = [    
        (_check_closing_date, 'Error ! La Fecha Fin no puede ser menor a la Fecha Inicio', ['date_end']),
       # (_validar_tiempo_actual, 'La Fecha no puede ser menor a la actual', ['Fecha Inicio'])
       ]
    
agenda_agenda()

