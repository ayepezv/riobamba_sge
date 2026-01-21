# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

import logging

from osv import osv, fields
from tools.translate import _
import time
import netsvc
import decimal_precision as dp

class sInventory(osv.Model):
    _inherit = 'stock.inventory'
    
    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirm the inventory and writes its finished date
        @return: True
        """
        if context is None:
            context = {}
        # to perform the correct inventory corrections we need analyze stock location by
        # location, never recursively, so we use a special context
        product_obj = self.pool.get('product.product')
        product_context = dict(context, compute_child=False)

        location_obj = self.pool.get('stock.location')
        for inv in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for line in inv.inventory_line_id:
                if not line.product_id.standard_price>0:
                    raise osv.except_osv(('Error !'), ('No se puede crear una linea de un producto con precio menor o igual a CERO, Producto %s'%(line.product_id.name)))
                pid = line.product_id.id
                product_context.update(uom=line.product_uom.id, to_date=inv.date, date=inv.date, prodlot_id=line.prod_lot_id.id)
                amount = location_obj._product_get(cr, uid, line.location_id.id, [pid], product_context)[pid]

                change = line.product_qty - amount
                lot_id = line.prod_lot_id.id
                if change:
                    location_id = line.product_id.product_tmpl_id.property_stock_inventory.id
                    value = {
                        'name': 'INV:' + str(line.inventory_id.id) + ':' + line.inventory_id.name,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom.id,
                        'prodlot_id': lot_id,
                        'date': inv.date,
                    }
                    if change > 0:
                        value.update( {
                            'product_qty': change,
                            'location_id': location_id,
                            'location_dest_id': line.location_id.id,
                        })
                    else:
                        value.update( {
                            'product_qty': -change,
                            'location_id': line.location_id.id,
                            'location_dest_id': location_id,
                        })
                    move_ids.append(self._inventory_line_hook(cr, uid, line, value))
            message = _("Inventory '%s' is done.") %(inv.name)
            self.log(cr, uid, inv.id, message)
            self.write(cr, uid, [inv.id], {'state': 'confirm', 'move_ids': [(6, 0, move_ids)]})
            self.pool.get('stock.move').action_confirm(cr, uid, move_ids, context=context)
        return True

sInventory()

class inventoryLine(osv.Model):
    _inherit = 'stock.inventory.line'

    def create(self, cr, uid, vals, context):
        product_obj = self.pool.get('product.product')
        if vals['product_id']:
            producto = product_obj.browse(cr, uid, vals['product_id'])
            if producto.standard_price>0:
                return super(inventoryLine, self).create(cr, uid, vals, context=None)
            else:
                raise osv.except_osv(('Error !'), ('No se puede crear una linea de un product con precio menor o igual a CERO'))

    _columns = dict(
        category_id = fields.related('product_id','categ_id',type='many2one',relation='product.category',string='Categoria',store=True),
    )
inventoryLine()


class auxcardex(osv.Model):
    _name = 'aux.cardex'
    _columns = dict(
        code = fields.char('Codigo P',size=15),
        name = fields.many2one('product.product','Producto'),
        tipo_move = fields.selection([('i','i'),('e','e')],'Tipo'),
        qty = fields.float('Cantidad'),
        pu = fields.float('Precio Unitario'),
        total = fields.float('Total'),
        seq = fields.integer('Secuencia'),
    )
auxcardex()   

class stockMove(osv.Model):
    _inherit = 'stock.move'

    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        """
        Return the accounts and journal to use to post Journal Entries for the real-time
        valuation of the move.

        :param context: context dictionary that can explicitly mention the company to consider via the 'force_company' key
        :raise: osv.except_osv() is any mandatory account or journal is not defined.

        Redefino para considerar las cuentas que estan configuradas en
        objecto: ctas.categ
        """
        product_obj = self.pool.get('product.product')
        ctas_config = self.pool.get('ctas.categ')
        return True


    def _create_product_valuation_moves(self, cr, uid, move, context=None):
        """
        Generate the appropriate accounting moves if the product being moves is subject
        to real_time valuation tracking, and the source or destination location is
        a transit location or is outside of the company.
        """
        return True
##         print "ENTRA EN MI METODO Q NO GENERA ASIENTO DE INGRESO"
##         if move.product_id.valuation == 'real_time': # FIXME: product valuation should perhaps be a property?
##             if context is None:
##                 context = {}
##             src_company_ctx = dict(context,force_company=move.location_id.company_id.id)
##             dest_company_ctx = dict(context,force_company=move.location_dest_id.company_id.id)
##             account_moves = []
##             # Outgoing moves (or cross-company output part)
##             if move.location_id.company_id \
##                 and (move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal'\
##                      or move.location_id.company_id != move.location_dest_id.company_id):
##                 #redefinir para q tome la CC en base a la tabla
##                 journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, src_company_ctx)
##                 reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
##                 account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_dest, reference_amount, reference_currency_id, context))]

##             # Incoming moves (or cross-company input part)
##             #Comentado para que no genere asientos de ingreso
## #            if move.location_dest_id.company_id \
## #                and (move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal'\
## #                     or move.location_id.company_id != move.location_dest_id.company_id):
## #                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, dest_company_ctx)
## #                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
## #                account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_src, acc_valuation, reference_amount, reference_currency_id, context))]
## #
##             move_obj = self.pool.get('account.move')
##             for j_id, move_lines in account_moves:
##                 move_obj.create(cr, uid,
##                         {
##                          'journal_id': j_id,
##                          'line_id': move_lines,
##                          'ref': move.picking_id and move.picking_id.name})


    def onchange_subtotal_move(self, cr, uid, ids, subtotal, product_qty):
        """ On change of subtotal 
        @param product_id: Product id
        @return: Dictionary of values
        """
        result = {}
        value = subtotal / product_qty
        result['price_unit'] = value
#        self.write(cr, uid, ids[0],{'price_unit':value,})
        return {'value': result}

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
        result['categ_id'] = product.categ_id.id
        result['product_uom'] = product.uom_id.id
        return {'value': result}

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            total = (line.subtot / line.product_qty)
            res[line.id] = total
        return res

    def _amount_all_imp(self, cr, uid, ids, field_name, arg, context=None):
        '''    Calcula el valor por unidad y los impuestos
        '''
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            if order.type=='in':
                res[order.id] = {
                    'iva_value': 0.0,
                    'ice_value': 0.0,
                    'imp_verde': 0.0,
                }
                val = ice_line = iva_line=line_imp=ice_l=price_unit= aux_iva = 0.0
                vat_l=ice_l=0
                for tax in order.product_id.supplier_taxes_id:
                    if tax.tax_group=="vat" or tax.tax_group=="ice":
                        if tax.tax_group=="vat":# and tax.price_include==True:
                            vat_l=tax.amount                        
                        else:
                            if tax.tax_group=="ice":# and tax.price_include==True:
                                ice_l=tax.amount
                line_imp=float(ice_l)+float(vat_l)
                impuesto_line=(order.subtot*(line_imp))
                if ice_l!=0:
                    ice_line=impuesto_line*(float(ice_l)/line_imp)
                    iva_line=impuesto_line-ice_line
                else: 
                    iva_line=impuesto_line
                aux_iva = 0
                if order.tax_type =='IVA':
                    if order.picking_id.iva:
                        aux_iva = (order.subtot)*(order.picking_id.iva/100.00)
                    else:
                        aux_iva = (order.subtot * 0.12)  #0.14
                elif order.tax_type =='IVA e ICE':
                    if order.picking_id.iva:
                        aux_iva = (order.subtot)*(order.picking_id.iva/100.00)
                    else:
                        aux_iva = (order.subtot * 0.12) #o.14
                res[order.id]['imp_iva']=aux_iva#(iva_line)
                res[order.id]['imp_ice']=(ice_line)
                res[order.id]['price_unit']=order.subtot/order.product_qty
                res[order.id]['price_unit_inc_imp']=(order.subtot+aux_iva)/order.product_qty
                res[order.id]['total']=(float(order.subtot)+aux_iva)
            elif order.type=='out':
                res[order.id] = {
                    'iva_value': 0.0,
                    'ice_value': 0.0,
                    'imp_verde': 0.0,
                    'price_unit':0.0,
                    'total':0.0,
                }
                res[order.id]['price_unit']=order.product_id.standard_price
                res[order.id]['total']=(order.product_id.standard_price*order.product_qty)
                res[order.id]['subtot']=(order.product_id.standard_price*order.product_qty)
            else:
                return res
        return res

    _columns = dict(
#        date = fields.related('picking_id', 'date_done', type='date',
#                                   string='Fecha Realizado', store=True),
        objeto_id = fields.related('picking_id', 'objeto_id', type='many2one', relation='picking.objeto',
                                   string='Objeto receptor', store=True),
        standard_ant = fields.float('Promedio Anterior'),
        tax_type = fields.selection([('IVA','IVA'),('ICE','ICE'),('IVA e ICE','IVA e ICE')],'Impuestos'),
        department_id = fields.related('picking_id', 'unidad_id', type='many2one', relation='hr.department',
                                       string='Departamento', store=True),
        direccion_id = fields.related('department_id', 'direccion_id', type='many2one', relation='hr.department',
                                       string='Direccion', store=True),
        solicitant_id = fields.related('picking_id', 'solicitant_id', type='many2one', relation='hr.employee',
                                       string='Solicitante', store=True),
        amount_tax = fields.float('Imp.', digits_compute= dp.get_precision('Stock')),
        subtot = fields.float('Sub Total', digits_compute= dp.get_precision('Stock')),
        total = fields.function(_amount_all_imp, digits_compute= dp.get_precision('Stock'), string='Total',store=True,
             multi="sums",help="Valor Total"), 
        imp_iva = fields.function(_amount_all_imp, digits_compute= dp.get_precision('Stock'), string='IVA',store=True,
             multi="sums",help="Valor de IVA"),
        imp_ice = fields.function(_amount_all_imp, digits_compute= dp.get_precision('Stock'), string='ICE',store=True,
             multi="sums",help="Valor de ICE"),
        imp_verde = fields.function(_amount_all_imp, digits_compute= dp.get_precision('Stock'), string='Imp. Verde',store=True,
             multi="sums",help="Valor de impuesto verde"),
        price_unit = fields.function(_amount_all_imp, string='Precio Unitario', type="float",multi="sums",store=True,
                                   digits_compute= dp.get_precision('Stock')),#fields.float('Subtotal'), #funcion
        price_unit_inc_imp = fields.function(_amount_all_imp, string='Precio Unitario Inc. Imp', type="float",multi="sums",store=True,
                                   digits_compute= dp.get_precision('Stock')),#fields.float('Subtotal'), #funcion
        subtotal = fields.function(_amount_line, string='Subtotal', type="float",
                                   digits_compute= dp.get_precision('Stock'), store=True),#fields.float('Subtotal'), #funcion
        categ_id = fields.related('product_id', 'categ_id', type='many2one', relation='product.category',
                                  string='Linea', store=True),
        type_p = fields.related('product_id', 'type', type='char',
                                   string='Tipo Producto', store=True),
        presp_ref = fields.related('picking_id', 'presp_ref', type='many2one', relation='budget.certificate',
                                  string='Cert. Presp.', store=True),
        project_id = fields.related('presp_ref', 'project_id', type='many2one', relation='project.project',
                                  string='Proyecto', store=True),
        partner_id = fields.related('picking_id', 'partner_id', type='many2one', relation='res.partner',
                                  string='Proveedor', store=True),
        type_id = fields.related('picking_id','type_internal_menu', type='char',
                                  string='Tipo', store=True),
        product_uom = fields.related('product_id', 'uom_id', type='many2one', relation='product.uom',
                                  string='UDM', store=True),
        type = fields.related('picking_id','type', type='char',
                                 string='Tipo', store=True),
        num_egreso = fields.related('picking_id','name', type='char',
                                 string='Num. Egreso/Ingreso', store=True),
        num_solicitud = fields.related('picking_id','number', type='char',
                                 string='Num. Solicitud', store=True),
        
        )

    def _get_location_dest(self, cr, uid, ids, context=None):
        location_obj = self.pool.get('stock.location')
        if context:
            if not context['type']=='in':
                location_ids = location_obj.search(cr, uid, [('usage','=','customer')],limit=1)
                if not location_ids:
                    raise osv.except_osv(('Error de configuración'), ('No tiene una ubicación tipo cliente definida, configure una por favor'))
                return location_ids[0]


    def create(self, cr, uid, vals, context=None):
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        location_obj = self.pool.get('stock.location')
        if vals.has_key('picking_id'):
            picking = picking_obj.browse(cr, uid, vals['picking_id'])
        if context:
            if context.has_key('crear'):
                if context['crear'] == True:
                    return super(stockMove, self).create(cr, uid, vals, context=context)
        if context:
            if context.has_key('type'):
                if context['type']=='in':
                    vals['location_dest_id'] = picking.bodega_id.id     
                    location_ids = location_obj.search(cr, uid, [('usage','=','supplier')],limit=1)
                    if not location_ids:
                        raise osv.except_osv(('Error de configuración'), ('No tiene una ubicación tipo proveedor definida, configure una por favor'))
                    vals['location_id'] = location_ids[0]
                elif context['type']=='internal':
                    vals['location_dest_id'] = picking.bodega_dest_id.id
                    vals['location_id'] = picking.bodega_id.id 
                elif context['type']=='out':
                    product = product_obj.browse(cr, uid, vals['product_id'])
                    vals['subtot'] = vals['product_qty'] * product.standard_price
                    vals['location_id'] = picking.bodega_id.id     
                    location_ids = location_obj.search(cr, uid, [('usage','=','customer')],limit=1)
                    if not location_ids:
                        raise osv.except_osv(('Error de configuración'), ('No tiene una ubicación tipo cliente definida, configure una por favor'))
                    vals['location_dest_id'] = location_ids[0]
        else:
            return super(stockMove, self).create(cr, uid, vals, context=context)
#            raise osv.except_osv(('Error de usuario'), ('No puede crear movimientos desde esta opción'))
#captura el id retornado cmabia el name con '/' y ya
        return super(stockMove, self).create(cr, uid, vals, context=context)
    
    _defaults = dict(
        name = '/',
        tax_type = 'IVA',
        location_dest_id = _get_location_dest,
        #        location_id  = _get_location,
        )
stockMove()

class stockLocation(osv.Model):
    _inherit = 'stock.location'
    _columns = dict(
        responsable_id = fields.many2one('res.users','Responsable',required=True),
        usuario_ids = fields.many2many('res.users','bu_rel','b_id','u_id','Usuarios'),
        is_general = fields.boolean('Es general'),
        type_loc = fields.selection([('Corriente','Corriente'),('Inversion','Inversion')],'Tipo Bodega'),
        )

stockLocation()

class pickingDocType(osv.Model):
    _name = 'picking.doc.type'
    _columns = dict(
        name = fields.char('Documento',size=16,required=True),
        #movimiento = fields.selection([('out', 'Egresos'), ('in', 'Ingresos'), ('internal', 'Transacciones')],'Movimiento',required=True),
        generar_factura = fields.boolean('Genera Factura?', help='Activar la casilla en caso que el registro en inventario necesite generar factura'),
        )
pickingDocType()

class pickingObjeto(osv.Model):
    _name = 'picking.objeto'
    _columns = dict(
        name = fields.char('Objeto Receptor',size=128,required=True),
    )
pickingObjeto()

class stockPicking(osv.Model):
    _inherit = 'stock.picking'
    _order = 'date desc,name desc'
    __logger = logging.getLogger(_inherit)

    def action_print_picking(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        picking = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [picking.id],
                 'model': 'stock.picking'}
        if picking.type=='in':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'stock.picking.in',
                'model': 'stock.picking',
                'datas': datas,
                'nodestroy': True,            
            }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'stock.picking.out',
                'model': 'stock.picking',
                'datas': datas,
                'nodestroy': True,            
            }

    def action_number(self, cr, uid, ids, context=None):
        seq = self.pool.get('ir.sequence')
        if context is None:
            context = {}
        for pick in self.browse(cr, uid, ids, context):
            if pick.type == 'in' or (pick.type == 'internal' and not pick.require_guia):
                break
 #           auth = pick.stock_journal_id.authorisation_id
 #           number = seq.get(cr, uid, auth.sequence_id.code)
 #           number = '%s-%s-%s' % (auth.serie_entidad, auth.serie_emision,number)
 #           self.write(cr, uid, pick.id, {'name':number})
 #           message = _("El documento %s ha sido creado." % number)
 #           self.log(cr, uid, pick.id, message)
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
                 'model': 'stock.picking'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'stock.picking.rqm',
            'model': 'account.retention',
            'datas': datas,
            'nodestroy': True,            
                }

    def print_req_bodega(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir la solicitud de compra
        '''        
        if not context:
            context = {}
        req = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [req.id], 'model': 'stock.picking'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pick.req',
            'model': 'stock.picking',
            'datas': datas,
            'nodestroy': True,                        
            }

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        #Aqui debe tomar la secuencia
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        pick_obj = self.pool.get('stock.picking')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            #colocar fecha de realizado en el documento
            #if time.strftime('%Y-%m-%d') < pick.document_date:
            #    raise osv.except_osv('Error', 'La fecha de realizacion debe ser mayor o igual a la fecha del documento')
            if not pick.date_done:
                pick_obj.write(cr, uid, [pick.id],{'date_done':time.strftime('%Y-%m-%d')})
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.type=='out':
                    if move.product_id.qty_available<=0:
                        raise osv.except_osv('Error', 'No puede realizar egresos de productos que no tienen stock disponible')
                    aux_su = move.product_qty * move.product_id.standard_price
                    move_obj.write(cr, uid, move.id, {
                        'subtot': aux_su,
                    })
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom',False)
#                product_price = partial_data.get('product_price',0.0)
                product_price = move.price_unit
                product_currency = partial_data.get('product_currency',False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)
                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average') and (move.product_id.type in ('product','asset')):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                    if product.id in product_avail:
                        product_avail[product.id] += qty
                    else:
                        product_avail[product.id] = product.qty_available
                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, product_price)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                        if product.qty_available <= 0:
                            #considera iva
                            new_std_price = move.price_unit_inc_imp
                            #new_std_price = move.price_unit
                        else:
                            # Get the standard price
                            new_price = move.price_unit_inc_imp
                            #amount_unit = product.price_get('standard_price', context=context)[product.id]
                            amount_unit = product.standard_price
                            #considerar el iva en el standard para en el egreso solo el standar por pu
                            new_std_price = ((amount_unit * product_avail[product.id]) + (new_price * qty))/(product_avail[product.id] + qty)
                            #new_std_price = ((amount_unit * product_avail[product.id]) + (new_price * qty))/(product_avail[product.id] + qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})
                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})


            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking:
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick.type)),
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    context['type'] = pick.type
                    move_obj.copy(cr, uid, move.id, defaults, context)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty' : move.product_qty - partial_qty[move.id],
                            'product_uos_qty': move.product_qty - partial_qty[move.id], #TODO: put correct uos_qty
                            
                        })
            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking])
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
            else:
                self.action_move(cr, uid, [pick.id])
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}
            ###secuencia
            seq_obj_name = ''
            tabla_obj = self.pool.get('stock.config.sequence')
            tabla_ids = tabla_obj.search(cr, uid, [('bodega_id','=',pick.bodega_id.id)],limit=1)
            if not tabla_ids:
                raise osv.except_osv(('Error de configuración'), ('No existe tabla de secuencias definida para la bodega'))
            tabla = tabla_obj.browse(cr, uid, tabla_ids[0])
            if pick.type_internal_menu:
                if pick.type_internal_menu=='in':
                    seq_obj_name =  tabla.in_seq.code
                elif pick.type_internal_menu=='indev':
                    seq_obj_name =  tabla.in_dev_seq.code
                elif pick.type_internal_menu=='out':
                    seq_obj_name =  tabla.out_seq.code
                elif pick.type_internal_menu=='outdev':
                    seq_obj_name =  tabla.out_dev_seq.code
                else:
                    seq_obj_name =  tabla.internal_seq.code
            else:
                seq_obj_name =  tabla.out_seq.code
            if pick.name[0:1]=='/':
                aux_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
                self.write(cr, uid, pick.id, {
                    'name':aux_name,
                })
        return res

    def _get_taxes_invoice(self, cr, uid, move_line, type):
        """ Gets taxes on invoice
        @param move_line: Stock move lines
        @param type: Type of invoice
        @return: Taxes Ids for the move line
        """
        if type in ('in_invoice', 'in_refund'):
            taxes = move_line.product_id.supplier_taxes_id
        else:
            taxes = move_line.product_id.taxes_id
        context = {'budget_type':move_line.categ_id.budget, 'aplic_id': move_line.categ_id.presp_aplic_id.id}
        if move_line.picking_id and move_line.picking_id.partner_id and move_line.picking_id.partner_id:
            return self.pool.get('account.fiscal.position').map_tax(
                cr,
                uid,
                move_line.picking_id.partner_id.property_account_position,
                taxes,
                context
            )
        else:
            return map(lambda x: x.id, taxes)

    def _get_taxes_invoice_po(self, cr, uid, move_line, type):
        """ Gets taxes on invoice
        @param move_line: Stock move lines
        @param type: Type of invoice
        @return: Taxes Ids for the move line
        """
        if type in ('in_invoice', 'in_refund'):
            taxes = move_line.product_id.supplier_taxes_id
        else:
            taxes = move_line.product_id.taxes_id
        context = {'budget_type':move_line.product_id.categ_id.budget, 'aplic_id': move_line.product_id.categ_id.presp_aplic_id.id}
        if True:
            return self.pool.get('account.fiscal.position').map_tax(
                cr,
                uid,
                move_line.order_id.partner_id.property_account_position,
                taxes,
                context
            )
        else:
            return map(lambda x: x.id, taxes)

    def _prepare_invoice_line(self, cr, uid, group, picking, budget_line, invoice_id,
                              invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
        @param group: True or False
        @param picking: picking object
        @param: move_line: move_line object
        @param: invoice_id: ID of the related invoice
        @param: invoice_vals: dict used to created the invoice
        @return: dict that will be used to create the invoice line
        """
        categ_obj = self.pool.get('product.category')
        ctas_config_obj = self.pool.get('ctas.categ')
        post_obj = self.pool.get('budget.post')
        name = picking.presp_ref.notes
        origin = picking.name or ''
        if invoice_vals['type'] in ('out_invoice', 'out_refund'):
            account_id = move_line.product_id.product_tmpl_id.\
                    property_account_income.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_income_categ.id
        else:
#            line_ctas_ex = ctas_config_obj.search(cr, uid, [('budget_ex','child_of',[budget_line.budget_post.id])],limit=1)
#            line_ctas_inv = ctas_config_obj.search(cr, uid, [('budget_inv','child_of',[budget_line.budget_post.id])],limit=1)
            line_ctas_ex = ctas_config_obj.search(cr, uid, [('budget_ex','=',budget_line.budget_post.id)],limit=1)
            line_ctas_inv = ctas_config_obj.search(cr, uid, [('budget_inv','=',budget_line.budget_post.id)],limit=1)
            if line_ctas_ex:
                line_ctas = ctas_config_obj.browse(cr, uid, line_ctas_ex[0])
                account_id = line_ctas.account_ex_normal.id
                categ_id = line_ctas.categ_id.id
            elif line_ctas_inv:
                line_ctas = ctas_config_obj.browse(cr, uid, line_ctas_inv[0])
                account_id = line_ctas.account_ex_program.id
                categ_id = line_ctas.categ_id.id
            else:
                line_ctas_ex = ctas_config_obj.search(cr, uid, [('budget_ex','=',budget_line.budget_post.parent_id.id)],limit=1)
                line_ctas_inv = ctas_config_obj.search(cr, uid, [('budget_inv','=',budget_line.budget_post.parent_id.id)],limit=1)
                if line_ctas_ex:
                    line_ctas = ctas_config_obj.browse(cr, uid, line_ctas_ex[0])
                    account_id = line_ctas.account_ex_normal.id
                    categ_id = line_ctas.categ_id.id
                elif line_ctas_inv:
                    line_ctas = ctas_config_obj.browse(cr, uid, line_ctas_inv[0])
                    account_id = line_ctas.account_ex_program.id
                    categ_id = line_ctas.categ_id.id
                else:
                    raise osv.except_osv(('Error de configuracion'),'No existe configuracion de la partida %s con la categoria en el ingreso de bodega' % (budget_line.budget_post.code))
        if invoice_vals['fiscal_position']:
            fp_obj = self.pool.get('account.fiscal.position')
            fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
            account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        # set UoS if it's a sale and the picking doesn't have one
#        uos_id = move_line.product_uos and move_line.product_uos.id or False
#        if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
#            uos_id = move_line.product_uom.id
        #barrer el ingreso por categoria y pasar solo BI
        aux_price_unit = (budget_line.amount_commited)/(1.12)
        return {
            'budget_id':budget_line.id,
            'categ_id':categ_id,
            'name': name,
            'origin': origin,
            'invoice_id': invoice_id,
 #           'uos_id': uos_id,
     #       'product_id': move_line.product_id.id,
            'account_id': account_id,
            'price_unit': aux_price_unit,#self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
#            'discount': self._get_discount_invoice(cr, uid, move_line),
            'quantity': 1,
#            'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
 #           'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
        }

    def _prepare_invoice_line_po(self, cr, uid, group, picking, move_line, invoice_id,
                              invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line if service or asset
        @param group: True or False
        @param picking: picking object
        @param: purchase_line: purchase_line object
        @param: invoice_id: ID of the related invoice
        @param: invoice_vals: dict used to created the invoice
        @return: dict that will be used to create the invoice line
        """
        budget_obj = self.pool.get('budget.post')
        if invoice_vals['type'] in ('out_invoice', 'out_refund'):
            account_id = move_line.product_id.product_tmpl_id.\
                    property_account_income.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_income_categ.id
        else:
            #factura de proveedor
            account_id = move_line.product_id.product_tmpl_id.\
                    property_account_expense.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_expense_categ.id
        if invoice_vals['fiscal_position']:
            fp_obj = self.pool.get('account.fiscal.position')
            fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
            account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        # set UoS if it's a sale and the picking doesn't have one
#        uos_id = move_line.product_uos and move_line.product_uos.id or False
#        if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
        uos_id = move_line.product_uom.id
        budget = ''
        #pasar el budget dependiendo la cta de categ valido
        if picking.presp_ref:
            #colocar el budget q sea correcto por lo menos, no el primero que encuentra
#            if move_line.product_id.property_account_expense:
#                account_id_aux = move_line.product_id.property_account_expense
#            else:
#                account_id_aux = move_line.product_id.categ_id.property_account_expense_categ
            for budget_line in picking.presp_ref.line_ids:
                budget = budget_line.id
                continue
        return {
            'budget_id':budget,
            'categ_id':move_line.product_id.categ_id.id,
            'name': move_line.product_id.name,
            'origin': picking.purchase_id.name,
            'invoice_id': invoice_id,
            'uos_id': uos_id,
            'product_id': move_line.product_id.id,
            'account_id': account_id,
            'price_unit': move_line.price_unit,#self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
#            'discount': self._get_discount_invoice(cr, uid, move_line),
            'quantity': move_line.product_qty,
#            'invoice_line_tax_id': [(6, 0, [x.id for x in move_line.taxes_id])],
            'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice_po(cr, uid, move_line, invoice_vals['type']))],
            'account_analytic_id': move_line.account_analytic_id.id or False,
        }

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
#            if not picking.solicitant_id.user_id:
#                raise osv.except_osv(('Error'), ('El empleado no tiene usuario asignado:  '+picking.solicitant_id.complete_name))
            if group and partner.id in invoices_group:
                invoice_id = invoices_group[partner.id]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals_group = self._prepare_invoice_group(cr, uid, picking, partner, invoice, context=context)
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
            else:
                invoice_vals = self._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
                if picking.partner_id.authorisation_ids:
                    invoice_vals['auth_inv_id'] = picking.partner_id.authorisation_ids[0].id
                invoice_vals['reference'] = picking.number
                invoice_vals['date_invoice'] = picking.document_date
                invoice_vals['certificate_id'] = picking.presp_ref.id
                invoice_vals['aux_invoice']=True
                invoice_vals['new_number']=picking.number
           #     invoice_vals['picking_id'] = picking.id
                invoice_vals['reference_type'] = 'invoice_partner'
                context_aux = {}
                context_aux['inventario']='inventario'
                inv_aux = invoice_obj.onchange_certificate_id(cr, uid, ids, picking.presp_ref.id,context_aux)
                if not inv_aux['value']['account_id']:
                    raise osv.except_osv(('Error de configuración'), ('No existe cuenta por pagar para la partida del compromiso'))
                invoice_vals['account_id']=inv_aux['value']['account_id']
                invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
                picking_obj.write(cr, uid, picking.id,{'invoice_id':invoice_id})
                invoices_group[partner.id] = invoice_id
            res[picking.id] = invoice_id
            for line_budget in picking.presp_ref.line_ids:
                vals = self._prepare_invoice_line(cr, uid, group, picking, line_budget,
                                invoice_id, invoice_vals, context=context)
                if vals:
                    invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
#                    self._invoice_line_hook(cr, uid, move_line, invoice_line_id)
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
    
    def onchange_solicitant(self, cr, uid, ids, solicitant_id, context={}):
        emp_obj = self.pool.get('hr.employee')
        if solicitant_id:
            vals={}
            empleado = emp_obj.browse(cr, uid, solicitant_id)
            return {'value':{'unidad_id':empleado.department_id.id}}

    def onchange_bodega(self, cr, uid, ids, bodega_id, context={}):
        if bodega_id:
            vals={}
            obj_type = self.pool.get('stock.location')
            bodega = obj_type.browse(cr, uid, bodega_id, context)
            if bodega.type_loc=='Corriente':
                return {'value':{'type_loc':'Corriente'}}
            if bodega.type_loc=='Inversion':
                return {'value':{'type_loc':'Inversion'}}


    def onchange_documento(self, cr, uid, ids, document_id, context={}):
        if document_id:
            vals={}
            obj_type = self.pool.get('picking.doc.type')
            documento = obj_type.browse(cr, uid, document_id, context)
            if documento.generar_factura:
                vals['invoice_state'] = '2binvoiced'
            else:
                vals['invoice_state'] = 'none'
        return {'value':vals}

    def action_load_line(self, cr, uid, id, context):
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        for this in self.browse(cr, uid, id):
#            for picking in this.related_picking.id:
            picking_obj.write(cr, uid, this.id, {
                    'partner_id':this.related_picking.partner_id.id,
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

    def write(self, cr, uid, ids, vals, context=None):
        move_obj = self.pool.get('stock.move')
        if vals.has_key('date_done'):
            for this in self.browse(cr, uid, ids):
                move_ids = move_obj.search(cr, uid, [('picking_id','=',this.id)])
                if move_ids:
                    for move_id in move_ids:
                        move_obj.write(cr, uid,move_id,{
                            'date':vals['date_done'],
                        })
        return super(stockPicking, self).write(cr, uid, ids, vals, context)

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
        vals['unidad_id'] = solicitant_id.department_id.id
        #tomar la secuencia en base a la transaccion
        if ('name' not in vals) or (vals.get('name')=='/'):
            tabla_obj = self.pool.get('stock.config.sequence')
            tabla_ids = tabla_obj.search(cr, uid, [('bodega_id','=',vals['bodega_id'])],limit=1)
            if not tabla_ids:
                raise osv.except_osv(('Error de configuración'), ('No existe tabla de secuencias definida para la bodega'))
            tabla = tabla_obj.browse(cr, uid, tabla_ids[0])
            if context.has_key('type_internal_menu'):
#                if context['type_internal_menu']=='in':
#                    seq_obj_name =  tabla.in_seq.code
#                elif context['type_internal_menu']=='indev':
#                    seq_obj_name =  tabla.in_dev_seq.code
#                elif context['type_internal_menu']=='out':
#                    seq_obj_name =  tabla.out_seq.code
#                elif context['type_internal_menu']=='outdev':
#                    seq_obj_name =  tabla.out_dev_seq.code
##                else:
 #                   seq_obj_name =  tabla.internal_seq.code
                vals['type_internal_menu'] = context['type_internal_menu']
            else:
                vals['type_internal_menu'] = 'out'
                vals['type'] = 'out'
#                seq_obj_name =  tabla.out_seq.code
        vals['name'] = '/'
        return super(stockPicking, self).create(cr, uid, vals, context)

    def print_comprobante_bodega(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir la solicitud de compra
        '''        
        if not context:
            context = {}
        solicitud = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [solicitud.id], 'model': 'purchase.requisition'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchase.req',
            'model': 'purchase.requisition',
            'datas': datas,
            'nodestroy': True,                        
            }        

    def action_process(self, cr, uid, ids, context=None):
        if context is None: context = {}
        context = dict(context, active_ids=ids, active_model=self._name)
        for this in self.browse(cr, uid, ids):
            if this.type == 'out':
                continue
            for line in this.move_lines:
                if not line.subtot > 0 or line.product_qty < 0:
                    raise osv.except_osv(('Error de usuario'), ('El subtotal y la cantidad debe ser mayor a cero'))
        partial_id = self.pool.get("stock.partial.picking").create(cr, uid, {}, context=context)
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'stock.partial.picking',
            'res_id': partial_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }

    
    def draft_validate(self, cr, uid, ids, context=None):
        """ Validates picking directly from draft state.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        self.draft_force_assign(cr, uid, ids)        
        for pick in self.browse(cr, uid, ids, context=context):
            for lines in  pick.move_lines:
                if pick.type_internal_menu in ('in','indev'): #validar precios
                    if lines.price_unit <=0 or lines.total<=0:
                        raise osv.except_osv(('Error'), ('Verifique el precios y total del producto:  '+lines.product_id.name))
                else:#validar solo cantidad que haya disponible
                    if lines.product_id.standard_price<=0:
                        raise osv.except_osv(('Error'), ('Verifique el precios y total del producto:  '+lines.product_id.name))
                    if lines.product_qty > lines.product_id.qty_available:
                        if lines.product_id.default_code:
                            str_prod = lines.product_id.default_code + ' ' + lines.product_id.name
                        else:
                            str_prod = lines.product_id.name
                        raise osv.except_osv(('Error'), ('No existe cantidad suficiente de %s para realizar el egreso, tiene disponible %s y esta tratando de egresar %s') % (str_prod,str(lines.product_id.qty_available),str(lines.product_qty)))
            move_ids = [x.id for x in pick.move_lines]            
            self.pool.get('stock.move').force_assign(cr, uid, move_ids)
            wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
        return self.action_process(
            cr, uid, ids, context=context)
        
    def action_revert_done(self, cr, uid, ids, context=None):
        """ Revert picking.
        @return: True """
        period_obj = self.pool.get('account.period')
        invoice_obj = self.pool.get('account.invoice')
        product_obj = self.pool.get('product.product')
        for picking in self.browse(cr, uid, ids):
            period_ids = period_obj.search(cr, uid, [('state','=','draft'),('date_start','<=',picking.date_done),('date_stop','>=',picking.date_done)])
            if not period_ids:
                raise osv.except_osv(('Error de usuario'), 
                                     ('No existe periodo contable abierto para la fecha del movimiento'))
            if picking.invoice_id:
                #borra la factura
                invoice = invoice_obj.browse(cr, uid, picking.invoice_id.id)
                if invoice.state=='draft':
                    invoice_obj.unlink(cr, uid, [invoice.id])
                else:
                    raise osv.except_osv(('Error de usuario'), 
                                         ('No puede reversar el movimiento ya que la factura relacionada se encuentra validada, verifique que la factura este en borrador'))
            #solo si es ingreso
            if picking.type=='in':
                for line in picking.move_lines:
                    qty_anterior = line.product_id.qty_available - line.product_qty
                    if qty_anterior == 0:
    #                    precio_anterior = ((line.product_id.standard_price * line.product_id.qty_available)-(line.subtotal*line.product_qty))/1
                        precio_anterior = ((line.product_id.standard_price * line.product_id.qty_available)-(line.subtotal*line.product_qty))/1
                    else:
                        precio_anterior = ((line.product_id.standard_price * line.product_id.qty_available)-(line.subtotal*line.product_qty))/qty_anterior
    #                    precio_anterior = ((line.product_id.standard_price * line.product_id.qty_available)-(line.subtotal*line.product_qty))/qty_anterior
                    product_obj.write(cr, uid, line.product_id.id,{
                        'standard_price':precio_anterior,
                    })
        if not len(ids):
            return False
        cr.execute('select id from stock_move where picking_id IN %s and state=%s', (tuple(ids), 'done'))
	line_ids = map(lambda x: x[0], cr.fetchall())
        self.write(cr, uid, ids, {'state': 'draft',
                                  'invoice_state':'2binvoiced'})
        self.pool.get('stock.move').write(cr, uid, line_ids, { 'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for inv_id in ids:
            # Deleting the existing instance of workflow for SO
            wf_service.trg_delete(uid, 'stock.picking', inv_id, cr)
            wf_service.trg_create(uid, 'stock.picking', inv_id, cr)
        for (id,name) in self.name_get(cr, uid, ids):
            message = _("The stock picking '%s' has been set in draft state.") %(name,)
            self.log(cr, uid, id, message)
        return True        
        

    def confirm_aprobe(self, cr, uid, ids, context=None):
        """ Confirms picking.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'assigned'})
        return True

    def _get_bodega(self, cr, uid, ids, context=None):
        bodega_obj = self.pool.get('stock.location')
        bodega_ids = bodega_obj.search(cr, uid, [])
        if bodega_ids:
            return bodega_ids[0]
        else:
            raise osv.except_osv(('Error de configuración'), ('No tiene bodegas definidas'))

    def _get_user(self, cr, uid, ids, context=None):
        return uid

    def _get_department(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        return user.context_department_id.id


    def _amount_all_total_inv(self, cr, uid, ids, field_name, arg, context=None):
        '''    Calcula el valor por unidad y los impuestos
        '''
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = 0.0
            val = 0
            for line in picking.move_lines:
                val += line.total
            res[picking.id]=val
        return res

    def _amount_all_subtotal_inv(self, cr, uid, ids, field_name, arg, context=None):
        '''    Calcula el valor subtotal
        '''
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = 0.0
            val = 0
            for line in picking.move_lines:
                if line.imp_iva>0:
                    val += line.subtot
            res[picking.id]=val
        return res

    def _amount_all_subtotal_inv0(self, cr, uid, ids, field_name, arg, context=None):
        '''    Calcula el valor subtotal iva 0
        '''
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = 0.0
            val = 0
            for line in picking.move_lines:
                if line.imp_iva==0:
                    val += line.subtot
            res[picking.id]=val
        return res

    def _amount_all_taxes_inv(self, cr, uid, ids, field_name, arg, context=None):
        '''    Calcula el valor subtotal
        '''
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = 0.0
            val = 0
            for line in picking.move_lines:
                aux = line.imp_iva + line.imp_ice + line.imp_verde
                val += aux
            res[picking.id]=val
        return res

    def _get_account_inv(self, cr, uid, ids, name, args, context=None):
        res = {}
        aux_categ = []
        move_obj = self.pool.get('stock.move')
        categ_obj = self.pool.get('product.category')
        aux_detalle = ''
        for picking in self.browse(cr, uid, ids):
            for line in picking.move_lines:
                if not line.product_id.categ_id.id in aux_categ:
                    aux_categ.append(line.product_id.categ_id.id)
            for categ_id in aux_categ:
                categoria = categ_obj.browse(cr, uid, categ_id)
                line_ids = move_obj.search(cr, uid, [('categ_id','=',categ_id),('picking_id','=',picking.id)])
                aux_value = 0
                for line_id in line_ids:
                    line = move_obj.browse(cr, uid, line_id)
                    aux_value += line.total
                if categoria.code:
                    aux_detalle += categoria.code + ' ' + categoria.name + ' = ' + str(aux_value) + '\r\n'
                else:
                    aux_detalle += categoria.name + ' = ' + str(aux_value) + '\r\n'
            res[picking.id] = aux_detalle
        return res

    _columns = dict(
        iva = fields.integer('Iva Aplicado'),
        categ_aux = fields.function(_get_account_inv, store=True, string='Cuentas',type='text'),
        objeto_id = fields.many2one('picking.objeto','Objeto Receptor'),
        req_id = fields.many2one('stock.requisition','Requerimiento'),
        subtotal_inv = fields.function(_amount_all_subtotal_inv, digits_compute= dp.get_precision('Account'), 
                                           string='SubTotal',store=True,
                                           ),
        subtotal_inv_0 = fields.function(_amount_all_subtotal_inv0, digits_compute= dp.get_precision('Account'), 
                                           string='SubTotal IVA 0',store=True,
                                           ),
        total_taxes = fields.function(_amount_all_taxes_inv, digits_compute= dp.get_precision('Account'), 
                                           string='Impuestos',store=True,
                                           ),
        total_inventario = fields.function(_amount_all_total_inv, digits_compute= dp.get_precision('Account'), 
                                           string='Total',store=True,
                                           help="Valor Total"),
        type_loc = fields.related('bodega_id','type_loc', type='char', 
                                  string='Tipo Ubicacion', store=True),
        related_picking = fields.many2one('stock.picking','Mov. Relacionado'),
        type_internal_menu = fields.char('Tipo Interno',size=10),
        is_oc = fields.boolean('Viene de OC'),
        state = fields.selection([
                ('draft', 'Borrador'),
                ('auto', 'Waiting Another Operation'),
                ('confirmed', 'Solicitado'),
                ('assigned', 'Aprobado'),
                ('done', 'Finalizado'),
                ('cancel', 'Cancelado'),
                ], 'State', readonly=True, select=True,
                                 help="* Draft: not confirmed yet and will not be scheduled until confirmed\n"\
                                     "* Confirmed: still waiting for the availability of products\n"\
                                     "* Available: products reserved, simply waiting for confirmation.\n"\
                                     "* Waiting: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"\
                                     "* Done: has been processed, can't be modified or cancelled anymore\n"\
                                     "* Cancelled: has been cancelled, can't be confirmed anymore"),
        document_id = fields.many2one('picking.doc.type','Tipo Documento'),
        number = fields.char('Num. documento',size=37),
        document_date = fields.date('Fecha documento'),
        invoice_id = fields.many2one('account.invoice','Factura Relacionada'),
        #entrega_id = fields.many2one('hr.employee','Entrega'),
        solicitant_id = fields.many2one('hr.employee','Solicitado por'),
        solicitant_user_id = fields.many2one('res.users','Creado por'),
        receptor_type = fields.boolean('Recibe empleado?', help="Activado si la persona que recibe es un empleado. Desactivado si es otra persona"),
        receptor_id = fields.many2one('hr.employee','Recibe'),
        receptor = fields.char('Recibe',size=256),
        receptor_job = fields.char('Cargo (Recibe)', size=30),
        receptor_ced = fields.char('Cedula o id (recibe)', size=13),
        create_user_id = fields.many2one('res.users','Creado por',readonly=True,required=True),
        ie_type = fields.many2one('ie.type','Tipo de transaccion'),
        presp_ref = fields.many2one('budget.certificate','Pres. Referencial',help="Permite seleccionar los presupuestos referenciales certificados y que no esten siendo utilizados en otro proceso, al anular una solicitud de compra este presupuesto se libera y puede ser utilizado en un nuevo proceso"),
        
        #unidad_id = fields.many2one('hr.department','Unidad Req.'),
        unidad_id = fields.related('solicitant_id', 'department_id', type="many2one", relation='hr.department', string="Unidad Req.", store=True),
        objeto_id_id = fields.many2one('account.asset.asset','Vehiculo/Maquinaria'),
        project_type = fields.selection([('Obra','Obra'),('Programa','Programa')],'Obra/Programa'),
        project_id = fields.many2one('account.analytic.account','Proyecto/Programa'),
        resp_obra_id = fields.many2one('hr.employee','Resp. de proyecto'),
        #fields.related('presp_ref', 'project_id', type='many2one', relation='project.project',
                                    #string='Proyecto', store=True),
        bodega_id = fields.many2one('stock.location','Bodega',required=True),
        bodega_dest_id = fields.many2one('stock.location','Bodega destino'),
#        responsable_id = fields.related('bodega_id','responsable_id', type="many2one", relation='res.users', string='Responsable'),
        responsable_id = fields.many2one('hr.employee','Autorizado por:'),
        partner_id = fields.many2one('res.partner','Proveedor'),
        date_done = fields.date('Fecha de transaccion'),
        tiene_contrato = fields.boolean('Tiene contrato?',help='Active la casilla para relacionar la transaccion a un contrato'),
        destino = fields.selection([('proyecto', 'Proyecto/Programa'),
                                    ('objeto', 'Vehiculo/Maquinaria'),
                                    ], 'Objeto Receptor'),
        invoice_state = fields.selection([('2binvoiced', 'Generar Factura'),
                                          ('none', 'No aplicable'),
                                          ('invoiced','Facturado'),
                                          ], 'Control factura'),
        )


    def _get_autoriza(self, cr, uid, ids,context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        if user.context_department_id:
            return user.context_department_id.coordinador_id.id

    def _check_date_picking(self, cr, uid, ids, context=None):
        return True
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            period_ids = period_obj.search(cr, uid, [('state','=','draft'),('date_start','<=',this.date_done),('date_stop','>=',this.date_done)])
            if not period_ids:
                return False
        return True

    def unlink(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        if context is None:
            context = {}
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.state in ['done','cancel']:
                raise osv.except_osv(_('Error'), _('You cannot remove the picking which is in %s state !')%(pick.state,))
            elif pick.name!='/':
                raise osv.except_osv(_('Error'), _('No puede eliminar movimientos !'))
            else:
                ids2 = [move.id for move in pick.move_lines]
                ctx = context.copy()
                ctx.update({'call_unlink':True})
                if pick.state != 'draft':
                    #Cancelling the move in order to affect Virtual stock of product
                    move_obj.action_cancel(cr, uid, ids2, ctx)
                #Removing the move
                move_obj.unlink(cr, uid, ids2, ctx)

        return super(stock_picking, self).unlink(cr, uid, ids, context=context)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Reference must be unique!'),
        ]

    _constraints = [
        (_check_date_picking,'La fecha de documento no permite regresar el periodo contable esta cerrado',[]),
        ] 

    _defaults = dict(
        #entrega_id = lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id,
        #esta mal, deberia buscar el empleado, no el usuario
#        unidad_id = _get_department,
        solicitant_user_id = _get_user,
        create_user_id = _get_user,
        #bodega_id = _get_bodega,
        responsable_id = _get_autoriza,
    #    date_done = time.strftime('%Y-%m-%d'),
        destino = 'proyecto',
        receptor_type = True,
        project_type = 'Programa',
        )

stockPicking()

class ie_type(osv.Model):
    _name = 'ie.type'

    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv('Error', 'No pueden eliminar tipos de transacciones')
        return False    

    _columns = dict(
        name = fields.char('Concepto',size=32,required=True),
        is_compra = fields.boolean('Es compra'),
        #movimiento = fields.selection([('out', 'Egresos'), ('in', 'Ingresos'), ('internal', 'Transacciones')],'Movimiento',required=True),
#        seq_id = fields.many2one('ir.sequence','Secuencia',required=True),
        )
ie_type()

class stock_config_sequence(osv.Model):
    _name = 'stock.config.sequence'

    _columns = dict(
        bodega_id = fields.many2one('stock.location','Bodega',required=True),
        in_seq = fields.many2one('ir.sequence','Secuencia Ingresos',required=True),
        in_dev_seq = fields.many2one('ir.sequence','Secuencia Ingresos Devolución',required=True),
        out_seq = fields.many2one('ir.sequence','Secuencia Egresos',required=True),
        out_dev_seq = fields.many2one('ir.sequence','Secuencia Egresos Devolución',required=True),
        internal_seq = fields.many2one('ir.sequence','Secuencia Transferencias Internas',
                                       required=True),
        )
stock_config_sequence()


class stockDetalle(osv.Model):
    _name = 'stock.detalle'
    _columns = dict(
        st_id = fields.many2one('stock.account.move','Egresos'),
        categ_id = fields.many2one('product.category','Categoria'),
        total = fields.float('Total'),
    )
stockDetalle()

class StockAccountMove(osv.Model):
    _name = 'stock.account.move'

    def _get_move_lines(self, cr, uid, ids, fields, args, context):
        res = {}
        for obj in self.browse(cr, uid, ids):
            lines = []
            res[obj.id] = []
            if obj.move_id:
                lines += [line.id for line in obj.move_id.line_id]
            res[obj.id] = lines
        return res

    _columns = {
        'tipo':fields.selection([('corriente','Corriente'),('inversion','Inversion'),('Todos','Todos')],'Tipo'),
        'period_id': fields.many2one('account.period', string='Periodo', required=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear', string='Ejercicio Fiscal',
                                         required=True),
        'name': fields.char('Núm de Documento', size=32, required=True, readonly=True),
        'all_locations': fields.boolean('Todas las bodegas'),
        'location_id': fields.many2one('stock.location', string='Bodega', domain=[('usage','=','internal')]),
        'move_id': fields.many2one('account.move', string='Diario de Egreso'),
        'acc_line_ids': fields.function(_get_move_lines, method=True, string="Detalle Contable",
                                        type="one2many", relation="account.move.line"),        
        'stock_line_ids': fields.many2many('stock.move', 'stock_acc_move_rel', 'acc_id', 'move_id', string='Detalle de Egresos'),
        'state': fields.selection([('draft','Borrador'),
                                   ('done', 'Registrado'),
                                   ('contabilizado', 'Contabilizado')], string='Estado', required=True),
        'detalle_ids': fields.one2many('stock.detalle','st_id','Detalle'),
        }

    def _get_fy(self, cr, uid, context=None):
        return self.pool.get('account.fiscalyear').find(cr, uid)

    def _get_period(self, cr, uid, context=None):
        return self.pool.get('account.period').find(cr, uid)[0]

    _defaults = {
        'tipo':'Inversion',
        'state': 'draft',
        'all_locations': True,
        'fiscalyear_id': _get_fy,
        'period_id': _get_period,
        'name': '**'
        }

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        
    def action_read_moves(self, cr, uid, ids, context=None):
        st_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking') 
        categ_obj = self.pool.get('product.category')
        detalle_obj = self.pool.get('stock.detalle')
        for obj in self.browse(cr, uid, ids, context):
            detalle_ant_ids = detalle_obj.search(cr, uid, [('st_id','=',obj.id)])
            if detalle_ant_ids:
                detalle_obj.unlink(cr, uid, detalle_ant_ids)
            picking_ids = picking_obj.search(cr, uid, [('date_done','>=',obj.period_id.date_start),('date_done','<=',obj.period_id.date_stop),
                      ('type','=','out'),('state','=','done')])
            if obj.tipo=='Todos':
                categ_ids = categ_obj.search(cr, uid, [])
            else:
                categ_ids = categ_obj.search(cr, uid, [('budget','=',obj.tipo)])
            for categ_id in categ_ids:
                aux_total_categ = 0
                st_moves_categ = st_obj.search(cr, uid, [('picking_id','in',picking_ids),('categ_id','=',categ_id)])
                if st_moves_categ:
                    for st_move_id in st_moves_categ:
                        movimiento = st_obj.browse(cr, uid, st_move_id)
                        aux_total_categ += movimiento.total
                    detalle_obj.create(cr, uid, {
                        'st_id':obj.id,
                        'categ_id':categ_id,
                        'total':aux_total_categ,
                    })
            res = st_obj.search(cr, uid, [('picking_id','in',picking_ids),('categ_id','in',categ_ids)])
            values = [(6,0,res)]
            self.write(cr, uid, obj.id, {'stock_line_ids': values})
        return True

    def action_create_move(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        category_obj = self.pool.get('product.category')
        st_move_obj = self.pool.get('stock.move')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        categ_ids = []
        for obj in self.browse(cr, uid, ids, context):
            journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
            if not journal_ids:
                raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
            period_ids = period_obj.find(cr, uid, obj.period_id.date_start)
            if not period_ids:
                raise osv.except_osv('Error de configuracion', 'No existe periodo contable definido para la fecha de garantia')
            desc_aux = 'REGISTRO DE INVENTARIOS DEL MES DE ' + obj.period_id.name 
            move_id = move_obj.create(cr, uid, {
                'journal_id':journal_ids[0],
                'period_id':period_ids[0],
                'date':obj.period_id.date_stop,
                'partner_id':1,
                'type2_id':'Inventario',
                'ref':desc_aux,
                'narration':desc_aux,
            })
            aux_debit = 0
            for line in obj.detalle_ids:
                aux_debit += line.total
                if not line.categ_id.property_account_income_categ.id:
                    raise osv.except_osv(('Error de configuracion'), 'No existe cuenta de gasto inventario para la categoria %s'%(line.categ_id.name))
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'partner_id':1,
                    'name':'Inv',
                    'credit':line.total,
                    'account_id':line.categ_id.property_account_income_categ.id,
                })
                if not line.categ_id.property_account_expense_categ.id:
                    raise osv.except_osv(('Error de configuracion'), 'No existe cuenta de gasto para la categoria %s'%(line.categ_id.name))
                aux_categ_gasto = line.categ_id.property_account_expense_categ.id
                move_line_obj.create(cr, uid, {
                    'move_id':move_id,
                    'partner_id':1,
                    'name':'Gasto',
                    'debit':line.total,
                    'account_id':aux_categ_gasto,
                })
        return True

    def action_create_moveANTERIOR(self, cr, uid, ids, context=None):
        """
        Genera asiento contable de egreso con afectacion a costos
        TODO: Agrupacion de cuentas, considerar todas las lineas
        """
        move_obj = self.pool.get('account.move')
        line_obj = self.pool.get('account.move.line')
        ctas_obj = self.pool.get('ctas.categ')
        line_data = {}
        for obj in self.browse(cr, uid, ids, context):
            debito = 0
            credito = 0
            monto_complemento = 0
            period_id = obj.period_id.id
            move_lines = []
            complementarias = []
            for line in obj.stock_line_ids:
                if not line.product_id.cost_method == 'average':
                    continue
                picking = line.picking_id
                credito = line.product_id.standard_price * line.product_qty
                debito += credito
                journal_id = line.product_id.categ_id.property_stock_journal.id
                if not journal_id:
                    raise osv.except_osv('Error', 'No ha configurado un diario de inventario.')
                analytic_journal_id = line.product_id.categ_id.property_stock_journal.analytic_journal_id.id
                if not analytic_journal_id:
                    raise osv.except_osv('Error', 'No ha configurado un diario de costos.')
                type_b = picking.project_type.lower()
                categ_id = line.product_id.categ_id.id
                #cta de linea
                res = ctas_obj.search(cr, uid, [('categ_id','=',categ_id)], limit=1)
                ctas = ctas_obj.browse(cr, uid, res[0])
                account = ctas.account_ex_normal
                if picking.project_type.lower() == 'corriente':
                    account = ctas.account_ex_normal
                else:
                    if picking.project_type.lower() == 'obra':
                        account = ctas.account_ex_project
                    else:
                        account = ctas.account_ex_program
                #Ctas complemento
                if account.in_stock:
                    complementarias.append(ctas.account_comp_id)
                    monto_complemento += credito                    
                account_expense_id = ctas.account_expense.id
                if not line_data.get(account.id):
                    line_data[account.id] = {
                        'name': obj.all_locations and 'TODAS LAS BODEGAS' or location_id.name,
                        'journal_id': journal_id,
                        'period_id': period_id,
                        'account_id': account.id,
                        'date': picking.date_done,
                        'debit': 0.00,
                        'credit': 0.00,
                        }
                    if picking.project_id:
                        line_data[account.id]['analytic_lines'] = [(0,0,{
                            'name': 'CONSUMO %s' % obj.period_id.name,
                            'date': obj.period_id.date_stop,
                            'account_id': picking.project_id.id,
                            'unit_amount': line.product_qty,
                            'amount': -credito,
                            'product_id': line.product_id.id,
                            'general_account_id': account.id,
                            'journal_id': analytic_journal_id,
                            'ref': '/' 
                            })]
                line_data[account.id]['credit'] += credito
            for k,v in line_data.items():
                move_lines.append((0,0,v))
            line_ex = {'name': 'CONSUMO %s' % obj.period_id.name,
                       'journal_id': journal_id,
                       'period_id': period_id,
                       'date': obj.period_id.date_stop,
                       'account_id': account_expense_id,
                       'credit': 0.00,
                       'debit': debito+monto_complemento}
            move_lines.append((0,0,line_ex))
            complementarias = list(set(complementarias))
            for com in complementarias:
                line_com = {'name': 'COMPLEMENTO',
                            'journal_id': journal_id,
                            'date': obj.period_id.date_stop,
                            'account_id': com.id,
                            'credit': monto_complemento}
                move_lines.append((0,0,line_com))
            move_data = {'name': '/',
                         'ref': 'CONSUMO %s' % obj.period_id.name,
                         'journal_id': journal_id,
                         'date': picking.date_done,
                         'line_id': move_lines}
            move_id = move_obj.create(cr, uid, move_data)
        return True
