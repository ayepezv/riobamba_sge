# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################
import time
from osv import osv, fields

class objetoReceptorLine(osv.TransientModel):
    _name = 'objeto.receptor.line'
    _columns = dict(
        ob_id = fields.many2one('objeto.receptor.rp','Objeto'),
        date = fields.date('Fecha'),
        product_id = fields.many2one('product.product','Producto'),
        documento = fields.char('Documento',size=20),
        solicitant_id = fields.many2one('hr.employee','Solicitado por'),
        qty = fields.float('Cantidad'),
        pu = fields.float('Precio Unitario'),
        total = fields.float('Total'),
    )
objetoReceptorLine()

class objetoReceptorRp(osv.TransientModel):
    _name = 'objeto.receptor.rp'
    _columns = dict(
        receptor_id = fields.many2one('picking.objeto','Objeto receptor'),
        date_start = fields.date('Fecha Desde'),
        date_end = fields.date('Fecha hasta'),
        line_ids = fields.one2many('objeto.receptor.line','ob_id','Detalle'),
    )
    
    def loadReceptorMove(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('objeto.receptor.line')
        move_obj = self.pool.get('stock.move')
        for this in self.browse(cr, uid, ids):
            antes_ids = line_obj.search(cr, uid, [('ob_id','=',this.id)])
            if antes_ids:
                line_obj.unlink(cr, uid, antes_ids)
            move_ids = move_obj.search(cr, uid, [('objeto_id','=',this.receptor_id.id),('date','>=',this.date_start),('date','<=',this.date_end),
                                                 ('picking_id.state','=','done')])
            if move_ids:
                for move_id in move_ids:
                    move = move_obj.browse(cr, uid, move_id)
                    if move.picking_id.solicitant_id:
                        line_obj.create(cr, uid, {
                            'ob_id':this.id,
                            'date':move.date,
                            'product_id':move.product_id.id,
                            'documento':move.picking_id.name,
                            'solicitant_id':move.picking_id.solicitant_id.id,
                            'qty':move.product_qty,
                            'pu':move.price_unit_inc_imp,
                            'total':move.total,
                        })
                    else:
                        line_obj.create(cr, uid, {
                            'ob_id':this.id,
                            'date':move.date,
                            'product_id':move.product_id.id,
                            'documento':move.picking_id.name,
                            'qty':move.product_qty,
                            'pu':move.price_unit_inc_imp,
                            'total':move.total,
                        })
        return True

    def printPickingReceptor(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'objeto.receptor.rp'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'objeto_receptor',
            'model': 'objeto.receptor.rp',
            'datas': datas,
            'nodestroy': True,                        
            }

objetoReceptorRp()

class saldoInventarioLineLine(osv.TransientModel):
    _name = 'saldo.inventario.line.line'
    _columns = dict(
        name = fields.many2one('product.product','Producto'),
        saldo = fields.float('Saldo'),
        l_id = fields.many2one('saldo.inventario.line','Detalle'),
    )
saldoInventarioLineLine()

class saldoInventarioLine(osv.TransientModel):
    _name = 'saldo.inventario.line'
    _columns = dict(
        line_ids = fields.one2many('saldo.inventario.line.line','l_id','Detalle'),
        sc_id = fields.many2one('saldo.inventario','Inventario Corriente'),
        si_id = fields.many2one('saldo.inventario','Inventario Inversion'),
        category_id = fields.many2one('product.category','Categoria'),
        total = fields.float('TOTAL'),
    )
saldoInventarioLine()

class saldoInventario(osv.TransientModel):
    _name = 'saldo.inventario'
    _columns = dict(
        date = fields.date('Fecha'),
        linec_ids = fields.one2many('saldo.inventario.line','sc_id','Detalle Corriente'),
        linei_ids = fields.one2many('saldo.inventario.line','si_id','Detalle Inversion'),
    )

    def printSaldoInventario(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'saldo.inventario'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'saldo_inventario',
            'model': 'saldo.inventario',
            'datas': datas,
            'nodestroy': True,                        
            }

    def printSaldoInventarioDetalle(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'saldo.inventario'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'saldo_inventario_detalle',
            'model': 'saldo.inventario',
            'datas': datas,
            'nodestroy': True,                        
            }
    
    def computeSaldoInventario(self, cr, uid, ids, context=None):
        categ_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        line_obj = self.pool.get('saldo.inventario.line')
        line_line_obj = self.pool.get('saldo.inventario.line.line')
        categ_cids = categ_obj.search(cr, uid, [('budget','=','corriente')])
        categ_iids = categ_obj.search(cr, uid, [('budget','=','inversion')])
        move_obj = self.pool.get('stock.move')
        lineas_corriente = []
        for this in self.browse(cr, uid, ids):
            id_aux = this.id 
            line_ant_sc = line_obj.search(cr, uid, [('sc_id','=',id_aux)])
            if line_ant_sc:
                line_obj.unlink(cr, uid, line_ant_sc)
            line_ant_ic = line_obj.search(cr, uid, [('si_id','=',id_aux)])
            if line_ant_ic:
                line_obj.unlink(cr, uid, line_ant_ic)
            for categ_cid in categ_cids:
                #product_cids = product_obj.search(cr, uid, [('categ_id','=',categ_cid),('qty_available','>',0)])
                product_cids = product_obj.search(cr, uid, [('categ_id','=',categ_cid),('type','=','product')])
                if product_cids:
                    aux_valor = 0
                    l_id = line_obj.create(cr, uid, {
                        'sc_id':id_aux,
                        'category_id':categ_cid,
                        'total':aux_valor,
                    })
                    for product_cid in product_cids:
                        saldo = 0
                        producto = product_obj.browse(cr, uid, product_cid)
                        move_ids = move_obj.search(cr, uid, [('product_id','=',product_cid),('date','<=',this.date),('state','=','done')])
                        if move_ids:
                            ingresos = egresos = 0
                            for move_id in move_ids:
                                move = move_obj.browse(cr, uid, move_id)
                                if move.type=='out':
                                    egresos += move.product_qty
                                else:
                                    ingresos += move.product_qty
                            saldo = ingresos - egresos
                            if saldo>0:
                                aux_valor_producto = saldo * producto.standard_price
                                aux_valor += aux_valor_producto
                                line_line_id = line_line_obj.create(cr, uid, {
                                    'name':producto.id,
                                    'saldo':saldo,
                                    'l_id':l_id,
                                })
                    if aux_valor>0:
                        line_obj.write(cr, uid, l_id,{'total':aux_valor})
                    else:
                        line_obj.unlink(cr, uid, l_id)
            aux_valor = 0
            for categ_iid in categ_iids:
                product_iids = product_obj.search(cr, uid, [('categ_id','=',categ_iid),('type','=','product')])
                if product_iids:
                    aux_valor = 0
                    l_id = line_obj.create(cr, uid, {
                        'si_id':id_aux,
                        'category_id':categ_iid,
                        'total':aux_valor,
                    })
                    for product_iid in product_iids:
                        saldo = 0
                        producto = product_obj.browse(cr, uid, product_iid)
                        move_ids = move_obj.search(cr, uid, [('product_id','=',product_iid),('date','<=',this.date),('state','=','done')])
                        if move_ids:
                            ingresos = egresos = 0
                            for move_id in move_ids:
                                move = move_obj.browse(cr, uid, move_id)
                                if move.type=='out':
                                    egresos += move.product_qty
                                else:
                                    ingresos += move.product_qty
                            saldo = ingresos - egresos
                            if saldo>0:
                                aux_valor_producto = saldo * producto.standard_price
                                aux_valor += aux_valor_producto
                                line_line_id = line_line_obj.create(cr, uid, {
                                    'name':producto.id,
                                    'saldo':saldo,
                                    'l_id':l_id,
                                })
                    if aux_valor>0:
                        line_obj.write(cr, uid, l_id,{'total':aux_valor})
                    else:
                        line_obj.unlink(cr, uid, l_id)
        return True
        
    _defaults = dict(
        date = time.strftime('%Y-%m-%d'),
    )

saldoInventario

class productTipo(osv.Model):
    _inherit = 'product.product'
    _columns = dict(
        tipo = fields.related('categ_id','budget',type='char',size=32,store=True),
    )
productTipo()

