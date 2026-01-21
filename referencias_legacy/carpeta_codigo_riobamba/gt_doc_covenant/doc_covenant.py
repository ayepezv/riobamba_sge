# -*- coding: utf-8 -*-
##############################################################################
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
from time import strftime
import time
from datetime import datetime, date
import decimal_precision as dp
from string import upper

class doc_covenant_covenant(osv.osv):
    _name = "doc_covenant.covenant"
    #_inherit = "doc_contract.contract"
        
    def action_send_mail(self, cr, uid, ids, context=None):
        template_obj = self.pool.get('email.template')
        model_obj = self.pool.get('ir.model')
        for covenant in self.browse(cr, uid, ids, context):
            model = model_obj.search(cr, uid, [('model','=','doc_covenant.covenant')],limit=1)
            for mod in model:
               modelo = model_obj.browse(cr, uid, mod)
               template_ids = template_obj.search(cr, uid, [('model_id','=',mod)],limit=1)
               for template_id in template_ids:
                  template_obj.send_mail(cr, uid,
                                         template_id,
                                         covenant.id, context=context)
        return True 
    
    
    def wkf_draft_open(self, cr, uid, ids, context=None):
        obj_doc_covenant_stage = self.pool.get('doc_covenant.stage')
        obj_doc_covenant_state = self.pool.get('doc_covenant.state')
        obj_historial = self.pool.get('doc.covenant.historial')
        for covenant in self.browse(cr, uid, ids, context):
#            if not (covenant.expedient_ids):
#                raise osv.except_osv('Mensaje de Advertencia !', '¡No se ha asignado ninguna referencia con un tramite!')
            if not (covenant.beneficiary_ids):
                raise osv.except_osv('Mensaje de Error !', '¡Debe asignar por lo menos un beneficiario!')
            if not (covenant.ubication_cv_ids):
                raise osv.except_osv('Mensaje de Error !', '¡Debe asignar por lo menos una localidad!')
            self.write(cr, uid, [covenant.id],{
                    #'doc_covenant_stage_id':stage_results[0]['id'],
                    'state':'legalizing',
                    'creation_date':time.strftime('%Y-%m-%d %H:%M:%S'),
                    #                                                     'stage_user_id':stage.user_id.id,
                    #                                                     'state_stage_planning':state_results[0]['id'],
                    #                                                      'stage_contract':'planning' 
                    })
            obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                           'usuario':uid,
                                           'name':'Convenio Iniciado',
                                           'covenant_id':covenant.id})
            self.create_directory(cr, uid, ids, context)
            #self.create_beneficiary(cr, uid, ids, context)
        return True

    def wkf_open_distribution(self, cr, uid, ids, context=None):
        obj_historial = self.pool.get('doc.covenant.historial')
        for covenant in self.browse(cr, uid, ids, context):
            if covenant.firma_contratista==False or covenant.firma_max==False:
                raise osv.except_osv('Mensaje de Error !', 'No se han completado el registro de firmas correspondientes')
            self.write(cr, uid, [covenant.id],{'state':'open'})
            obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                           'usuario':uid,
                                           'name':'Convenio Distribucion',
                                           'covenant_id':covenant.id})
        return True
    
    def wkf_distribution_ejec(self, cr, uid, ids, context=None):
        obj_historial = self.pool.get('doc.covenant.historial')
        for covenant in self.browse(cr, uid, ids, context):
            if not len(covenant.distribucion_users)>0:
                raise osv.except_osv('Mensaje de Error !', 
                                     'Es necesario distribuir al menos a un usuario')
            if not covenant.chk_covenant:
                raise osv.except_osv('Mensaje de Error !',
                                     'No se ha adjuntado el archivo copia del convenio')
            self.write(cr, uid, [covenant.id],{'state':'execution'})
            obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                           'usuario':uid,
                                           'name':'Convenio Ejecucion',
                                           'covenant_id':covenant.id})
        return True

    def wkf_open_done(self, cr, uid, ids, context=None):
        obj_historial = self.pool.get('doc.covenant.historial')
        for covenant in self.browse(cr, uid, ids, context):
            if not covenant.chk_acta_cierre:
                raise osv.except_osv('Mensaje de Error !', 'No se ha adjuntado el archivo Acta de cierre del convenio')
            self.write(cr, uid, [covenant.id],{'state':'done'})
            obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                           'usuario':uid,
                                           'name':'Convenio Finalizado',
                                           'covenant_id':covenant.id})
        return True
        
    def create_directory(self, cr, uid, ids, context=None):
    #Crear un directorio cada vez que se crea un trámite, el directorio se crea bajo 
    #el directorio principal “Trámites” y con el nombre del código del trámite.
        obj_document_directory = self.pool.get('document.directory')
        obj_ir_attachment = self.pool.get('ir.attachment')
        for covenant in self.browse(cr, uid, ids, context):
            dir_covenant = obj_document_directory.search(cr, uid, [('name','=','Convenios')], limit=1)
            if dir_covenant:
                pid = obj_document_directory.create(cr, uid, {'name' : 'Convenio - ' + str(covenant.code_covenant),
                                       'parent_id' : dir_covenant[0],
                                       'user_id' : None})
                self.write(cr, uid, [covenant.id], {'directory_id': pid})
            else:
                raise osv.except_osv('Mensaje de Advertencia !', 'No existe el directorio padre "Convenios"')       
        return True
    
    
    """def create_beneficiary(self, cr, uid, ids, context=None):
        pdb.set_trace()
        obj_doc_beneficiary = self.pool.get('doc_covenant.beneficiary')
        obj_beneficiary_rel = self.pool.get('covenant_beneficiary.rel')
        for covenant in self.browse(cr, uid, ids, context):
            if covenant.beneficiary_ids:
                for beneficiary in covenant.beneficiary_ids:
                    obj_beneficiary_rel.create(cr, uid, {'beneficiary_id':beneficiary.id,
                                                         'covenant_id':covenant.id})
        return True"""
    
        
        
    def stage_change_planning(self, cr, uid, ids, context=None):
        obj_doc_covenant_stage = self.pool.get('doc_covenant.stage')
        obj_doc_covenant_state = self.pool.get('doc_covenant.state')
        for covenant in self.browse(cr, uid, ids):
            seq_stage_ids = obj_doc_covenant_stage.search(cr, uid, [('seq_stage','=',2)])
            if not (seq_stage_ids):
                raise osv.except_osv('Mensaje de Advertencia !', 'No es posible trabajar en esta Etapa')
            stage_results = obj_doc_covenant_stage.read(cr, uid, seq_stage_ids, ['seq_stage','name','id'])
            if not (stage_results):
                raise osv.except_osv('Mensaje de Advertencia !', 'No es posible trabajar en esta Etapa')
            stage = obj_doc_covenant_stage.browse(cr, uid, stage_results[0]['id']) 
            if not (stage.user_id.id):
                raise osv.except_osv('Mensaje de Advertencia !', 'No se ha asignado un usuario responsable a cada etapa del convenio...')     
            state_ids=obj_doc_covenant_state.search(cr, uid, [('stage_id','=',stage_results[0]['id'])])
            if not (state_ids):
                raise osv.except_osv('Mensaje de Advertencia !', 'Los parámetros de configuración no han sido completados...')
            state_results = obj_doc_covenant_state.read(cr, uid, state_ids, ['seq_state','id'])
            sequence_state = covenant.state_stage_planning.seq_state
            state_planning_ids=obj_doc_covenant_state.search(cr, uid, [('stage_id','=',covenant.doc_covenant_stage_id.id)])
            if sequence_state != len(state_planning_ids):
                raise osv.except_osv('Mensaje de Advertencia !', 'No se han completado los estados de la etapa...')            
            self.write(cr, uid, [covenant.id],{'doc_covenant_stage_id':stage_results[0]['id'],
                                              'stage_user_id':stage.user_id.id,
                                              #'state_planning':'done',
                                              #'state_syndicate':'open',
                                              'state_stage_syndicate' : state_results[0]['id'],
                                              'stage_contract':'syndicate'})
            #self.action_send_mail(cr, uid, ids, context)
        return True
    
    
    def stage_change_syndicate(self, cr, uid, ids, context=None):
        obj_doc_covenant_stage = self.pool.get('doc_covenant.stage')
        obj_doc_covenant_state = self.pool.get('doc_covenant.state')
        for covenant in self.browse(cr, uid, ids):
            seq_stage_ids = obj_doc_covenant_stage.search(cr, uid, [('seq_stage','=',3)])
            if not (seq_stage_ids):
                raise osv.except_osv('Mensaje de Advertencia !', 'No es posible trabajar en esta Etapa')
            stage_results = obj_doc_covenant_stage.read(cr, uid, seq_stage_ids, ['seq_stage','name','id'])
            stage = obj_doc_covenant_stage.browse(cr, uid, stage_results[0]['id'])
            if not (stage.user_id.id):
                raise osv.except_osv('Mensaje de Advertencia !', 'No se ha asignado un usuario responsable a cada etapa del convenio...')      
            state_ids=obj_doc_covenant_state.search(cr, uid, [('stage_id','=',stage_results[0]['id'])])
            if not (state_ids):
                raise osv.except_osv('Mensaje de Advertencia !', 'Los parámetros de configuración no han sido completados...')
            state_results = obj_doc_covenant_state.read(cr, uid, state_ids, ['seq_state','id'])
            sequence_state = covenant.state_stage_syndicate.seq_state
            state_syndicate_ids=obj_doc_covenant_state.search(cr, uid, [('stage_id','=',covenant.doc_covenant_stage_id.id)])
            if sequence_state != len(state_syndicate_ids):
                raise osv.except_osv('Mensaje de Advertencia !', 'No se han completado los estados de la etapa...')
            if not (covenant.term):
                    raise osv.except_osv('Mensaje de Advertencia !', 'El campo "Plazo" es obligatorio..')
            if not (covenant.subscription_date_covenant):
                    raise osv.except_osv('Mensaje de Advertencia !', 'El campo "Fecha Suscripción" es obligatorio..')
            self.write(cr, uid, [covenant.id],{'doc_covenant_stage_id':stage_results[0]['id'],
                                              'stage_user_id':stage.user_id.id,
                                              'state_stage_secretary' : state_results[0]['id'],
                                              'stage_contract':'secretary'})
            #self.action_send_mail(cr, uid, ids, context)
        return True
    
    
    def stage_change_secretary(self, cr, uid, ids, context=None):
        obj_doc_covenant_stage = self.pool.get('doc_covenant.stage')
        obj_doc_covenant_state = self.pool.get('doc_covenant.state')
        for covenant in self.browse(cr, uid, ids):
            seq_stage_ids = obj_doc_covenant_stage.search(cr, uid, [('seq_stage','=',4)])
            if not (seq_stage_ids):
                raise osv.except_osv('Mensaje de Advertencia !', 'No es posible trabajar en esta Etapa')
            stage_results = obj_doc_covenant_stage.read(cr, uid, seq_stage_ids, ['seq_stage','name','id'])
            stage = obj_doc_covenant_stage.browse(cr, uid, stage_results[0]['id'])
            if not (stage.user_id.id):
                raise osv.except_osv('Mensaje de Advertencia !', 'No se ha asignado un usuario responsable a cada etapa del convenio...')      
            state_ids=obj_doc_covenant_state.search(cr, uid, [('stage_id','=',stage_results[0]['id'])])
            if not (state_ids):
                raise osv.except_osv('Mensaje de Advertencia !', 'Los parámetros de configuración no han sido completados...')
            state_results = obj_doc_covenant_state.read(cr, uid, state_ids, ['seq_state','id'])
            sequence_state = covenant.state_stage_secretary.seq_state
            state_secretary_ids=obj_doc_covenant_state.search(cr, uid, [('stage_id','=',covenant.doc_covenant_stage_id.id)])
            if sequence_state != len(state_secretary_ids):
                raise osv.except_osv('Mensaje de Advertencia !', 'No se han completado los estados de la etapa...')
            if not (covenant.date_received):
                raise osv.except_osv('Mensaje de Advertencia !', 'El campo "Fecha Recibe" es obligatorio..')
            if not (covenant.dispatch_office_number):
                raise osv.except_osv('Mensaje de Advertencia !', 'El campo "Nro.Oficio Despacho" es obligatorio..')
            
            self.write(cr, uid, [covenant.id],{'doc_covenant_stage_id':stage_results[0]['id'],
                                              'stage_user_id':stage.user_id.id,
                                              'state_stage_fiscalizacion' : state_results[0]['id'],
                                              'stage_contract':'fiscalizacion'})
            #self.action_send_mail(cr, uid, ids, context)
        return True
    
    def create(self, cr, uid, vals, context=None):
#        obj_sequence = self.pool.get('ir.sequence')
        obj_employee = self.pool.get('hr.employee')
#        code_covenant = obj_sequence.get(cr, uid, 'seq.doc.covenant')
#        vals.update({'code_covenant': code_covenant})
        #si hay tramite o sino lo crea
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        employee_id = user.employee_id.id
        if not employee_id:
            raise osv.except_osv(('Mensaje de Error !'), ('El usuario %s Administrador del Contrato no esta relacionado a un empleado del sistema') % (user.name))
        solicitant_id = user.employee_id
        if not solicitant_id.department_id.id and solicitant_id.job_id.id:
            raise osv.except_osv('Mensaje de Error !', 'El usuario creador no tiene departamento y/o cargo')
        #Si no hay el tramite lo crea, con la tarea
        resumen = 'Convenio creado: ' + vals['code_covenant']
        if vals['expedient_id']:
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,
                                                                {'other_action_chk': True,
                                                                 'other_action' : 'Para su conocimiento' ,
                                                                 'description': 'Estimado: ' + solicitant_id.complete_name,
                                                                 'department': solicitant_id.department_id.id,
                                                                 'employee_id' : solicitant_id.id,
                                                                 'job_id': solicitant_id.job_id.id,
                                                                 'user_id': uid,
                                                                 'expedient_id':vals['expedient_id'],
                                                                 'state': 'done',
                                                                 'assigned_user_id':uid,
                                                                 }, context=context)
        else:
            expedient_id= self.pool.get('doc_expedient.expedient').create(cr, uid,
                                                                          {'name':  str('Convenio Creado: ') + vals['name'],
                                                                           'state': 'draft',
                                                                           'ubication':'internal',
                                                                           'resumen': resumen}, context=context)
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,
                                                                {'other_action_chk': True,
                                                                 'other_action' : 'Para su conocimiento',
                                                                 'description': 'Estimado: ' + solicitant_id.complete_name,
                                                                 'department': solicitant_id.department_id.id,
                                                                 'employee_id' : solicitant_id.id,
                                                                 'job_id': solicitant_id.job_id.id,
                                                                 'user_id': uid,
                                                                 'expedient_id':expedient_id,
                                                                 'state': 'done',
                                                                 'assigned_user_id':uid,
                                                                 }, context=context)
            vals['expedient_id']=expedient_id
            self.pool.get('doc_expedient.expedient').action_draft_created(cr, uid, [expedient_id],context)
        self.pool.get('doc_expedient.task').write(cr, uid, [task_id], {'state':'done'})
        res_id = super(doc_covenant_covenant, self).create(cr, uid, vals, context=context)
        return res_id
    
    
    def stage_change_fiscalizacion(self, cr, uid, ids, context=None):
        obj_doc_covenant_state = self.pool.get('doc_covenant.state')
        for covenant in self.browse(cr, uid, ids):
            sequence_state = covenant.state_stage_fiscalizacion.seq_state
            state_fiscalizacion_ids=obj_doc_covenant_state.search(cr, uid, [('stage_id','=',covenant.doc_covenant_stage_id.id)])
            if sequence_state != len(state_fiscalizacion_ids):
                raise osv.except_osv('Mensaje de Advertencia !', 'No se han completado los estados de la etapa...')
            #if stage_results:
            self.write(cr, uid, [covenant.id],{'state_fiscalizacion':'open',
                                              'stage_contract':'finish'})
        return True
        
    def _is_state_stage(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for covenant in self.browse(cr, uid, ids, context=context):
            seq_stage = covenant.doc_covenant_stage_id.seq_stage
            if seq_stage == 1:
                res[covenant.id] = covenant.state_stage_planning.name
            if seq_stage == 2:
                res[covenant.id] = covenant.state_stage_syndicate.name
            if seq_stage == 3:
                res[covenant.id] = covenant.state_stage_secretary.name
            if seq_stage == 4:
                res[covenant.id] = covenant.state_stage_fiscalizacion.name
        return res
    
    def onchange_other_type(self, cr, uid, ids, doc_covenant_type_id, context=None):
        #pdb.set_trace()
        if doc_covenant_type_id:
            obj_doc_covenant_type = self.pool.get('doc_covenant.type')
            covenant_type = obj_doc_covenant_type.browse(cr, uid, doc_covenant_type_id)
            if upper(covenant_type.name) == "OTRO":
                return {'value':{'chk_other_type':True}}
        return {'value':{'chk_other_type':False, 'other_type':''}}
    
    
    def write(self, cr, uid, ids, vals, context=None):
        obj_doc_covenant_stage = self.pool.get('doc_covenant.stage')
        now_date = time.strftime('%Y-%m-%d')
        res = super(doc_covenant_covenant,self).write(cr, uid, ids, vals, context)
        for covenant in self.browse(cr, uid, ids):
            if covenant.subscription_date_covenant:
                if not covenant.subscription_date_covenant <= now_date:
                    raise osv.except_osv(('Mensaje de Advertencia!'), ('¡La fecha de subcripcion debe ser menor o igual a la fecha actual!'))
                if covenant.compromised_contribution_company < 0 or covenant.total_compromised_contribution_company < 0 or covenant.compromised_contribution_counterpart < 0 or covenant.total_compromised_contribution_counterpart < 0:
                    raise osv.except_osv(('Mensaje de Advertencia!'), ('¡Existen valores negativos ingresados!'))
            if covenant.partial_delivery_certificate:
                if not covenant.partial_delivery_certificate <= now_date:
                    raise osv.except_osv(('Mensaje de Advertencia!'), ('¡La fecha "Acta Entrega Parcial" debe ser menor o igual a la fecha actual!'))
            if covenant.provicional_final_certificate:
                if not covenant.provicional_final_certificate <= now_date:
                    raise osv.except_osv(('Mensaje de Advertencia!'), ('¡La fecha "Acta Provisional-Definitiva" debe ser menor o igual a la fecha actual!'))
                if not covenant.provicional_final_certificate >= covenant.partial_delivery_certificate:
                    raise osv.except_osv(('Mensaje de Advertencia!'), ('¡La fecha "Acta Provisional-Definitiva" debe ser mayor o igual a la fecha "Acta Entrega Parcial"!'))
            if covenant.termination_certificate:
                if not covenant.termination_certificate <= now_date:
                    raise osv.except_osv(('Mensaje de Advertencia!'), ('¡La fecha "Acta de Terminación" debe ser menor o igual a la fecha actual!'))
                if not covenant.termination_certificate >= covenant.provicional_final_certificate:
                    raise osv.except_osv(('Mensaje de Advertencia!'), ('¡La fecha "Acta de Terminación" debe ser mayor o igual a la fecha "Acta Provisional-Definitiva"!'))          
        return res
    
    def unlink(self, cr, uid, ids, *args, **kwargs):
        for covenant in self.browse(cr, uid, ids):
            if covenant.state != 'draft':
                raise osv.except_osv('Operación no Permitida  !', '¡No se puede eliminar los convenios!')
        return super(doc_covenant_covenant, self).unlink(cr, uid, ids, *args, **kwargs)
    
    def _is_group_dpto_legal_cv(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        m  = self.pool.get('ir.model.data')
        for covenant in self.browse(cr, uid, ids, context=context):
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_cv_info_general').id
            user = self.pool.get('res.users').browse(cr, uid, uid)
            if group_id in [g.id for g in user.groups_id]:
                res[covenant.id] = True
            else:
                res[covenant.id] = False
        return res
    
    def _is_group_distribucion_cv(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        m  = self.pool.get('ir.model.data')
        for covenant in self.browse(cr, uid, ids, context=context):
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_cv_distribucion').id
            user = self.pool.get('res.users').browse(cr, uid, uid)
            if group_id in [g.id for g in user.groups_id]:
                res[covenant.id] = True
            else:
                res[covenant.id] = False
        return res
    
    
    def _is_group_fiscalizacion_cv(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        m  = self.pool.get('ir.model.data')
        for covenant in self.browse(cr, uid, ids, context=context):
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_cv_fiscalizacion').id
            user = self.pool.get('res.users').browse(cr, uid, uid)
            if group_id in [g.id for g in user.groups_id]:
                res[covenant.id] = True
            else:
                res[covenant.id] = False
        return res
    
    def _is_not_stage_cv(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        info_general = False
        dpto_legal = False
        distribucion = False
        fiscalizacion = False
        m  = self.pool.get('ir.model.data')
        for covenant in self.browse(cr, uid, ids, context=context):
            user = self.pool.get('res.users').browse(cr, uid, uid)
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_cv_fiscalizacion').id
            if group_id in [g.id for g in user.groups_id]:
                dpto_legal = True
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_cv_distribucion').id
            if group_id in [g.id for g in user.groups_id]:
                distribucion = True
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_cv_dpto_legal').id
            if group_id in [g.id for g in user.groups_id]:
                dpto_legal = True
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_cv_info_general').id
            if group_id in [g.id for g in user.groups_id]:
                info_general = True    
            
            if info_general or dpto_legal or distribucion or fiscalizacion:
                res[covenant.id] = False
            else:
                res[covenant.id] = True
        return res
    
    
    def _is_user_cv(self, cr, uid, ids, field_name, arg, context=None):
    #Método que devuelve “True” si el usuario actual es el mismo que el que creo el trámite, caso
    #contrario devolverá “False”
        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            res[contract.id] = False
        return res
    
    def subir_convenio(self, cr, uid, ids, context=None):
        obj_ir_attachment = self.pool.get('ir.attachment')
        for conv in self.browse(cr, uid, ids):
            obj_ir_attachment.create(cr, uid, {'parent_id':conv.directory_id.id,
                                               'datas':conv.data_contract,
                                               'name':'Convenio',
                                               'datas_fname':conv.data_covenant_fname,
                                               'document_covenant_id':conv.id
                                               })
            self.write(cr, uid, [conv.id], {'chk_covenant':True})
        return True

    def _check_subscription_date(self, cr, uid, ids, context=None):
        now_date = time.strftime('%Y-%m-%d')
        for contract in self.browse(cr, uid, ids):
            if contract.subscription_date > now_date:
                return False
            return True

    def _amount_all_cinvoice(self, cr, uid, ids, field_name, arg, context=None):
        '''    Calcula el valor de facturas y el extra del contrato
        '''
        res = {}
        for covenant in self.browse(cr, uid, ids, context=context):
            res[covenant.id] = {
                'amount_total_invoice': 0.0,
                'amount_extra': 0.0,
            }
            total_invoice = total_extra = 0
            for invoice in covenant.invoice_ids:
                total_invoice += invoice.amount_pay
            if total_invoice > covenant.amount:
                total_extra = total_invoice - covenant.amount
            res[covenant.id]['amount_total_invoice']=total_invoice
            res[covenant.id]['amount_extra']=total_extra
        return res

    def __group_info_general(self, cr, uid, context=None):
        #pdb.set_trace()
        res = {}
        m  = self.pool.get('ir.model.data')
        obj_user = self.pool.get('res.users')
        group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_cv_info_general').id
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if group_id in [g.id for g in user.groups_id]:
            res = True
        else:
            res = False
        return res

    def subir_contrato(self, cr, uid, ids, context=None):
        obj_ir_attachment = self.pool.get('ir.attachment')
        for covenant in self.browse(cr, uid, ids):
            obj_ir_attachment.create(cr, uid, {'parent_id':covenant.directory_id.id,
                                               'datas':covenant.data_contract,
                                               'name':'Contrato',
                                               'datas_fname':covenant.data_covenant_fname,
                                            #   'document_type_id':tipo_documento.id,
                                               'document_contract_id':covenant.id})
#            self.write(cr, uid, [contract.id], {'chk_contrato':True})
        return True

    def subir_doc_acta_cierre(self, cr, uid, ids, context=None):
        obj_ir_attachment = self.pool.get('ir.attachment')
        for covenant in self.browse(cr, uid, ids):
            obj_ir_attachment.create(cr, uid, {'parent_id':covenant.directory_id.id,
                                               'datas':covenant.data_acta_cierre,
                                               'name':'Acta de Cierre',
                                               'datas_fname':covenant.data_acta_cierre_fname,
                                   #            'document_type_id':tipo_documento.id,
                                               'document_covenant_id':covenant.id})
            self.write(cr, uid, [covenant.id], {'chk_acta_cierre':True})
        return True

    _columns = dict(
        chk_covenant = fields.boolean('Doc.Convenio Adjunto'),
#        data_contract_fname = fields.char('Doc.Contrato',size=256),
        supervisory = fields.many2one('res.users', 'Fiscalizador'),
        cambiar_fiscalizador = fields.boolean('Cambiar Fiscalizador', 
                                              help="Marque esta casilla si desea cambiar el fiscalizador del Contrato"),
        fecha_inicio = fields.date('Fecha Inicio'),
        seq_stage = fields.integer('Secuencia', help="Da el orden de la secuencia cuando se muestra una lista de etapas"),                             
        fecha_terminacion = fields.date('Fecha Terminación'),
        data_acta_cierre = fields.binary('Doc.Acta de Cierre'),
        data_acta_cierre_fname = fields.char('Doc.Designación Fiscalizador',size=256),
        chk_acta_cierre = fields.boolean('Doc.Acta de Cierre Adjunto'),
        prf_ids = fields.many2many('crossovered.budget.certificate','cov_pr_rel','c_id','pr_id','Docs. Presupuestarios'),
        directory_id = fields.many2one('document.directory', 'Directorio', readonly=True),
        stage_secretary_notes = fields.text('Notas'),
        distribucion_users = fields.many2many('res.users', 'c_u_id','c_id','u_id', 
                                              'Distribucion de Documentos'),
        data_covenant_fname = fields.char('Doc.Convenio',size=256),
        observaciones = fields.text('Observaciones'),
        state = fields.selection([('draft', 'Borrador'),
                                  ('legalizing', 'Abierto'),
                                  ('open', 'Distribución'),
                                  ('execution', 'Ejecución'),
                                  ('cancelled', 'Anulado'), 
                                  ('done', 'Finalizado')], 'Estado', 
                                 readonly=True, required=True),
        user_id = fields.many2one('res.users', 'Creado por', select=1, readonly=True),
        creation_date = fields.datetime('Fecha creación', select=True, readonly=True),
        expedient_id = fields.many2one('doc_expedient.expedient', 'Trámite Relacionado', 
                                       help="Trámite relacionado, si no selecciona uno,este se creará automaticamente"),
        code_covenant = fields.char('Código', size=64),
        year  = fields.char(string='Año', size=64),
        subscription_date = fields.date('Fecha Suscripción'),
        name = fields.char('Descripcion', size=512, required="True"),
        #owner = fields.function(_is_user, store=False, string='Propietario', type='boolean', help="Indica que el usuario actual del sistema sea el mismo que el que creo el convenio"),
        department_id = fields.many2one('hr.department', 'Unidad Req.'),
        term = fields.char('Plazo Entrega(dias)', size=64),
        crossovered_budget_certificate_id = fields.many2one('crossovered.budget.certificate', 
                                                            'Cert. Presupuestaria', select=1),
        firma_contratista = fields.boolean('Contraparte'),
        firma_max = fields.boolean('Máxima Autoridad / Delegado'),
        delegado = fields.many2one('hr.employee','Delegado',
                                   help="Ingrese el nombre de la Máxima Autoridad delegada"),
        payment_term_id = fields.many2one('account.payment.term','Terminos de pago'),
        payment_lines = fields.one2many('contract.payment.line','covenant_id','Plan de Pagos'),
        historial_lines = fields.one2many('doc.covenant.historial', 'covenant_id', 'Historial'),
        admin_uid = fields.many2one('res.users', 'Administrador', select=1),
        cambiar_administrador = fields.boolean('Cambiar Admin.Convenio', 
                                               help="Marque esta casilla si desea cambiar el Administrador del Convenio"),
        dispatch_office_number = fields.char('Nro. Oficio Despacho', size=64),
        date_received = fields.date('Fecha Recepción'),
        data_contract = fields.binary('Doc.Convenio'),

        info_general = fields.function(_is_group_dpto_legal_cv, store=False, 
                                        string='Dpto. Legal', type='boolean', 
                                        help="Indica que el usuario es del grupo Dpto. Legal"),
        distribucion_cv = fields.function(_is_group_distribucion_cv, store=False, 
                                          string='Distribucion', type='boolean',
                                          help="Indica que el usuario es del grupo Distribución"),
        fiscalizacion_cv = fields.function(_is_group_fiscalizacion_cv, store=False, 
                                           string='Fiscalizacion', type='boolean',
                                           help="Indica que el usuario es del grupo Ficalización"),
        not_stage = fields.function(_is_not_stage_cv, store=False, 
                                    string='No pertenece a ninguna Etapa', type='boolean', 
                                    help="Indica que el usuario no pertenece a ninguna etapa del convenio"),
        owner_cv = fields.function(_is_user_cv, 
                                   store=False, string='Propietario', 
                                   type='boolean',
                                   help="Indica que el usuario actual del sistema sea el mismo que el que creo el contrato"),
        expedient_ids = fields.one2many('doc_expedient.expedient', 'covenant_id', 'Trámites'),

        doc_covenant_stage_id = fields.many2one('doc_covenant.stage', 'Etapa', readonly=True),
#        state_stage = fields.function(_is_state_stage, store=False, string='Estado de la Etapa', type='char', help="Indica que el usuario participa en el Trámite"),
        #state_planning = fields.selection([('open', 'Abierto'),('completed', 'Completado'),('done', 'Realizado'),], 'Estado Planificacion', readonly=True),
        #stage_planning_notes = fields.text('Notas'),
        state_stage_planning = fields.many2one('doc_covenant.state', 'Estado'),
        state_stage_syndicate = fields.many2one('doc_covenant.state', 'Estado'),
        state_stage_secretary = fields.many2one('doc_covenant.state', 'Estado'),
        state_stage_fiscalizacion = fields.many2one('doc_covenant.state', 'Estado'),
        doc_covenant_type_id = fields.many2one('doc_covenant.type', 'Tipo de convenio', required=True),
        doc_contract_type_id = fields.integer('Tipo de convenio', required=False),
        doc_contract_modality_id = fields.integer('Modalidades', required=False),
        subscription_date_covenant = fields.date('Fecha Suscripción'),
        other_type = fields.char('Otro Tipo', size=64),
        chk_other_type = fields.boolean('Otro tipo de convenio', help="Muestra el campo otro tipo de convenio"),
        compromised_contribution_company = fields.float('Económico'),
        total_compromised_contribution_company = fields.float('Total'),
        obs = fields.char('Observaciones',size=256),
        compromised_contribution_counterpart = fields.float('Económico'),
        total_compromised_contribution_counterpart = fields.float('Total'),
        obs1 = fields.char('Observaciones',size=256),
        amount = fields.float('Monto Total (Sin IVA)'),
        contribution_made_company = fields.float('GPA'),
        contribution_made_counterpart = fields.float('Contraparte'),
        final_amount = fields.float('Monto Final'),
        
        stage_contract = fields.selection([('draft', 'Borrador'),('planning', 'Planificacion'),('syndicate', 'Sindicatura'),('secretary', 'Secretaria'),('fiscalizacion', 'Fiscalizacion'),
                                           ('finish', 'Finalizado') ], 'Etapa Contrato'),
        ubication_cv_ids = fields.one2many('doc_covenant.ubication', 'covenant_id', 'Ubicaciones'),
        amount_total_invoice = fields.function(_amount_all_cinvoice, digits_compute= dp.get_precision('Account'), 
                                               string='Total Facturas(Sin IVA)',store=True,multi="sums_c"),
        amount_extra = fields.function(_amount_all_cinvoice, digits_compute= dp.get_precision('Account'), 
                                       string='Total Extra(Sin IVA)',store=True,multi="sums_c"), 
        #state_stage = fields.related('doc_contract_stage_id','seq_stage', type='integer', string='Secuencia de la Etapa'),
        beneficiary_ids = fields.one2many('doc_covenant.beneficiary', 'covenant_id', 'Beneficiarios del Convenio'),
        
        #        beneficiary_ids = fields.many2many('doc_covenant.beneficiary', 'covenant_beneficiary_rel', 'covenant_id', 'beneficiary_id', 'Referencia con Trámites'),
        beneficiary_covenant_ids = fields.one2many('covenant_beneficiary.rel', 'covenant_id', 'Beneficiarios del Convenio'),
        document_ids = fields.one2many('ir.attachment', 'document_covenant_id', 'Documentos Convenios'),
        partial_delivery_certificate = fields.date('Acta Entrega Parcial'),
        provicional_final_certificate = fields.date('Acta Provisional-Definitiva'),
        termination_certificate = fields.date('Acta de Terminación'),

        
    )
    
    _constraints = [
        (_check_subscription_date, 
         '¡El campo "% Fecha Suscripcion" debe ser menor o igual a la fecha actual!',
         ['% subscription_date']),
        ]

    _order = "creation_date desc"
    _defaults = dict(
        user_id = lambda self, cr, uid, ctx:uid,
        state = 'draft',
        #doc_covenant_stage_id = 1,
        info_general = __group_info_general,        
        owner_cv = True, 
        creation_date = lambda *a: strftime('%Y-%m-%d %H:%M:%S'),        
    )

doc_covenant_covenant()

class PaymentLine(osv.Model):
    _inherit = 'contract.payment.line'
    _columns = {
        'covenant_id': fields.many2one('doc_covenant.covenant', 'Convenio'),
        }


class doc_covenant_historial(osv.osv):
    _name = 'doc.covenant.historial'
    _columns = dict(             
        name = fields.char('Descripción', size=256),
        fecha_hora = fields.datetime('Fecha - Hora'),
        usuario = fields.many2one('res.users', 'Usuario'),
        covenant_id = fields.many2one('doc_covenant.covenant', 'Convenio'),
    )
doc_covenant_historial()

class doc_covenant_stage(osv.osv):
    _name = "doc_covenant.stage"
    
    def unlink(self, cr, uid, ids, *args, **kwargs):
        for conv_stage in self.browse(cr, uid, ids):
            raise osv.except_osv('Operación no Permitida  !', '¡No se puede eliminar las etapas del convenio!')
        return super(doc_covenant_stage, self).unlink(cr, uid, ids, *args, **kwargs)
          
    _columns = dict(

        name = fields.char('Nombre', size=64, required=True),
        desc = fields.text('Descripcion'),
        user_id = fields.many2one('res.users', 'Usuario responsable', select=1),
        #user_ids = fields.one2many('res.users', 'stage_id', 'Usuarios responsables', readonly=False),
        state_ids = fields.one2many('doc_covenant.state', 'stage_id', 'Estados de las etapas', readonly=False),
    )
    _order = 'seq_stage'
    
doc_covenant_stage()


class doc_covenant_state(osv.osv):
    _name = "doc_covenant.state"
    _columns = dict(
        seq_state = fields.integer('Secuencia', required=True, help="Da el orden de la secuencia cuando se muestra una lista de estados"),                               
        name = fields.char('Name', size=64, required=True),
        stage_id = fields.many2one('doc_covenant.stage', 'Etapas', readonly=True),
        stage_sequence = fields.related('stage_id','seq_stage', type='integer', string='Secuencia de la Etapa'),
    )
    _order = 'seq_state'
doc_covenant_state()


class Doc_Expedient_Expedient(osv.osv):
    _inherit = "doc_expedient.expedient"
    _columns = dict(                   
        covenant_id = fields.many2one('doc_covenant.covenant', 'Convenio', readonly=True),
    )
Doc_Expedient_Expedient()


class doc_covenant_type(osv.osv):
    _name = 'doc_covenant.type'
    _columns = dict(
        #code = fields.char('Codigo', size=64, required="True"),
        name = fields.char('Nombre', size=64, required="True"),
        desc = fields.text('Descripcion'),
    )
doc_covenant_type()


class Ir_Attachment(osv.osv):
    _inherit = 'ir.attachment'
    _columns = dict(
        document_covenant_id = fields.many2one('doc_covenant.covenant', 'Convenio', readonly=True),
   )
Ir_Attachment()

class doc_covenant_beneficiary(osv.osv):
    
    def onchange_parish(self, cr, uid, ids, context=None):
        return {'value':{'parroquia':''}}
    
    _name = 'doc_covenant.beneficiary' 
    _columns = dict(
        name = fields.char('Descripción', size=64, required=True),
        representative = fields.char('Representante', size=64,required=True),
        canton = fields.many2one('res.country.state.canton', 'Canton',required=True),
        parroquia = fields.many2one('res.country.state.parish', 'Parroquia',required=True),
        covenant_id = fields.many2one('doc_covenant.covenant', 'Convenio'),
    )
doc_covenant_beneficiary()

class covenant_beneficiary_rel(osv.osv):
    _name = 'covenant_beneficiary.rel'
    
    def write(self, cr, uid, ids, vals, context=None):
        now_date = time.strftime('%Y-%m-%d')
        res = super(covenant_beneficiary_rel,self).write(cr, uid, ids, vals, context)
        for cov_benef_rel in self.browse(cr, uid, ids):
            if cov_benef_rel.economic < 0 or cov_benef_rel.total < 0 or cov_benef_rel.realized < 0:
                raise osv.except_osv(('Mensaje de Advertencia!'), ('¡Existen valores negativos ingresados en la pestaña "Beneficiarios y Obras" !'))      
        return res
    
    
    def unlink(self, cr, uid, ids, *args, **kwargs):
        for conv in self.browse(cr, uid, ids):
            raise osv.except_osv('Operación no Permitida  !', '¡No se puede eliminar estos registros!')
        return super(covenant_beneficiary_rel, self).unlink(cr, uid, ids, *args, **kwargs)
    
    
    _columns = dict(
        beneficiary_id = fields.many2one('doc_covenant.beneficiary', 'Beneficiario'),
        name = fields.char('Descripción', size=64),
        economic = fields.float('Económico'),
        total = fields.float('Total'),
        realized = fields.float('Realizado'),
        works_ids = fields.one2many('doc_covenant.work', 'beneficiary_id', 'Obras', readonly=False),
        covenant_id = fields.many2one('doc_covenant.covenant', 'Convenio', readonly=True),
    )
covenant_beneficiary_rel()

class doc_covenant_ubication(osv.osv):
    _name = 'doc_covenant.ubication'
    
    def onchange_parish(self, cr, uid, ids, context=None):
        return {'value':{'parroquia':''}}
    
    _columns = dict(      
        name = fields.char('Nombre', size=64),
        canton = fields.many2one('res.country.state.canton', 'Canton'),
        parroquia = fields.many2one('res.country.state.parish', 'Parroquia'),
        comunidad = fields.char('Comunidad', size=64),
        covenant_id = fields.many2one('doc_covenant.covenant', 'Contrato', select=1),
        #contract_state = fields.related('contract_id','state', type='selection', selection = [('draft', 'Borrador'),
         #                         ('open', 'En Progreso'),
          #                        ('cancelled', 'Anulado'), 
           #                       ('done', 'Finalizado')], string='Estado del Contrato', 
            #                      readonly=True, store=True,),
    )
doc_covenant_ubication()



class doc_covenant_work(osv.osv):
    _name = 'doc_covenant.work'
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(doc_covenant_work,self).write(cr, uid, ids, vals, context)
        for cov_work in self.browse(cr, uid, ids):
            if cov_work.economic < 0 or cov_work.total < 0 or cov_work.realized < 0:
                raise osv.except_osv(('Mensaje de Advertencia!'), ('¡Existen valores negativos ingresados en "Obras de Beneficiarios"!'))          
        return res
    
    def create(self, cr, uid, vals, context=None):
        now_date = time.strftime('%Y-%m-%d')
        economic = vals['economic']
        total = vals['total']
        realized = vals['realized']
        if economic < 0 or total < 0 or realized < 0:
            raise osv.except_osv(('Mensaje de Advertencia!'), ('¡Existen valores negativos ingresados en la pestaña "Beneficiarios y Obras" !'))     
        res_id = super(doc_covenant_work, self).create(cr, uid, vals, context=context)
        return res_id
    
        
    _columns = dict(
        name = fields.char('Obra', size=64, required=True),
        economic = fields.float('Económico'),
        total = fields.float('Total'),
        realized = fields.float('Realizado'),
        partial_delivery_date = fields.date('Fecha entrega parcial'),
        provisional_date_final = fields.date('Fecha provis defin.'),
        state = fields.selection([('pending', 'Pendiente'),('execution', 'En Ejecución'),
                                           ('done', 'Concluido'),], 'Estado'),
        beneficiary_id = fields.many2one('covenant_beneficiary.rel', 'Beneficiario', readonly=True),
    )
doc_covenant_work()


















# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
