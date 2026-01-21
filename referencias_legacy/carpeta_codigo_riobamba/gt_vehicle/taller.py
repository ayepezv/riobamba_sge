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

class repairTaller(osv.Model):
    _name = 'repair.taller'

    _STATE = [('No Operativo','No Operativo'),('Operativo','Operativo'),('Reparacion','Reparacion')]
    _TYPE_TALLER = [('Publico','Publico'),('Privado','Privado')]

    _columns = dict(
        type_taller = fields.selection(_TYPE_TALLER,'Tipo'),
        state = fields.selection(_STATE,'Estado'),
        name = fields.char('Nombre',size=32,required=True),
        jefe_id = fields.many2one('hr.employee','Jefe/Responsable',required=True),
        capacity = fields.integer('Capacidad'),
        state_id = fields.many2one('res.country.state','Provincia'),
        canton_id = fields.many2one('res.country.state.canton','Canton'),
        parish_id = fields.many2one('res.country.state.parish','Parroquia'),
        direccion = fields.char('Calles',size=256,required=True),
        )
    _defaults = dict(
        state = 'Operativo',
        )
repairTaller()

class repairOrderLine(osv.Model):
    _name = 'repair.order.line'

    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            if not formulario.order_id.state=='draft':
                raise osv.except_osv('Error', 'No pueden eliminar detalle de ordenes de reparación')
        return False

    _columns = dict(
        name = fields.many2one('product.product','Repuesto',required=True),
        qty = fields.integer('Cantidad'),
        in_order = fields.boolean('Solicitar Compra'),
        order_id = fields.many2one('repair.order','Orden Reparación'),
        )


class repairOrder(osv.Model):
    _name = 'repair.order'
    _description = 'Órdenes Reparación'
    _order='name desc'
    _STATE = [('solicitada','Solicitado'),('proceso','Proceso'),('terminada','Terminado')]
    
    def unlink(self, cr, uid, ids, context=None):
        for formulario in self.browse(cr, uid, ids, context):
            if not formulario.state=='draft':
                raise osv.except_osv('Error', 'Solo pueden eliminar ordenes de reparación en borrador')
        return False

    def repair_create_sc(self, cr, uid, ids, *args):
        purchase_req_obj = self.pool.get('purchase.requisition')
        purchase_req_line_obj = self.pool.get('purchase.requisition.line')
        for this in self.browse(cr, uid, ids):
            p_req = purchase_req_obj.create(cr, uid, {
                    'origin' :this.ref,
                    'user_id':uid,
                    'description':this.description,
                    })
            for line in this.product_ids:
                if line.in_order==True:
                    purchase_req_line_obj.create(cr, uid, {
                        'product_id':line.name.id,
                        'product_qty':line.qty,
                        'requisition_id':p_req,
                        })
        return True

    def repair_proceso(self, cr, uid, ids, *args):
        mov_obj = self.pool.get('repair.order')
        stock_picking_obj = self.pool.get('stock.picking')
        stock_move_obj = self.pool.get('stock.move')
        
        for this in self.browse(cr, uid, ids):
            mov_obj.write(cr, uid, this.id,{
                    'state' : 'proceso',
                    })
       #     picking_id = stock_picking_obj.create(cr, uid, {
        #            'name' : this.ref,
         #           'origin' : this.ref,
         #          'solicitant_id':this.solicitant_id.id,
          #          })
          #  for line in this.product_ids:
          #     stock_move_obj.create(cr, uid, {
          #                  'name':'repuesto',
          #                  'date':this.date_start,
          #                  'date_expected':this.date_start,
          #                  'product_id':line.name.id,
          #                  'product_qty':line.qty,
          #                  'product_uom':line.name.uom_id.id,
          #                  'location_id':1,
          #                  'location_dest_id':1,
          #                  'picking_id':picking_id,
          #                  })
        return True

    def repair_terminado(self, cr, uid, ids, *args):
        mov_obj = self.pool.get('repair.order')
        for this in self.browse(cr, uid, ids):
            mov_obj.write(cr, uid, this.id,{
                    'state' : 'terminada',
                    })
        return True

    def create(self, cr, uid, vals, context):
        obj_sequence = self.pool.get('ir.sequence')
        vals['ref'] = obj_sequence.get(cr, uid, 'repair.order')
        return super(repairOrder, self).create(cr, uid, vals, context=None)
    
    def validar_tiempo(self, cr, uid, ids, fecha1,context=None):
        res_value = {}        
        if fecha1:
            time_fecha1 = datetime.strptime(fecha1, "%Y-%m-%d %H:%M:%S")
            time_fecha1 = time_fecha1.replace(second=00)
            res_value['date_start']=str(time_fecha1)                    
        return {'value':res_value}

    _columns = dict(
        type_repair = fields.selection([('Preventivo','Preventivo'),('Correctivo','Correctivo')],'Tipo'),
        ref = fields.char('Número',size=8,readonly=True),
        name = fields.many2one('vehicle.vehicle','Vehículo',required=True),
        date_start = fields.datetime('Fecha Solicitud',required=True),
        description = fields.text('Observaciones',required=True),
        km_ingreso = fields.related('name','km', type='char',string='Km. Ingreso', store=True),
        project_id = fields.many2one('project.project','Proyecto',required=True),
        product_ids = fields.one2many('repair.order.line','order_id','Detalle Repuestos'),
        state = fields.selection(_STATE,'Estado'),
        taller_id = fields.many2one('repair.taller','Taller',required=True),
        solicitant_id = fields.many2one('hr.employee','Solicitado por'),
        )

    _defaults = dict(
        type_repair = 'Preventivo',
        state = 'solicitada',
        date_start = time.strftime('%Y-%m-%d %H:%M:%S'),
        )

