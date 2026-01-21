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

class stockRequisitionLine(osv.Model):
    _name = 'stock.requisition.line'

    def onchange_product_line(self, cr, uid, ids, product_id):
        """ On change of product 
        @param product_id: Product id
        @return: Dictionary of values
        """
        result = {}
        if not product_id:
            return {'value': result}
        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, product_id)
        result['uom_id'] = product.uom_id.id
        return {'value': result}

    _columns = dict(
        req_id = fields.many2one('stock.requisition','Requerimiento'),
        product_id = fields.many2one('product.product','Producto',required=True),
        qty = fields.float('Cantidad'),
        uom_id = fields.related('product_id','uom_id',type='many2one',readonly=True,
                                relation='product.uom',string='Unidad Medida',store=True)
        )


stockRequisitionLine()

class stockRequisition(osv.Model):
    _name = 'stock.requisition'
    _order = 'date desc'

    _columns = dict(
        state = fields.selection([('Borrador','Borrador'),('Solicitado','Solicitado'),('Aprobado','Aprobado')],'Estado'),
        create_user_id = fields.many2one('res.users','Creado por'),
        date = fields.datetime('Fecha Creacion'),
        tramite_id = fields.many2one('doc_expedient.expedient','Tramite'),
        name = fields.char('Codigo',size=10),
        solicitant_id = fields.many2one('hr.employee','Solicitado por'),
        recibe_id = fields.many2one('hr.employee','Recibe:'),
        unidad_id = fields.many2one('hr.department',"Unidad Req."),
        bodega_id = fields.many2one('stock.location','Bodega'),
        objeto_id_id = fields.many2one('account.asset.asset','Vehiculo/Maquinaria'),
        project_id = fields.many2one('project.project','Proyecto'),
        move_lines = fields.one2many('stock.requisition.line','req_id','Detalle'),
        note = fields.text('Observaciones'),
        )

    def onchange_solicitant(self, cr, uid, ids, solicitant_id, context={}):
        usr_obj = self.pool.get('res.users')
        usuario = usr_obj.browse(cr, uid, uid)
        if usuario:
            vals={}
            return {'value':{'unidad_id':usuario.context_department_id.id}}

    def create(self, cr, uid, vals, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        usuario = self.pool.get('res.users').browse(cr, uid, uid)
        solicitant_id = self.pool.get('hr.employee').browse(cr, uid, vals['solicitant_id'])
        vals['name'] = obj_sequence.get(cr, uid, 'stock.requisition')
        vals['unidad_id'] = usuario.context_department_id.id
        if vals['tramite_id']:
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                         'other_action' : str('Requerimiento a bodega creado') ,
                                                                         'description': 'Servidor: ' + solicitant_id.complete_name,
                                                                         'user_id': uid,
                                                                         'expedient_id':vals['tramite_id'],
                                                                         'state': 'done',
                                                                         'type':'of_know',
                                                                         'assigned_user_id':uid,
                                                                         })
        else:
            resume = str('Requerimiento Bodega')
            expedient_id= self.pool.get('doc_expedient.expedient').create(cr, uid,{'name': resume,
                                                                                   'state': 'draft',
                                                                                   'ubication':'internal',
                                                                                   'resumen': resume})
            task_id= self.pool.get('doc_expedient.task').create(cr, uid,{'other_action_chk': True,
                                                                         'other_action' : str('Requerimiento a bodega creado') ,
                                                                         'description': 'Servidor: ' + solicitant_id.complete_name,
                                                                         'user_id': uid,
                                                                         'expedient_id':expedient_id,
                                                                         'state': 'done',
                                                                         'type':'of_know',
                                                                         'assigned_user_id':uid,
                                                                         })
            vals['tramite_id']=expedient_id
            self.pool.get('doc_expedient.expedient').action_draft_created(cr, uid, [expedient_id])
        self.pool.get('doc_expedient.task').write(cr, uid, [task_id], {'state':'done'})
        return super(stockRequisition, self).create(cr, uid, vals, context=None)

    def draft_confirmed(self, cr, uid, ids, context=None):
        """ Confirms picking.
        @return: True
        """
        for this in self.browse(cr, uid, ids):
            for line in this.move_lines:
                if line.product_id.qty_available < 0:
                    raise osv.except_osv(('Error !'), 'No puede solicitar el producto %s tiene disponible %s y esta solicitando %s'%(line.product_id.name,str(line.product_id.qty_available),str(line.product_qty)))
        self.write(cr, uid, ids, {'state': 'Solicitado'})
        return True

    def _prepare_order_picking(self, cr, uid, order, context=None):
        return {
            'ie_type':type_compra[0],
            'type_internal_menu':'in',
            'is_oc':True,
            'responsable_id':order.solicitant_id.id,
            'solicitant_id':order.req_id.solicitant_id.id,
            'unidad_id':order.req_id.department_id.id,
            'tramite_id':order.tramite_id.id,
            'name': '/',#self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
            'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
            'date': order.date_order,
            'type': 'in',
            'internal_type':'in',
            'address_id': order.dest_address_id.id or order.partner_address_id.id,
            'invoice_state': '2binvoiced' if order.invoice_method == 'picking' else 'none',
            'purchase_id': order.id,
            'company_id': order.company_id.id,
            'move_lines' : [],
            'bodega_id' : bodega_id,
            'presp_ref' : order.req_id.presp_ref.id,
            'partner_id' : order.partner_id.id,
            }   

    def return_draft(self, cr, uid, ids, context=None):
        req_obj = self.pool.get('stock.requisition')
        for this in self.browse(cr, uid, ids):
            if uid==this.create_user_id.id:
                req_obj.write(cr, uid, this.id,{
                        'state':'Borrador',
                        })
            else:
                raise osv.except_osv(('Error de acceso'), ('Solo el usuario creador del requerimiento puede regresar a borrador'))
        return True

    def confirm_aprobe(self, cr, uid, ids, context=None):
        """ Confirms picking.
        @return: True
        """
        #crea el picking en draft
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
#        picking_id = self.pool.get('stock.picking').create(cr, uid, self._prepare_order_picking(cr, uid, order, context),context)  
        self.write(cr, uid, ids, {'state': 'Aprobado'})
        return True

    def print_rqm(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de retencion
        '''                
        if not context:
            context = {}
        picking = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [picking.id],
                 'model': 'stock.requisition'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'stock.picking.rqm',
            'model': 'account.retention',
            'datas': datas,
            'nodestroy': True,            
                }

    def _get_user(self, cr, uid, ids, context=None):
        return uid

    _defaults = dict(
        state = 'Borrador',
        create_user_id = _get_user,
        date = lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        )

stockRequisition()
