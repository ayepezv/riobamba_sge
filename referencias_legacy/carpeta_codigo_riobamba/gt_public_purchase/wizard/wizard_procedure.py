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

class wizard_procedureInherit(osv.osv_memory):
   _inherit='wizard.procedure'

#   def _validate_procedure(self, cr, uid, ids, context=None):
#      import pdb
#      pdb.set_trace()
#      obj_config = self.pool.get('purchase.config')
#      obj_value = self.pool.get('purchase.value.line')
#      for contract in self.browse(cr, uid, ids):
#         try:
#            value_id=obj_value.search(cr, uid, [('objeto','=',contract.objeto.id),('name','=',contract.procedimiento.id)])[0]
#            value_results = obj_value.read(cr, uid, value_id, ['id','name','desde','hasta','p_id'])
#         except IndexError:
#            raise osv.except_osv('Mensaje de Error !', '¡No existe relación entre el Objeto y el Procedimiento de Contratación!')
#         if value_results:
#            if contract.amount >= value_results['desde'] and contract.amount <= value_results['hasta']:
#               pass
#            else:
#               return False
#      return True

   _columns = dict( 
      name = fields.text('Objeto de proceso'),
      date = fields.date('Fecha Recepcion'),
      presp_ref = fields.many2one('crossovered.budget.certificate','Cert. Presupuestaria'),
#      objeto = fields.many2one('doc_contract.type','Objeto Contratación',required=True),
#      contract_type = fields.many2one('purchase.contract.type',
#                                      'Procedimiento',
#                                      required=True),
      type_process = fields.many2one('purchase.value.line','Tipo Proceso',required=True),
      responsable_id = fields.many2one('hr.employee','Responsable'),
      tramite_id = fields.many2one('doc_expedient.expedient','Trámite',required=True,
                                   help="Es el tramite relacionado al proceso si usted no lo selecciona este se crea automaticamente"),
      )
   
   _defaults = dict(
       date = time.strftime("%Y-%m-%d"),
    )

   def create_procedure(self, cr, uid, ids, context):
      procedure_obj = self.pool.get('purchase.public.process')
      state_obj = self.pool.get('purchase.process.state')
      date_state = self.pool.get('date.state')
      if context is None:
         context = {}
      seq_obj = self.pool.get('ir.sequence')
      for this in self.browse(cr, uid, ids):
         if not this.tramite_id:
            tramite_id = self._create_tramite(cr, uid, this, context)
            self._create_task(cr, uid, this, tramite_id)
         else:
            tramite_id = this.tramite_id.id
            self._create_task(cr, uid, this, tramite_id)
#         tipo_id = this.contract_type.id
         state_ids = state_obj.search(cr, uid, [('sequence','=',0)], limit=1)
         states = state_obj.read(cr, uid, state_ids, ['code','id','name'])
         state_aux = 'None'
         self.pool.get('crossovered.budget.certificate').write(cr, uid, this.presp_ref.id, 
                                                               {'is_lock':'True'})
         if states:
            state_aux = states[0]['code']
            state_name = states[0]['name']
            id_state = states[0]['id']
            procedure_id = procedure_obj.create(cr, uid, {
#                  'code' : seq_num,
#                  'type_contract_id' : this.contract_type.id,
                  'name' : this.name,
                  'date':this.date,
                  'user_id' : this.responsable_id.user_id.id,
                  'tramite_id' : tramite_id,
                  'state' : id_state,
                  'actual_state' : state_name,
#                  'type_id':this.objeto.id,
                  'type_process':this.type_process.id,
                  'presp_ref':this.presp_ref.id,
                  'responsable_id':this.responsable_id.id,
                  'amount':0,
                  })
            for line_state in this.type_process.name.state_ids:
               date_state.create(cr, uid, {
                     'state_id' : line_state.id,
                     'public_id' : procedure_id,
                     'date_to' : time.strftime('%Y-%m-%d'),
                     'date_from' : time.strftime('%Y-%m-%d'),
                     })
            #Send Mail
#            template_obj = self.pool.get('email.template')
#            model_obj = self.pool.get('ir.model')
#            model = model_obj.search(cr, uid, [('model','=','purchase.public.process')],limit=1)
#            if model:
#               for mod in model:
#                  modelo = model_obj.browse(cr, uid, mod)
 #                 template_ids = template_obj.search(cr, uid, [('model_id','=',mod)],limit=1)
 #                 for template_id in template_ids:
 #                    template_obj.send_mail(cr, uid,
 #                                           template_id,
 #                                           procedure_id, context=context)
            value = {
               'name':'Proceso de Compra Pública',
               'view_type': 'form',
               'view_mode': 'tree,form',
               'res_model': 'purchase.public.process',
               'res_id': procedure_id,
               'type': 'ir.actions.act_window',
#               'context' : {'type_contract_id':tipo_id}
               }
            return value
         else:
            raise osv.except_osv(('Error de configuración !'), ('No existen estados o no esta definido un estado con secuencia 0 para el tipo de contratación seleccionada!'))

   def _check_amount_incop(self, cr, uid, ids, context=None):
      obj_config = self.pool.get('purchase.config')
      obj_value = self.pool.get('purchase.value.line')
      for this in self.browse(cr, uid, ids):
#         try:
#            value_id=obj_value.search(cr, uid, [('objeto','=',this.objeto.id),('name','=',this.contract_type.id)])[0]
#            value_results = obj_value.read(cr, uid, value_id, ['id','name','desde','hasta','p_id'])
#         except IndexError:
#            raise osv.except_osv('Mensaje de Error !', '¡No existe relación entre el Objeto y el Procedimiento de Contratación!')
#         if value_results:
         if this.presp_ref.amount_total >= this.type_process.desde and this.presp_ref.amount_total <= this.type_process.hasta:
            pass
         else:
            return False
      return True
    
   _constraints = [
      (_check_amount_incop, 'Error! El valor no esta dentro del rango establecido para el Procedimiento de Contratación...',['Monto'])
      ]

wizard_procedureInherit()

