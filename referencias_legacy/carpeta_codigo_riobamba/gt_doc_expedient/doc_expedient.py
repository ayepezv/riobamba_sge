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

from osv import osv, fields
from lxml import etree
from time import strftime
import time
from datetime import datetime, date
import netsvc
from tools.translate import _
from tools import ustr


def _links_get(self, cr, uid, context=None):
    obj = self.pool.get('res.request.link')
    ids = obj.search(cr, uid, [], context=context)
    res = obj.read(cr, uid, ids, ['object', 'name'], context)
    return [(r['object'], r['name']) for r in res]

class doc_expedient_expedient(osv.osv):
    _name = "doc_expedient.expedient"
    
    def action_draft_created(self, cr, uid, ids, context=None):
    #Cambia el estado de un trámite de “Borrador” a “Activo”
        obj_sequence = self.pool.get('ir.sequence')
        obj_expedient_task = self.pool.get('doc_expedient.task')
        for expedient in self.browse(cr, uid, ids):
            if not(expedient.tasks):
                raise osv.except_osv('Mensaje de Advertencia !', 'El Tramite debe iniciar con una o mas Tareas')
            #self.create_directory(cr, uid, ids, context)
            #self.action_send_mail(cr, uid, ids, context)
            self.send_tasks(cr, uid, ids, context)
            self.create_task_user(cr, uid, ids, context)
            self.show_view_expedient_tree(cr, uid, ids, context)
            if expedient.chk_removed:
                self.write(cr, uid, ids, {'state': 'created'})
            else:
#                self.write(cr, uid, ids, {'state': 'created', 'creation_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                self.write(cr, uid, ids, {'state': 'created'})
        return True
        
    
    def create_task_user(self, cr, uid, ids, context=None):
    #Crear la tarea con la que inicia le Trámite.
        obj_employee = self.pool.get('hr.employee')
        obj_task = self.pool.get('doc_expedient.task')
        for expedient in self.browse(cr, uid, ids):
            user_id = expedient.user_id.id
            employee_id = expedient.user_id.employee_id.id#obj_employee.search(cr, uid, [('user_id','=',user_id)])
            if not employee_id:
                raise osv.except_osv('Mensaje de Advertencia !', 'Empleado sin cuenta de usuario del sistema')
            employee = obj_employee.browse(cr, uid, employee_id)
            if not (employee.department_id.id or employee.job_id.id):
                raise osv.except_osv('Mensaje de Advertencia !', 'Se requiere que el usuario actual este ligado a un Cargo y Departamento...')
            obj_task.create(cr, uid,{'other_action_chk': True,
                                'desc_task': 'Tarea Inicio del Trámite',
                                'other_action': 'Tarea Inicio del Trámite',
                                #'department': employee.department_id.id,
                                'user_id' : user_id,
                                #'job_id': employee.job_id.id,
                                #'employee_id': employee_id[0],
                                'assigned_user_id' : user_id,
                                'priority': 'normal',
                                'expedient_id':expedient.id,
                                'description': False,
                                'state': 'done',
                                'task_sequence': 1,
                                'included': True,
                                }, context=context)
        return True
        
        
    def action_created_cancelled(self, cr, uid, ids):
    #Cambia el estado de un trámite de “Activo” a “Anulado”
        self.check_state_envios(cr, uid, ids)
        self.cancel_task_expedient(cr, uid, ids)
        self.write(cr, uid, ids, {'state': 'cancelled'})
        
        
    def action_draft_cancelled(self, cr, uid, ids):
    #Cambia el estado de un trámite de “Borrador” a “Anulado”
        self.write(cr, uid, ids, {'state': 'cancelled','directory_id':False})
        
                
    def action_removed_draft(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state':'draft'})
        
            
    def removed_expedient(self, cr, uid, ids, context):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        obj_task = self.pool.get('doc_expedient.task')
        obj_ir_attachment = self.pool.get('ir.attachment')
        for obj in self.browse(cr, uid, ids, context):
            expedient_id = obj.id
            if obj.state != 'cancelled' or len(obj.tasks) > 1:
                    raise osv.except_osv('Mensaje de Advertencia !', 'El tramite no debe contener tareas para ser descartado')    
            if obj.references:
                raise osv.except_osv('Mensaje de Advertencia !', 'El tramite no debe tener referencias para ser descartado')
            task_ids = obj_task.search(cr, uid,[('expedient_id','=',obj.id)])
            if task_ids:
                for task_id in task_ids:
                    task = obj_task.browse(cr, uid, task_id)
                    if task.documents:
                        for doc in task.documents:
                            obj_ir_attachment.unlink(cr,uid,[doc.id])
                    obj_task.unlink(cr,uid,[task.id])
                    
            if obj.ubication == 'external':
                self.write(cr, uid, [obj.id], {'canton':False,'parroquia':False,'locality':'',
                                               'institution':False,'name_person':False,'direccion':'',
                                               'number_office':'','telefono':'','date_entry':False})
            return self.write(cr, uid, [obj.id], {'state':'removed','chk_removed':True})
        
        #result = mod_obj.get_object_reference(cr, uid, 'gt_doc_expedient', 'action_doc_expedient_form_sent1')
        #id = result and result[1] or False
        #result = act_obj.read(cr, uid, [id], context=context)[0]
        #domain = result['domain']
        #dd = eval(domain)
        #dd.append(('base_state','=', 'sent'))
        #domain = str(dd)
        #result['domain'] = dd
        #return result

                    
        
    def send_tasks(self, cr, uid, ids, context=None):
    #Cambia de estado de “Borrador” a “Pendiente” las tareas iniciales de un tramite, 
    #es decir se envían las tarase a sus destinatarios.
        for expedient in self.browse(cr, uid, ids):
            for task in expedient.tasks:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'doc_expedient.task', task.id, 'wkf_draft_progress', cr)
        return True
    
    
    def cancel_task_expedient(self, cr, uid, ids):
    #Anula todas las tareas de un trámite, luego que se ha anulado el mismo.
        obj_task = self.pool.get('doc_expedient.task')
        for expedient in self.browse(cr, uid, ids):
            tasks = obj_task.search(cr, uid, [('expedient_id','=',expedient.id)])
            if tasks:
                for task_id in tasks:
                    obj_task.write(cr, uid, task_id, {'state': 'cancelled'})
        return True
            
            
    def create_directory(self, cr, uid, ids, context=None):
    #Crear un directorio cada vez que se crea un trámite, el directorio se crea bajo 
    #el directorio principal “Trámites” y con el nombre del código del trámite.
        obj_document_directory = self.pool.get('document.directory')
        obj_ir_attachment = self.pool.get('ir.attachment')
        for expedient  in self.browse(cr, uid, ids, context):
            dir_exp_parent_id = obj_document_directory.search(cr, uid, [('name','=',ustr('Tramites'))], limit=1)
            if expedient.chk_removed:
                pid = expedient.directory_id.id
            
            if dir_exp_parent_id and not expedient.chk_removed:
                #id_exp_parent = obj_document_directory.read(cr, uid, ids_dir_cont, ['id'])
                pid = obj_document_directory.create(cr, uid, {'name' : ustr('Tramite - ' + str(expedient.code)),
                                                              'parent_id' : dir_exp_parent_id[0],
                                                              'user_id':None,
                                                              'storage_id':2})
                self.write(cr, uid, expedient.id, {'directory_id': pid})
            if expedient.documents:
                for doc in expedient.documents:
                    obj_ir_attachment.write(cr, uid, doc.id, {'parent_id': pid})
        return True
       
        
    def check_state_envios(self, cr, uid, ids):
    #Verifica el estado del las tareas previo a la anulación de un trámite, 
    #No se puede anular un trámite si existen tareas en estado “Realizado”
        obj_doc_expedient_task = self.pool.get('doc_expedient.task')
        for expedient in self.browse(cr, uid, ids):
            tasks = obj_doc_expedient_task.search(cr, uid, [('expedient_id','=',expedient.id)])
            if tasks:
                for task_id in tasks:
                    task = obj_doc_expedient_task.read(cr, uid, task_id, ['state','task_sequence'])
                    if task['state'] == 'done' and task['task_sequence'] != 1:
                        raise osv.except_osv('Mensaje de Advertencia !', 'Existen tareas del tramite que deben ser anuladas')            
        return True
            
            
    def action_send_mail(self, cr, uid, ids, context=None):
        template_obj = self.pool.get('email.template')
        model_obj = self.pool.get('ir.model')
        for expedient in self.browse(cr, uid, ids, context):
            model = model_obj.search(cr, uid, [('model','=','doc_expedient.expedient')],limit=1)
            for mod in model:
               modelo = model_obj.browse(cr, uid, mod)
               template_ids = template_obj.search(cr, uid, [('model_id','=',mod)],limit=1)
               for template_id in template_ids:
                  template_obj.send_mail(cr, uid,
                                         template_id,
                                         expedient.id, context=context)
        return True
    
    
    def __get_def_directory(self, cr, uid, context=None):
    # Asigna un directorio por defecto a un trámite en estado "Borrador", el
    # es cambiado cuando se inicia el trámite
        dirobj = self.pool.get('document.directory')
        return dirobj._get_root_directory(cr, uid, context)
    
    
    def _get_document_task(self, cr, uid, ids):
        result = {}
        for task in self.pool.get('doc_expedient.task').browse(cr, uid, ids, context=context):
            result[task.expedient_id.id] = True
        return result.keys()     
    STORE_VAR = {'doc_expedient.expedient': (lambda self, cr, uid, ids, c={}: ids, ['tasks'], 10),
                  'doc_expendient.task': (_get_document_task, ['state'], 10)}
    
        
    def write(self, cr, uid, ids, vals, context=None):
    # Redefinición del metodo para controlar la eliminación o agregación de referencias entre trámites
        #print vals
        try:
            vec = []
            for tramite in self.browse(cr, uid, ids):
                for referencia in tramite.references:
                    vec.append(referencia.id)    
            ref_ids = vals['references'][0][2]
            ids_borrar = set(vec)-set(ref_ids)
            for borrar in ids_borrar:
                cr.execute("delete from expedient_expedient_rel where expedient_id = %s and expediente_id = %s",(borrar,ids[0]))
            super(doc_expedient_expedient,self).write(cr, uid, ref_ids, {'references': [(6,0,ids)]})
        except:
            pass
        devolver = super(doc_expedient_expedient,self).write(cr, uid, ids, vals, context)
        self.calcular_estados(cr, uid, ids, context)
        return devolver
    
    def calcular_estados(self, cr, uid, ids, context=None):
        #obj_expedient = self.pool.get('doc_expedient.expedient')
        ids_expedient = []
        try:
            largo = len(ids)
            ids_expedient = ids
        except:
            ids_expedient = [ids]
        for expediente in self.browse(cr, uid, ids_expedient, context):
            #expediente = obj_expedient.browse(cr, uid, tarea_actual.expedient_id.id)
            state_draft = []
            state_open = []
            state_sent = []
            state_cancelled = []
            state_removed = []
            sent = False
            cancel = False
            draft = False
            if expediente.state=='draft':
                state_draft.append(expediente.user_id.id)
            if expediente.state=='cancelled':
                state_cancelled.append(expediente.user_id.id)
            for task in expediente.tasks:
                if task.state == 'progress':
                    if task.user_id.id not in state_sent: state_sent.append(task.user_id.id)
                    if task.assigned_user_id.id not in state_open: state_open.append(task.assigned_user_id.id)
                if task.state == 'done' and expediente.state != 'removed':
                    if task.assigned_user_id.id not in state_sent: state_sent.append(task.assigned_user_id.id)
                    if task.user_id.id not in state_sent: state_sent.append(task.user_id.id)
                #if task.state == 'cancelled' and task.included and expediente.state != 'cancelled':
                #    if task.user_id.id not in state_cancelled: state_cancelled.append(task.user_id.id)
                #    if task.assigned_user_id.id not in state_cancelled: state_cancelled.append(task.assigned_user_id.id)
                if task.state == 'draft' and expediente.state=='draft':
                    if task.user_id.id not in state_draft: state_draft.append(task.user_id.id)
            #respaldo_open = state_open
            respaldo_sent = state_sent
            state_sent = []
            for tarea_sent in respaldo_sent:
                if tarea_sent not in state_open:
                    state_sent.append(tarea_sent)
            #respaldo_cancelled = state_cancelled
            #state_cancelled = []
            #for tarea_cancelled in respaldo_cancelled:
            #    if (tarea_cancelled not in state_sent) and (tarea_cancelled not in state_open):
            #        state_cancelled.append(tarea_cancelled)
            string_draft = ""
            string_open = ""
            string_sent = ""
            string_cancelled = ""
            string_removed = ""
            for item in state_draft:
                string_draft += "-" + str(item) + "-"
            for item in state_open:
                string_open += "-" + str(item) + "-"
            for item in state_sent:
                string_sent += "-" + str(item) + "-"
            for item in state_cancelled:
                string_cancelled += "-" + str(item) + "-"
            for item in state_removed:
                string_removed += "-" + str(item) + "-"
            super(doc_expedient_expedient,self).write(cr, uid, expediente.id, {'state_draft': string_draft,
                                                                     'state_open': string_open,
                                                                     'state_sent': string_sent,
                                                                     'state_cancelled': string_cancelled,
                                                                     'state_removed': string_removed}, context)
        return True
            
        
    def create(self, cr, uid, vals, context=None):
    # Redefinición del metodo para agregar un código cuando se crea un trámite, ademas
    # crea las referencias entre trámites que se definieron previo a la creación de un trámite
        if not vals.has_key('code'):
            obj_sequence = self.pool.get('ir.sequence')
            ubicacion = vals['ubication']
            if ubicacion == 'internal':
                code = obj_sequence.get(cr, uid, 'doc.expedient.type.in')
            if ubicacion == 'external':
                code = obj_sequence.get(cr, uid, 'doc.expedient.type.ext')
            vals.update({'code': code})
        vals.update({'code_assigned':True})
        #import pdb
        obj_document_directory = self.pool.get('document.directory')
        obj_ir_attachment = self.pool.get('ir.attachment')
        dir_exp_parent_id = obj_document_directory.search(cr, uid, [('name','=','Tramites')], limit=1)
        pid = obj_document_directory.create(cr, uid, {'name' : 'Tramite - ' + str(vals['code']),
                                                      'parent_id' : dir_exp_parent_id[0],
                                                      'user_id': None,
                                                      'storage_id': 2})
        vals.update({'directory_id':pid})
        #if vals.has_key('tasks'):
        #    for tarea in vals['tasks']:
        #        pdb.set_trace()
        #        auxiliar = tarea[2]
        #        if auxiliar.has_key('documents'):
        #            for documento in tarea[2]['documents']:
        #                documento[2].update({'parent_id':pid})
        #pdb.set_trace()
        res_id = super(doc_expedient_expedient, self).create(cr, uid, vals, context=context)
        self.calcular_estados(cr, uid, [res_id], context)
        try:
            ref_ids = vals['references'][0][2]
            for ref_id in ref_ids:
                cr.execute('insert into expedient_expedient_rel (expedient_id,expediente_id) values(%s,%s)',(ref_id,res_id))
        except:
            pass
        return res_id
    
    def _check_expedient_ref(self, cr, uid, ids, context=None):
    # Verificar este método
        if context == None:
            context = {}
        try:
            ref_ids = vals['references'][0][2]
            for ref_id in ref_ids:
                cr.execute('insert into expedient_expedient_rel (expedient_id,expediente_id) values(%s,%s)',(ref_id,res_id))
        except:
            pass
        return res_id


    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        #import pdb
        #pdb.set_trace()
        if not limit:
            limit = 80
        else:
            if limit>80:
                limit = 80
        return super(doc_expedient_expedient, self).search(cr, uid, args, offset=offset, limit=80, order=order, context=context, count=count)
        

    def search_respaldo(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        # Redefinición del método search, para obtener el estado de un trámite segun el usuario actual
        # Crea una lista de trámites de acuerdo a lo solicitado en la búsqueda
        t_open = []
        t_sent = []
        t_draft = []
        t_cancelled = []
        open = False
        sent = False
        draft = False
        cancelled = False
        users = False
        search_defaul = False
        if args:
            for item in args:          
                if item[0] == 'base_state' and item[2] == 'open':
                    open = True
                elif item[0] == 'base_state' and item[2] == 'sent':
                    sent = True
                elif item[0] == 'base_state' and item[2] == 'draft':
                    draft = True
                elif item[0] == 'base_state' and item[2] == 'cancelled':
                    cancelled = True
            if (open or sent or draft or cancelled):
                args = []
        ids = super(doc_expedient_expedient, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
        if not isinstance(ids, list):
            ids = [ids]
        #self.compute_state(cr, uid, ids, context)
        for obj in self.browse(cr, uid, ids, context):
            #print obj.task_state, obj.base_state
            if obj.task_state == 'open':
                t_open.append(obj.id)
            elif obj.task_state == 'sent':
                t_sent.append(obj.id)
            elif obj.task_state == 'draft':
                t_draft.append(obj.id)
            elif obj.task_state == 'cancelled':
                t_cancelled.append(obj.id)
            self.write(cr, uid, obj.id, {'base_state': obj.task_state,'ref_db': obj.ref_chk})
        if open:
            ids = t_open
        elif sent:
            ids = t_sent
        elif draft:
            ids = t_draft
        elif cancelled:
            ids = t_cancelled
        return ids
    
    
    def compute_state(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {})
        
        
    def name_get(self, cr, uid, ids, context=None):
    # Redefinición del método para concatenar un trámite con su código respectivo.
        task_obj = self.pool.get('doc_expedient.task')
        if context is None:
            context = {}
        res = []
        task_id = context.get('task_id',False)
        if task_id:
            for t in task_obj.browse(cr, uid, [task_id], context):
                #text = t.expedient_id.code + ' - ' + t.expedient_id.name
                text = t.expedient_id.code
                res.append((t.expedient_id.id, text))
        else:
            for t in self.browse(cr, uid, ids, context):    
                #text = t.code + ' - ' + t.name
                text = t.code
                res.append((t.id, text))
        return res
    
    
    def name_search(self, cr, uid, name='', args=[], operator='ilike', context={}, limit=80):
    # Redefinición del método, Cuado se redefine el metodo name_get es necesario redefinir el
    # metodo name_serch para que las busquedas lo haga por el campo definido en el metodo name_get
        try:
            ids = []
            ids_name = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
            ids = list(set(ids + ids_name))
            if name:
                ids_code = self.search(cr, uid, [('code', operator, name)] + args, limit=limit, context=context)
                ids = list(set(ids + ids_code))
            return self.name_get(cr, uid, ids, context=context)
        except:
            ids = []
            return self.name_get(cr, uid, ids, context=context)
    
        
    def show_view_expedient_tree(self, cr, uid, ids, context):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        for obj in self.browse(cr, uid, ids, context):
            result = mod_obj.get_object_reference(cr, uid, 'gt_doc_expedient', 'action_doc_expedient_form_open')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
        return result

  
        
    def search_task_expedient(self, cr, uid, ids, context):
    # Este metodo actua sobre el domain de la accion "action_doc_expedient_task_form1", y le agrega
    # un criterio mas de busquema a la expresion como es: ('expedient_id','=',obj.id)
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        for obj in self.browse(cr, uid, ids, context):
            result = mod_obj.get_object_reference(cr, uid, 'gt_doc_expedient', 'action_doc_expedient_task_form1')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['context']="{'search_op':'complex', 'search_default_expendient_id':%s}"%obj.id
            domain = result['domain']
            dd = eval(domain)
            dd.append(('expedient_id','=', obj.id))
            domain = str(dd)
            result['domain'] = dd
        return result
    
    
    def search_expedient_ref(self, cr, uid, ids, context):
    # Verificar la existencia de este metodo
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        for obj in self.browse(cr, uid, ids, context):
            result = mod_obj.get_object_reference(cr, uid, 'gt_doc_expedient', 'action_doc_expedient_form_ref')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
        return result
        
    
    def unlink(self, cr, uid, ids, *args, **kwargs):
        for exp in self.browse(cr, uid, ids):
            raise osv.except_osv(_('Operación no Permitida  !'), _('No se puede eliminar un tramite.'))
        return super(doc_expedient_expedient, self).unlink(cr, uid, ids, *args, **kwargs)
    

    def get_task_state(self, cr, uid, ids, fields, args, context=None):
    # Metodo que devuelve el estado de un tramite, segun el usuario actual del sistema
    # Condidera todas las tareas del usuario en un tramite y devuelve un mensaje con respecto
    # al estado de sus tareas  
        res = {}
        task_obj = self.pool.get('doc_expedient.task')
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = ''
            #task_ids = task_obj.search(cr, uid, [('state','in',['progress','done','cancelled']),('assigned_user_id.id','=',uid),('expedient_id','=',obj.id)])    
            task_ids = task_obj.search(cr, uid, [('expedient_id','=',obj.id),'|',('assigned_user_id.id','=',uid),('user_id.id','=',uid)])
            if task_ids:
                sent = False
                cancel = False
                draft = False
                for task in task_obj.browse(cr, uid, task_ids, context=context):
                    if task.state == 'progress' and task.assigned_user_id.id == uid:
                        res[obj.id] = 'open'
                        break
                    if (task.state == 'done' and task.assigned_user_id.id == uid and obj.state != 'removed'):
                        res[obj.id] = 'sent'
                        sent = True 
                    if (task.state == 'done' and task.user_id.id == uid and obj.state != 'removed'):
                        res[obj.id] = 'sent'
                        sent = True 
                    if task.state == 'progress' and task.user_id.id == uid:
                        res[obj.id] = 'sent'
                        sent = True
                    if task.user_id.id == uid and task.state == 'cancelled' and task.included and obj.state != 'cancelled':
                        res[obj.id] = 'sent'
                        sent = True
                    if task.state == 'draft' and task.user_id.id == uid:
                        if not sent:
                            res[obj.id] = 'draft'
                            draft = True
                    if task.assigned_user_id.id == uid and task.state == 'cancelled' and task.included:
                        if not sent and not draft:
                            res[obj.id] = 'cancelled'
                            cancel = True
                    if task.user_id.id == uid and task.state == 'cancelled' and not task.included:
                        if not sent and not draft:
                            res[obj.id] = 'cancelled'
                            cancel = True    
                    #sql = "UPDATE doc_expedient_expedient set base_state='%s' WHERE id=%s" % (res[obj.id], obj.id)
                    #cr.execute(sql)
        return res
    
    def _is_user(self, cr, uid, ids, field_name, arg, context=None):
    #Método que devuelve “True” si el usuario actual es el mismo que el que creo el trámite, caso
    #contrario devolverá “False”
        res = {}
        for exp in self.browse(cr, uid, ids, context=context):
            if exp.user_id.id == uid:
                res[exp.id] = True
            else:
                res[exp.id] = False
        return res
    
    
    def _is_ref(self, cr, uid, ids, field_name, arg, context=None):
    #Método que devuelve True o False a un tramite cuando se lo quiere referenciar. 
    #Este valor dependerá si el usuario tiene tareas asignadas en el tramite y no haya sido desvinculado.
        res = {}
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        task_obj = self.pool.get('doc_expedient.task')
        
        for exp in self.browse(cr, uid, ids, context=context):
            task_ids = task_obj.search(cr, uid, [('state','in',['progress','done','cancelled']),
                                                 ('assigned_user_id.id','=',uid),('expedient_id','=',exp.id),
                                                 ('included','=',True)])
            if task_ids:
                res[exp.id] = True
            else:
                res[exp.id] = False
        return res
    
    
    def onchange_parish(self, cr, uid, ids, parroquia, canton, context=None):
    # Método que devuelve las parroquias de acuerdo al cantón seleccionado por el usuario
        if parroquia:
            obj_parish = self.pool.get('res.country.state.parish')
            parroquia = obj_parish.browse(cr, uid, parroquia)
            if not parroquia.canton_id.id == canton:
                return {'value':{'parroquia':''}}
        return {}
    
    def onchange_canton(self, cr, uid, ids, parroquia, context=None):
    # Método que devuelve el cantón de acuerdo a la parroquia seleccionada por el usuario
        if not parroquia:
            return {}
        obj_parish = self.pool.get('res.country.state.parish')
        parroquia = obj_parish.browse(cr, uid, parroquia)
        return {'value':{'canton':parroquia.canton_id.id}}
    
    _order = "creation_date desc"
    _columns = dict(
        owner = fields.function(_is_user, store=False, string='Propietario', type='boolean', help="Indica que el usuario actual del sistema sea el mismo que el que creo el trámite"),
        code_assigned = fields.boolean('Código Asignado', help="Indica que se ha asignado un codigo a un tramite"),
        ref_chk = fields.function(_is_ref, store=False, string='Conocido', type='boolean', help="Indica que el usuario participa en el Trámite"),
        ref_db = fields.boolean('Participa en el Trámite', help="Indica que el usuario participa en el Trámite"),
        chk_removed = fields.boolean('Trámite Descartado', help="Indica que un trámite ha sido descartado y puede ser reutilizado"),
        name = fields.char('Asunto', size=256, required=True),
        code = fields.char('Núm.Trámite', size=64),
        ubication = fields.selection([('internal', 'Interno'),('external', 'Externo')],
            'Tipo Origen', readonly=False, required=True,
            help='El tipo de trámite con respecto a su origen (Interno / Externo)'
        ),
        # De aqui cambia lo de abajo y el flujo nada mas.    
        user_id = fields.many2one('res.users', 'Creado por', select=1, required=True),
        user_name = fields.related('user_id', 'name', type='char', size=128, string='Creado por', store=True),
        state = fields.selection([('draft', 'Borrador'),
                                  ('created', 'Activo'),
                                  ('cancelled', 'Anulado'), 
                                  ('removed', 'Descartado')], 'Estado del Trámite', 
                                  required=True,),
        creation_date = fields.datetime('Fecha creación', select=True),
        resumen = fields.text('Resumen', required=True),
        tasks = fields.one2many('doc_expedient.task', 'expedient_id', "Tareas del Trámite"),
        justification = fields.char('Justificativo de Anulación', size=128, readonly="True"),
        institution = fields.char('Institución', size=128),
        name_person = fields.char('Nombre del Solicitante', size=128),
        number_office = fields.char('Núm.Oficio', size=64),
        date_entry = fields.datetime('Fecha de Ingreso'),
        canton = fields.many2one('res.country.state.canton', 'Cantón'),
        parroquia = fields.many2one('res.country.state.parish', 'Parroquia'),
        locality = fields.char('Localidad', size=64),
        direccion = fields.char('Dirección', size=64),
        telefono = fields.char('Teléfono', size=64),
        references = fields.many2many('doc_expedient.expedient', 'expedient_expedient_rel', 'expedient_id', 'expediente_id', 'Referencia con Trámites'),
        
        documents = fields.related('directory_id', 'file_ids', type='one2many', relation='ir.attachment', string='Documentos', readonly=True),
        directory_id = fields.many2one('document.directory', 'Directorio', readonly=True),
        task_state = fields.function(get_task_state, method=True, store=False, string='Mensaje de Tarea', 
                                type='selection', selection=[('draft','Borrador'),
                                                             ('open','Pendiente'),
                                                             ('sent','Realizado'),
                                                             ('cancelled','Anulado'),
                                                             ('removed','Descartado')],
                                help="Campo funcion que que obtiene el estado del tramite en funcion de sus tareas y usuario actual, NO se almacena en la base de datos"),
        base_state = fields.function(get_task_state, method=True, store=False, string='Mensaje de Tarea', 
                                type='selection', selection=[('draft','Borrador'),
                                                             ('open','Pendiente'),
                                                             ('sent','Realizado'),
                                                             ('cancelled','Anulado'),
                                                             ('removed','Descartado')],
                                help="Campo funcion que que obtiene el estado del tramite en funcion de sus tareas y usuario actual, NO se almacena en la base de datos"),
        #base_state = fields.selection([('draft','Borrador'),
        #                               ('open','Pendiente'),
        #                               ('sent', 'Realizado'),
        #                               ('cancelled', 'Anulado'),
        #                               ('removed','Descartado')], string="Mensaje de Tarea", readonly=False, store=False,
        #                        help="Campo funcion que que obtiene el estado del tramite en funcion de sus tareas y usuario actual, SI se almacena en la base de datos"),
        state_draft = fields.text('Usuarios con estado Borrador'),
        state_open = fields.text('Usuarios con estado Pendiente'),
        state_sent = fields.text('Usuarios con estado Realizado'),
        state_cancelled = fields.text('Usuarios con estado Anulado'),
        state_removed = fields.text('Usuarios con estado Descartado'),
    )
    _defaults = dict(
        state = 'draft',             
        user_id = lambda self, cr, uid, ctx:uid,
        creation_date = lambda *a: strftime('%Y-%m-%d %H:%M:%S'),
        directory_id = __get_def_directory,
        #base_state = 'draft',
        ubication = 'internal',
        owner = True,
        code_assigned = False,
        chk_removed = False,
    )
    #_order = "creation_date asc"
    
    _sql_constraints = []
doc_expedient_expedient()


class doc_expedient_action(osv.osv):
    _name = 'doc_expedient.action'
    _columns = dict(
        name = fields.char('Descripción', size=64, required=True),
        desc = fields.text('Descripción', size=64),
        type = fields.selection([('action', 'Acción'),('of_know', 'Conocimiento')],
            'Tipo de Acción', required=True),
    )
    
    def iniciar_tramites(self, cr, uid, ids, context={}):
        obj_tramites = self.pool.get('doc_expedient.expedient')
        ids_tramites = obj_tramites.search(cr, uid, [('state','=','draft')], context=context)
        obj_tramites.action_draft_created(cr, uid, ids_tramites, context=context)
    
    def calcular_estados(self, cr, uid, ids, context={}):
        obj_tramites = self.pool.get('doc_expedient.expedient')
        ids_tramites = obj_tramites.search(cr, uid, [], context=context)
        obj_tramites.calcular_estados(cr, uid, ids_tramites, context=context)
        
    def crear_directorios(self, cr, uid, ids, context={}):
        obj_tramites = self.pool.get('doc_expedient.expedient')
        ids_tramites = obj_tramites.search(cr, uid, [], context=context)
        obj_tramites.create_directory(cr, uid, ids_tramites, context=context)

    def renombrar_directorios(self, cr, uid, ids, context={}):
        obj_document_directory = self.pool.get('document.directory')
        obj_ir_attachment = self.pool.get('ir.attachment')
        directory_ids = obj_document_directory.search(cr, uid, [('name','ilike','Trámite')])
        for directorio in obj_document_directory.browse(cr, uid, directory_ids, context):
            name = "Tramite" + directorio.name[8:]
            obj_document_directory.browse(cr, uid, directorio.id, {'name':name})
        return True

    def calcular_secuencias(self, cr, uid, ids, context={}):
        obj_tramites = self.pool.get('doc_expedient.expedient')
        obj_tareas = self.pool.get('doc_expedient.task')
        ids_tramites = obj_tramites.search(cr, uid, [], context=context)
        for tramite in obj_tramites.browse(cr, uid, ids_tramites, context=context):
            ids_tareas = obj_tareas.search(cr, uid, [('expedient_id','=',tramite.id)], order='date_task', context=context)
            secuencial=0
            for tarea in obj_tareas.browse(cr, uid, ids_tareas, context=context):
                secuencial = secuencial + 1
                obj_tareas.write(cr, uid, tarea.id, {'task_sequence':secuencial,'directory_id':tramite.directory_id.id}, context=context)
        
doc_expedient_action()


class doc_expedient_task(osv.osv):
    _name = "doc_expedient.task"
    
    def action_draft_progress(self, cr, uid, ids, context=None):
        #self.merge_directory(cr, uid, ids, context)
        self.do_send(cr, uid, ids, context)
        for tasks in self.browse(cr, uid, ids, context):
            if (tasks.members):
                self.create_task_cc(cr, uid, ids, context=None)
        self.responded_task(cr, uid, ids, context=None)
        self.write(cr, uid, ids, {'state': 'progress','date_task':time.strftime('%Y-%m-%d %H:%M:%S')})
        return {'type':'ir.actions.act_window_close'}
    
        
    def responded_task(self, cr, uid, ids, context=None):
        for task in self.browse(cr, uid, ids):
            parent_task_id = task.parent_task
            if parent_task_id != 0:
                pt = self.browse(cr, uid, parent_task_id)
                if pt.state == 'progress':
                    self.write(cr, uid, parent_task_id, {'state':'done','responded':True})
        return {'type':'ir.actions.act_window_close'}
        
        
    def action_progress_done(self, cr, uid, ids, context=None):
        self.control_action_task(cr, uid, ids, context)
        #self.write(cr, uid, ids, {'state': 'done', 'included':True})
    
    def task_progress_done(self, cr, uid, ids, context=None):
        obj_action = self.pool.get('doc_expedient.action')
        for task in self.browse(cr, uid, ids):
            if (task.assigned_user_id.id != uid):
                raise osv.except_osv('Mensaje de Error !', 'No esta autorizado para realizar esta accion...')
            if (task.state != 'progress'):
                raise osv.except_osv('Mensaje de Error !', 'No puede realizar esta accion, La tarea ha sido anulada...')
            #verificar accion de la tarea
            if task.action_id.id:
                action_task = obj_action.browse(cr, uid, task.action_id.id)
                if action_task.type == 'of_know':
                    self.write(cr, uid, ids, {'state': 'done'})
            else:
                self.write(cr, uid, ids, {'state': 'done'})
            self.write(cr, uid, [task.id], {'included':True})
        return True
    
    def responder_tarea(self, cr, uid, ids, context):
    # Este metodo actua sobre el domain de la accion "action_doc_expedient_task_form1", y le agrega
    # un criterio mas de busquema a la expresion como es: ('expedient_id','=',obj.id)
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        for obj in self.browse(cr, uid, ids, context):
            result = mod_obj.get_object_reference(cr, uid, 'gt_doc_expedient', 'action_doc_expedient_task_respond')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['context']="{'task_id':%s}"%obj.id
            #result['type']="form"
            #result['view_mode']="form"
            #result['target']="current"

        return result

        
    def control_action_task(self, cr, uid, ids, context=None):
        for task in self.browse(cr, uid, ids, context):
            if (task.assigned_user_id.id != uid):
                raise osv.except_osv('Mensaje de Advertencia !', 'No esta autorizado para realizar esta accion...')
            if (task.state != 'progress'):
                raise osv.except_osv('Mensaje de Advertencia !', 'No puede realizar esta accion, La tarea ha sido anulada...')
            if not task.other_action_chk:
                self.write(cr, uid, ids, {'state': 'done'})
            self.write(cr, uid, ids, {'included':True})
        return True
           
        
    def action_done_cancelled(self, cr, uid, ids, context=None):
        #self.control_action_task(cr, uid, ids, context)
        self.write(cr, uid, ids, {'state': 'cancelled'})
        
    def onchange_action(self, cr, uid, ids, action_id, context=None):
        if action_id:
            action = self.pool.get("doc_expedient.action").browse(cr, uid, action_id ,context)
            if action.type == 'action':
                return {'value': {'need_reply':True}}
            else:
                return {'value': {'need_reply':False}}
        return False
        
        
    def onchange_job_id(self, cr, uid, ids, context=None):        
        return {'value':{'job_id':'','employee_id':''}}
    
    
    def onchange_job(self, cr, uid, ids, employee_id, context=None):
        if not employee_id:
            return {}
        obj_employee = self.pool.get('hr.employee')
        employee = obj_employee.browse(cr, uid, employee_id)
        return {'value':{'job_id':employee.job_id.id}}
    
    
    def onchange_employee_id(self, cr, uid, ids, job_id, employee_id, department_id, context=None): 
         if job_id and department_id:
            if employee_id:
                for obj_emp in self.pool.get('hr.employee').browse(cr, uid, [employee_id], context):
                    if obj_emp.job_id.id != job_id:
                        employee_id = self.pool.get('hr.employee').search(cr, uid, [('job_id','=', job_id),
                                                                                    ('department_id','=', department_id),])  
                        if employee_id:
                            return {'value':{'employee_id':employee_id[0]}}
                        else:
                            return {'value':{'employee_id':''}}
            else:
                employee_id= self.pool.get('hr.employee').search(cr, uid, [('job_id','=', job_id),
                                                                            ('department_id','=', department_id),])  
                if employee_id:
                    return {'value':{'employee_id':employee_id[0]}}
                else:
                    return {'value':{'employee_id':''}}
                
    
    def unlink(self, cr, uid, ids, *args, **kwargs):
        borrar = False
        obj_expedient = self.pool.get('doc_expedient.expedient')
        for task in self.browse(cr, uid, ids):
            expedient_id = task.expedient_id.id
            expediente = obj_expedient.browse(cr, uid, expedient_id)
            if task.state != 'draft':
                borrar = False
            if task.state == 'cancelled' and task.included == False:
                borrar = True
            if task.state == 'done' and task.user_id.id == uid and task.task_sequence == 1 and len(expediente.tasks) < 2:
                borrar = True
            if not borrar:
                raise osv.except_osv(_('Operación no Permitida  !'), _('No se puede eliminar una tarea.'))
        return super(doc_expedient_task, self).unlink(cr, uid, ids, *args, **kwargs)
    
    def eliminar_tareas(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        obj_ir_attachment = self.pool.get('ir.attachment')
        obj_expedient = self.pool.get('doc_expedient.expedient')
        expedient_id = False
        for task in self.browse(cr, uid, ids):
            if task.state == 'cancelled' and task.included == False:
                expedient_id = task.expedient_id.id
                if task.documents:
                    for doc in task.documents:
                        obj_ir_attachment.unlink(cr,uid,[doc.id])
                self.unlink(cr, uid, [task.id])
                
        result = mod_obj.get_object_reference(cr, uid, 'gt_doc_expedient', 'action_doc_expedient_form_sent1')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        domain = result['domain']
        dd = eval(domain)
        dd.append(('base_state','=', 'sent'))
        domain = str(dd)
        result['domain'] = dd
        return result
    
    
    def onchange_other_action(self, cr, uid, ids, context=None):
        return {'value':{'action_id':'','other_action':'','need_reply':''}}
    
    
    def create_task_cc(self, cr, uid, ids, context=None):
        obj_action = self.pool.get('doc_expedient.action')
        #action_ids = obj_action.search(cr, uid, [('type','=','of_know')])
        #if not action_ids:
        #    raise osv.except_osv('Mensaje de Advertencia !', 'No esta ingresado un tipo de Acción para las Tareas CC')
        #action = obj_action.read(cr, uid, action_ids, ['id','name'])
        for tasks in self.browse(cr, uid, ids, context):
            if tasks.members:
                for user in tasks.members:
                    #need_reply = False
                    #if tasks.action_id:
                    #    action = self.pool.get("doc_expedient.action").browse(cr, uid, tasks.action_id.id, context)
                    #    if action.type == 'action':
                    #        need_reply=True
                    #    else:
                    #        need_reply=False
                    
                    self.create(cr, uid,{'other_action_chk': False,                                                                       
                        #'action_id' : tasks.action_id.id,
                        'other_action' : 'PARA SU CONOCIMIENTO (CC)',
                        'desc_task': 'PARA SU CONOCIMIENTO (CC)',
                        #'department': user.department_id.id,
                        'user_id' : tasks.user_id.id,
                        'need_reply': False,
                        #'job_id': user.job_id.id,
                        'assigned_user_id': user.id,
                        'priority': tasks.priority,
                        'expedient_id':tasks.expedient_id.id,
                        'description': tasks.description or False,
                        'state': 'progress',
                        'type': 'of_know',
                        'task_ref_id': tasks.id,
                        'cc': True,
                        }, context=context)
        return True
                
        
    def create(self, cr, uid, vals, context=None):
        expedient_id = False
        obj_expedient_action = self.pool.get('doc_expedient.action')
        obj_doc_expedient = self.pool.get('doc_expedient.expedient')
        try:
            expedient_id = vals['expedient_id']
        except:
            pass
        if not expedient_id:
            try:
                task_id = context.get('task_id',False)
                if task_id:
                    task = self.browse(cr, uid, task_id)
                    expedient_id = task.expedient_id.id          
                else:
                    expedient_id = context.get('active_id',False)
            except:
                pass
        valor = ''    
        try:          
            action_id = vals['action_id']
            valor = vals['desc_task']
            if action_id and not valor:
                action = obj_expedient_action.browse(cr, uid, action_id)
                valor = action.name
                if action.type=='action':
                    vals['need_reply'] = True
                else:
                    vals['need_reply'] = False
        except:
            pass
        try:
            if not valor:
                valor = vals['other_action']
        except:
            pass
        # Agrega un orden secuencial a las tareas de un tramite
        expedient = obj_doc_expedient.browse(cr, uid, expedient_id, context)
        expedient_state = expedient.state
        task_ids = self.search(cr, uid, [('expedient_id','=',expedient_id)])
        if task_ids:
            if expedient_state == 'draft':
                seq = len(task_ids)+2
            else:
                seq = len(task_ids)+1
        else:
            seq = 2
        try:
            if vals['task_sequence']:
                seq = 1
        except:
            pass
        emp_obj = self.pool.get('hr.employee')
        usuario = self.pool.get('res.users').browse(cr, uid, vals['assigned_user_id'])
#        if (not usuario.context_department_id) or (not usuario.job_id):
#            raise osv.except_osv(('Mensaje de Error !'),('Se requiere que el usuario %s de la tarea este ligado a un Cargo y Departamento...') %(usuario.employee_id.complete_name))
        if valor:
            vals.update({'desc_task':valor, 'task_sequence':seq, 'name':seq, 'expedient_id':expedient_id})
        else:
            vals.update({'task_sequence':seq, 'name':seq, 'expedient_id':expedient_id})
        res_id = super(doc_expedient_task, self).create(cr, uid, vals, context=context)
        obj_doc_expedient.calcular_estados(cr, uid, expedient_id, context=context)
        try:
            task_id = context.get('task_id',False)
            if task_id:
                task = self.browse(cr, uid, task_id)
                if task.state == 'done':
                    cr.execute('update doc_expedient_task set responded=%s where id=%s', (True, task.id))          
        except:
            pass
        return res_id
                    
    
    def action_send_mail(self, cr, uid, ids, context=None):
        template_obj = self.pool.get('email.template')
        model_obj = self.pool.get('ir.model')
        for expedient_task in self.browse(cr, uid, ids, context):
            model = model_obj.search(cr, uid, [('model','=','doc_expedient.task')],limit=1)
            for mod in model:
               modelo = model_obj.browse(cr, uid, mod)
               template_ids = template_obj.search(cr, uid, [('model_id','=',mod)],limit=1)
               for template_id in template_ids:
                  template_obj.send_mail(cr, expedient_task.assigned_user_id.id,
                                         template_id,
                                         expedient_task.id, context=context)
        return True
    
    
    def merge_directory(self, cr, uid, ids, context=None):
        obj_ir_attachment = self.pool.get('ir.attachment')
        expedient_expedient = self.pool.get('doc_expedient.expedient')
        for task in self.browse(cr, uid, ids, context):
            directory_expedient = task.expedient_id.directory_id.id
            if not directory_expedient:
                raise osv.except_osv('Mensaje de Advertencia !', 'No se puede agregar documentos al tramite debido a que su directorio ha sido eliminado')
            self.write(cr, uid, task.id, {'directory_id': directory_expedient})
            if task.documents:
                for doc in task.documents:
                    import pdb
                    pdb.set_trace()
                    obj_ir_attachment.write(cr, uid, doc.id, {'parent_id': directory_expedient})
        return True
    
    
    def _get_directory(self, cr, uid, context={}):
        directory = context['directory_id']
        return directory
        
    
    def __get_def_directory(self, cr, uid, context=None):
        #Este metodo agrega por defecto un directorio temporal
        #"Documents", cuando la tarea es creada se redirecciona
        #al directorio correspondiente del tramite
        dirobj = self.pool.get('document.directory')
        return dirobj._get_root_directory(cr, uid, context)
    
    
    def _get_expedient(self, cr, uid, context=None):
        exp_id = context.get('active_id', False)
        expediente = self.pool.get('doc_expedient.expedient').browse(cr, uid, exp_id)
        return expediente.id
    
        
    def do_send(self, cr, uid, ids, context={}):
        #import pdb 
        #pdb.set_trace()
        request = self.pool.get('res.request')
        for task in self.browse(cr, uid, ids, context=context):
            vals = {}
            expedient = task.expedient_id
            if expedient:
                if not task.assigned_user_id.id:
                    raise osv.except_osv(('Error !'), ('Verifique que el empleado tenga un usuario relacionado'))
                else:                    
                    request.create(cr, uid,{'name': _('%s') % expedient.code,
                                            'state': 'waiting',
                                            'module': 'TRÁMITES',
                                            'act_from': task.user_id.id,
                                            'act_to': task.assigned_user_id.id,
                                            'ref_partner_id': 1,
                                            'ref_doc1': 'doc_expedient.expedient,%d'% (expedient.id,),
                                            'ref_doc2': 'doc_expedient.task,%d'% (task.id,),
                                            }, context=context)
            if task.members:
                for user in task.members:
                    request.create(cr, uid,{'name': "Asignacion de tarea(s) en el tramite cod: '%s'" % expedient.code,
                        'state': 'waiting',
                        'module': 'TRÁMITES',
                        'act_from': task.user_id.id,
                        'act_to': user.id,
                        'ref_partner_id': 1,
                        'ref_doc1': 'doc_expedient.expedient,%d'% (expedient.id,),
                        'ref_doc2': 'doc_expedient.task,%d'% (task.id,),
                        }, context=context)
        vals.update({'state': 'draft'})
        self.write(cr, uid, [task.id],vals, context=context)
        message = "Se ha creado una nueva tarea en el Tramite: '%s'" % (expedient.code),
        self.log(cr, uid, task.id, message[0])
        return True
        
            
    def do_send_cc(self, cr, uid, ids, context=None):
        if not isinstance(ids,list): ids = [ids]
        for task in self.browse(cr, uid, ids, context):
            members = task.members
            if members:
                c=0
                for t in members: 
                    data = {'state': 'progress'}
                    user = members[c]['id']
                    message = ("Esta es una accion simplemente de consulta")
                    self.log(cr, user, task.id, message)
                    c=c+1    
        return True
    
    
    def task_done_cancelled(self, cr, uid, ids, context=None):
        for task in self.browse(cr, uid, ids):
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'doc_expedient.task', task.id, 'wkf_done_cancelled', cr)
            #self.control_action_task(cr, uid, [task.id], context)
            self.write(cr, uid, [task.id], {'state': 'cancelled'})
        return True
    
    
    def do_open_docs(self, cr, uid, ids, context=None):
        pass
    def task_urgent(self, cr, uid, ids, context=None):
        pass
    def task_normal(self, cr, uid, ids, context=None):
        pass
    
    def task_dissocier(self, cr, uid, ids, context=None):
        for task in self.browse(cr, uid, ids, context=context):
            if task.state != 'cancelled':
                raise osv.except_osv(('Error !'), ('No se puede desvincular la tarea'))
            self.write(cr, uid, ids, {'included': False})
        return True
    
    def get_parent_task(self, cr, uid, context=None):
        if context:
            if context.get('active_model') == 'doc_expedient.task':
                return context.get('active_id')
        return False
    
    def _is_user(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            if task.user_id.id == uid:
                res[task.id] = True
            else:
                res[task.id] = False
                
            sql = "UPDATE doc_expedient_task set owner_task_db='%s' WHERE id=%s" % (res[task.id], task.id)
            cr.execute(sql)
        return res
    
    def search_respaldo(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False): 
        #import pdb        
        if limit:
            if limit > 80: limit=80
        else:
            limit=80
        #pdb.set_trace()
        return super(doc_expedient_task, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
        
    
    
    def _is_assigned(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            if task.assigned_user_id.id == uid and task.task_sequence != 1:
                res[task.id] = True
            else:
                res[task.id] = False
        return res
    
    
    def _is_assigned_draft(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            if task.user_id.id == uid and task.state == 'draft':
                res[task.id] = True
            else:
                res[task.id] = False
                
            sql = "UPDATE doc_expedient_task set task_draft_db='%s' WHERE id=%s" % (res[task.id], task.id)
            cr.execute(sql)
        return res
    

    _columns = dict(
        name = fields.char('Descripción', size=64),
        owner_task = fields.function(_is_user, store=False, string='Propietario de la Tarea', type='boolean', help="Indica que el usuario actual del sistema sea el mismo que el que lo creo la tarea"),
        owner_task_db = fields.boolean('Propietario de la Tarea', help="Indica que el usuario actual del sistema sea el mismo que el que lo creo la tarea"),
        
        
        task_draft = fields.function(_is_assigned_draft, store=False, string='Tarea Draft', type='boolean', help="Indica que el usuario creo una tarea en brorrador"),
        task_draft_db = fields.boolean('Tarea Draft DB', help="Indica que el usuario creo una tarea en brorrador"),
        
        #task_progress = fields.function(_is_assigned_progress, store=False, string='Tarea Progress', type='boolean', help="Indica que el usuario tiene tareas pendientes o realizadas"),
        #task_progress_db = fields.boolean('Tareas en Progreso ', help="Indica que el usuario tiene tareas pendientes o realizadas"),
        
        assigned_task = fields.function(_is_assigned, store=False, string='Usuario Asignado', type='boolean', help="Indica que el usuario actual del sistema sea el asignado a la tarea"),
        responded = fields.boolean('Responded', help="Indica que una tarea ha sido respondida"),
        included = fields.boolean('Conocido', help="Indica que el usuario está participado en el trámite"),
        tasks = fields.boolean('Tasks', help="Indica que la visualizacion de tareas del tramite"),
        action_id = fields.many2one('doc_expedient.action', 'Tarea'),
        type = fields.selection([('action', 'Acción'),('of_know', 'Conocimiento')],'Tipo de Acción'),
        type_action = fields.related('action_id', 'type', type='selection', selection=[('action', 'Accion'),('of_know', 'Conocimiento')], string='Acción de una tarea'),
        other_action_chk = fields.boolean('Otra', 
          help="Marque esta casilla si la acción es distinta de las propuesta en el campo: Tarea"),
        other_action = fields.char('Otra Tarea', size=256),
        need_reply = fields.boolean('Requiere Respuesta?', help="Esta casilla se activará en el caso que la tarea requiera una respuesta"),
        date_task = fields.datetime('Fecha creación', select=True),
        desc_task = fields.char('Tarea', size=64),
        expedient_id = fields.many2one('doc_expedient.expedient', 'Trámite', required=False),
        justification = fields.char('Justificativo de Anulación', size=128, readonly="True"),
        #expedient_code = fields.related('expedient_id','code', type='char', string='Núm.Trámite'),
        task_sequence = fields.integer('Núm.Tarea'),
        expedient_name = fields.related('expedient_id','name', type='char', string='Trámite'),
        expedient_state = fields.related('expedient_id','state', type='selection', selection = [('draft', 'Borrador'),
                                  ('created', 'Creado'),
                                  ('cancelled', 'Anulado'), 
                                  ('done', 'Archivado')], string='Estado Trámite', 
                                  readonly=True, store=True,),
        priority = fields.selection([('normal', 'Normal'),
                          ('medium', 'Media'),
                          ('urgent', 'Urgente'),], 'Prioridad', 
                          required=True),
        user_id = fields.many2one('res.users', 'Enviado por', required=True),
        user_login = fields.related('user_id','login', type="char", size=32, string="Origen", store=True),
        user_department = fields.related('user_id','context_department_id', type="many2one", relation="hr.department", string="Departamento (crea)", store=False),
        #job_id = fields.many2one('hr.job', 'Cargo', required=True),
        #department = fields.many2one('hr.department', string='Departamento', required=True),
        #employee_id = fields.many2one('hr.employee', 'Asignado a', required=True),
        assigned_user_id = fields.many2one('res.users','Usuario asignado', required=True),
        assigned_user_login = fields.related('assigned_user_id','login', type="char", size=32, string="Destino", store=True),
        assigned_user_department = fields.related('assigned_user_id','context_department_id', type="many2one", relation="hr.department", string="Departamento", store=False),
        description = fields.text('Descripción'),
        state = fields.selection([('draft', 'Borrador'),
                          ('progress', 'Pendiente'),
                          ('done', 'Realizado'),
                          ('cancelled', 'Anulado')], 'Estado', 
                          required=True,),
        documents = fields.one2many('ir.attachment', 'document_id', "Documentos"),
        task_ref_id = fields.many2one('doc_expedient.task', 'Referencia de Tarea',
            help="Permite referenciar a una tarea, para el envio de tareas CC"),
        parent_task = fields.integer('Tarea Padre'),
        directory_id = fields.many2one('document.directory', 'Directorio', readonly=True),
        documents_ref = fields.related('task_ref_id','documents', type='one2many', relation="ir.attachment", string='Documentos de Referencia', 
            readonly=True, help="Obtine los documentos, en el caso de envio de tareas CC"),
        cc = fields.boolean('CC', help="Campo booleando que indica que una tarea ha sido enviada CC"),
        members = fields.many2many('res.users', 'task_user_rel', 'expedient_task_id', 'user_id', 'Miembros de una Tarea'),
        sugerence = fields.char('Sugerencia', size=64, help="Permite sugerir parametros con respecto a la prioridad de la tarea; Por Ejemplo: Un periodo de tiempo para resolver la tarea..."),
    )
    _defaults = dict(
        state = 'draft',
        priority = 'normal',
        expedient_id = _get_expedient,
        parent_task = get_parent_task,             
        user_id = lambda self, cr, uid, ctx:uid,
        directory_id = __get_def_directory,
        #directory_id = 1,
        date_task = lambda *a: strftime('%Y-%m-%d %H:%M:%S'),
        cc = False,
        owner_task = True,
        assigned_task = False,
        responded = False,
        included = False,
    )
    _order = "task_sequence desc"
    
    def write(self, cr, uid, ids, vals, context=None):
        obj_expedient = self.pool.get('doc_expedient.expedient')
        ids_tareas = []
        try:
            largo = len(ids)
            ids_tareas = ids
        except:
            ids_tareas = [ids]
        result = super(doc_expedient_task,self).write(cr, uid, ids, vals, context)
        if vals.has_key('action_id'):
            action = self.pool.get('doc_expedient.action').browse(cr, uid, action_id)
            if action.type=='action':
                vals['need_reply'] = True
            else:
                vals['need_reply'] = False
        for tarea in self.browse(cr, uid, ids_tareas, context):
            obj_expedient.calcular_estados(cr, uid, [tarea.expedient_id.id], context)
        return result
    
    def calcular_estados_respaldo(self, cr, uid, ids, context=None):
        obj_expedient = self.pool.get('doc_expedient.expedient')
        ids_tareas = []
        try:
            largo = len(ids)
            ids_tareas = ids
        except:
            ids_tareas = [ids]
        for tarea_actual in self.browse(cr, uid, ids_tareas, context):
            expediente = obj_expedient.browse(cr, uid, tarea_actual.expedient_id.id)
            state_draft = []
            state_open = []
            state_sent = []
            state_cancelled = []
            state_removed = []
            sent = False
            cancel = False
            draft = False
            if not expediente.tasks:
                state_draft.append(uid)
            for task in expediente.tasks:
                if task.state == 'progress' and task.assigned_user_id.id == uid:
                    state_open.append(uid)
                    #res[obj.id] = 'open'
                    break
                if (task.state == 'done' and task.assigned_user_id.id == uid and tarea_actual.state != 'removed'):
                    state_sent.append(uid)
                    #res[obj.id] = 'sent'
                    sent = True
                if (task.state == 'done' and task.user_id.id == uid and tarea_actual.state != 'removed'):
                    state_sent.append(uid)
                    #res[obj.id] = 'sent'
                    sent = True 
                if task.state == 'progress' and task.user_id.id == uid:
                    state_sent.append(uid)
                    #res[obj.id] = 'sent'
                    sent = True
                if task.user_id.id == uid and task.state == 'cancelled' and task.included and tarea_actual.state != 'cancelled':
                    state_sent.append(uid)
                    #res[obj.id] = 'sent'
                    sent = True
                if task.state == 'draft' and task.user_id.id == uid:
                    if not sent:
                        state_draft.append(uid)
                        #res[obj.id] = 'draft'
                        draft = True
                if task.assigned_user_id.id == uid and task.state == 'cancelled' and task.included:
                    if not sent and not draft:
                        state_cancelled.append(uid)
                        #res[obj.id] = 'cancelled'
                        cancel = True
                if task.user_id.id == uid and task.state == 'cancelled' and not task.included:
                    if not sent and not draft:
                        state_cancelled.append(uid)
                        #res[obj.id] = 'cancelled'
                        cancel = True    
                #sql = "UPDATE doc_expedient_expedient set base_state='%s' WHERE id=%s" % (res[obj.id], obj.id)
                #cr.execute(sql)
            string_draft = ""
            string_open = ""
            string_sent = ""
            string_cancelled = ""
            string_removed = ""
            for item in state_draft:
                string_draft = "-" + str(item) + "-"
            for item in state_open:
                string_open = "-" + str(item) + "-"
            for item in state_sent:
                string_sent = "-" + str(item) + "-"
            for item in state_cancelled:
                string_cancelled = "-" + str(item) + "-"
            for item in state_removed:
                string_removed = "-" + str(item) + "-"
            return {'state_draft': string_draft,
                    'state_open': string_open,
                    'state_sent': string_sent,
                    'state_cancelled': string_cancelled,
                    'state_removed': string_removed}    
            
            
    def _check_documents(self, cr, uid, ids, context=None):
        for task in self.browse(cr, uid, ids):
            if task.documents:
                for doc in task.documents:
                    if not doc.datas:
                        return False
        return True
    
    _constraints = [
        #(_check_documents, 'Error! Un adjunto no ha sido agregado correctamente',['documents'])
    ]

doc_expedient_task()


class Ir_Attachment(osv.osv):
    _inherit = 'ir.attachment'

    _columns = dict(
                    document_id = fields.many2one('doc_expedient.task', 'Tarea'),
                    document_expedient_id = fields.many2one('doc_expedient.expedient', 'Expediente'),
                    ref_doc1 = fields.reference('Document Ref', selection=_links_get, size=128),
                    #datas =  fields.binary('Data', filters='*.odt'),
    )
    
    def create(self, cr, uid, vals, context=None):
        
        if vals.has_key('document_id'):
            obj_task = self.pool.get('doc_expedient.task')
            tarea = obj_task.browse(cr, uid, vals['document_id'],context=context)
            vals.update({'parent_id':tarea.expedient_id.directory_id.id})
        res_id = super(Ir_Attachment, self).create(cr, uid, vals, context=context)
        return res_id
    
    def onchange_datas(self, cr, uid, ids, datas, context=None):
        if datas:
            pass
        else:
            return {'warning':{'title':'Advertencia','message':'El documento no podra ser almacenado si se encuentra en vacio'}}
    
    #def write(self, cr, uid, ids, values, context=None):
    #    if values.has_key('datas_fname'):
    #        values['db_datas'] = False
    #    return super(Ir_Attachment, self).write(cr, uid, ids, values, context=context)
    
    #def _validar_archivo(self, cr, uid, ids, context=None):
    #    obj = self.browse(cr, uid, ids[0], context=context)
    #    #import pdb
    #    #pdb.set_trace()
    #    if obj.datas_fname == False:
    #        return False
    #    if obj.datas == False:
    #        return False
    #    return True

    def _validar_archivo_directorio(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        ids_similares = self.search(cr, uid, [('datas_fname','=',obj.datas_fname),('parent_id','=',obj.parent_id.id)], context=context)
        if len(ids_similares)>1:
            return False
        return True
    
    _constraints = [
    #                (_validar_archivo, 'No se puede almacenar sin la informacion del archivo', ['datas_fname','datas']),
                    (_validar_archivo_directorio, 'No se puede almacenar un documento con el mismo nombre en un directorio', ['datas_fname','datas','parent_id']),
                    ]

    
Ir_Attachment()


class Res_Users(osv.osv):
    _inherit = 'res.users'
    _columns = dict(
        expedient_task_id = fields.many2one('doc_expedient.task', 'Tarea', readonly=True),
   )
Res_Users()


class Hr_Employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = dict(
        task_id = fields.many2one('doc_expedient.task', 'Tarea', readonly=True),
   )
Hr_Employee()
