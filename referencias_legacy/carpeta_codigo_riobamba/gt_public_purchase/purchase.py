# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Gnuthink Software Labs Cia. Ltda.
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
import time
from datetime import date

class PurchaseType(osv.Model):
    _name = 'purchase.type'
    _description = 'Tipos de Compra'

    _columns = dict(
        code = fields.char('Código', size=32, required=True),
        name = fields.char('Tipo', size=32, required=True),
        )


class PurchaseContractType(osv.Model):
    _name = 'purchase.contract.type'
    _description = 'Contract Types'

    def create(self, cr, uid, vals, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        vals['code'] = obj_sequence.get(cr, uid, 'purchase.contract.type')
        return super(PurchaseContractType, self).create(cr, uid, vals, context=None)

    _columns = dict(
        code = fields.char('Código', size=32),
        name = fields.char('Procedimiento', size=128, required=True),
        )    


class LogStateChange(osv.Model):
    _name = 'log.state.change'
    _description = 'Log de cambios de estado de la compra'
    _columns = dict(
        date = fields.datetime('Fecha Modificación'),
        user_id = fields.many2one('res.users','Usuario'),
        state_to = fields.char('Estado anterior',size=64),
        state_from = fields.char('Estado nuevo',size=64),
        public_id = fields.many2one('purchase.public.process','Contratación'),
        )


class PurchasePublicProcess(osv.Model):
    _name = 'purchase.public.process'
    _order = 'date desc'

    def purchase_anulate(self, cr, uid, ids, context=None):
        log_obj = self.pool.get('log.state.change')
        public_obj = self.pool.get('purchase.public.process')
        #deberia bloquear el formulario de compra publica
        for purchase in self.browse(cr, uid, ids):
            state_ids = state_obj.search(cr, uid, [('code','=',purchase.state.code)], limit=1)
            actual_state = state_obj.browse(cr, uid, state_ids)
            for this in actual_state:
                public_obj.write(cr, uid, purchase.id, {
                        'internal_state':'anulated',
                        })
                log_obj.create(cr, uid, {
                        'date':time.strftime('%Y-%m-%d %H:%M:%S'),
                        'user_id':uid,
                        'state_to':this.name,
                        'state_from':'Anulado',
                        'public_id':purchase.id,
                        })
        return True

    _OBJ_CONTRACT = [('b','Bienes'),('s','Servicios'),('bienes','Bienes y Servicios'),
                     ('obras','Obras'),('consultoria','Consultoría')]

    def _generate_log(self, cr, uid, id, state, context=None ):
        req_obj = self.pool.get('purchase.public.process')
        log_obj = self.pool.get('log.state.change')
        req=req_obj.browse(cr, uid, id)
        log_obj.create(cr, uid, {
                'user_id':uid,
                'public_id':id,
                'date':time.strftime('%Y-%m-%d %H:%M:%S'),
                'state_to':req.internal_state,
                'state_from':state,
                })
        return True

    def create(self, cr, uid, vals, context=None):
        self.pool.get('crossovered.budget.certificate').write(cr, uid, vals['presp_ref'],{
                'is_lock':True,
                })
        solicitant_id = self.pool.get('hr.employee').browse(cr, uid, vals['responsable_p_id'])
        if vals['tramite_id']:
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,
                                                                {'other_action_chk': True,
                                                                 'other_action' : str('Solicitud de compra') ,
                                                                 'description': 'Servidor: ' + solicitant_id.complete_name,
                                                                 'department': solicitant_id.department_id.id,
                                                                 'employee_id' : solicitant_id.id,
                                                                 'job_id': solicitant_id.job_id.id,
                                                                 'user_id': uid,
                                                                 'expedient_id':vals['tramite_id'],
                                                                 'state': 'done',
                                                                 'assigned_user_id':uid,
                                                                 }, context=context)
        else:
            resume = str('Solicitud de compra: ') + vals['name']
            expedient_id= self.pool.get('doc_expedient.expedient').create(cr, uid,
                                                                          {'name': resume ,
                                                                           'state': 'draft',
                                                                           'ubication':'internal',
                                                                           'resumen': resume}, context=context)
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,
                                                                {'other_action_chk': True,
                                                                 'other_action' : str('Solicitud de compra') ,
                                                                 'description': 'Servidor: ' + solicitant_id.complete_name,
                                                                 'department': solicitant_id.department_id.id,
                                                                 'employee_id' : solicitant_id.id,
                                                                 'job_id': solicitant_id.job_id.id,
                                                                 'user_id': uid,
                                                                 'expedient_id':expedient_id,
                                                                 'state': 'done',
                                                                 'assigned_user_id':uid,
                                                                 }, context=context)
            vals['tramite_id']=expedient_id
            self.pool.get('doc_expedient.expedient').action_draft_created(cr, uid, [expedient_id],context)
        self.pool.get('doc_expedient.task').write(cr, uid, [task_id], {'state':'done'})
        return super(PurchasePublicProcessInherit, self).create(cr, uid, vals, context=None)

        
    def onchange_amount_cp(self, cr, uid, ids, amount, presp_ref):
        result = {}
        cross_obj = self.pool.get('crossovered.budget.certificate')
        budget = cross_obj.browse(cr, uid, presp_ref)
        if not presp_ref:
            raise osv.except_osv('Mensaje de Error !', 
                                 '¡Seleccione la certificación presupuestaria!')
        if amount > budget.amount_certified:
            raise osv.except_osv(('Aviso'), ('El monto adjudicado $ %s es mayor al certificado $ %s') %(str(amount),str(budget.amount_certified)))
        if amount < 1:
            raise osv.except_osv('Mensaje de Error !', 
                                 '¡El monto debe ser mayor o igual a 1!')
        return result

    def _get_uid(self, cr, uid, context=None):
        return uid

    def _get_user_c(self, cr, uid, context=None):
        #tomar el usuario de sindicatura y colocarlo
        sindicature_obj = self.pool.get('contract.sindicature')
        sindicature_ids = sindicature_obj.search(cr, uid, [],limit=1)
        if not sindicature_ids:
            raise osv.except_osv('Mensaje de Error !', '¡No esta configurado el usuario de sindicatura en la tabla de configuración de contratos!')
        return sindicature_ids[0]

    def _check_delegado(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if len(this.delegado_ids)<1:
                return False
        return True

    def _check_amount_incop(self, cr, uid, ids, context=None):
        obj_config = self.pool.get('purchase.config')
        obj_value = self.pool.get('purchase.value.line')
        for this in self.browse(cr, uid, ids):
            if this.presp_ref.amount_certified >= this.type_process.desde and this.presp_ref.amount_total <= this.type_process.hasta:
                pass
            else:
                raise osv.except_osv('Mensaje de Error !', '¡Verifique el monto del documento presupuestario no esta dentro del rango del proceso contratacion!')
                #return False
        return True

    _INTERNAL_STATE = [('draft','Borrador'),('process','Proceso'),('Cancelado','Cancelado'),('Desierto','Desierto'),
                       ('adjudicated','Adjudicado'),('anulated','Anulado'),('Finalizado','Finalizado'),
                       ('c_anulado','Contrato Anulado')]

    _columns = dict(
        create_date_cp = fields.date('Fecha Creación',readonly=True),
        delegado_ids = fields.many2many('hr.employee','cp_emp_rel','cp_id','e_id','Delegados Calificación'),
        date = fields.date('Fecha Recepción'),
        tramite_id = fields.many2one('doc_expedient.expedient','Trámite',
                                   help="Es el tramite relacionado al proceso si usted no lo selecciona este se crea automaticamente"),
        folder_number = fields.char('Número Carpeta',size=16),
        costo_pliego = fields.float('Costo Pliegos'),
        code = fields.char('Código de Proceso', size=32),
        name = fields.text('Objeto del Proceso'),
        type_process = fields.many2one('purchase.value.line','Tipo Proceso',required=True),
#        type_id = fields.many2one('doc_contract.type','Objeto Contratación',readonly=True),
        presp_ref = fields.many2one('crossovered.budget.certificate',
                                    'Cert. Presupuestaria',required=True),
        budget_ref = fields.float('Presupuesto Referencial (sin IVA)'),
#        type_contract_id = fields.many2one('purchase.contract.type',
#                                           'Procedimiento',
#                                           required=True),
        payment_term_id = fields.text('Forma de Pago'),
        amount = fields.float('Monto Adjudicado',help="Es el monto con el que se adjudica el proceso, si usted coloca un monto superios al certificado, le aparecerá un mensage de advertencia"),
        deadline = fields.integer('Plazo de Entrega (días)'),
        deadline_quotation = fields.integer('Vigencia de Oferta (días)'),
        responsable_p_id = fields.many2one('hr.employee',
                                         'Responsable Portal'),
        responsable_id = fields.many2one('hr.employee',
                                  'Responsable de Proceso'),
        description = fields.text('Descripción'),
        order_id = fields.many2one('purchase.order', 'Orden de Compra'),
        partner_id = fields.many2one('res.partner','Adjudicatario'),
        create_user = fields.many2one('res.users','Creado por'),
#        contract_id = fields.many2one('purchase.contract', string='Contrato'),
#        budget_line_id = fields.many2one('crossovered.budget.lines',
#                                         string='Partida Presupuestaria'),
        log_ids = fields.one2many('log.state.change','public_id','Historial'),
        date_ids = fields.one2many('date.state','public_id','Fechas Estados'),
        internal_state = fields.selection(_INTERNAL_STATE,'Estado'),
#        purchase_order_line = fields.one2many('purchase.order.line','public_id','Productos'),
        actual_state = fields.char('Estado Actual',size=32),
        coordination_dept = fields.many2one('hr.department','Unidad Requirente'),
        contract_id = fields.many2one('doc_contract.contract','Contrato Proveedor'),
        observation = fields.text('Observaciones'),
        c_user = fields.many2one('res.users','Usuario Contrato'),
        type_person = fields.selection([('nat','Natural'),('jur','Jurídica'),('asoc','Asociación/Consorcio')],'Tipo'),
        adj_name = fields.char('Nombre/Raz. Social',size=128),
        rep_legal = fields.char('Rep. Legal',size=256),
        ruc = fields.char('RUC',size=13),
        rup = fields.char('RUP',size=13),
        )

    _defaults = dict(
#        c_user = _get_user_c,
        #        state = _get_state,
        create_user = _get_uid,
        type_person = 'nat',
        internal_state = 'draft',
        create_date_cp = lambda *a: time.strftime('%Y-%m-%d'),
        date = lambda *a: time.strftime('%Y-%m-%d'),
        )

    _sql_constraints = [
        ('code_cp_uniq', 'unique (code)', 'El codigo debe ser unico !')
        ]

    _constraints = [
        (_check_delegado, 'Error! Debe por lo menos asignar un delegado...',['Delegados']),
        (_check_amount_incop, 'Error! El valor no esta dentro del rango establecido para el Procedimiento de Contratación...',['Monto'])
        ]

    def finalization(self, cr, uid, ids, context=None):
        log_obj = self.pool.get('log.state.change')
        for purchase in self.browse(cr, uid, ids):
            log_obj.create(cr, uid, {
                    'date':time.strftime('%Y-%m-%d %H:%M:%S'),
                    'user_id':uid,
                    'state_to':'Adjudicado',
                    'state_from':'Finalizado',
                    'public_id':purchase.id,
                })
        self.write(cr, uid, ids[0],{
            'internal_state':'Finalizado',
            })
        return True

    def adjudication(self, cr, uid, ids, context=None):
        contract_obj = self.pool.get('doc_contract.contract')
        log_obj = self.pool.get('log.state.change')
        public_obj = self.pool.get('purchase.public.process')
        cmb_lines = []
        mat_lines = []
        ins_lines = []
        for purchase in self.browse(cr, uid, ids):
            if not purchase.partner_id.name:
                if purchase.adj_name==False or purchase.rep_legal==False or purchase.ruc==False or purchase.rup==False:
                    raise osv.except_osv('Mensaje de Error !', '¡Ingrese la información del adjudicatario!')
            state_ids = state_obj.search(cr, uid, [('code','=',purchase.state.code)], limit=1)
            actual_state = state_obj.browse(cr, uid, state_ids)
#            for this in actual_state:
            log_obj.create(cr, uid, {
                    'date':time.strftime('%Y-%m-%d %H:%M:%S'),
                    'user_id':uid,
                    'state_to':'Borrador',
                    'state_from':'Adjudicado',
                    'public_id':purchase.id,
                    })
                #sacar el uid de sindicatura y mandar en el uid
            c_id = contract_obj.create(cr, purchase.create_user.id, {
                    'is_cp':True,
                    'cp_id':purchase.id,
                    'codigo_contrato':'/',
                    'ref_cp':purchase.code,
                    'name':purchase.name,
                    'partner_id':purchase.partner_id.id,
                    'expedient_id':purchase.tramite_id.id,
                    'chk_create_expedient':False,
                    'amount':purchase.amount,
                    'subscription_date':time.strftime('%Y-%m-%d'),
                    'fecha_inicio':time.strftime('%Y-%m-%d'),
                    'term':purchase.deadline,
                    'user_id':purchase.c_user.id,
                    'department_id':purchase.coordination_dept.id,
                    'objeto':purchase.type_process.objeto.id,
                    'procedimiento':purchase.type_process.name.id,
#                    'crossovered_budget_certificate_id':purchase.presp_ref.id,
                        })
            public_obj.write(cr, uid, purchase.id, {
                    'internal_state':'adjudicated',
                    'contract_id':c_id,
                    })            
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                         'other_action':str('Finaliza proceso'),
                                                                         'description':'Servidor: ' + purchase.responsable_p_id.complete_name + ' ' + 'Finaliza el proceso de compras',
                                                                         'department': purchase.coordination_dept.id,
                                                                         'employee_id' : purchase.responsable_p_id.id,
                                                                         'job_id': purchase.responsable_p_id.job_id.id,
                                                                         'user_id': uid,
                                                                         'expedient_id':purchase.tramite_id.id,
                                                                         'state': 'done',
                                                                         'assigned_user_id':purchase.responsable_p_id.user_id.id,
                                                                         }, context=context)
        return True
    
    
class Purchase_Value_Line(osv.osv):
   _inherit = 'purchase.value.line'

   _columns = dict(
       objeto = fields.many2one('doc_contract.type', 'Objeto Contratación', required=True),
   )
Purchase_Value_Line()     

class docCovenantInvoice(osv.osv):
    _inherit = 'doc_covenant.covenant'
    _columns = dict(
        invoice_ids = fields.many2many('account.invoice','inv_cv_rel','inv_id','c_id','Facturas Relacionadas'),
        pick_ids = fields.many2many('stock.picking','pick_cv_rel','pick_id','c_id','Ingresos Bodega'),
        )       

docCovenantInvoice()
    
class Doc_Contract_Contract(osv.osv):
   _inherit = 'doc_contract.contract'
   
   def onchange_modality_id(self, cr, uid, ids, context=None):        
        return {'value':{'procedimiento':''}}

   _columns = dict(
       ref_cp = fields.char('Cod. Proceso CP',size=32,readonly=True),
       objeto = fields.many2one('doc_contract.type', 'Objeto Contratación', required=True),
       procedimiento = fields.many2one('purchase.contract.type', 'Procedimiento', required=True),
       invoice_ids = fields.many2many('account.invoice','inv_c_rel','inv_id','c_id','Facturas Relacionadas'),
       cp_id = fields.many2one('purchase.public.process','Compra Publica'),
   )

   def _check_amount_incop(self, cr, uid, ids, context=None):
       obj_config = self.pool.get('purchase.config')
       obj_value = self.pool.get('purchase.value.line')
       for contract in self.browse(cr, uid, ids):
           try:
               value_id=obj_value.search(cr, uid, [('objeto','=',contract.objeto.id),('name','=',contract.procedimiento.id)])[0]
               value_results = obj_value.read(cr, uid, value_id, ['id','name','desde','hasta','p_id'])
           except IndexError:
               raise osv.except_osv('Mensaje de Error !', '¡No existe relación del monto entre el Objeto y el Procedimiento de Contratación!')
           if value_results:
               if contract.amount >= value_results['desde'] and contract.amount <= value_results['hasta']:
                   pass
               else:
                   return False
       return True
    
   _constraints = [
       (_check_amount_incop, 'Error! El valor no esta dentro del rango establecido para el Procedimiento de Contratación...',['Monto'])
    ]

Doc_Contract_Contract() 




class doc_contract_type(osv.osv):
    _name = 'doc_contract.type'
    _columns = dict(
        #code = fields.char('Codigo', size=64, required=True),
        name = fields.char('Nombre', size=64, required=True),
        #ir_sequence_id = fields.many2one('ir.sequence', 'Secuencias', required="True"),
        desc = fields.text('Descripcion'),
    )
doc_contract_type()



class doc_contract_type_document(osv.osv):
    _name = 'doc.contract.type.document'
    _columns = dict(
        name = fields.char('Tipo Documento', size=64, required=True),
        perfil = fields.selection([('info_general', 'Información General'),
                                 ('distribucion', 'Distribución'),
                                  ('ejecucion', 'Ejecución')], 'Perfil', required=True),
        unico = fields.boolean('Doc.Único'),
        contract_type_id = fields.many2one('doc_contract.type', 'Objeto de Contratación'),
    )
doc_contract_type_document()


class Ir_Attachment(osv.osv):
    _inherit = 'ir.attachment'
    _columns = dict(
        document_type_id = fields.many2one('doc.contract.type.document', 'Tipo Documento'),
   )
Ir_Attachment()


class purchaseContractType(osv.Model):
    _inherit = 'purchase.contract.type'
    _columns = dict(
        contract_type = fields.many2one('doc_contract.type','Objeto Contratación',required=True),
        )

purchaseContractType()
