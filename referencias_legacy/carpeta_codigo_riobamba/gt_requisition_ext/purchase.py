# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
from osv import osv, fields
import time
from gt_tool import amount_to_text_ec


class cajaChicaVale(osv.Model):
    _name = 'caja.chica.vale'

    def _compute_total_vale(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            aux = this.subtotal - this.retencion
        res[this.id] = aux
        return res

    def _total_letras(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        for this in self.browse(cr, uid, ids):
            letra = amount_to_text_ec.amount_to_text_ec(this.cantidad)
            res[this.id] = letra
        return res

    _columns = dict(
        letras = fields.function(_total_letras, string="Cantidad", store=True, type="char",size=256), 
        create_user_id = fields.many2one('res.users','Creado por'),
        solicitud_id = fields.many2one('caja.chica.solicitud','Solicitud de caja chica'),
        name = fields.char('Codigo',size=8),
        lugar_id = fields.many2one('res.country.state.parish','Lugar'),
        date = fields.date('Fecha'),
        unidad_id = fields.many2one('hr.department','Unidad Requirente'),
        concepto = fields.text('Concepto'),
        detalle = fields.text('Para'),
        subtotal = fields.float('Total'),
        retencion = fields.float('Valor Retenido'),
        cantidad = fields.function(_compute_total_vale,string='Total - Retencion',type="float",store=True),
        state = fields.selection([('Borrador','Borrador'),('Ejecutado','Ejecutado')],'Estado'),
    )

    def onchange_solicitud_vale(self, cr, uid, ids, solicitud_id, context={}):
        solicitud_obj = self.pool.get('caja.chica.solicitud')
        solicitud = solicitud_obj.browse(cr, uid, solicitud_id)
        vals = {}
        aux_detalle = ''
        aux_subtotal = 0
        for line in solicitud.line_ids:
            aux_detalle = line.name + '\r\n'
            aux_subtotal += line.subtotal
        return {'value':{'detalle':solicitud.desc,'concepto':aux_detalle,'subtotal':aux_subtotal}}

    def print_vale_caja(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        vale = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [vale.id],
                 'model': 'caja.chica.vale'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'caja.vale',
            'model': 'caja.chica.vale',
            'datas': datas,
            'nodestroy': True,            
                }

    def return_vale_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'Borrador'})
        return True

    def vale_draft_ejecutado(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if this.name=='/':
                obj_sequence = self.pool.get('ir.sequence')
                aux_name = obj_sequence.get(cr, uid, 'caja.chica.vale')
                self.write(cr, uid, ids, {'state':'Ejecutado','name':aux_name,})
            else:
                self.write(cr, uid, ids, {'state':'Ejecutado'})
        return True

    def _get_user(self, cr, uid, ids, context=None):
        return uid

    _defaults = dict(
        name = '/',
        state = 'Borrador',
        create_user_id = _get_user,
    )
cajaChicaVale()

class cajaChicaSolicitudLine(osv.Model):
    _name = 'caja.chica.solicitud.line'

    def _compute_subtotal(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            aux = this.qty * this.pu
        res[this.id] = aux
        return res

    _columns = dict(
        caja_id = fields.many2one('caja.chica.solicitud','Caja'),
        name = fields.char('Descripcion',size=128),
        unidad = fields.many2one('product.uom','Unidad'),
        qty = fields.float('Cantidad'),
        pu = fields.float('Precio Unidad'),
        subtotal = fields.function(_compute_subtotal,string='Subtotal',type="float",store=True),  
    )
cajaChicaSolicitudLine()
class cajaChicaSolicitud(osv.Model):
    _name = 'caja.chica.solicitud'

    def print_sol_caja(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de retencion
        '''                
        if not context:
            context = {}
        caja = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [caja.id],
                 'model': 'caja.chica.solicitud'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'caja.solicitud',
            'model': 'caja.chica.solicitud',
            'datas': datas,
            'nodestroy': True,            
                }

    def return_caja_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'Borrador'})
        return True

    def caja_draft_solicitado(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if this.name=='/':
                obj_sequence = self.pool.get('ir.sequence')
                aux_name = obj_sequence.get(cr, uid, 'caja.chica.solicitud')
                self.write(cr, uid, ids, {'state':'Solicitado','name':aux_name,})
            else:
                self.write(cr, uid, ids, {'state':'Solicitado'})
        return True

    def _get_user(self, cr, uid, ids, context=None):
        return uid

    _columns = dict(
        create_user_id = fields.many2one('res.users','Creado por'),
        date = fields.date('Fecha'),
        name = fields.char('Numero',size=10),
        solicita_id = fields.many2one('hr.employee','Solicitado por:'),
        aprobador_id = fields.many2one('hr.employee','Aprueba'),
        department_id = fields.related('solicita_id','department_id',type='many2one',relation='hr.department',string='Departamento:',store=True),
        desc = fields.text('Descripcion'),
        line_ids = fields.one2many('caja.chica.solicitud.line','caja_id','Detalle'),
        state = fields.selection([('Borrador','Borrador'),('Solicitado','Solicitado')],'Estado'),
        asset_id = fields.many2one('account.asset.asset','Vehiculo/Maquinaria'),
        flag = fields.boolean('Bandera'),
    )

    _defaults = dict(
        flag = False,
        name = '/',
        state = 'Borrador',
        create_user_id = _get_user,
        date = lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        )

cajaChicaSolicitud()

#class puOrderLineExt(osv.Model):
#    _inherit = 'purchase.order.line'
#    _columns = dict(
#        uom_desc = fields.char('U. Medida',size=12),
#    )
#puOrderLineExt()

class reqSinProducto(osv.Model):
    _inherit = 'purchase.requisition'

    _columns = dict(
        aprueba_aux = fields.many2one('hr.employee','Aprobador',
                            help="El sistema imprime en la firma el jefe inmediato, pero si usted llena este campo la persona seleccionada saldra para la firma"),
        partida_aux = fields.char('Partida presupuestaria',size=128),
    )
    
    def _validate_lines(self, cr, uid, ids, context=None, opc=1):
        #Aqui se deberia validar solamente que no se compre mas de lo pedido
        j = 0
        band = True
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                total_solicitud = line.product_qty
                aux = 0 
                if opc==1:
                    for po in this.purchase_ids:
                        for po_line in po.order_line:
                            if po_line.select:
                                aux += po_line.product_qty
                else:
                    for po in this.purchase_select_ids:
                        for po_line in po.order_line:
                            if po_line.select:
                                aux += po_line.product_qty
                if aux<1:
                    raise osv.except_osv(('Error !'), 'No puede comprar CERO, esta comprando %s del producto %s y la solicitud es por %s'%(str(aux),line.product_id.name,str(line.product_qty)))
        return True

    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
        """
        Create New RFQ for Supplier
        """
        if context is None:
            context = {}
        assert partner_id, 'Debe seleccionar un proveedor'
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')
        fiscal_position = self.pool.get('account.fiscal.position')
        addres_obj = self.pool.get('res.partner.address')
        uom_obj = self.pool.get('product.uom')
        supplier = res_partner.browse(cr, uid, partner_id, context=context)
        delivery_address_id = res_partner.address_get(cr, uid, [supplier.id], ['delivery'])['delivery']
        supplier_pricelist = supplier.property_product_pricelist_purchase or False
        res = {}
        for requisition in self.browse(cr, uid, ids, context=context):
            uom_ids = uom_obj.search(cr, uid, [])
#            for line in requisition.line_ids:
#                if not line.product_id:
#                    raise osv.except_osv(('Error de usuario'), ('Para la cotizacion de proveedor deben estar seleccionados productos en la solicitud'))
            if supplier.id in filter(lambda x: x, [rfq.state <> 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
                print "MSG"
            location_id = requisition.warehouse_id.lot_input_id.id
            po_ids = len(requisition.purchase_ids)
            seq =requisition.name + "-" +str(po_ids)
            adress_aux = 0
            if delivery_address_id:
                adress_aux = delivery_address_id
            else:
                adress_aux = addres_obj.create(cr, uid, {
                    'name':supplier.direccion,
                    'street':supplier.direccion,
                })
            purchase_id = purchase_order.create(cr, uid, {
                'name':seq,
                'origin': requisition.name,
                'partner_id': supplier.id,
                'partner_address_id': adress_aux,
                'pricelist_id': supplier_pricelist.id,
                'location_id': location_id,
                'company_id': requisition.company_id.id,
                'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
                'requisition_id':requisition.id,
                'warehouse_id':requisition.warehouse_id.id,
                'notes':requisition.description,
            })
            res[requisition.id] = purchase_id
            for line in requisition.line_ids:
                k = 0
                product = line.product_id
                #seller_price, qty, default_uom_po_id, date_planned = self._seller_details(cr, uid, line, supplier, context=context)
#                taxes_ids = product.supplier_taxes_id
                if product.default_code:
                    srt_aux = product.default_code + ' ' + product.name
                else:
                    srt_aux = product.name
#                if len(product.supplier_taxes_id)<0:
#                     raise osv.except_osv(('Error de configuración'), ('El producto %s no tiene configurado impuestos') %(str_aux))
                taxes_ids = []
#                for impuesto in product.supplier_taxes_id:
#                    if impuesto.tax_group=="vat" or impuesto.tax_group=="ice":
#                        taxes_ids.append(impuesto)
                taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
#                if not requisition.cotizar_all:
#                    qty_stock = product.qty_available
#                    qty = abs(qty_stock - qty)
                qty=line.product_qty
                if qty>0:
                    k += 1
                    line_desc = ''
                    if line.desc:
                        desc = line.desc
                    if line.product_id:
                        purchase_order_line.create(cr, uid, {
                            'order_id': purchase_id,
                            'name': desc,
                            'product_qty': qty,
                            'product_id': line.product_id.id,
                            'qty_available':product.qty_available,
                            'product_uom': line.product_id.uom_id.id,
                            'uom_desc':line.product_id.uom_id.name,
                            'price_unit': 0,
                            'date_planned': time.strftime('%d-%m-%Y'),
                            'notes': product.description_purchase,
                            'taxes_id': [(6, 0, taxes)],
                            'presp_ref':requisition.presp_ref.id,
                            }, context=context)
                    else:
                        purchase_order_line.create(cr, uid, {
                            'order_id': purchase_id,
                            'name': desc,
                            'product_qty': qty,
                            'qty_available':product.qty_available,
                      #      'product_uom': uom_ids[0],
                            'price_unit': 0,
                            'date_planned': time.strftime('%d-%m-%Y'),
                            'notes': product.description_purchase,
                            'taxes_id': [(6, 0, taxes)],
                            'presp_ref':requisition.presp_ref.id,
                            }, context=context)
                if not k>0:
                    purchase_order.write(cr, uid, purchase_id,{
                            'select':False,
                            })
        return res

    def tender_in_progress(self, cr, uid, ids, context=None):
        config_obj = self.pool.get('purchase.config.infima')
        budget_obj = self.pool.get('budget.certificate')
        config_ids = config_obj.search(cr, uid, [('activo','=',True)],limit=1)
        if config_ids:
            config = config_obj.browse(cr, uid, config_ids[0])
            monto_maximo = config.monto_maximo
        else:
            raise osv.except_osv(('Error de configuración'), ('No tiene tabla de configuración de montos de infima cuantia activa'))
        for this in self.browse(cr, uid, ids):
            solicitant_user = this.usr_solicitant_id.id
            if this.presp_ref.amount_total > monto_maximo:
                raise osv.except_osv(('Error de usuario'), ('El monto del presupuesto referencial %s es mayor al permitido para realizar el proceso de infima cuantía %s') %(str(this.presp_ref.amount_total),str(monto_maximo)))
            total_items = len(this.line_ids)
            if len(this.line_ids)>0:
                self.write(cr, uid, ids, {'state':'in_progress',
                                          'revert':False,
                                          'total_items':total_items,} ,context=context)
                budget_obj.write(cr, uid, this.presp_ref.id, {'is_lock':True})
                self._generate_log(cr, uid, ids[0],'En proceso')
            else:
                raise osv.except_osv(('Error Usuario'), ('Debe ingresar por lo menos una linea en la solicitud de compra'))
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'gt_government_procedure', 'action_purchase_requisition_alone')
        id_view = result and result[1] or False
        result = act_obj.read(cr, uid, [id_view], context=context)[0]
        return result    

reqSinProducto()

class assetCaja(osv.Model):
    _inherit = 'account.asset.asset'
    _columns = dict(
        caja_ids = fields.one2many('caja.chica.solicitud','asset_id','Detalle Caja Chica'),
    )
assetCaja()
