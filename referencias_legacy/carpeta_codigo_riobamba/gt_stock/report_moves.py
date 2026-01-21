# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

import time
from osv import fields, osv

##ingresos detalle movimiento

class ingresoDetalleMoveLineLine(osv.TransientModel):
    _name = 'ingreso.detalle.move.line.line'
    _columns = dict(
        numero = fields.char('Numero',size=15),
        move_id = fields.many2one('stock.picking','Ingreso'),
        move_id2 = fields.many2one('stock.move','Move'),
        l_id = fields.many2one('ingreso.detalle.move.line','Categoria'),
        product_id = fields.many2one('product.product','Producto'),
        cantidad = fields.float('Cantidad'),
        subtotal = fields.float('Subtotal'),
    )
ingresoDetalleMoveLineLine()

class ingresoDetalleMoveLine(osv.TransientModel):
    _name = 'ingreso.detalle.move.line'
    _columns = dict(
        line_ids = fields.one2many('ingreso.detalle.move.line.line','l_id','Detalle Items'),
        kardex_id = fields.many2one('ingreso.detalle.move','Ingreso Categoria'),
        categ_id = fields.many2one('product.category','Categoria/Familia'),
        cantidad = fields.float('Cantidad'),
        subtotal = fields.float('Subtotal'),
    )
ingresoDetalleMoveLine()

class ingresoDetalleMove(osv.TransientModel):
    _name = 'ingreso.detalle.move'
    _columns = dict(
        line_ids = fields.one2many('ingreso.detalle.move.line','kardex_id','Detalle'),
        date_start = fields.date('Fecha desde'),
        date_end = fields.date('Fecha Hasta'),
        category_id = fields.many2one('product.category','Categoria'),
    )

    def print_ingreso_categm(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.ingreso.detalle.move'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'ingreso.detalle.move',
            'model': 'ingreso.detalle.move',
            'datas': datas,
            'nodestroy': True,                        
            }

    def create_ingreso_categoriam(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        categ_obj = self.pool.get('product.category')
        line_obj = self.pool.get('ingreso.detalle.move.line')
        line_line_obj = self.pool.get('ingreso.detalle.move.line.line')
        product_obj = self.pool.get('product.product')
        categ_ids = []
        for this in self.browse(cr, uid, ids):
            line_ids_antes = line_obj.search(cr, uid, [('kardex_id','=',this.id)])
            line_obj.unlink(cr, uid, line_ids_antes)
            if this.category_id:
                move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),('product_id.categ_id','=',this.category_id.id),
                                                     ('date','<=',this.date_end),('state','=','done'),('type','=','in')],order='date')
            else:
                move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                     ('date','<=',this.date_end),('state','=','done'),('type','=','in')],order='date')
            if move_ids:
                for move_id in move_ids:
                    move_aux = move_obj.browse(cr, uid, move_id)
                    if not move_aux.categ_id.id in categ_ids:
                        categ_ids.append(move_aux.categ_id.id)
                for categ_id in categ_ids:
                    move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                         ('date','<=',this.date_end),('state','=','done'),('type','=','in'),
                                                         ('categ_id','=',categ_id)],order='date')
                    #aqui creo el diccionario producto total
                    dict_p = {}
                    cantidad = subtotal = 0
                    if move_ids:
                        l_id = line_obj.create(cr, uid, {
                            'kardex_id':this.id,
                            'categ_id':categ_id,
                            'cantidad':cantidad,
                            'subtotal':subtotal,
                        })
                        for move_id in move_ids:
                            move = move_obj.browse(cr, uid, move_id)
                            subtotal += move.total
                            cantidad += move.product_qty
                            line_line_obj.create(cr, uid, {
                                'l_id':l_id,
                                'product_id':move.product_id.id,
                                'move_id':move.picking_id.id,
                                'numero':move.picking_id.name,
                                'cantidad':move.product_qty,
                                'subtotal':move.total,
                                'move_id2':move.id,
                            })    
                        line_obj.write(cr, uid, l_id,{'subtotal':subtotal,'cantidad':cantidad})

ingresoDetalleMove()

##egresos por departamento
class egresoDireccionLineLine(osv.TransientModel):
    _name = 'egreso.direccion.line.line'
    _columns = dict(
        line_id = fields.many2one('egreso.direccion.line','Detalle',ondelete='cascade'),
        categ_id = fields.many2one('product.category','Categoria/Familia'),
        cantidad = fields.float('Cantidad'),
        subtotal = fields.float('Subtotal'),
    )
egresoDireccionLineLine()
class egresoDireccionLine(osv.TransientModel):
    _name = 'egreso.direccion.line'
    _columns = dict(
        kardex_id = fields.many2one('egreso.direccion','Ingreso Direccion'),
        line_ids = fields.one2many('egreso.direccion.line.line','line_id','Detalle Categoria'),
        department_id = fields.many2one('hr.department','Departamento'),
        total = fields.float('Total'),
    )
egresoDireccionLine()
class egresoDireccion(osv.TransientModel):
    _name = 'egreso.direccion'
    _columns = dict(
        line_ids = fields.one2many('egreso.direccion.line','kardex_id','Detalle'),
        date_start = fields.date('Fecha desde'),
        date_end = fields.date('Fecha Hasta'),
    )
    def print_egreso_direccion(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.egreso.direccion'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'egreso.direccion',
            'model': 'egreso.direccion',
            'datas': datas,
            'nodestroy': True,                        
            }

    def create_egreso_direccion(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        categ_obj = self.pool.get('product.category')
        line_obj = self.pool.get('egreso.direccion.line')
        line_line_obj = self.pool.get('egreso.direccion.line.line')
        department_ids = []
        for this in self.browse(cr, uid, ids):
            line_ids_antes = line_obj.search(cr, uid, [('kardex_id','=',this.id)])
            line_obj.unlink(cr, uid, line_ids_antes)
            move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                 ('date','<=',this.date_end),('state','=','done'),('type','=','out')],order='date')
            if move_ids:
                for move_id in move_ids:
                    move_aux = move_obj.browse(cr, uid, move_id)
                    if not move_aux.department_id.id in department_ids:
                        department_ids.append(move_aux.department_id.id)
                for department_id in department_ids:
                    categ_ids = []
                    line_id = line_obj.create(cr, uid, {
                                'kardex_id':this.id,
                                'department_id':department_id,
                    })
                    move_direccion_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),('department_id','=',department_id),
                                                 ('date','<=',this.date_end),('state','=','done'),('type','=','out')],order='date')
                    for move_2 in move_direccion_ids:
                        move_aux1 = move_obj.browse(cr, uid, move_2)
                        if not move_aux1.categ_id.id in categ_ids:
                            categ_ids.append(move_aux1.categ_id.id)
                    total_direccion = 0 
                    for categ_id in categ_ids:
                        move_categ_direccion_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                             ('date','<=',this.date_end),('state','=','done'),('type','=','out'),
                                                             ('categ_id','=',categ_id),('department_id','=',department_id)],order='date')
                        cantidad = subtotal = 0
                        for move_direccion_categ_id in move_categ_direccion_ids:
                            move_detalle = move_obj.browse(cr, uid, move_direccion_categ_id)
                            cantidad += move_detalle.product_qty
                            subtotal += move_detalle.total
                        line_line_id = line_line_obj.create(cr, uid, {
                            'line_id':line_id,
                            'categ_id':categ_id,
                            'cantidad':cantidad,
                            'subtotal':subtotal,
                        })
                        total_direccion += subtotal
                    line_obj.write(cr, uid, line_id,{'total':total_direccion})
egresoDireccion()


##ingreso por direccion
class ingresoDireccionLineLine(osv.TransientModel):
    _name = 'ingreso.direccion.line.line'
    _columns = dict(
        line_id = fields.many2one('ingreso.direccion.line','Detalle',ondelete='cascade'),
        categ_id = fields.many2one('product.category','Categoria/Familia'),
        cantidad = fields.float('Cantidad'),
        subtotal = fields.float('Subtotal'),
    )
ingresoDireccionLineLine()
class ingresoDireccionLine(osv.TransientModel):
    _name = 'ingreso.direccion.line'
    _columns = dict(
        kardex_id = fields.many2one('ingreso.direccion','Ingreso Direccion'),
        line_ids = fields.one2many('ingreso.direccion.line.line','line_id','Detalle Categoria'),
        direccion_id = fields.many2one('hr.department','Direccion'),
        total = fields.float('Total'),
    )
ingresoDireccionLine()
class ingresoDireccion(osv.TransientModel):
    _name = 'ingreso.direccion'
    _columns = dict(
        line_ids = fields.one2many('ingreso.direccion.line','kardex_id','Detalle'),
        date_start = fields.date('Fecha desde'),
        date_end = fields.date('Fecha Hasta'),
    )
    def print_ingreso_direccion(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.ingreso.direccion'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'ingreso.direccion',
            'model': 'ingreso.direccion',
            'datas': datas,
            'nodestroy': True,                        
            }

    def create_ingreso_direccion_(self, cr, uid, ids, context=None):
        #de prueba
        move_obj = self.pool.get('stock.move')
        move_ids = move_obj.search(cr, uid, [])
        for this in self.browse(cr, uid, ids):
            for move_id in move_ids:
                move = move_obj.browse(cr, uid, move_id)
                if move.department_id.direccion_id:
                    move_obj.write(cr, uid, move_id,{
                        'direccion_id':move.department_id.direccion_id.id,
                    })
            #metodo real
        return True
            

    def create_ingreso_direccion(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        categ_obj = self.pool.get('product.category')
        line_obj = self.pool.get('ingreso.direccion.line')
        line_line_obj = self.pool.get('ingreso.direccion.line.line')
        direccion_ids = []
        for this in self.browse(cr, uid, ids):
            line_ids_antes = line_obj.search(cr, uid, [('kardex_id','=',this.id)])
            line_obj.unlink(cr, uid, line_ids_antes)
            move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                 ('date','<=',this.date_end),('state','=','done'),('type','=','in')],order='date')
            if move_ids:
                for move_id in move_ids:
                    move_aux = move_obj.browse(cr, uid, move_id)
                    if not move_aux.direccion_id.id in direccion_ids:
                        direccion_ids.append(move_aux.direccion_id.id)
                for direccion_id in direccion_ids:
                    categ_ids = []
                    line_id = line_obj.create(cr, uid, {
                                'kardex_id':this.id,
                                'direccion_id':direccion_id,
                    })
                    move_direccion_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),('direccion_id','=',direccion_id),
                                                 ('date','<=',this.date_end),('state','=','done'),('type','=','in')],order='date')
                    for move_2 in move_direccion_ids:
                        move_aux1 = move_obj.browse(cr, uid, move_2)
                        if not move_aux1.categ_id.id in categ_ids:
                            categ_ids.append(move_aux1.categ_id.id)
                    total_direccion = 0 
                    for categ_id in categ_ids:
                        move_categ_direccion_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                             ('date','<=',this.date_end),('state','=','done'),('type','=','in'),
                                                             ('categ_id','=',categ_id),('direccion_id','=',direccion_id)],order='date')
                        cantidad = subtotal = 0
                        for move_direccion_categ_id in move_categ_direccion_ids:
                            move_detalle = move_obj.browse(cr, uid, move_direccion_categ_id)
                            cantidad += move_detalle.product_qty
                            subtotal += move_detalle.total
                        line_line_id = line_line_obj.create(cr, uid, {
                            'line_id':line_id,
                            'categ_id':categ_id,
                            'cantidad':cantidad,
                            'subtotal':subtotal,
                        })
                        total_direccion += subtotal
                    line_obj.write(cr, uid, line_id,{'total':total_direccion})
ingresoDireccion()
###egresos por categoria
class egresoCategoriaLine(osv.TransientModel):
    _name = 'egreso.categoria.line'
    _columns = dict(
        kardex_id = fields.many2one('egreso.categoria','Egreso Categoria'),
        categ_id = fields.many2one('product.category','Categoria/Familia'),
        cantidad = fields.float('Cantidad'),
        subtotal = fields.float('Subtotal'),
    )
egresoCategoriaLine()

class egresoCategoria(osv.TransientModel):
    _name = 'egreso.categoria'
    _columns = dict(
        line_ids = fields.one2many('egreso.categoria.line','kardex_id','Detalle'),
        date_start = fields.date('Fecha desde'),
        date_end = fields.date('Fecha Hasta'),
    )

    def print_egreso_categ(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.egreso.categoria'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'egreso.categoria',
            'model': 'egreso.categoria',
            'datas': datas,
            'nodestroy': True,                        
            }

    def create_egreso_categoria(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        categ_obj = self.pool.get('product.category')
        line_obj = self.pool.get('egreso.categoria.line')
        categ_ids = []
        for this in self.browse(cr, uid, ids):
            line_ids_antes = line_obj.search(cr, uid, [('kardex_id','=',this.id)])
            line_obj.unlink(cr, uid, line_ids_antes)
            move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                 ('date','<=',this.date_end),('state','=','done'),('type','=','out')],order='date')
            if move_ids:
                for move_id in move_ids:
                    move_aux = move_obj.browse(cr, uid, move_id)
                    if not move_aux.categ_id.id in categ_ids:
                        categ_ids.append(move_aux.categ_id.id)
                for categ_id in categ_ids:
                    move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                         ('date','<=',this.date_end),('state','=','done'),('type','=','out'),
                                                         ('categ_id','=',categ_id)],order='date')
                    cantidad = subtotal = 0
                    for move_id in move_ids:
                        move = move_obj.browse(cr, uid, move_id)
                        cantidad += move.product_qty
                        subtotal += move.total
                    line_obj.create(cr, uid, {
                        'kardex_id':this.id,
                        'categ_id':categ_id,
                        'cantidad':cantidad,
                        'subtotal':subtotal,
                    })


egresoCategoria()

###ingresos por categoria
class ingresoCategoriaLineLine(osv.TransientModel):
    _name = 'ingreso.categoria.line.line'
    _columns = dict(
        l_id = fields.many2one('ingreso.categoria.line','Categoria'),
        product_id = fields.many2one('product.product','Producto'),
        cantidad = fields.float('Cantidad'),
        subtotal = fields.float('Subtotal'),
    )
ingresoCategoriaLineLine()

class ingresoCategoriaLine(osv.TransientModel):
    _name = 'ingreso.categoria.line'
    _columns = dict(
        line_ids = fields.one2many('ingreso.categoria.line.line','l_id','Detalle Items'),
        kardex_id = fields.many2one('ingreso.categoria','Ingreso Categoria'),
        categ_id = fields.many2one('product.category','Categoria/Familia'),
        cantidad = fields.float('Cantidad'),
        subtotal = fields.float('Subtotal'),
    )
ingresoCategoriaLine()

class ingresoCategoria(osv.TransientModel):
    _name = 'ingreso.categoria'
    _columns = dict(
        line_ids = fields.one2many('ingreso.categoria.line','kardex_id','Detalle'),
        date_start = fields.date('Fecha desde'),
        date_end = fields.date('Fecha Hasta'),
        category_id = fields.many2one('product.category','Categoria'),
    )

    def print_ingreso_categ(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.ingreso.categoria'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'ingreso.categoria',
            'model': 'ingreso.categoria',
            'datas': datas,
            'nodestroy': True,                        
            }

    def print_ingreso_categ_detalle(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.ingreso.categoria.line'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'ingreso.categoria.line',
            'model': 'ingreso.categoria',
            'datas': datas,
            'nodestroy': True,                        
            }

    def create_ingreso_categoria(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        categ_obj = self.pool.get('product.category')
        line_obj = self.pool.get('ingreso.categoria.line')
        line_line_obj = self.pool.get('ingreso.categoria.line.line')
        product_obj = self.pool.get('product.product')
        categ_ids = []
        for this in self.browse(cr, uid, ids):
            line_ids_antes = line_obj.search(cr, uid, [('kardex_id','=',this.id)])
            line_obj.unlink(cr, uid, line_ids_antes)
            if this.category_id:
                move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),('product_id.categ_id','=',this.category_id.id),
                                                     ('date','<=',this.date_end),('state','=','done'),('type','=','in')],order='date')
            else:
                move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                     ('date','<=',this.date_end),('state','=','done'),('type','=','in')],order='date')
            if move_ids:
                for move_id in move_ids:
                    move_aux = move_obj.browse(cr, uid, move_id)
                    if not move_aux.categ_id.id in categ_ids:
                        categ_ids.append(move_aux.categ_id.id)
                for categ_id in categ_ids:
                    move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                         ('date','<=',this.date_end),('state','=','done'),('type','=','in'),
                                                         ('categ_id','=',categ_id)],order='date')
                    #aqui creo el diccionario producto total
                    dict_p = {}
                    cantidad = subtotal = 0
                    for move_id in move_ids:
                        move = move_obj.browse(cr, uid, move_id)
                        if dict_p.has_key(move.product_id.id):#move.product_id.id in dict_p:
                            dict_p[move.product_id.id] += move.product_qty
                        else:
                            dict_p[move.product_id.id] = move.product_qty
                        cantidad += move.product_qty
                        subtotal += move.total
                    l_id = line_obj.create(cr, uid, {
                        'kardex_id':this.id,
                        'categ_id':categ_id,
                        'cantidad':cantidad,
                        'subtotal':subtotal,
                    })
                    for product_id in dict_p:
                        aux_sub = 0
                        producto = product_obj.browse(cr, uid, product_id)
                        aux_sub = dict_p[product_id] * producto.standard_price
                        line_line_obj.create(cr, uid, {
                            'l_id':l_id,
                            'product_id':product_id,
                            'cantidad':dict_p[product_id],
                            'subtotal':aux_sub,
                        })

ingresoCategoria()

###kardex por categoria de producto

class kardexCategoriaLineLine(osv.TransientModel):
    _name = 'kardex.categoria.line.line'
    _columns = dict(
        l_id = fields.many2one('kardex.categoria.line','Detalle'),
        name = fields.many2one('product.product','Producto'),
        cantidad = fields.float('Cantidad'),
        precio = fields.float('Precio'),
        total = fields.float('Total'),
    )
kardexCategoriaLineLine()

class kardexCategoriaLine(osv.TransientModel):
    _name = 'kardex.categoria.line'
    _order = 'code asc'
    _columns = dict(
        line_ids = fields.one2many('kardex.categoria.line.line','l_id','Detalle'),
        kardex_id = fields.many2one('kardex.categoria','Kardex Categoria'),
        kardex_id2 = fields.many2one('kardex.categoria','Kardex Categoria'),
        categ_id = fields.many2one('product.category','Categoria/Familia'),
        code = fields.char('Codigo',size=32),
        inicial = fields.float('Inicial'),
        ingreso = fields.float('Ingresos'),
        egreso = fields.float('Egresos'),
        saldo = fields.float('Saldo'),
    )
kardexCategoriaLine()

class kardexCategoria(osv.TransientModel):
    _name = 'kardex.categoria'
    _columns = dict(
        line_ids = fields.one2many('kardex.categoria.line','kardex_id','Detalle Corriente'),
        line_ids2 = fields.one2many('kardex.categoria.line','kardex_id2','Detalle Inversion'),
#        categ_id = fields.many2one('product.category'),
        date_start = fields.date('Fecha desde'),
        date_end = fields.date('Fecha Hasta'),
        inicial = fields.float('Inicial'),
        ingreso = fields.float('Ingresos'),
        egreso = fields.float('Egresos'),
        saldo = fields.float('Saldo'),
    )

    def print_categ_kdx(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.kardex.categoria'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'kardex.categoria',
            'model': 'kardex.categoria',
            'datas': datas,
            'nodestroy': True,                        
            }

    def print_categ_kdxdet(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.kardex.categoria'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'kardex.categoriadet',
            'model': 'kardex.categoria',
            'datas': datas,
            'nodestroy': True,                        
            }

    def create_kdx_categoria(self, cr, uid, ids, context=None):
        #preguntar if li
        parameter_obj = self.pool.get('ir.config_parameter')
        lim_ids = parameter_obj.search(cr, uid, [('key','=','slini')],limit=1)
        lim = False
        if lim_ids:
            lim = True
        if lim:
            self.create_kdx_categoria_li(cr, uid, ids)
        else:
            self.create_kdx_categoria_all(cr, uid, ids)

    def create_kdx_categoria_all(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        categ_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        account_obj = self.pool.get('account.account')
        line_obj = self.pool.get('kardex.categoria.line')
        line_line_obj = self.pool.get('kardex.categoria.line.line')
        fiscal_obj = self.pool.get('account.fiscalyear')
        fiscal_obj = self.pool.get('account.fiscalyear')
        account_obj = self.pool.get('account.account')
        categ_ids = []
        for this in self.browse(cr, uid, ids):
            line_ids_antes = line_obj.search(cr, uid, [('kardex_id','=',this.id)])
            line_ids_antes2 = line_obj.search(cr, uid, [('kardex_id2','=',this.id)])
            line_obj.unlink(cr, uid, line_ids_antes)
            line_obj.unlink(cr, uid, line_ids_antes2)
#            categ_ids = categ_obj.search(cr, uid, [('name','!=','All products')])
#            categ_ids = [4]
            categ_ids = categ_obj.search(cr, uid, [])
            for categ_id in categ_ids:
                inicialc = ingresoc = egresoc = saldoc = aux_saldo = 0
                categoria = categ_obj.browse(cr, uid, categ_id)
                product_ids = product_obj.search(cr, uid, [('categ_id','=',categ_id),('type','=','product')])
                #if not categoria.code:
                #    continue
                code_aux = ''
                if categoria.code:
                    code_aux = categoria.code.replace('.','')
                if categoria.budget=='corriente':
                    line_id = line_obj.create(cr, uid, {
                        'kardex_id':this.id,
                        'categ_id':categ_id,
                        'code':code_aux,
                    })
                else:
                    line_id = line_obj.create(cr, uid, {
                        'kardex_id2':this.id,
                        'categ_id':categ_id,
                        'code':code_aux,
                    })
                if product_ids:
                    for product_id in product_ids:
                        ingresoqty = egresoqty = saldoqty = 0
                        ingreso = egreso = egreso_i = ingreso_i = saldo = aux = 0
                        product = product_obj.browse(cr, uid, product_id)
                        move_ids = move_obj.search(cr, uid, [('product_id','=',product_id),('state','=','done'),('date','<=',this.date_end)])
                        if move_ids:
                            aux_ini = aux_in = aux_eg = 0
                            for move_id in move_ids:
                                move = move_obj.browse(cr, uid, move_id)
                                if move.date>=this.date_start:
                                    if move.type=='out':
                                        egreso += move.total#.product_qty
                                    else:
                                        if move.total>0:
                                            ingreso += move.total#product_qty
                                        else:
                                            aux_total = 0
                                            aux_total = move.product_qty * product.standard_price
                                            ingreso += aux_total
                                else:
                                    if move.type=='out':
                                        egreso_i += move.product_qty
                                    else:
                                        ingreso_i += move.product_qty
                                inicial = ingreso_i - egreso_i
                                inicial = inicial * product.standard_price
                                if move.type=='out':
                                    egresoqty += move.product_qty
                                else:
                                    ingresoqty += move.product_qty
#                            import pdb
#                            pdb.set_trace()
                            #inicialc += inicial
#                            print "INICIAL", inicial, ingreso_i, egreso_i
#                            if inicial<0:
#                                import pdb
#                                pdb.set_trace()
                            saldoqty = ingresoqty - egresoqty
                            saldo = inicial + ingreso - egreso
                            aux_total_p = saldoqty * product.standard_price
                            if saldoqty>0:
                                line_line_obj.create(cr, uid, {
                                    'l_id':line_id,
                                    'name':product_id,
                                    'cantidad':saldoqty,
                                    'precio':product.standard_price,
                                    'total':aux_total_p,
                                })
                            #de la categoria
#                            if ingreso >0 or egreso>0:
#                                print "PRODCTU", product.default_code, product.name
#                                print "INGR, EGR, price", ingreso, egreso, product.standard_price
                            aux_ini = inicial * product.standard_price
                            inicialc += aux_ini
                            aux_in = ingreso #* product.standard_price
                            ingresoc += aux_in
                            aux_eg = egreso #* product.standard_price
                            egresoc += aux_eg
                            #aux_saldo += (aux_ini+ingreso-egreso)
                if inicialc>0 or ingresoc>0 or egresoc>0:
                    aux_saldo = inicialc + ingresoc - egresoc
                    line_obj.write(cr, uid, line_id,{
                        'inicial':inicialc,
                        'ingreso':ingresoc,
                        'egreso':egresoc,
                        'saldo':aux_saldo,
                    })
                else:
                    line_obj.unlink(cr, uid, line_id)
        return True


    def create_kdx_categoria_li(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        categ_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        account_obj = self.pool.get('account.account')
        line_obj = self.pool.get('kardex.categoria.line')
        line_line_obj = self.pool.get('kardex.categoria.line.line')
        fiscal_obj = self.pool.get('account.fiscalyear')
        fiscal_obj = self.pool.get('account.fiscalyear')
        account_obj = self.pool.get('account.account')
        categ_ids = []
        for this in self.browse(cr, uid, ids):
            line_ids_antes = line_obj.search(cr, uid, [('kardex_id','=',this.id)])
            line_ids_antes2 = line_obj.search(cr, uid, [('kardex_id2','=',this.id)])
            line_obj.unlink(cr, uid, line_ids_antes)
            line_obj.unlink(cr, uid, line_ids_antes2)
            categ_ids = categ_obj.search(cr, uid, [('name','!=','All products')])
            #categ_ids = [25]
            #categ_ids = [3]
            for categ_id in categ_ids:
                inicialc = ingresoc = egresoc = saldoc = aux_saldo = 0
                categoria = categ_obj.browse(cr, uid, categ_id)
                if not categoria.code:
                    continue
                product_ids = product_obj.search(cr, uid, [('categ_id','=',categ_id),('type','=','product')])
                code_aux = categoria.code.replace('.','')
                account_ids = account_obj.search(cr, uid, [('code','=',code_aux)])
                if not account_ids:
                    continue
                ctx = {}
                fiscal_ids = fiscal_obj.search(cr, uid, [('date_start','<=',this.date_start),('date_stop','>=',this.date_end)])
                ctx['fiscalyear'] = fiscal_ids[0]
                ctx['date_from'] = this.date_start
                ctx['date_to'] =  this.date_start
                ctx['state'] = 'posted'
                account = account_obj.read(cr, uid, account_ids[0], ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx) 
                inicial = abs(account['balance'])
                if categoria.budget=='corriente':
                    line_id = line_obj.create(cr, uid, {
                        'kardex_id':this.id,
                        'categ_id':categ_id,
                        'code':categoria.code,
                        'inicial':inicial,
                    })
                else:
                    line_id = line_obj.create(cr, uid, {
                        'kardex_id2':this.id,
                        'categ_id':categ_id,
                        'code':categoria.code,
                        'inicial':inicial,
                    })
                if product_ids:
                    for product_id in product_ids:
                        ingresoqty = egresoqty = saldoqty = 0
                        ingreso = egreso = saldo = aux = 0
                        product = product_obj.browse(cr, uid, product_id)
                        move_ids = move_obj.search(cr, uid, [('product_id','=',product_id),('state','=','done'),('date','<=',this.date_end)])
                        if move_ids:
                            for move_id in move_ids:
                                move = move_obj.browse(cr, uid, move_id)
                                if move.date>=this.date_start:
                                    if move.type=='out':
                                        egreso += move.total
                                    else:
                                        ingreso += move.total
                                if move.type=='out':
                                    egresoqty += move.product_qty
                                else:
                                    ingresoqty += move.product_qty
                            saldoqty = ingresoqty - egresoqty
                            saldo = inicial + ingreso - egreso
                            aux_total_p = saldoqty * product.standard_price
                            if saldoqty>0:
                                line_line_obj.create(cr, uid, {
                                    'l_id':line_id,
                                    'name':product_id,
                                    'cantidad':saldoqty,
                                    'precio':product.standard_price,
                                    'total':aux_total_p,
                                })
                            #de la categoria
                            aux_ini = inicial * product.standard_price
                            inicialc += aux_ini
                            aux_in = ingreso * product.standard_price
                            ingresoc += ingreso#aux_in
                            aux_eg = egreso * product.standard_price
                            egresoc += egreso#aux_eg
                            #aux_saldo += (aux_ini+ingreso-egreso)
                if inicialc>0 or ingresoc>0 or egresoc>0 or aux_saldo>0:
                    print "CREA LINEA"
                    aux_saldo = inicial + ingresoc - egresoc
                    line_obj.write(cr, uid, line_id,{
                        #'inicial':inicialc,
                        'ingreso':ingresoc,
                        'egreso':egresoc,
                        'saldo':aux_saldo,
                    })
                else:
                    line_obj.unlink(cr, uid, line_id)
        return True

    def create_kdx_categoria2(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        categ_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        account_obj = self.pool.get('account.account')
        line_obj = self.pool.get('kardex.categoria.line')
        fiscal_obj = self.pool.get('account.fiscalyear')
        categ_ids = []
        for this in self.browse(cr, uid, ids):
            line_ids_antes = line_obj.search(cr, uid, [('kardex_id','=',this.id)])
            line_ids_antes2 = line_obj.search(cr, uid, [('kardex_id2','=',this.id)])
            line_obj.unlink(cr, uid, line_ids_antes)
            line_obj.unlink(cr, uid, line_ids_antes2)
            move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                 ('date','<=',this.date_end),('state','=','done'),('type','in',('out','in'))],order='date')
            if move_ids:
                for move_id in move_ids:
                    move_aux = move_obj.browse(cr, uid, move_id)
                    if not move_aux.categ_id.id in categ_ids:
                        categ_ids.append(move_aux.categ_id.id)
                #deberia ser todas las categ
                categ_ids = []
                categ_ids2 = categ_obj.search(cr, uid, [('name','!=','All products')])
                for categ_id in categ_ids2:
                    categ = categ_obj.browse(cr, uid, categ_id)
                    if categ.code:
                        categ_ids.append(categ.id)
                    else:
                        categ_ids.append(categ.id)
                categ_ids = [25]
                for categ_id in categ_ids:
                    categoria = categ_obj.browse(cr, uid, categ_id)
                    move_ids_2 = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                         ('date','<=',this.date_end),('state','=','done'),('type','in',('in','out')),
                                                         ('categ_id','=',categ_id)],order='date')
                    move_ids1 = move_obj.search(cr, uid, [('type_p','=','product'),
                                                         ('state','=','done'),('type','in',('in','out')),
                                                         ('categ_id','=',categ_id)],order='date')
                    move_ids2 = move_obj.search(cr, uid, [('type_p','=','product'),
                                                          ('state','=','done'),('id','not in',move_ids1),
                                                         ('categ_id','=',categ_id)],order='date')
                    move_ids = move_ids1 + move_ids2
                    #ojo aqui deberia sar haya o no qty
                    product_ids = product_obj.search(cr, uid, [('categ_id','=',categ_id),('type','=','product'),('qty_available','>',0)])
                    inicial = saldo = aux = 0
                    for product_id in product_ids:
                        product = product_obj.browse(cr, uid, product_id)
                        aux = product.standard_price * product.qty_available
                        saldo += aux 
                    #total
                    ingreso = egreso = 0
                    if move_ids:
                        for move_id in move_ids:
                            move = move_obj.browse(cr, uid, move_id)
                            if move.type == 'in' or move.total==0:
                                if move.total>0:
                                    ingreso += move.total
                                else:
                                    aux_total_inicial = move.product_qty*move.product_id.standard_price
                                    ingreso += aux_total_inicial
                            else:
                                egreso += move.total
                    #el inicial tomar lo que esta contable
                    if categoria.code:
                        code_aux = categoria.code.replace('.','')
                    else:
                        code_aux = ''
                    #solo limon
                    limon = True
                    account_ids = []
                    if limon:
                        account_ids = account_obj.search(cr, uid, [('code','=',code_aux)])
                        ctx = {}
                        fiscal_ids = fiscal_obj.search(cr, uid, [('date_start','<=',this.date_start),('date_stop','>=',this.date_end)])
                        ctx['fiscalyear'] = fiscal_ids[0]
                        ctx['date_from'] = this.date_start
                        ctx['date_to'] =  this.date_start
                        ctx['state'] = 'posted'
                    if account_ids:
                        account = account_obj.read(cr, uid, account_ids[0], ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx) 
                        inicial = abs(account['balance'])
                    else:
                        if saldo>0:
                            if move_ids2:
                                aux_inicial = 0
                                for move_id2 in move_ids2:
                                    move_inicial = move_obj.browse(cr, uid, move_id2)
                                    aux_inicial += move_inicial.product_qty*move_inicial.product_id.standard_price
                                inicial = aux_inicial
                            else:
                                inicial = abs(saldo + egreso - ingreso)
                        else:
                            if move_ids2:
                                aux_inicial = 0
                                for move_id2 in move_ids2:
                                    move_inicial = move_obj.browse(cr, uid, move_id2)
                                    aux_inicial += move_inicial.product_qty*move_inicial.product_id.standard_price
                                inicial = aux_inicial
                            else:
                                inicial = abs(saldo)
                    ingreso = egreso = 0
                    for move_id in move_ids_2:
                        move = move_obj.browse(cr, uid, move_id)
                        if move.type == 'in':
                            ingreso += move.total
                        else:
                            egreso += move.total
                    saldo = inicial + ingreso - egreso
                    if (saldo>0 or inicial>0 or ingreso>0 or egreso>0):
                        if categoria.budget=='corriente':
                            line_obj.create(cr, uid, {
                                'kardex_id':this.id,
                                'categ_id':categ_id,
                                'code':categoria.code,
                                'inicial':inicial,
                                'ingreso':ingreso,
                                'egreso':egreso,
                                'saldo':saldo,
                            })
                        else:
                            line_obj.create(cr, uid, {
                                'kardex_id2':this.id,
                                'categ_id':categ_id,
                                'code':categoria.code,
                                'inicial':inicial,
                                'ingreso':ingreso,
                                'egreso':egreso,
                                'saldo':saldo,
                            })

kardexCategoria()

########
class kardexCategoriaLineC(osv.TransientModel):
    _name = 'kardex.categoria.linec'
    _order = 'code asc'
    _columns = dict(
        kardex_id = fields.many2one('kardex.categoriac','Kardex Categoria'),
        kardex_id2 = fields.many2one('kardex.categoriac','Kardex Categoria'),
        categ_id = fields.many2one('product.category','Cuenta'),
        code = fields.char('Codigo',size=32),
        inicial = fields.float('Inicial Inventario'),
        ingreso = fields.float('Ingresos Inventario'),
        egreso = fields.float('Egresos Inventario'),
        saldo = fields.float('Saldo Inventario'),
        inicialc = fields.float('Inicial Contable'),
        ingresoc = fields.float('Ingresos Contable'),
        egresoc = fields.float('Egresos Contable'),
        saldoc = fields.float('Saldo Contable'),
        diferencia = fields.float('DIFERENCIA'),
    )
kardexCategoriaLineC()

class kardexCategoriaC(osv.TransientModel):
    _name = 'kardex.categoriac'
    _columns = dict(
        line_ids = fields.one2many('kardex.categoria.linec','kardex_id','Detalle Corriente'),
        line_ids2 = fields.one2many('kardex.categoria.linec','kardex_id2','Detalle Inversion'),
#        categ_id = fields.many2one('product.category'),
        date_start = fields.date('Fecha desde'),
        date_end = fields.date('Fecha Hasta'),
        inicial = fields.float('Inicial'),
        ingreso = fields.float('Ingresos'),
        egreso = fields.float('Egresos'),
        saldo = fields.float('Saldo'),
    )

    def print_categ_kdxc(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.kardex.categoriac'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'kardex.categoriac',
            'model': 'kardex.categoriac',
            'datas': datas,
            'nodestroy': True,                        
            }

    def create_kdx_categoriac(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        account_obj = self.pool.get('account.account')
        categ_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        line_obj = self.pool.get('kardex.categoria.linec')
        fiscal_obj = self.pool.get('account.fiscalyear')
        account_obj = self.pool.get('account.account')
        categ_ids = []
        for this in self.browse(cr, uid, ids):
            line_ids_antes = line_obj.search(cr, uid, [('kardex_id','=',this.id)])
            line_obj.unlink(cr, uid, line_ids_antes)
            line_ids_antes_inv = line_obj.search(cr, uid, [('kardex_id2','=',this.id)])
            line_obj.unlink(cr, uid, line_ids_antes_inv)
            move_ids = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                 ('date','<=',this.date_end),('state','=','done'),('type','in',('out','in'))],order='date')
            if move_ids:
                for move_id in move_ids:
                    move_aux = move_obj.browse(cr, uid, move_id)
                    if not move_aux.categ_id.id in categ_ids:
                        categ_ids.append(move_aux.categ_id.id)
                #deberia ser todas las categ
                categ_ids = []
                categ_ids2 = categ_obj.search(cr, uid, [])
                for categ_id in categ_ids2:
                    categ = categ_obj.browse(cr, uid, categ_id)
                    if categ.code:
                        categ_ids.append(categ.id)
                for categ_id in categ_ids:
                    categoria = categ_obj.browse(cr, uid, categ_id)
                    move_ids_2 = move_obj.search(cr, uid, [('date','>=',this.date_start),('type_p','=','product'),
                                                         ('date','<=',this.date_end),('state','=','done'),('type','in',('in','out')),
                                                         ('categ_id','=',categ_id)],order='date')
                    move_ids = move_obj.search(cr, uid, [('type_p','=','product'),
                                                         ('state','=','done'),('type','in',('in','out')),
                                                         ('categ_id','=',categ_id)],order='date')
                    #ojo aqui deberia sar haya o no qty
                    product_ids = product_obj.search(cr, uid, [('categ_id','=',categ_id),('type','=','product'),('qty_available','>',0)])
                    inicial = saldo = aux = 0
                    for product_id in product_ids:
                        product = product_obj.browse(cr, uid, product_id)
                        aux = product.standard_price * product.qty_available
                        saldo += aux 
                    #total
                    ingreso = egreso = 0
                    if move_ids:
                        for move_id in move_ids:
                            move = move_obj.browse(cr, uid, move_id)
                            if move.type == 'in':
                                ingreso += move.total
                            else:
                                egreso += move.total
                    code_aux = categoria.code.replace('.','')
                    account_ids = account_obj.search(cr, uid, [('code','=',code_aux)])
                    ctx = {}
                    fiscal_ids = fiscal_obj.search(cr, uid, [('date_start','<=',this.date_start),('date_stop','>=',this.date_end)])
                    ctx['fiscalyear'] = fiscal_ids[0]
                    ctx['date_from'] = this.date_start
                    ctx['date_to'] =  this.date_start
                    ctx['state'] = 'posted'
                    account = account_obj.read(cr, uid, account_ids[0], ['id','type','code','name','debit','credit','balance','parent_id','level'], ctx) 
                    inicial = abs(account['balance'])
                    #        inicial = saldo + egreso - ingreso
                    #else:
                    #    inicial = saldo
                    ingreso = egreso = 0
                    for move_id in move_ids_2:
                        move = move_obj.browse(cr, uid, move_id)
                        if move.type == 'in':
                            ingreso += move.total
                        else:
                            egreso += move.total
                    saldo = inicial + ingreso - egreso
                    #contabilidad
                    inicialc = saldoc = auxc = 0
                    aux_code_categ = categoria.code.replace('.','')
                    account_ids = account_obj.search(cr, uid, [('code','=',aux_code_categ)])
                    if not account_ids:
                        raise osv.except_osv('Error de CONFIGURACION','No se ha encontrado cuenta contable para la categoria %s.'%(categoria.code))
                    ctx2 = {}
                    ctx2.update({'state': 'posted'})
                    ctx2.update({'date_from': this.date_start,
                                 'date_to': this.date_start})
                    account_inicio = account_obj.read(cr, uid, account_ids, ['code','name','debit','credit', 'balance','level','sufijo_esigef'], ctx2)
                    inicialc = account_inicio[0]['balance']
                    ctx3 = {}
                    ctx3.update({'state': 'posted'})
                    ctx3.update({'date_from': this.date_start,
                                 'date_to': this.date_end})
                    account_inicio_flujo = account_obj.read(cr, uid, account_ids, ['code','name','debit','credit', 'balance','level','sufijo_esigef'], ctx3)
                    saldoc = account_inicio_flujo[0]['balance']
                    ingresoc = account_inicio_flujo[0]['debit'] - account_inicio[0]['debit']
                    egresoc = account_inicio_flujo[0]['credit'] - account_inicio[0]['credit']
                    diferencia = abs(saldo - saldoc)
                    if categoria.budget=='corriente':
                        if (saldo>0 or inicial>0 or ingreso>0 or egreso>0):
                            line_obj.create(cr, uid, {
                                'kardex_id':this.id,
                                'categ_id':categ_id,
                                'code':categoria.code,
                                'inicial':inicial,
                                'ingreso':ingreso,
                                'egreso':egreso,
                                'saldo':saldo,
                                'inicialc':inicialc,
                                'ingresoc':ingresoc,
                                'egresoc':egresoc,
                                'saldoc':saldoc,
                                'diferencia':diferencia,
                            })
                    else:
                       if (saldo>0 or inicial>0 or ingreso>0 or egreso>0):
                            line_obj.create(cr, uid, {
                                'kardex_id2':this.id,
                                'categ_id':categ_id,
                                'code':categoria.code,
                                'inicial':inicial,
                                'ingreso':ingreso,
                                'egreso':egreso,
                                'saldo':saldo,
                                'inicialc':inicialc,
                                'ingresoc':ingresoc,
                                'egresoc':egresoc,
                                'saldoc':saldoc,
                                'diferencia':diferencia,
                            })
kardexCategoria()
##CONTA

class reportMoveLine(osv.TransientModel):
    _name = 'report.move.line'
    _order = 'id desc'
    _columns = {
        'h_id':fields.many2one('report.move.head','Reporte'),
        'department_id':fields.many2one('hr.department','Departamento'),
        'qty':fields.float('Cantidad'),
        'saldo':fields.float('Stock'),
        'cu':fields.float('Costo Unitario'),
        'ct':fields.float('Costo Total'),
        'documento':fields.char('Documento',size=12),
        'date':fields.date('Fecha'),
        'tot_cu':fields.float('Total Unitario'),
        'tipo':fields.char('Tipo Ingreso/Egreso',size=256),
        'tot_ct':fields.float('Total'),
        'location_dest_id':fields.many2one('stock.location','Bodega'),
        }
reportMoveLine()

class reportMoveHead(osv.TransientModel):
    _name = 'report.move.head'

    def print_line_move_kdx(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.move.head'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'kdx.bodega',
            'model': 'report.move.head',
            'datas': datas,
            'nodestroy': True,                        
            }

    def create_line_move_kdx(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        line_obj = self.pool.get('report.move.line')
        product_obj = self.pool.get('product.product')
        for this in self.browse(cr, uid, ids):
            #borrar los anteriores
            lines_antes = line_obj.search(cr, uid, [('h_id','=',this.id)])
            if lines_antes:
                line_obj.unlink(cr, uid, lines_antes)
            disponible_today = this.product_id.qty_available
            move_all = move_obj.search(cr, uid, [('product_id','=',this.product_id.id),('date','>=',this.date_start),('picking_id.state','=','done'),
                                                   ('state','=','done'),('type','!=','internal')],order='date')
            aux_in = aux_out = 0
            for line_all_id in move_all:
                move_a = move_obj.browse(cr, uid, line_all_id)
                if move_a.type=='in':
                    aux_in += move_a.product_qty
                elif move_a.type=='out':
                    aux_out += move_a.product_qty
            disponible_fecha = disponible_today + aux_out - aux_in
            move_lines = move_obj.search(cr, uid, [('product_id','=',this.product_id.id),('date','>=',this.date_start),('picking_id.state','=','done'),
                                                   ('date','<=',this.date_end),('state','=','done'),('type','!=','internal')],order='date')
            t_in = t_out = tin_usd = tout_usd = total = 0
            saldo_aux = disponible_fecha
            move_line_start_ids = move_obj.search(cr, uid, [('product_id','=',this.product_id.id),('date','>=',this.date_start),('state','=','done'),
                                                            ('date','<=',this.date_end),('id','not in',move_lines)],
                                                  order='date')
            if move_line_start_ids:
                move = move_obj.browse(cr, uid, move_line_start_ids[0])
                line_obj.create(cr, uid, {
                    'h_id':this.id,
                    'documento':move.name,
                    'qty':move.product_qty,
                    'tipo':'INICIAL',
                    'cu':move.product_id.standard_price,
                    'tot_cu':(move.product_id.standard_price * move.product_qty),
                    'ct':(move.product_id.standard_price * move.product_qty),
                    'saldo':move.product_qty,
                    'date':move.date,
                })
            for line in move_lines:
                move = move_obj.browse(cr, uid, line)
                if move.type=='out':
                    aux_tipo = 'EGR <- '
                    if move.picking_id.note:
                        aux_tipo = 'EGR <- ' + move.picking_id.note
                    t_out += move.product_qty
                    tout_usd += move.subtot
                    saldo_aux = saldo_aux - move.product_qty
                else:
                    aux_tipo = 'ING -> '
                    if move.picking_id.note:
                        aux_tipo = 'ING -> ' + move.picking_id.note
                    tin_usd += move.subtot
                    t_in += move.product_qty
                    saldo_aux = saldo_aux + move.product_qty
                total = tin_usd - tout_usd
                line_obj.create(cr, uid, {
                    'h_id':this.id,
                    'department_id':move.department_id.id,
                    'documento':move.picking_id.name, #move.num_egreso
                    'qty':move.product_qty,
                    'tipo':aux_tipo,
                    'cu':move.price_unit,
                    'tot_cu':(move.price_unit * move.product_qty),
                    'ct':move.subtot,
                    'saldo':saldo_aux,
                    'date':move.date,
                    'location_dest_id':move.location_dest_id.id,
                })
            if total<0:
                total = 0
            self.write(cr, uid, this.id,{
                'total':total,
                'total_in':t_in,
                'total_out':t_out,
                'total_in_usd':tin_usd,
                'total_out_usd':tout_usd,
                'qty_inicial':disponible_fecha,
            })
        return True

    _columns = {
        'qty_inicial':fields.float('Cantidad Inicial'),
        'date_start':fields.date('Desde'),
        'date_end':fields.date('Hasta'),
        'product_id':fields.many2one('product.product','Producto',required=True),
        'bodega_id':fields.many2one('stock.location','Bodega',required=True),
        'line_ids':fields.one2many('report.move.line','h_id','Detalle'),
        'total':fields.float('Total DINERO($)'),
        'total_in':fields.float('Total Ingreso Cantidad (QTY)'),
        'total_out':fields.float('Total Egreso Cantidad (QTY)'),
        'total_in_usd':fields.float('Total Ingreso Dinero ($)'),
        'total_out_usd':fields.float('Total Egreso Dinero ($)'),
        }

    def _get_bodega(self, cr, uid, ids, context=None):
        location_obj = self.pool.get('stock.location')
        location_ids = location_obj.search(cr, uid, [('is_general','=',True)],limit=1)
        if location_ids:
            return location_ids[0]

    _defaults = dict(
        bodega_id = _get_bodega,
        date_start = time.strftime('%Y-%m-%d'),
        date_end = time.strftime('%Y-%m-%d'),
        )
    
reportMoveHead()

# saldo de productos

########### corte fecha
class saldoLineDate(osv.TransientModel):
    _name = 'saldo.line.date'
    _columns = dict(
        #saldop_id = fields.many2one('saldo.product.date','Detalle'),
        saldoh_id = fields.many2one('saldo.head.date','Detalle'),
        product_id = fields.many2one('product.product','Producto'),
        udm_id = fields.many2one('product.uom','Unidad'),
        qty = fields.float('Cantidad'),
        valor = fields.float('Precio',digits=(3,3)),
        total = fields.float('Total',digits=(3,3)),
    )
saldoLineDate()

class saldoHeadDate(osv.TransientModel):
    _name = 'saldo.head.date'
    _columns = dict(
        saldop_id = fields.many2one('saldo.product.date','Detalle'),
        categ_id = fields.many2one('product.category','Categoria'),
        line_ids = fields.one2many('saldo.line.date','saldoh_id','Detalle'),
    )
saldoHeadDate()

class saldoProductDate(osv.TransientModel):
    _name = 'saldo.product.date'

    def print_product_qty(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'saldo.product.date'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'saldo.product.date',
            'model': 'saldo.product.date',
            'datas': datas,
            'nodestroy': True,                        
            }

    def create_product_qty(self, cr, uid, ids, context=None):
        categ_obj = self.pool.get('product.category')
        line_obj = self.pool.get('saldo.line.date')
        head_obj = self.pool.get('saldo.head.date')
        p_obj = self.pool.get('saldo.product.date')
        product_obj = self.pool.get('product.product')
        move_obj = self.pool.get('stock.move')
        for this in self.browse(cr, uid, ids):
            aux_total = 0
            if len(this.line_ids)>0:
                line_ant = line_obj.search(cr, uid, [('saldop_id','=',this.id)])
                line_obj.unlink(cr, uid, line_ant)
            if this.categ_id:
                categ_ids = [this.categ_id.id]
                product_ids = product_obj.search(cr, uid, [('categ_id','=',this.categ_id.id),('type','=','product')])
            else:
                categ_ids = categ_obj.search(cr, uid, [])
                product_ids = product_obj.search(cr, uid, [('type','=','product')])
            for categ_id in categ_ids:
                head_id = head_obj.create(cr, uid, {'saldop_id':this.id,'categ_id':categ_id})
                product_ids = product_obj.search(cr, uid, [('categ_id','=',categ_id),('type','=','product')])
                for product_id in product_ids:
    #                move_ids = move_obj.search(cr, uid, [('product_id','=',product_id),('state','=','done'),('date','>=',this.date_start),('date','<=',this.date_end)])
                    move_ids = move_obj.search(cr, uid, [('product_id','=',product_id),('state','=','done'),('date','<=',this.date_end)])
                    qty = 0
                    if move_ids:
                        product = product_obj.browse(cr, uid, product_id)
                        for move_id in move_ids:
                            move = move_obj.browse(cr, uid, move_id)
                            if move.type:
                                if move.type=='out':
                                    qty-=move.product_qty
                                else:
                                    qty+=move.product_qty
                            else:
                                qty+=move.product_qty
                        valor = product.standard_price
                        total = qty * valor
                        if total>0:
                            line_obj.create(cr, uid, {
                                'saldoh_id':head_id,
                                'product_id':product_id,
                                'udm_id':product.uom_id.id,
                                'qty':qty,
                                'valor':valor,
                                'total':total,
                            })
        return True

    def _get_bodega(self, cr, uid, ids, context=None):
        location_obj = self.pool.get('stock.location')
        location_ids = location_obj.search(cr, uid, [('is_general','=',True)],limit=1)
        if location_ids:
            return location_ids[0]

    _columns = dict(
        date_start = fields.date('Fecha desde'),
        date_end = fields.date('Fecha hasta'),
        total = fields.float('Total',digits=(3,3)),
        bodega_id = fields.many2one('stock.location','Bodega',required=True),
        categ_id = fields.many2one('product.category','Categoria'),
#        line_ids = fields.one2many('saldo.line.date','saldop_id','Detalle'),
        line_ids = fields.one2many('saldo.head.date','saldop_id','Detalle'),
        )

    _defaults = dict(
        bodega_id = _get_bodega,
        )
    
saldoProductDate()
######### a la fecha
class reportSaldoLine(osv.TransientModel):
    _name = 'report.saldo.line'
    _columns = dict(
        saldoh_id = fields.many2one('report.saldo.categ','Detalle'),
        product_id = fields.many2one('product.product','Producto'),
        udm_id = fields.many2one('product.uom','Unidad'),
        qty = fields.float('Cantidad'),
        valor = fields.float('Precio',digits=(3,3)),
        total = fields.float('Total',digits=(3,3)),
    )
reportSaldoLine()

class reportSaldoCateg(osv.TransientModel):
    _name = 'report.saldo.categ'
    _columns = dict(
        saldop_id = fields.many2one('report.saldo.product','Saldos'),
        categ_id = fields.many2one('product.category','Categoria'),
        line_ids = fields.one2many('report.saldo.line','saldoh_id','Detalle'),
    )
reportSaldoCateg()

class reportSaldoProduct(osv.TransientModel):
    _name = 'report.saldo.product'

    def print_product_qty(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.saldo.product'}
#        return {
#            'type': 'ir.actions.report.xml',
#            'report_name': 'saldo.product.rml',
#            'model': 'report.saldo.product',
#            'datas': datas,
#            'nodestroy': True,                        
#            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'saldo.producto',
            'model': 'report.saldo.product',
            'datas': datas,
            'nodestroy': True,                        
            }

    def create_product_qty(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('report.saldo.line')
        p_obj = self.pool.get('report.saldo.producto')
        head_obj = self.pool.get('report.saldo.categ')
        product_obj = self.pool.get('product.product')
        categ_obj = self.pool.get('product.category')
        categ_ids = []
        for this in self.browse(cr, uid, ids):
            aux_total = 0
            if len(this.line_ids)>0:
                line_ant = line_obj.search(cr, uid, [('saldop_id','=',this.id)])
                line_obj.unlink(cr, uid, line_ant)
            if this.categ_id:
                #product_ids = product_obj.search(cr, uid, [('categ_id','=',this.categ_id.id),('type','=','product')])
                #product_ids = product_obj.search(cr, uid, [('categ_id','=',this.categ_id.id)])
                categ_ids = [this.categ_id.id]
                product_ids = product_obj.search(cr, uid, [('qty_available','>',0),('categ_id','=',this.categ_id.id),('type','=','product')])
            else:
                categ_ids = categ_obj.search(cr, uid, [])
                product_ids = product_obj.search(cr, uid, [('qty_available','>',0),('type','=','product')])
            for categ_id in categ_ids:
                head_id = head_obj.create(cr, uid, {'saldop_id':this.id,'categ_id':categ_id})
                product_ids = product_obj.search(cr, uid, [('categ_id','=',categ_id),('type','=','product')])
                for product_id in product_ids:
                    qty = valor = total = 0
                    product = product_obj.browse(cr, uid, product_id)
                    qty = product.qty_available
                    valor = product.standard_price
                    total = qty * valor
                    if total>0:
                        line_obj.create(cr, uid, {
                            'saldoh_id':head_id,
                            'product_id':product_id,
                            'udm_id':product.uom_id.id,
                            'qty':qty,
                            'valor':valor,
                            'total':total,
                        })
        return True

    def _get_bodega(self, cr, uid, ids, context=None):
        location_obj = self.pool.get('stock.location')
        location_ids = location_obj.search(cr, uid, [('is_general','=',True)],limit=1)
        if location_ids:
            return location_ids[0]

    _columns = dict(
        total = fields.float('Total',digits=(3,3)),
        bodega_id = fields.many2one('stock.location','Bodega',required=True),
        categ_id = fields.many2one('product.category','Categoria'),
        line_ids = fields.one2many('report.saldo.categ','saldop_id','Detalle'),
        )

    _defaults = dict(
        bodega_id = _get_bodega,
        )
    
reportSaldoProduct()

#Egresos
class reportEgresosLine(osv.TransientModel):
    _name = 'report.egresos.line'
    _order = 'date asc'
    _columns = dict(
        egr_id = fields.many2one('report.egresos','Reporte'),
        product_id = fields.many2one('product.product','Producto'),
        udm_id = fields.many2one('product.uom','Unidad'),
        qty = fields.float('Cantidad'),
        p_unitario = fields.float('P. Unitario',digits=(3,3)),
        total = fields.float('Total',digits=(3,3)),
        doc_egreso = fields.char('Nro. Doc. Egreso',size=15),
        date = fields.date('Fecha'),
        num_sol = fields.char('Nro. Solicitud',size=10),
        date_sol = fields.date('Fecha Solicitud'),
        solicitante_id = fields.many2one('hr.employee','Solicitante'),
    )
reportEgresosLine()
class reportEgresos(osv.TransientModel):
    _name = 'report.egresos'
    _columns = dict(
        line_ids = fields.one2many('report.egresos.line','egr_id','Detalle'),
        bodega_id = fields.many2one('stock.location','Bodega'),
        date_start = fields.date('Desde'),
        date_end = fields.date('Hasta'),
        unidad_id = fields.many2one('hr.department','Departamento'),
        solicitant_id = fields.many2one('hr.employee','Solicitante'),
    )

    def print_egreso(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.egresos'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'egreso.rml',
            'model': 'report.egreso.rml',
            'datas': datas,
            'nodestroy': True,                        
            }
#        return {
#            'type': 'ir.actions.report.xml',
#            'report_name': 'egreso.report',
#            'model': 'report.egresos',
##            'datas': datas,
#            'nodestroy': True,                        
#            }

    def create_egreso(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('report.egresos.line')
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        for this in self.browse(cr, uid, ids):
            if len(this.line_ids)>0:
                line_ant = line_obj.search(cr, uid, [('egr_id','=',this.id)])
                line_obj.unlink(cr, uid, line_ant)
            if this.unidad_id:
                move_ids = move_obj.search(cr, uid, [('state','=','done'),('type','=','out'),('date','>=',this.date_start),('picking_id.state','=','done'),
                                                     ('date','<=',this.date_end),('department_id','=',this.unidad_id.id)])
            elif this.solicitant_id:
                move_ids = move_obj.search(cr, uid, [('state','=','done'),('type','=','out'),('date','>=',this.date_start),('picking_id.state','=','done'),
                                                     ('date','<=',this.date_end),('solicitant_id','=',this.solicitant_id.id)])
            else:
                move_ids = move_obj.search(cr, uid, [('state','=','done'),('type','=','out'),('date','>=',this.date_start),('date','<=',this.date_end),
                                                     ('picking_id.state','=','done'),])
            for move_id in move_ids:
                qty = p_unitario = total = 0
                move = move_obj.browse(cr, uid, move_id)
                qty = move.product_qty
                product = product_obj.browse(cr, uid, move.product_id.id)
                if move.subtot <= 0:
                    aux_subtot = move.product_qty * move.price_unit
                    move_obj.write(cr, uid, move_id,{
                        'subtot':aux_subtot,
                    })
                if move.price_unit > 0:
                    p_unitario = move.price_unit
                else:
                    move_obj.write(cr, uid, move_id,{
                        'price_unit':move.product_id.standard_price,
                    })
                    p_unitario = move.product_id.standard_price
                total = qty * p_unitario
                line_obj.create(cr, uid, {
                    'egr_id':this.id,
                    'product_id':product.id,
                    'udm_id':product.uom_id.id,
                    'qty':qty,
                    'p_unitario':p_unitario,
                    'doc_egreso':move.picking_id.name,
                    'total':total,
                    'date':move.date,
                    'num_sol':move.num_solicitud,
                    'date_sol':move.picking_id.document_date,
                    'solicitante_id':move.solicitant_id.id,
                })
        return True

    def _get_bodega(self, cr, uid, ids, context=None):
        location_obj = self.pool.get('stock.location')
        location_ids = location_obj.search(cr, uid, [('is_general','=',True)],limit=1)
        if location_ids:
            return location_ids[0]

    _defaults = dict(
        bodega_id = _get_bodega,
        date_end = time.strftime('%Y-%m-%d')
    )

reportEgresos()


#Ingresos
class reportIngresosLineLine(osv.TransientModel):
    _name = 'report.ingresos.line.line'
    _columns = dict(
        line_id = fields.many2one('report.ingresos.line','Detalle'),
        product_id = fields.many2one('product.product','Producto'),
        qty = fields.float('Cantidad'),
        total = fields.float('Total'),
    )
reportIngresosLineLine()
class reportIngresosLine(osv.TransientModel):
    _name = 'report.ingresos.line'
    _columns = dict(
        p_id = fields.many2one('report.ingresos','Ingreso'),
#        partner_id = fields.many2one('res.partner','Proveedor'),
#        monto = fields.float('Total Proveedor'),
#        line_ids = fields.one2many('report.ingresos.line.line','line_id','Detalle'),
        picking_id = fields.many2one('stock.picking','Ingresos'),
        move_id = fields.many2one('stock.move','MOve'),
    )
reportIngresosLine()
class reportIngresos(osv.TransientModel):
    _name = 'report.ingresos'
    _columns = dict(
        line_ids = fields.one2many('report.ingresos.line','p_id','Detalle'),
        bodega_id = fields.many2one('stock.location','Bodega'),
        date_start = fields.date('Desde'),
        date_end = fields.date('Hasta'),
    )

    def print_ingreso(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        line_obj = self.pool.get('report.ingresos.line')
        picking_obj = self.pool.get('stock.picking')
        for this in self.browse(cr, uid, ids):
            picking_ids = picking_obj.search(cr, uid, [('state','=','done'),('type','=','in'),('date','>=',this.date_start),('date','<=',this.date_end)])
            for pick_id in picking_ids:
                picking = picking_obj.browse(cr, uid, pick_id)
                for move in picking.move_lines:
                    line_obj.create(cr, uid, {
                        'p_id':this.id,
                        'picking_id':pick_id,
                        'move_id':move.id,
                    })
        report = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [report.id], 'model': 'report.ingresos'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'ingreso.report',
            'model': 'report.ingreso',
            'datas': datas,
            'nodestroy': True,                        
            }

    def _get_bodega(self, cr, uid, ids, context=None):
        location_obj = self.pool.get('stock.location')
        location_ids = location_obj.search(cr, uid, [('is_general','=',True)],limit=1)
        if location_ids:
            return location_ids[0]

    _defaults = dict(
        bodega_id = _get_bodega,
        date_end = time.strftime('%Y-%m-%d')
    )

reportIngresos()
