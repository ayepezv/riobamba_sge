# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import osv, fields
import time
from datetime import date
from tools.translate import _
import decimal_precision as dp
import netsvc

class POLine(osv.Model):
    _inherit = 'purchase.order.line'

    def _check_values(self, cr, uid, ids):
        result = False
        for obj in self.browse(cr, uid, ids):
            if obj.product_qty > 0 and obj.price_unit >= 0:
                result = True
        return result

    def _amount_line_s(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            if line.select:
                taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty)
                cur = line.order_id.pricelist_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
            else:
                res[line.id] = 0
        return res

    def _amount_tax_line(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        po_line_obj = self.pool.get('purchase.order.line')
        po_obj = self.pool.get('purchase.order')
        fiscal_obj = self.pool.get('account.fiscal.position')
        base_i = 0
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'amount_tax': 0.0,
                'tot_included': 0.0,
                'price_subtotal_s':0.0,
                }
            base_i = line.product_qty * line.price_unit
            aux_iva = line.order_id.iva
            if line.tax_type=='IVA':
                if aux_iva:
                    aux_p = (float(aux_iva)/100.00)
                    aux = (base_i * aux_p)
                else:
                    aux = (base_i * 0.12)  #0.14
                res[line.id]['price_subtotal_s'] = base_i
                res[line.id]['amount_tax'] = aux
                res[line.id]['tot_included'] = base_i + aux
                return res
            else:
                aux = 0 
                res[line.id]['price_subtotal_s'] = base_i
                res[line.id]['amount_tax']  = aux
                res[line.id]['tot_included']  = aux + base_i
                return res
#            po_line_obj.write(cr, uid, line.id, {
#                'amount_tax':aux,
#            })
            #aqui calcular en base a si hay iva o ice o nada
            #po = po_obj.browse(cr, uid, line.order_id.id)
            #taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty)
            #cur = line.order_id.pricelist_id.currency_id
            #res[line.id] = cur_obj.round(cr, uid, cur, taxes['total_included']-taxes['total'])

    def _amount_total_inc_line(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = line.price_subtotal_s + line.amount_tax#cur_obj.round(cr, uid, cur, line.price_subtotal_s + line.amount_tax)
        return res

    _columns = dict(
        tax_type = fields.selection([('IVA','IVA'),('ICE','ICE'),('IVA e ICE','IVA e ICE')],'Impuestos'),
#        price_subtotal_s = fields.function(_amount_line_s, type="float", store=True,string='Subtotal', 
#                                           digits_compute= dp.get_precision('Purchase Price')),
        price_subtotal_s = fields.function(_amount_tax_line, multi="tl",type="float", store=True,string='Subtotal', 
                                           digits_compute= dp.get_precision('Purchase Price')),
        amount_tax = fields.function(_amount_tax_line, string='Imp.', multi="tl",store=True,digits_compute= dp.get_precision('Purchase Price')),
#        tot_included = fields.function(_amount_total_inc_line, string='Total', store=True,digits_compute= dp.get_precision('Purchase Price')),
        tot_included = fields.function(_amount_tax_line, string='Total', multi="tl",store=True,digits_compute= dp.get_precision('Purchase Price')),
        select = fields.boolean('Seleccionar'),
        is_group = fields.boolean('Agrupar'),
        qty_available = fields.float('Cant. Disponible'),
        presp_ref = fields.many2one('budget.certificate','Pres. Referecial'),
        uom_desc = fields.char('U. Medida',size=12),
        )

    _defaults = dict(
        select = True,
        tax_type ='IVA',
    )

    _constraints = [
        (_check_values,'Los valores de precio unitario y cantidad deben ser mayor a cero',['product_qty','price_unit']),
        ]

POLine()


class purchaseOrder(osv.Model):
    _inherit = 'purchase.order'

    def has_stockable_product(self,cr, uid, ids, *args):
        for order in self.browse(cr, uid, ids):
            for order_line in order.order_line:
                if order_line.product_id and order_line.product_id.product_tmpl_id.type in ('product', 'consu','asset'):
                    return True
        return False

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = aux_taxes = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                aux_taxes += line.amount_tax
                #if line.select: #si queremos calcular solamente de los seleccionados
                val1 += line.price_subtotal
                for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, order.partner_address_id.id, line.product_id.id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax']=aux_taxes#cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + aux_taxes#res[order.id]['amount_tax']
        return res

    def seleccionar_requisition(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('purchase.order.line')
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                if line.select:
                    line_obj.write(cr, uid, line.id, {'select':False})
                else:
                    line_obj.write(cr, uid, line.id, {'select':True})
        return True

    def calcular_valores(self, cr, uid, ids, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                #if line.select: #si queremos calcular solamente de los seleccionados
                val1 += line.price_subtotal
                for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, order.partner_address_id.id, line.product_id.id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res['amount_tax']=cur_obj.round(cr, uid, cur, val)
            res['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
            res['amount_total']=res['amount_untaxed'] + res['amount_tax']
            self.write(cr, uid, ids, res, context)
        return res

    def _amount_all_iva(self, cr, uid, ids, field_name, arg, context=None):
        '''    Desglosa el valor de iva, ice e impuesto verde 
        por cotizaciion
        '''
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'iva_value': 0.0,
                'ice_value': 0.0,
                'imp_verde': 0.0,
            }
            val = ice_line = iva_line=line_imp=ice_l= impuesto_line = 0.0
            cur = order.pricelist_id.currency_id
            imp_prueba=0
            for order_line in order.order_line:
                #if order_line.select:
#                    vat_l=ice_l=0
#                    for tax in order_line.taxes_id:
#                        if tax.tax_group=="vat":# and tax.price_include==True:
#                            vat_l=tax.porcentaje
#                        else:
#                            if tax.tax_group=="ice":# and tax.price_include==True:
#                                ice_l=tax.porcentaje
#                    line_imp=float(vat_l)+float(ice_l)
                    #impuesto_line=(order_line.product_qty*order_line.price_unit)*(line_imp/(100.00))#+line_imp))
                print "ivasssssss", order_line.amount_tax, impuesto_line
                impuesto_line += order_line.amount_tax
                aux = 0 
#                    if ice_l!=0:
#                        ice_line+=impuesto_line*(float(ice_l)/line_imp)
#                        iva_line+=impuesto_line-(impuesto_line*(float(ice_l)/line_imp))
#                    else: 
#                        iva_line+=impuesto_line
            res[order.id]['iva_value']=cur_obj.round(cr, uid, cur, impuesto_line)
            res[order.id]['ice_value']=cur_obj.round(cr, uid, cur, 0)
            res[order.id]['imp_verde']=cur_obj.round(cr, uid, cur, 0)
        return res

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        partner = self.pool.get('res.partner')
        if not partner_id:
            return {'value':{'partner_address_id': False, 'fiscal_position': False}}
        supplier_address = partner.address_get(cr, uid, [partner_id], ['default'])
        supplier = partner.browse(cr, uid, partner_id)
        pricelist = supplier.property_product_pricelist_purchase.id
        ec_type = supplier.partner_incop_type
        fiscal_position = supplier.property_account_position and supplier.property_account_position.id or False
        return {'value':{'partner_address_id': supplier_address['default'],'partner_incop_type':ec_type ,'pricelist_id': pricelist, 'fiscal_position': fiscal_position}}

    def print_oc_req(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir la orden de compra
        '''        
        if not context:
            context = {}
        order_obj = self.pool.get('purchase.order')
        order = order_obj.browse(cr, uid, ids, context)[0]
        datas = {'ids': [order.id], 'model': 'purchase.order'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchase.order.m',
            'model': 'purchase.order',
            'datas': datas,
            'nodestroy': True,                        
            }

    def action_invoice_create(self, cr, uid, ids, context=None):
        """Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
        Relaciona el presupuesto referencial
        :param ids: list of ids of purchase orders.
        :return: ID of created invoice.
        :rtype: int
        """
        res = False

        journal_obj = self.pool.get('account.journal')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        fiscal_obj = self.pool.get('account.fiscal.position')
        property_obj = self.pool.get('ir.property')

        for order in self.browse(cr, uid, ids, context=context):
            pay_acc_id = order.partner_id.property_account_payable.id
            journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase'),('company_id', '=', order.company_id.id)], limit=1)
            if not journal_ids:
                raise osv.except_osv(_('Error !'),
                    _('There is no purchase journal defined for this company: "%s" (id:%d)') % (order.company_id.name, order.company_id.id))

            # generate invoice line correspond to PO line and link that to created invoice (inv_id) and PO line
            inv_lines = []
            for po_line in order.order_line:
                if po_line.product_id:
                    acc_id = po_line.product_id.product_tmpl_id.property_account_expense.id
                    if not acc_id:
                        acc_id = po_line.product_id.categ_id.property_account_expense_categ.id
                    if not acc_id:
                        raise osv.except_osv(_('Error !'), _('There is no expense account defined for this product: "%s" (id:%d)') % (po_line.product_id.name, po_line.product_id.id,))
                else:
                    acc_id = property_obj.get(cr, uid, 'property_account_expense_categ', 'product.category').id
                fpos = order.fiscal_position or False
                acc_id = fiscal_obj.map_account(cr, uid, fpos, acc_id)

                inv_line_data = self._prepare_inv_line(cr, uid, acc_id, po_line, context=context)
                inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                inv_lines.append(inv_line_id)

                po_line.write({'invoiced':True, 'invoice_lines': [(4, inv_line_id)]}, context=context)

            # get invoice data and create invoice
            inv_data = {
                'name': order.partner_ref or order.name,
                'reference': order.partner_ref or order.name,
                'account_id': pay_acc_id,
                'type': 'in_invoice',
                'partner_id': order.partner_id.id,
                'currency_id': order.pricelist_id.currency_id.id,
                'address_invoice_id': order.partner_address_id.id,
                'address_contact_id': order.partner_address_id.id,
                'journal_id': len(journal_ids) and journal_ids[0] or False,
                'invoice_line': [(6, 0, inv_lines)], 
                'origin': order.name,
                'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
                'payment_term': order.partner_id.property_payment_term and order.partner_id.property_payment_term.id or False,
                'company_id': order.company_id.id,
                'certificate_id':order.presp_ref.id,
            }
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            # compute the invoice
            inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)

            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv_id)]}, context=context)
            res = inv_id
        return res

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        return {
            'name': order.name + ': ' + (order_line.name or ''),
            'product_id': order_line.product_id.id,
            'product_qty': order_line.product_qty,
            'product_uos_qty': order_line.product_qty,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': order_line.date_planned,
            'date_expected': order_line.date_planned,
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'address_id': order.dest_address_id.id or order.partner_address_id.id,
            'move_dest_id': order_line.move_dest_id.id,
            'state': 'draft',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': order_line.price_unit,
            'amount_tax' :order_line.amount_tax,
            'subtotal':order_line.price_subtotal,
        }

    def _create_pickings(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """Creates pickings and appropriate stock moves for given order lines, then
        confirms the moves, makes them available, and confirms the picking.

        If ``picking_id`` is provided, the stock moves will be added to it, otherwise
        a standard outgoing picking will be created to wrap the stock moves, as returned
        by :meth:`~._prepar0,00e_order_picking`.

        Modules that wish to customize the procurements or partition the stock moves over
        multiple stock pickings may override this method and call ``super()`` with
        different subsets of ``order_lines`` and/or preset ``picking_id`` values.

        :param browse_record order: purchase order to which the order lines belong
        :param list(browse_record) order_lines: purchase order line records for which picking
                                                and moves should be created.
        :param int picking_id: optional ID of a stock picking to which the created stock moves
                               will be added. A new picking will be created if omitted.
        :return: list of IDs of pickings used/created for the given order lines (usually just one)
        """
        context = {}
        context['type_internal_menu']='in'
        context['type']='in'
        if not picking_id: 
            picking_id = self.pool.get('stock.picking').create(cr, uid, self._prepare_order_picking(cr, uid, order, context),context)
        todo_moves = []
        stock_move = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        for order_line in order_lines:
            if not order_line.product_id:
                continue
            if order_line.product_id.type in ('product', 'consu','asset'):
                #aqui pasar en el context un parametro para q no use el create modificado sino el normal
                context = {}
                context['crear'] = True
                move = stock_move.create(cr, uid, self._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context),context)
                if order_line.move_dest_id:
                    order_line.move_dest_id.write({'location_id': order.location_id.id})
                todo_moves.append(move)
        stock_move.action_confirm(cr, uid, todo_moves)
        stock_move.force_assign(cr, uid, todo_moves)
        wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return [picking_id]


    def _prepare_order_picking(self, cr, uid, order, context=None):
        location_obj = self.pool.get('stock.location')
        #sacar la bodega de los productos
 #       for line_o in order.req_id.line_ids:
  #         if line_o.product_id.type in ('product','consu'):
        bodega_ids = location_obj.search(cr, uid, [('is_general','=',True)])
        bodega_id = bodega_ids[0]
        type_compra = self.pool.get('ie.type').search(cr, uid, [('is_compra','=',True)],limit=1)
        if order.req_id:
            return {
                'ie_type':type_compra[0],
                'type_internal_menu':'in',
                'is_oc':True,
                'responsable_id':order.solicitant_id.id,
                'solicitant_id':order.req_id.solicitant_id.id,
                'unidad_id':order.req_id.department_id.id,
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
        else:
            bodega_ids = location_obj.search(cr, uid, [('is_general','=',True)],limit=1)
            if len(bodega_ids)<1:
                 raise osv.except_osv(('Error de configuración!'),('No existe bodega general configurada'))
            return {
                'type_internal_menu':'in',
                'responsable_id':order.solicitant_id.id,
                'solicitant_id':order.solicitant_id.id,
                'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
                'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
                'date': order.date_order,
                'type': 'in',
                'partner_id':order.partner_id.id,
                'address_id': order.dest_address_id.id or order.partner_address_id.id,
                'invoice_state': '2binvoiced' if order.invoice_method == 'picking' else 'none',
                'purchase_id': order.id,
                'company_id': order.company_id.id,
                'bodega_id' : bodega_ids[0],
                'move_lines' : [],
                'presp_ref' : order.presp_ref.id,
                }

    def _compute_items(self, cr, uid, ids, a, b, c):
        po = self.pool.get('purchase.order')
        res = {}
        aux = 0
        this = self.browse(cr, uid, ids[0])
        for line in this.order_line:
            if line.select:
                aux += line.product_qty
        res[this.id] = aux
        return res

    def _is_select(self, cr, uid, ids, a, b, c):
        this = self.browse(cr, uid, ids[0])
        res = {}
        aux = False
        if this.number_select > 0:
            aux = True
        res[this.id] = aux
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = dict(
        date_order = fields.date('Fecha Pedido'),
        date_acta = fields.date('Fecha Acta'),
        was_recomended = fields.boolean('fue recomendado'),
        is_finish = fields.boolean('Finalizado'),
        is_cotizacion = fields.boolean('Cot'),
        partner_incop_type = fields.selection([('economia_popular','Economia popular y solidaria'),
                                                 ('micro','Micro'),
                                                 ('pequena','Pequena'),
                                                 ('mediana', 'Mediana'),
                                                 ('grande','Grande')], 'Tipo Actor Económico'),
        solicitant_id = fields.many2one('hr.employee','Responsable'),
        select = fields.boolean('Seleccionada'),
        select_item = fields.function(_is_select,string='Seleccionada',type="boolean",store=True),
        order_ref = fields.many2one('purchase.order','Orden Padre'),
        is_son = fields.boolean('Separada'),
        iva = fields.related('requisition_id','iva', type='selection', 
                                   string='IVA', store=True),
        state_sol = fields.related('requisition_id','state', type='selection', 
                                   string='Estado', store=True),
        active = fields.boolean('Activo'),
        in_stock = fields.boolean('Tiene en stock'),
        procedencia = fields.char('Procedencia',size=32,required=True),
        tipo = fields.selection([('Generico','Generico'),('Marca','Marca')],'Tipo'),
        tiempo_entrega = fields.integer('Tiempo entrega(días)'),
        dias_credito = fields.integer('Días Crédito(días)'),
        garantia = fields.integer('Garantía(meses)'),
        validez = fields.integer('Validéz oferta(días)'),
        lugar_entrega = fields.selection([('Entrega Directa','Entrega Directa'),('Bodega del GPA','Bodega del GPA'),
                                          ('Entrega en la obra','Entrega en la obra'),('Bodega de proveedor','Bodega de proveedor'),
                                          ('Otro','Otro')],'Lugar Entrega'),
        number_select = fields.function(_compute_items,string='#Items',type="integer",store=True),
        requisition_select_id = fields.many2one('purchase.requisition','Solicitud'),
        req_id = fields.many2one('purchase.requisition','Solicitud Compra'),
        presp_ref = fields.many2one('budget.certificate','Pres. Referecial'),
        payment_term = fields.many2one('account.payment.term','Término de pago',required=True),
        iva_value= fields.function(_amount_all_iva, digits_compute= dp.get_precision('Account'), string='IVA',method=True,
                                   multi="sums",help="Valor de IVA",store=True,
                                   ),
        ice_value= fields.function(_amount_all_iva, digits_compute= dp.get_precision('Account'), string='ICE',method=True,
                                   multi="sums",help="Valor de ICE",store=True),
        imp_verde= fields.function(_amount_all_iva, digits_compute= dp.get_precision('Account'), string='Imp. Verde',method=True,
                                   multi="sums",help="Valor de impuesto verde",store=True),
         )

    def quit_all(self, cr, uid, ids, context=None):
        po_line_obj = self.pool.get('purchase.order.line')
        po_obj = self.pool.get('purchase.order')
        number_select = ""
        for this in self.browse(cr, uid, ids):
            for line in this.order_line:
                po_line_obj.write(cr, uid, line.id,{
                        'select':False,
                        })
        return True

    def load_product(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', [])
        data =  self.browse(cr, uid, active_ids[0], context=context)[0]
        for line in data.line_ids:
            product = line.product_id
            seller_price, qty, default_uom_po_id, date_planned = self._seller_details(cr, uid, line, supplier, context=context)
            taxes_ids = product.supplier_taxes_id
            taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
            purchase_order_line.create(cr, uid, {
                    'order_id': ids[0],
                    'name': product.partner_ref,
                    'product_qty': qty,
                    'product_id': product.id,
                    'product_uom': default_uom_po_id,
                    'price_unit': seller_price,
                    'date_planned': date_planned,
                    'notes': product.description_purchase,
                    'taxes_id': [(6, 0, taxes)],
                    }, context=context)
        return True

    def select_all(self, cr, uid, ids, context=None):
        po_obj = self.pool.get('purchase.order')
        po_line_obj = self.pool.get('purchase.order.line')
        number_select = ""
        for this in self.browse(cr, uid, ids):
            for line in this.order_line:
                po_line_obj.write(cr, uid, line.id,{
                        'select':True,
                        })
        return True

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        vals = {}
        obj_sequence = self.pool.get('ir.sequence')
        vals['name'] = obj_sequence.get(cr, uid, 'purchase.order')
        self.write(cr, uid, ids, vals)
        ##tomar la secuencia aqui
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(('Error !'),('No puede confirmar una orden de compra sin lineas de detalle.'))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)
            message = ("Orden de compra '%s' confirmada.") % (po.name,)
            self.log(cr, uid, po.id, message)
        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'done', 'validator' : uid})
        return True        

    def purchase_cut(self, cr, uid, ids, context=None):
        if context is None: context = {}
        context = dict(context, active_ids=ids, active_model=self._name)
        sep_id = self.pool.get("separate.order").create(cr, uid, {}, context=context)
        return {
            'name':"Separar Order Compra",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'separate.order',
            'res_id': sep_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }

    def _get_payment_term(self, cr, uid, ids, context=None):
        pay_obj = self.pool.get('account.payment.term')
        pay_ids = pay_obj.search(cr, uid, [])
        if not len(pay_ids)>0:
            raise osv.except_osv(('Error de configuración'), ('No se ha definido ningun termino de pago'))
        return pay_ids[0]

    def _check_desc(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if this.add_disc < 0 or this.add_disc > 100: 
                return False
        return True

    _constraints = [
        (_check_desc,'El descuento debe estar entre 0 y 100',[]),
        ] 

    _sql_constraints = [
        ('name_uniq', 'unique()', 'Order Reference must be unique per Company!'),
    ]

    _defaults = dict(
        date_acta = time.strftime('%Y-%m-%d'),
        is_cotizacion = True,
        name = '/',
        select = True,
        active = True,
        tipo = 'Generico',
        location_id = 1,
        pricelist_id = 1,
        procedencia = 'Ecuador',
        payment_term = _get_payment_term,
#        invoice_method = 'order',
        invoice_method = 'picking',
        partner_incop_type = 'micro',
#        order_line = _get_lines_po,
        )

purchaseOrder()
