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
from tools import ustr

class stockExpedient(osv.osv):
    _inherit = "stock.picking"
     
   def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        if context is None:
            context = {}

        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        picking_obj = self.pool.get('stock.picking')
        invoices_group = {}
        res = {}
        inv_type = type
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.invoice_state != '2binvoiced':
                continue
            partner = picking.partner_id#self._get_partner_to_invoice(cr, uid, picking, context=context)
            if not partner:
                raise osv.except_osv(_('Error, no partner !'),
                    _('Please put a partner on the picking list if you want to generate invoice.'))

            if not inv_type:
                inv_type = self._get_invoice_type(picking)
            if not picking.solicitant_id.user_id:
                raise osv.except_osv(('Error'), ('El empleado no tiene usuario asignado:  '+picking.solicitant_id.complete_name))
            if group and partner.id in invoices_group:
                invoice_id = invoices_group[partner.id]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals_group = self._prepare_invoice_group(cr, uid, picking, partner, invoice, context=context)
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
            else:
                invoice_vals = self._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
                if len(picking.partner_id.authorisation_ids)>0:
                    invoice_vals['auth_inv_id'] = picking.partner_id.authorisation_ids[0].id
                invoice_vals['reference'] = picking.number
                invoice_vals['date_invoice'] = picking.document_date
                invoice_vals['tramite_id'] = picking.tramite_id.id
                invoice_vals['certificate_id'] = picking.presp_ref.id
                invoice_vals['picking_id'] = picking.id
                invoice_vals['reference_type'] = 'invoice_partner'
                invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
                picking_obj.write(cr, uid, picking.id,{'invoice_id':invoice_id})
                invoices_group[partner.id] = invoice_id
            res[picking.id] = invoice_id
            for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                if move_line.scrapped:
                    # do no invoice scrapped products
                    continue
                vals = self._prepare_invoice_line(cr, uid, group, picking, move_line,
                                invoice_id, invoice_vals, context=context)
                if vals:
                    invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
                    self._invoice_line_hook(cr, uid, move_line, invoice_line_id)
            #crear las lineas de factura tambien si es activos o servicios
            if picking.purchase_id:
                for purchase_line in picking.purchase_id.order_line:
                    if purchase_line.product_id.type in ('service','asset'):
                        vals1 = self._prepare_invoice_line_po(cr, uid, group, picking, purchase_line,
                                                              invoice_id, invoice_vals, context=context)
                        if vals1:
                            invoice_line_id_po = invoice_line_obj.create(cr, uid, vals1, context=context)
            #################
            invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
                    set_total=(inv_type in ('in_invoice', 'in_refund')))
            self.write(cr, uid, [picking.id], {
                'invoice_state': 'invoiced',
                }, context=context)
            self._invoice_hook(cr, uid, picking, invoice_id)
        self.write(cr, uid, res.keys(), {
            'invoice_state': 'invoiced',
            }, context=context)
        return res


    def action_load_line(self, cr, uid, id, context):
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        for this in self.browse(cr, uid, id):
#            for picking in this.related_picking.id:
            picking_obj.write(cr, uid, this.id, {
                    'tramite_id':this.related_picking.tramite_id.id,
                    'partner_id':this.related_picking.partner_id.id,
                    'contract_id':this.related_picking.contract_id.id,
                    'purchase_id':this.related_picking.purchase_id.id,
                    'min_date':this.related_picking.min_date,
                    #'bodega_id':this.related_picking.bodega_id.id,
                    'solicitant_id':this.related_picking.solicitant_id.id,
                    'unidad_id':this.related_picking.unidad_id.id,
                    'responsable_id':this.related_picking.responsable_id.id,
                    'document_id':this.related_picking.document_id.id,
                    'number':this.related_picking.number,
                    'document_date':this.related_picking.document_date,
                    'ie_type':this.related_picking.ie_type.id,
                    'receptor_id':this.related_picking.receptor_id.id,
                    'project_id':this.related_picking.project_id.id,
                    'objeto_id_id':this.related_picking.objeto_id_id.id,
                    })
            for move_line in this.related_picking.move_lines:
                new_line = move_obj.copy_data(cr, uid, move_line.id)
                new_line['picking_id']= this.id
                if this.type == 'out':
                    context['type'] = 'in'
                else:
                    context['type'] = 'out'
                id_creado = move_obj.create(cr, uid, new_line, context)
        return True

    def create(self, cr, uid, vals, context=None):
#        if not vals['type']:
#            vals['type']='internal'
        if context==None:
            context = {}
        obj_type = self.pool.get('picking.doc.type')
        if vals.has_key('document_id'):
            documento = obj_type.browse(cr, uid, vals['document_id'], context)
            if documento.generar_factura:
                vals['invoice_state'] = '2binvoiced'
            else:
                vals['invoice_state'] = 'none'
        seq_obj_name = ''
        usuario = self.pool.get('res.users').browse(cr, uid, uid)
        solicitant_id = self.pool.get('hr.employee').browse(cr, uid, vals['solicitant_id'])
        context['crear'] = 'crear'
        vals['unidad_id'] = solicitant_id.id
        if vals['tramite_id']:
            #crea el tramite
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                         'other_action' : str('Ingreso Bodega') ,
                                                                         'description': 'Servidor: ' + solicitant_id.complete_name,
                                                                #         'department': solicitant_id.department_id.id,
                                                                #         'employee_id' : solicitant_id.id,
                                                                #         'job_id': solicitant_id.job_id.id,
                                                                         'user_id': uid,
                                                                         'expedient_id':vals['tramite_id'],
                                                                         'state': 'done',
                                                                         'type':'of_know',
                                                                         'assigned_user_id':uid,
                                                                         })
        else:
            resume = str('Ingreso Bodega')
            expedient_id= self.pool.get('doc_expedient.expedient').create(cr, uid,{'name': resume,
                                                                                   'state': 'draft',
                                                                                   'ubication':'internal',
                                                                                   'resumen': resume})
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                         'other_action' : str('Solicitud de compra') ,
                                                                         'description': 'Servidor: ' + solicitant_id.complete_name,
                                                                      #   'department': solicitant_id.department_id.id,
                                                                      #   'employee_id' : solicitant_id.id,
                                                                      #   'job_id': solicitant_id.job_id.id,
                                                                         'user_id': uid,
                                                                         'expedient_id':expedient_id,
                                                                         'state': 'done',
                                                                         'type':'of_know',
                                                                         'assigned_user_id':uid,
                                                                         })
            vals['tramite_id']=expedient_id
            self.pool.get('doc_expedient.expedient').action_draft_created(cr, uid, [expedient_id])
            self.pool.get('doc_expedient.task').write(cr, uid, [task_id], {'state':'done'})            
        #tomar la secuencia en base a la transaccion
        if ('name' not in vals) or (vals.get('name')=='/'):
            tabla_obj = self.pool.get('stock.config.sequence')
            tabla_ids = tabla_obj.search(cr, uid, [('bodega_id','=',vals['bodega_id'])],limit=1)
            if not tabla_ids:
                raise osv.except_osv(('Error de configuración'), ('No existe tabla de secuencias definida para la bodega'))
            tabla = tabla_obj.browse(cr, uid, tabla_ids[0])
            if context.has_key('type_internal_menu'):
                if context['type_internal_menu']=='in':
                    seq_obj_name =  tabla.in_seq.code
                elif context['type_internal_menu']=='indev':
                    seq_obj_name =  tabla.in_dev_seq.code
                elif context['type_internal_menu']=='out':
                    seq_obj_name =  tabla.out_seq.code
                elif context['type_internal_menu']=='outdev':
                    seq_obj_name =  tabla.out_dev_seq.code
                else:
                    seq_obj_name =  tabla.internal_seq.code
                vals['type_internal_menu'] = context['type_internal_menu']
            else:
                vals['type_internal_menu'] = 'out'
                vals['type'] = 'out'
                seq_obj_name =  tabla.out_seq.code
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        return super(stockPicking, self).create(cr, uid, vals, context)

    _columns = dict(
        tramite_id = fields.many2one('doc_expedient.expedient','Trámite',
                                     help="Tramite relacionado al proceso si usted no lo selecciona este se crea automáticamente"),
     )

stockExpedient()
