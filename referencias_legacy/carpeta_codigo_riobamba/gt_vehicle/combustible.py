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
from datetime import datetime

class commbustibleOrderLine(osv.Model):
    _name = 'combustible.order.line'

    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            if formulario.combustible_id.state=='aprobado':
                raise osv.except_osv('Error', 'No pueden eliminar detalle de solicitudes de movilización')
        return False

    _TIPO_COMBUSTIBLE = [('gextra','Gasolina Extra'),('gsuper','Gasolina Super'),('otros','Otros')]

    def _amount_subtotal(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            aux = this.qty * this.name.lst_price
        res[this.id] = aux
        return res
    
    
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        if context is None:
            context = {}        
        res = {'value': {'product_price' : False}}
        if not product_id:
            return res
        product_product = self.pool.get('product.product')
        product = product_product.browse(cr, uid, product_id, context)
        price = product.list_price
        res['value'].update({'product_price': price})
        return res
    '''
    def onchange_product_qty(self, cr, uid, ids,product_id, qty, context=None):
        if context is None:
            context = {}        
        res = {'value': {'sub_total' : False}}
        if not qty:
            return res
        product_product = self.pool.get('product.product')
        product = product_product.browse(cr, uid, product_id, context)
        price_prod = product.list_price
        total=price_prod*qty    
        res['value'].update({'sub_total': total})
        return res'''
    
    _columns = dict(
        name = fields.many2one('product.product','Combustible',required=True),
        product_price = fields.float('Precio', required=True),
        qty = fields.integer('Cantidad',required=True),
        sub_total = fields.function(_amount_subtotal, string='SubTotal', type="float", store=True),
        combustible_id = fields.many2one('combustible.order','Orden'),
        )

commbustibleOrderLine()

class combustibleOrder(osv.Model):
    _name = 'combustible.order'    
    _STATES = [('draft','Borrador'),('aprobado','Aprobado')]
    _order='name desc'

    def _check_line(self, cr, uid, ids):
        result = False
        for obj in self.browse(cr, uid, ids):
            if obj.line_ids:
                result = True
        return result
    
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            if formulario.state=='aprobado':
                raise osv.except_osv('Error', 'No pueden eliminar Órdenes de combustible aprobadas')
        return False

    def create(self, cr, uid, vals, context):
        obj_sequence = self.pool.get('ir.sequence')
        vals['ref'] = obj_sequence.get(cr, uid, 'combustible.order')       
        product_product = self.pool.get('product.product')
        aux=0 
        for this in vals['line_ids']:            
            prod=product_product.browse(cr,uid,this[2]['name'])
            if this[2]['qty']>0:                
                sub_total=prod.list_price*this[2]['qty']
                aux += sub_total                    
                vals['total'] = aux
            else:
                raise osv.except_osv('Error', 'Debe ingresar cantidad para el producto')                                                                        
        return super(combustibleOrder, self).create(cr, uid, vals, context=None)

    def combustible_aprobar(self, cr, uid, ids, *args):
        comb_obj = self.pool.get('combustible.order')
        for this in self.browse(cr, uid, ids):
            comb_obj.write(cr, uid, this.id,{
                    'state' : 'aprobado',
                    })
        return True

    def _amount_total(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                aux += line.sub_total
        res[this.id] = aux
        return res
    
    def validar_tiempo(self, cr, uid, ids, fecha1,context=None):
        res_value = {}        
        if fecha1:
            time_fecha1 = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_fecha1 = time_fecha1.replace(second=00)
            res_value['name']=str(time_fecha1)                    
        return {'value':res_value}
        
    _columns = dict(
        name = fields.datetime('Fecha',required=True),
        ref = fields.char('Número',size=20,readonly=True),
        project_id = fields.many2one('project.project','Proyecto',required=True),
        vehiculo_id = fields.many2one('vehicle.vehicle','Vehículo',required=True),
        observaciones = fields.text('Observaciones'),
        line_ids = fields.one2many('combustible.order.line','combustible_id','Detalle'),
        state = fields.selection(_STATES,'Estado',readonly=True),        
        total = fields.float('Total ($)',readonly=True),
        )
    
    _defaults = dict(
        state = 'draft',
        name = time.strftime('%Y-%m-%d %H:%M:%S'),
        )
    _constraints = [
        (_check_line,'Verifique que la órden de combustible tenga al menos tenga un producto',['line_ids']),
        ] 

combustibleOrder()

