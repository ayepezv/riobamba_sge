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
from lxml import etree
from datetime import datetime, date
from string import upper
import datetime
import zipfile
import os
import base64
import StringIO
from tools import ustr
import decimal_precision as dp


class contract_payment_line(osv.Model):
    _name = 'contract.payment.line'
    _columns = dict(
        desc = fields.char('Descripción',size=32),
        date = fields.date('Fecha'),
        amount = fields.float('Monto'),
        partner_id = fields.related('contract_id','partner_id',type="many2one",relation='res.partner',string='Contratista',store=True),
        contract_id = fields.many2one('doc_contract.contract','Contrato'),
        )
contract_payment_line()

class doc_contract_contract(osv.osv):
    _name = "doc_contract.contract"

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            #if record.employee_id.employee_lastname and record.employee_id.name:
            #    name = '%s %s' % (record.employee_id.employee_lastname, record.employee_id.name)
                name = record.codigo_contrato + " - " + record.name
                res.append((record.id, name))
        return res
        
    def abrir_contrato(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        obj_historial = self.pool.get('doc.contract.historial')
        contract_obj = self.pool.get('doc_contract.contract')
        payment_term_obj = self.pool.get('account.payment.term')
        term_line = self.pool.get('contract.payment.line')
        for contract in self.browse(cr, uid, ids, context):
            c_ids = contract_obj.search(cr, uid, 
                                        [('codigo_contrato','=',contract.codigo_contrato),
                                         ('state','!=','cancelled')])
            if len(contract.ubication_ids) < 1 or len(contract.payment_lines) < 1:
                raise osv.except_osv('Mensaje de Error !', 
                                     'Debe por lo menos registrar una localidad y un pago')
            aux = 0
            for p_line in contract.payment_lines:
                aux += p_line.amount
            if not round(aux,2)==round(contract.amount,2):
                raise osv.except_osv('Mensaje de Error !', 'El detalle de pagos debe ser igual al monto de contrato')
            if len(c_ids)>1:
                raise osv.except_osv('Mensaje de Error !', 'El código de contrato debe ser único')
            if contract.chk_notify_admin:
                self.action_send_mail(cr, uid, ids, context)
                sql = "UPDATE doc_contract_contract set chk_notify_admin='%s' WHERE id=%s" % (False, contract.id)
                cr.execute(sql)
            if not contract.user_id:
                self.write(cr, uid, [contract.id], {'user_id':uid}, context)
            elif contract.user_id.id != uid:
                raise osv.except_osv('Mensaje de Error !', 'El usuario actual no puede iniciar el contrato')
            self.create_directory(cr, uid, ids, context)              
            self.write(cr, uid, [contract.id],{'state': 'legalizing'})
            hid = obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                                 'usuario':uid,
                                                 'name':'Contrato Iniciado',
                                                 'contract_id':contract.id})
            #crear la lineas de obligaciones a pagar en base al monto y terminos de pago
#            totlines = payment_term_obj.compute(cr,
#                                                uid, contract.payment_term_id.id, contract.amount, #contract.subscription_date or False, context=context)
 #           j = 0
 #           for line in totlines:
 #               j += 1
 #               term_line.create(cr, uid, {
 #                       'num' :j,
 #                       'date':line[0],
 #                       'amount':line[1],
 #                       'contract_id':contract.id,
 #                       })
        return True
    
    
    def finalizar_etapa_legalizacion(self, cr, uid, ids, context=None):
        obj_historial = self.pool.get('doc.contract.historial')
        for contract in self.browse(cr, uid, ids):
            aux = 0
            for p_line in contract.payment_lines:
                aux += p_line.amount
#            if not aux==contract.amount:
#                raise osv.except_osv('Mensaje de Error !', 'El detalle de pagos debe ser igual al monto de contrato')
            if contract.firma_contratista==False or contract.firma_max==False:
                raise osv.except_osv('Mensaje de Error !', 'No se han completado el registro de firmas correspondientes')
            self.write(cr, uid, [contract.id],{'state':'open'})
            hid = obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                                 'usuario':uid,
                                                 'name':'Finaliza etapa legalización',
                                                 'contract_id':contract.id})            
        return True
    
    
    def create_directory(self, cr, uid, ids, context=None):
        obj_document_directory = self.pool.get('document.directory')
        obj_ir_attachment = self.pool.get('ir.attachment')
        for contract in self.browse(cr, uid, ids, context):
            dir_contract = obj_document_directory.search(cr, uid, [('name','=','Contratos')], limit=1)
            if dir_contract:
                pid = obj_document_directory.create(cr, uid, {'name' : 'Contrato - ' + str(contract.codigo_contrato),
                                       'parent_id' : dir_contract[0],
                                       'user_id' : None})
                self.write(cr, uid, [contract.id], {'directory_id': pid})
            else:
                raise osv.except_osv('Mensaje de Advertencia !', 'No existe el directorio padre "Contratos"')       
        return True
        
    
    def action_open_draft(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'draft'})
    
    
    def action_open_cancelled(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'cancelled'})
        
            
    def action_open_done(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'done'})
        
    
    def write(self, cr, uid, ids, vals, context=None):
        #pdb.set_trace()
        now_date = time.strftime('%Y-%m-%d')
        obj_attachment = self.pool.get('ir.attachment')
        obj_historial = self.pool.get('doc.contract.historial')
        obj_employee = self.pool.get('hr.employee')
        res = super(doc_contract_contract,self).write(cr, uid, ids, vals, context)
        for contract in self.browse(cr, uid, ids):
            if contract.chk_notify_admin and contract.cambiar_administrador:
                user_obj = self.pool.get('res.users')
                user = user_obj.browse(cr, uid, contract.admin_uid.id)
                try:
                    employee_id = obj_employee.search(cr, uid, [('user_id','=',contract.admin_uid.id)])[0]
                except IndexError:
                    raise osv.except_osv(('Mensaje de Error !'), ('El usuario %s Administrador del Contrato no esta relacionado a un empleado del sistema') %(user.name))
                employee = obj_employee.browse(cr, uid, employee_id)
                if not(employee.department_id.id and employee.job_id.id):
                    raise osv.except_osv('Mensaje de Error !', 'El usuario Administrador del Contrato no esta relacionado a un empleado del sistema')   
                sql = "UPDATE doc_contract_contract set chk_notify_admin='%s',cambiar_administrador='%s' WHERE id=%s" % (False, False, contract.id)
                cr.execute(sql)
                hid = obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                                 'usuario':uid,
                                                 'name':'Cambio de administrador',
                                                 'contract_id':contract.id})
            if contract.fecha_inicio:
                if not contract.fecha_inicio >= contract.subscription_date:
                    raise osv.except_osv(('Mensaje de Error'), ('La Fecha Inicio debe ser mayor o igual a la Fecha Suscripción'))
            if contract.fecha_notif_anticipo:
                if not contract.fecha_notif_anticipo >= contract.subscription_date:
                    raise osv.except_osv(('Mensaje de Error'), ('La Fecha Notif.Anticipo debe ser mayor o igual a la Fecha Suscripción'))
            if contract.fecha_terminacion:
                if not contract.fecha_terminacion >= contract.fecha_inicio:
                    raise osv.except_osv(('Mensaje de Error'), ('La Fecha Terminación debe ser mayor o igual a la Fecha Inicio'))
            if contract.fecha_cumplimiento:
                if not contract.fecha_cumplimiento >= contract.fecha_inicio:
                    raise osv.except_osv(('Mensaje de Error!'), ('La Fecha Cumplimiento debe ser mayor o igual a la Fecha Inicio'))                 
        return res
    
    
    def action_send_mail(self, cr, uid, ids, context=None):
        template_obj = self.pool.get('email.template')
        model_obj = self.pool.get('ir.model')
        for contract in self.browse(cr, uid, ids, context):
            model = model_obj.search(cr, uid, [('model','=','doc_contract.contract')],limit=1)
            for mod in model:
               modelo = model_obj.browse(cr, uid, mod)
               template_ids = template_obj.search(cr, uid, [('model_id','=',mod)],limit=1)
               for template_id in template_ids:
                  template_obj.send_mail(cr, uid,
                                         template_id,
                                         contract.id, context=context)
        return True
    
    
    def registrar_firma_contratista(self, cr, uid, ids, context=None):
        obj_historial = self.pool.get('doc.contract.historial')
        obj_employee = self.pool.get('hr.employee')
        for contract in self.browse(cr, uid, ids, context):
            try:
                employee_id = obj_employee.search(cr, uid, [('user_id','=',contract.user_id.id)])[0]
            except IndexError:
                raise osv.except_osv('Mensaje de Error !', '¡El usuario actual no esta relacionado a un empleado del sistema!')
            employee = obj_employee.browse(cr, uid, employee_id)
            self.write(cr, uid, [contract.id], {'firmas':'contratista',
                                                'firma_max':True,'firma_contratista':False}, context)
            hid = obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                                 'usuario':uid,
                                                 'name':'Registro firma contratista',
                                                 'contract_id':contract.id})
        return True
    
    
    def registrar_firma_max_autoridad(self, cr, uid, ids, context=None):
        obj_historial = self.pool.get('doc.contract.historial')
        obj_employee = self.pool.get('hr.employee')
        for contract in self.browse(cr, uid, ids, context):
            try:
                employee_id = obj_employee.search(cr, uid, [('user_id','=',contract.user_id.id)])[0]
            except IndexError:
                raise osv.except_osv('Mensaje de Error !', '¡El usuario actual no esta relacionado a un empleado del sistema!')
            employee = obj_employee.browse(cr, uid, employee_id)
            self.write(cr, uid, [contract.id], {'firmas':'max_autoridad',
                                                'firma_max':False}, context)
            hid = obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                                 'usuario':uid,
                                                 'name':'Registro firma máxima autoridad / delegado',
                                                 'contract_id':contract.id})
        return True
    
    
    def create(self, cr, uid, vals, context=None):
        obj_employee = self.pool.get('hr.employee')
        amount = vals['amount']
        if amount <= 0:
            raise osv.except_osv(('Mensaje de Advertencia!'), ('¡El monto ingresesado debe ser mayor que 0!'))
        obj_sequence = self.pool.get('ir.sequence')
 #       code = obj_sequence.get(cr, uid, 'seq.doc.contract')
 #       vals.update({'code': code})
        #saca el empleado del usuario creador
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        try:
            employee_id = user.employee_id.id
        except IndexError:
            raise osv.except_osv(('Mensaje de Error !'), ('El usuario %s Administrador del Contrato no esta relacionado a un empleado del sistema') % (user.name))
        solicitant_id = obj_employee.browse(cr, uid, employee_id)
        if not solicitant_id.department_id.id and solicitant_id.job_id.id:
            raise osv.except_osv('Mensaje de Error !', 'El usuario creador no tiene departamento y/o cargo')
        #Si no hay el tramite lo crea, con la tarea
        resumen = 'Contrato creado: ' + vals['codigo_contrato'] + '. ' 
        res_id = super(doc_contract_contract, self).create(cr, uid, vals, context=context)
        return res_id
    
    
    def unlink(self, cr, uid, ids, *args, **kwargs):
        for contract in self.browse(cr, uid, ids):
            if contract.state != 'draft':
                raise osv.except_osv('Operación no Permitida  !', '¡No se puede eliminar los contratos iniciados!')
        return super(doc_contract_contract, self).unlink(cr, uid, ids, *args, **kwargs)
    
    
    def zip_doc_contract(self, cr, uid, ids, context=None):
        obj_doc_directory = self.pool.get('document.directory')
        obj_ir_attachment = self.pool.get('ir.attachment')
        obj_doc_storage = self.pool.get('document.storage')
        for contract in self.browse(cr, uid, ids):
            dir_temp = "/home/openerp/"+contract.directory_id.name
            zf = zipfile.ZipFile(dir_temp + ".zip", "w")
            sub_directory_ids = obj_doc_directory.search(cr, uid, [('parent_id','=',contract.directory_id.id)])
            if sub_directory_ids:
                for sub_directory in obj_doc_directory.browse(cr, uid, sub_directory_ids):
                    #Tomamos el path del Medio de Almacenamiento del directorio
                    path_storage = obj_doc_storage.browse(cr, uid, sub_directory.storage_id.id).path
                    document_ids = obj_ir_attachment.search(cr, uid, [('parent_id','=',sub_directory.id)])
                    for document in obj_ir_attachment.browse(cr, uid, document_ids):
                        #ruta ="/home/javier/openerp/openerp_6.1/server/openerp/filestore/dev_gpa/"
                        ruta = path_storage + '/' + contract.directory_id.name + '/' + sub_directory.name + '/'
                        archivo = document.datas_fname
                        print "RUTAAAAAAAAAAAAA", ruta
                        zf.write(os.path.join(ruta, archivo), os.path.basename(archivo), zipfile.ZIP_DEFLATED)
                zf.close()    
                #comprimido = open(contract.directory_id.name + ".zip","rb").read().encode("base64")
                #self.write(cr, uid, [contract.id], {'datas':comprimido,'chk_zip':True})
                #dirname = "/home/openerp"
                #filename = contract.directory_id.name + ".zip"
                #print filename
                #pathname = os.path.abspath(os.path.join(dirname, filename))
                #if pathname.startswith(dirname):
                 #  os.remove(pathname)
            #os.system("rm "+contract.directory_id.name + ".zip")
        return True
    
            
    def finalizar_etapa_distribucion(self, cr, uid, ids, context=None):
        obj_employee = self.pool.get('hr.employee')
        obj_historial = self.pool.get('doc.contract.historial')
        for contract in self.browse(cr, uid, ids):
            if len(contract.distribucion_users) < 1:
                raise osv.except_osv('Mensaje de Error !', 
                                     'Debe por lo menos dsitribuir a un usuario los documentos')
            if not (contract.date_received):
                raise osv.except_osv('Mensaje de Error !', 
                                     'El campo "Fecha Recepción" es obligatorio..')
            if not (contract.dispatch_office_number):
                raise osv.except_osv('Mensaje de Error !', 
                                     'El campo "Nro. Oficio Despacho" es obligatorio..')
            if not contract.chk_contrato:
                raise osv.except_osv('Mensaje de Error !',
                                     'No se ha adjuntado el archivo copia del contrato')
            if not contract.distribucion_users:
                raise osv.except_osv('Mensaje de Error !', 
                                     'Es necesario distribuir al menos a un usuario')
            # Crea una tarea para el administrador del contrato
            if not (contract.admin_uid):
                raise osv.except_osv('Mensaje de Error !', 'El campo "Administrador" es obligatorio..')
            try:
                employee_id = obj_employee.search(cr, uid, [('user_id','=',contract.admin_uid.id)])[0]
            except IndexError:
                raise osv.except_osv('Mensaje de Error !', 'El usuario Administrador del Contrato no esta relacionado a un empleado del sistema')
            employee = obj_employee.browse(cr, uid, employee_id)
            if not (employee.department_id.id and employee.job_id.id):
                raise osv.except_osv('Mensaje de Error !', 'El usuario Administrador del Contrato no esta relacionado a un empleado del sistema')
            # Distribución de Documentos
            for user in contract.distribucion_users:
                try:
                    employee_id = obj_employee.search(cr, uid, [('user_id','=',user.id)])[0]
                except IndexError:
                    raise osv.except_osv('Mensaje de Error !', 'El usuario actual no esta relacionado a un empleado del sistema')
                employee = obj_employee.browse(cr, uid, employee_id)
                if not (employee.department_id.id and employee.job_id.id): 
                    raise osv.except_osv('Mensaje de Error !', 'Usuario a distribuir no esta relacionado a un empleado del sistema')
            self.write(cr, uid, [contract.id],{'state':'execution'})
            hid = obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                                 'usuario':uid,
                                                 'name':'Finaliza etapa distribución',
                                                 'contract_id':contract.id})            
        return True
    
    
    def subir_contrato(self, cr, uid, ids, context=None):
        obj_ir_attachment = self.pool.get('ir.attachment')
        for contract in self.browse(cr, uid, ids):
            if contract.data_contract:
                obj_ir_attachment.create(cr, uid, {'parent_id':contract.directory_id.id,
                                                   'datas':contract.data_contract,
                                                   'name':'Contrato',
                                                   'datas_fname':contract.data_contract_fname,
                                                   'document_contract_id':contract.id})
            else:
                raise osv.except_osv('Mensaje de Error !', 'Debe seleccionar el documento de contrato a subir')

            self.write(cr, uid, [contract.id], {'chk_contrato':True,
                                                'data_contract':''})
        return True
    
    
    def subir_doc_acta_cierre(self, cr, uid, ids, context=None):
        obj_ir_attachment = self.pool.get('ir.attachment')
        for contract in self.browse(cr, uid, ids):
            obj_ir_attachment.create(cr, uid, {'parent_id':contract.directory_id.id,
                                               'datas':contract.data_acta_cierre,
                                               'name':'Acta de Cierre',
                                               'datas_fname':contract.data_acta_cierre_fname,
                                               'document_contract_id':contract.id})
            self.write(cr, uid, [contract.id], {'chk_acta_cierre':True})
        return True
    
        
    def onchange_admin_uid(self, cr, uid, ids, admin_uid, context=None):
        flag_notify = True
        for contract in self.browse(cr, uid, ids, context):
            flag_notify = False
            if admin_uid:   
                if contract.admin_uid.id != admin_uid and contract.state == 'execution':
                    flag_notify = True
                else:
                    flag_notify = False
            else:
                flag_notify = False
        return {'value':{'chk_notify_admin':flag_notify}}
    
        
    def finalizar_contrato(self, cr, uid, ids, context=None):
        obj_historial = self.pool.get('doc.contract.historial')
        for contract in self.browse(cr, uid, ids):
            if not contract.chk_acta_cierre:
                raise osv.except_osv('Mensaje de Error !', 'No se ha adjuntado el archivo Acta de cierre del contrato')
            self.write(cr, uid, [contract.id],{'state':'done'})
            hid = obj_historial.create(cr, uid, {'fecha_hora':time.strftime('%Y-%m-%d %H:%M:%S'),
                                                 'usuario':uid,
                                                 'name':'Contrato Finalizado',
                                                 'contract_id':contract.id})
            return True
        
        
    def _get_year(self, cr, uid, context=None):
        year_actual = datetime.datetime.today().year
        return year_actual
    
        
    def _is_user(self, cr, uid, ids, field_name, arg, context=None):
    #Método que devuelve “True” si el usuario actual es el mismo que el que creo el trámite, caso
    #contrario devolverá “False”
        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            if contract.user_id.id == uid:
                res[contract.id] = True
            else:
                res[contract.id] = False
        return res
    
    
    def _is_admin_contract(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            if contract.admin_uid.id == uid:
                res[contract.id] = True
            else:
                res[contract.id] = False
        return res
    
    
    def _is_group_info_general(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        m  = self.pool.get('ir.model.data')
        for contract in self.browse(cr, uid, ids, context=context):
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_ct_info_general').id
            user = self.pool.get('res.users').browse(cr, uid, uid)
            if group_id in [g.id for g in user.groups_id]:
                res[contract.id] = True
            else:
                res[contract.id] = False
        return res
    
    def __group_info_general(self, cr, uid, context=None):
        #pdb.set_trace()
        res = {}
        m  = self.pool.get('ir.model.data')
        obj_user = self.pool.get('res.users')
        group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_ct_info_general').id
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if group_id in [g.id for g in user.groups_id]:
            res = True
        else:
            res = False
        return res
    
    
    def __perfil_info_general(self, cr, uid, context=None):
        res = {}
        m  = self.pool.get('ir.model.data')
        obj_user = self.pool.get('res.users')
        group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_ct_info_general').id
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if group_id in [g.id for g in user.groups_id]:
            res = 'info_general'
        else:
            res = False
        return res
    
    
    def _is_group_distribucion(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        m  = self.pool.get('ir.model.data')
        for contract in self.browse(cr, uid, ids, context=context):
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_ct_distribucion').id
            user = self.pool.get('res.users').browse(cr, uid, uid)
            if group_id in [g.id for g in user.groups_id]:
                res[contract.id] = True
            else:
                res[contract.id] = False
        return res
    
    
    def _is_group_ejecucion(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        m  = self.pool.get('ir.model.data')
        for contract in self.browse(cr, uid, ids, context=context):
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_ct_ejecucion').id
            user = self.pool.get('res.users').browse(cr, uid, uid)
            if group_id in [g.id for g in user.groups_id]:
                res[contract.id] = True
            else:
                res[contract.id] = False
        return res
    
    
    def _is_not_perfil(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        info_general = False
        distribucion = False
        ejecucion = False
        m  = self.pool.get('ir.model.data')
        for contract in self.browse(cr, uid, ids, context=context):
            user = self.pool.get('res.users').browse(cr, uid, uid)
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_ct_ejecucion').id
            if group_id in [g.id for g in user.groups_id]:
                ejecucion = True
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_ct_distribucion').id
            if group_id in [g.id for g in user.groups_id]:
                distribucion = True
            group_id = m.get_object(cr, uid, 'gt_document_manager', 'group_ct_info_general').id
            if group_id in [g.id for g in user.groups_id]:
                info_general = True    
            if info_general or distribucion or ejecucion:
                res[contract.id] = False
            else:
                res[contract.id] = True
        return res
    
    
    def get_perfil_usuario(self, cr, uid, ids, field_name, arg, context=None):
        #pdb.set_trace()
        res = {}
        m  = self.pool.get('ir.model.data')
        for contract in self.browse(cr, uid, ids, context=context):
            if contract.info_general:
                res[contract.id] = 'info_general'
            if contract.distribucion:
                res[contract.id] = 'distribucion'
            if contract.ejecucion:
                res[contract.id] = 'ejecucion'
            if contract.not_perfil:
                res[contract.id] = 'not_perfil'        
        return res
          
         
    def onchange_objeto(self, cr, uid, ids, context=None):        
        return {'value':{'procedimiento':''}}
       
    def _amount_all_cinvoice(self, cr, uid, ids, field_name, arg, context=None):
        '''    Calcula el valor de facturas y el extra del contrato
        '''
        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            res[contract.id] = {
                'amount_total_invoice': 0.0,
                'amount_extra': 0.0,
            }
            total_invoice = total_extra = 0
            for invoice in contract.invoice_ids:
                total_invoice += invoice.amount_pay
            if total_invoice > contract.amount:
                total_extra = total_invoice - contract.amount
            res[contract.id]['amount_total_invoice']=total_invoice
            res[contract.id]['amount_extra']=total_extra
        return res
    
     def _check_invoices(self, cr, uid, ids):
        result = True
        total = 0
        for obj in self.browse(cr, uid, ids):
            for invoice in obj.invoice_ids:
                total += invoice.amount_total
            if total > obj.amount:
                result = False
        return result      

    _columns = dict(
        invoice_ids = fields.many2many('account.invoice', 'contract_invoice_rel', 'contract_id', 'invoice_id', 
                                       'Facturas Relacionadas', help="Facturas del contratista"),
        is_cp = fields.boolean('Viene de CP'),
        payment_lines = fields.one2many('contract.payment.line','contract_id','Plan de Pagos'),
        info_general = fields.function(_is_group_info_general, store=False, string='Info.General', type='boolean', help="Indica que el usuario es del grupo Info.General"),
        distribucion = fields.function(_is_group_distribucion, store=False, string='Distributión', type='boolean', help="Indica que el usuario es del grupo Distribución"),
        ejecucion = fields.function(_is_group_ejecucion, store=False, string='Ejecución', type='boolean', help="Indica que el usuario es del grupo Ejecución"),
        not_perfil = fields.function(_is_not_perfil, store=False, string='No pertenece a ningun perfil', type='boolean', help="Indica que el usuario no pertenece a ningun perfil de usuario de contratos"),
        perfil_usuario = fields.function(get_perfil_usuario, method=True, store=False, string='Perfil Usuario', 
                                type='selection', selection=[('info_general', 'Información General'),
                                                             ('distribucion', 'Distribución'),
                                                             ('ejecucion', 'Ejecución'),
                                                             ('not_perfil', 'Ningún Perfil')],
                                help="Campo funcion que que obtiene el perfil del usuario actual del sistema, NO se almacena en la base de datos"),
        name = fields.char('Descripción', size=512, required=True),
        owner = fields.function(_is_user, store=False, string='Propietario', type='boolean', help="Indica que el usuario actual del sistema sea el mismo que el que creo el contrato"),
        admin_contract = fields.function(_is_admin_contract, store=False, string='Admin.Contrato', type='boolean', help="Indica que el usuario actual del sistema es el Administrador del Contrato"),
        code = fields.char('Código', size=64),
        codigo_contrato = fields.char('Código', size=32),
        datas = fields.binary('Archivo zip'),  
        year  = fields.char(string='Año', size=64),
        partner_id = fields.many2one('res.partner', 'Contratista', select=1),
        amount = fields.float('Monto Total (Sin IVA)'),
        amount_total_invoice = fields.function(_amount_all_cinvoice, digits_compute= dp.get_precision('Account'), 
                                               string='Total Facturas(Sin IVA)',store=True,multi="sums_c"),
        amount_extra = fields.function(_amount_all_cinvoice, digits_compute= dp.get_precision('Account'), 
                                       string='Total Extra(Sin IVA)',store=True,multi="sums_c"),
        term = fields.char('Plazo Entrega(dias)', size=64),
        user_id = fields.many2one('res.users', 'Creado por', select=1, readonly=True),
        admin_uid = fields.many2one('res.users', 'Administrador', select=1),
        cambiar_administrador = fields.boolean('Cambiar Admin.Contrato', 
                                               help="Marque esta casilla si desea cambiar el Administrador del Contrato"),
        cambiar_fiscalizador = fields.boolean('Cambiar Fiscalizador', 
                                               help="Marque esta casilla si desea cambiar el fiscalizador del Contrato"),
        chk_notify_admin = fields.boolean('Notify Admin'),
        
        crossovered_budget_certificate_id = fields.many2one('crossovered.budget.certificate', 
                                                            'Cert. Presupuestaria', select=1),
        stage_user_id = fields.many2one('res.users', 'Usuario Asignado', select=1),
        state = fields.selection([('draft', 'Borrador'),
                                  ('legalizing', 'Abierto'),
                                  ('open', 'Distribución'),
                                  ('execution', 'Ejecución'),
                                  ('cancelled', 'Anulado'), 
                                  ('done', 'Finalizado')], 'Estado', 
                                  readonly=True, required=True),
        notes = fields.text('Notas'),
        document_ids = fields.one2many('ir.attachment', 'document_contract_id', 'Documentos Contratos'),
        warranty_ids = fields.one2many('doc_contract.warranty', 'contract_id', 'Garantias de los Contratos'),
        directory_id = fields.many2one('document.directory', 'Directorio', readonly=True),
        
        chk_zip = fields.boolean('Zip'),
        firmas = fields.selection([('contratista', 'Contratista'),
                                  ('max_autoridad', 'Máxima Autoridad / Delegado')], 'Firmas', 
                                  readonly=True),
        firma_contratista = fields.boolean('Contratista'),
        firma_max = fields.boolean('Máxima Autoridad / Delegado'),
        delegado = fields.many2one('hr.employee','Delegado',
                                   help="Ingrese el nombre de la Máxima Autoridad delegada"),
         #doc_contract_stage_id = fields.many2one('doc_contract.stage', 'Etapa', readonly=True),
        #state_stage = fields.function(_is_state_stage, store=False, string='Estado de la Etapa', type='char', help="Indica que el usuario participa en el Trámite"),
        
        #state_stage_syndicate = fields.many2one('doc_contract.state', 'Estado'),
        #state_stage_secretary = fields.many2one('doc_contract.state', 'Estado'),
        #state_stage_fiscalizacion = fields.many2one('doc_contract.state', 'Estado'),
        #state_syndicate = fields.selection([('open', 'Abierto'),('completed', 'Completado'),('done', 'Realizado'),], 'Estado', readonly=True),
        #state_secretary = fields.selection([('open', 'Abierto'),('completed', 'Completado'),('done', 'Realizado'),], 'Estado', readonly=True),
        #state_fiscalizacion = fields.selection([('open', 'Abierto'),('completed', 'Completado'),('done', 'Realizado'),], 'Estado', readonly=True),
        stage_secretary_notes = fields.text('Notas'),
        observaciones_ejecucion = fields.text('Observaciones'),
        #stage_fiscalizacion_notes = fields.text('Notas'),
        subscription_date = fields.date('Fecha Suscripción'),
        fecha_cumplimiento = fields.date('Fecha Cumplimiento'),
        date_received = fields.date('Fecha Recepción'),
        dispatch_office_number = fields.char('Nro. Oficio Despacho', size=64),
        #stage_contract = fields.selection([('draft', 'Borrador'),('syndicate', 'Sindicatura'),('secretary', 'Secretaria'),('fiscalizacion', 'Fiscalizacion'),
         #                                  ('finish', 'Finalizado') ], 'Etapa Contrato'),
        ubication_ids = fields.one2many('doc_contract.ubication', 'contract_id', 'Ubicaciones'),
        vendor_payment_ids = fields.one2many('account.voucher', 'contract_id', 'Pagos Realizados'),
        department_id = fields.many2one('hr.department', 'Unidad Requirente'),
        data_contract = fields.binary('Doc.Contrato'),
        payment_term_id = fields.many2one('account.payment.term','Terminos de pago'),
        data_contract_fname = fields.char('Doc.Contrato',size=256),
        chk_contrato = fields.boolean('Doc.Contrato Adjunto'),
        
        data_acta_cierre = fields.binary('Doc.Acta de Cierre'),
        data_acta_cierre_fname = fields.char('Doc.Designación Fiscalizador',size=256),
        chk_acta_cierre = fields.boolean('Doc.Acta de Cierre Adjunto'),
        #designar_fiscalizador = fields.boolean('Designar Fiscalizador'),
        supervisory = fields.many2one('res.users', 'Fiscalizador'),
        other_commission = fields.text('Comision'),
        commission = fields.one2many('res.users', 'contract_commission_id', 'Comisión'),
        historial_lines = fields.one2many('doc.contract.historial', 'contract_id', 'Historial'),
        distribucion_users = fields.one2many('res.users', 'contract_distribution_id', 'Distribucion de Documentos'),
        percentage_advance = fields.float('% Anticipo'),
        #advance_amount = fields.float('Monto Anticipo'),
        fecha_inicio = fields.date('Fecha Inicio'),
        fecha_notif_anticipo = fields.date('Fecha Notif.Anticipo'),
        fecha_terminacion = fields.date('Fecha Terminación'),
        justification = fields.char('Justificativo de Anulación', size=128, readonly=True),
        creation_date = fields.datetime('Fecha creación', select=True, readonly=True),
        prf_ids = fields.many2many('crossovered.budget.certificate','con_pr_rel','c_id','pr_id','Docs. Presupuestarios'),
    )
    _order = "code desc"
    _defaults = dict(
        state = 'draft',
        owner = True,
        chk_contrato = False,
        user_id = lambda self, cr, uid, ctx:uid,
        creation_date = lambda *a: strftime('%Y-%m-%d %H:%M:%S'),
        info_general = __group_info_general,
        perfil_usuario = __perfil_info_general,
        year = _get_year,        
    )
    
    def _check_documents(self, cr, uid, ids, context=None):
        for contract in self.browse(cr, uid, ids):
            if contract.document_ids:
                for doc in contract.document_ids:
                    if not doc.datas_fname:
                        return False
        return True
    
    def _check_percentage_advance(self, cr, uid, ids, context=None):
        for contract in self.browse(cr, uid, ids):
            if contract.percentage_advance < 0 or contract.percentage_advance > 100:
                #raise osv.except_osv('Error !', 'El campo "% Anticipo" debe estar en el rango de 0 - 100')
                return False
            return True
        
    def _check_subscription_date(self, cr, uid, ids, context=None):
        now_date = time.strftime('%Y-%m-%d')
        for contract in self.browse(cr, uid, ids):
            if contract.subscription_date > now_date:
                return False
            return True
                #elif not contract.planned_end_date > contract.subscription_date:
                    #raise osv.except_osv(('Mensaje de Error !'), ('¡La fecha de cumplimiento debe ser mayor a la fecha de suscripción!'))
                    
    def _check_date_received(self, cr, uid, ids, context=None):
        now_date = time.strftime('%Y-%m-%d')
        for contract in self.browse(cr, uid, ids):
            if contract.date_received > now_date:
                return False
            return True
            
    def _check_monto_contrato(self, cr, uid, ids, context=None):
        for contract in self.browse(cr, uid, ids):
            aux = 0
            if contract.amount <= 0:
                return False
            return True

    def _check_monto_facturas(self, cr, uid, ids, context=None):
        for contract in self.browse(cr, uid, ids):
            amount_invoice = 0
            for invoice in contract.invoice_ids:
                amount_invoice += invoice.amount_vat_cero+invoice.amount_vat
                if (amount_invoice + invoice.amount_vat_cero+invoice.amount_vat) > contract.amount:
                    return False
            return True
        
    def _check_codigo_contrato(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        for contract in self.browse(cr, uid, ids):
            contract_ids = self.search(cr, uid, [('codigo_contrato','=',contract.codigo_contrato),
                                                 ('id','!=',contract.id),
                                                 ('state','!=','cancelled')])
            if contract_ids:
                return False
            return True
            
    _constraints = [
        (_check_invoices,'El monto de facturas no puede superar el del contrato',['Facturas']),
        (_check_documents, 'Error! Un adjunto no ha sido agregado correctamente',
         ['document_ids']),
        (_check_percentage_advance, 
         'El campo "% Anticipo" debe estar en el rango de 0 - 100',['% Anticipo']),
        (_check_subscription_date, 
         '¡El campo "% Fecha Suscripcion" debe ser menor o igual a la fecha actual!',
         ['% subscription_date']),
        (_check_date_received, 
         '¡El campo "% Fecha Recepción" debe ser menor o igual a la fecha actual!',
         ['% date_received']),
        (_check_monto_contrato, 
         '¡El campo "% Monto Total" debe ser mayor que 0',['% amount']),
        (_check_monto_facturas, 
         '¡El monto de facturas no debe superar al del contrato',['% amount']),
    ]
    
doc_contract_contract()


class doc_contract_ubication(osv.osv):
    _name = 'doc_contract.ubication'
    
    def onchange_parish(self, cr, uid, ids, context=None):
        return {'value':{'parroquia':''}}
    
    _columns = dict(      
        name = fields.char('Nombre', size=64),
        canton = fields.many2one('res.country.state.canton', 'Canton'),
        parroquia = fields.many2one('res.country.state.parish', 'Parroquia'),
        comunidad = fields.char('Comunidad', size=64),
        contract_id = fields.many2one('doc_contract.contract', 'Contrato', select=1),
        #contract_state = fields.related('contract_id','state', type='selection', selection = [('draft', 'Borrador'),
         #                         ('open', 'En Progreso'),
          #                        ('cancelled', 'Anulado'), 
           #                       ('done', 'Finalizado')], string='Estado del Contrato', 
            #                      readonly=True, store=True,),
    )
doc_contract_ubication()


class doc_contract_warranty(osv.osv):
    _name = 'doc_contract.warranty'

    def _get_move_lines(self, cr, uid, ids, fields, args, context):
        res = {}
        for obj in self.browse(cr, uid, ids):
            lines = []
            res[obj.id] = []
            if obj.move_id:
                lines += [line.id for line in obj.move_id.line_id]
            res[obj.id] = lines
        return res
    
    _columns = dict(             
        name = fields.char('Núm. Garantía', size=64, required=True),
        contract_id = fields.many2one('doc_contract.contract', 'Contrato', required=True),
        contratista_id = fields.related('contract_id', 'partner_id', type='many2one',
                                        relation='res.partner', string="Contratista",
                                        readonly=True),
        description = fields.related('contract_id', 'name', type='char', size=128, string='Descripción',
                                     readonly=True),
        num_contract = fields.related('contract_id', 'codigo_contrato', type='char',
                                      readonly=True,
                                      size=32, string='Núm. Contrato'),
        aseguradora_id = fields.many2one('res.partner', 'Aseguradora', required=True),
        fecha_emision = fields.date('Fecha de Inicio', required=True),
        fecha_fin = fields.date('Fecha Final', required=True),
        date_due = fields.date('Fecha de Vencimiento', required=True),
        type_warranty_id = fields.many2one('warranty.type', 'Tipo', required=True),
        amount = fields.float('Monto'),
        administrador_id = fields.related('contract_id', 'admin_uid', type='many2one', readonly=True,
                                          relation='res.users', string='Administrador'),
        fiscal_id = fields.related('contract_id', 'supervisory',
                                   type='many2one', relation='res.users',
                                   string='Fiscalizador', readonly=True),
        date_ids = fields.one2many('warranty.dates', 'warranty_id', string='Detalle de Renovaciones'),
        state = fields.selection([('draft', 'borrador'),
                                  ('done','Ingresado'),
                                  ('gone', 'Dada de Baja')], string='Estado', required=True),
        move_id = fields.many2one('account.move', string='Diario'),
        line_ids = fields.function(_get_move_lines, method=True, string="Detalle Contable",
                                    type="one2many", relation="account.move.line"),
    )

    _defaults = {
        'state': 'draft'
        }

    _sql_constraints = [('monto_mayor_cero', 'CHECK (amount>=0)', 'El monto debe ser mayor a cero.')]

    def onchange_contract(self, cr, uid, ids, contract_id):
        if not contract_id:
            return {}
        cont = self.pool.get('doc_contract.contract').browse(cr, uid, contract_id)
        res = {'value': {'contratista_id': cont.partner_id.id,
                         'description': cont.name,
                         'num_contract': cont.codigo_contrato,
                         'administrador_id': cont.admin_uid.id,
                         'fiscal_id': cont.supervisory.id}}
        return res

    def check_warranty_due(self, cr, uid, context=None):
        """
        metodo de verificacion de garantias vencidas
        en los proximos 15 dias
        days_due: Configurado en la compañia
        """
        days_due = self.pool.get('res.users').browse(cr, uid, uid).company_id.warranty_days_due
        now = datetime.today()
        date_due = now + datetime.timedelta(days=days_due)
        str_date = str(date_due) #datetime.strftime(date_due, '%Y-%m-%d')
        warranty_ids = self.search(cr, uid, [('date_due','>=',),('date_due','<=',str_date)])
        data = []
        for w in self.browse(cr, uid, warranty_ids):
            texto = """
            Aseguradora: %s,
            Contrato: %s %s,
            Administrador: %s,
            Fiscalizador: %s,
            Fecha de Vencimiento: %s
            """ % (w.aseguradora_id.name, w.contract_id.code, w.contract_id.name,
                   w.administrador_id.employee_id.complete_name, w.fiscal_id.employee_id.complete_name,
                   w.date_due)
            data.append(texto)

    def action_register(self, cr, uid, ids, context=None):
        acc_move = self.pool.get('account.move')
        for obj in self.browse(cr, uid, ids, context):
            period_id = self.pool.get('account.period').find(cr, uid, dt=obj.fecha_emision)[0]
            type_warranty = obj.type_warranty_id
            acc = [type_warranty.journal_id and type_warranty.journal_id.id or False,
                   type_warranty.cta_debit and type_warranty.cta_debit.id or False,
                   type_warranty.cta_credit and type_warranty.cta_credit.id or False]
            if False in acc:
                raise osv.except_osv('Error', 'No ha configurado las cuentas de orden de garantias')
            name = 'REGISTRO DE GARANTIA: %s, CONTRATO: %s ' % (obj.name, obj.num_contract)
            move_data = {
                'period_id': period_id,
                'ref': name,
                'journal_id': acc[0],
                'date': strftime('%Y-%m-%d'),
                'line_id': [(0,0,{'account_id': acc[1],
                                  'debit': obj.amount,
                                  'credit': 0,
                                  'name': name,
                                  'partner_id': obj.contratista_id.id,
                                  'ref': obj.description[:63]}),
                            (0,0,{'account_id': acc[2],
                                  'debit': 0,
                                  'credit': obj.amount,
                                  'name': name,
                                  'partner_id': obj.contratista_id.id,
                                  'ref': obj.description[:63]})]
                }
            move_id = acc_move.create(cr, uid, move_data)
            self.write(cr, uid, obj.id, {'move_id': move_id, 'state': 'done'})
        return True
        
            
    
doc_contract_warranty()

class WarrantyDates(osv.Model):
    _name = 'warranty.dates'

    _columns = {
        'date': fields.date('Fecha de Renovación', required=True),
        'date_due': fields.date('Fecha Vencimiento', required=True),
        'monto': fields.float('Monto'),
        'warranty_id': fields.many2one('doc_contract.warranty',
                                       string='Garantía', required=True),
        }

    _sql_constraints = [('monto_mayor_cero', 'CHECK (monto>=0)', 'El monto debe ser mayor a cero.')]


class WarrantyType(osv.Model):
    _inherit = 'warranty.type'

    _columns = {
        'journal_id': fields.many2one('account.journal', 'Diario'),
        'cta_debit': fields.many2one('account.account', 'Cuenta Debe'),
        'cta_credit': fields.many2one('account.account', 'Cuenta Haber')
        }


class doc_contract_historial(osv.osv):
    _name = 'doc.contract.historial'
    _columns = dict(             
        name = fields.char('Descripción', size=256),
        fecha_hora = fields.datetime('Fecha - Hora'),
        usuario = fields.many2one('res.users', 'Usuario'),
        contract_id = fields.many2one('doc_contract.contract', 'Contrato'),
    )
doc_contract_historial()


class Res_Users(osv.osv):
    _inherit = 'res.users'
    _columns = dict(
        #stage_id = fields.many2one('doc_contract.stage', 'Usuarios responsables', readonly=True),
        contract_commission_id = fields.many2one('doc_contract.contract', 'Comisión', readonly=True),
        contract_distribution_id = fields.many2one('doc_contract.contract', 'Distribución de Contratos', readonly=True),    
   )
Res_Users()


class Ir_Attachment(osv.osv):
    _inherit = 'ir.attachment'
    _columns = dict(
        document_contract_id = fields.many2one('doc_contract.contract', 'Contract', readonly=True),
   )
    _defaults = {
        'parent_id': None
    }
Ir_Attachment()


class Document_Directory(osv.osv):
    _inherit = 'document.directory'
    _columns = dict(
        document_directory_id = fields.many2one('doc_contract.contract', 'Contract', readonly=True),
   )
Document_Directory()


class Doc_Account_Voucher(osv.osv):
    _inherit = "account.voucher"
    _columns = dict(
        name = fields.char('Pago a Contrato', size=64),
        contract_type = fields.boolean('Pago a Contrato'),                   
        contract_id = fields.many2one('doc_contract.contract', 'Contrato'),
    )
Doc_Account_Voucher()


