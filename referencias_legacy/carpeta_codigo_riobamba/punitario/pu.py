# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from time import strftime, strptime

from osv import osv, fields

class unitarioProducto(osv.Model):
    _inherit = 'product.product'
    _columns = dict(
        is_unitario = fields.boolean('Analisis Costos Unitarios',help='Si marca este campo el bien o servicio se habilita para el calculo de precios unitarios'),
    )
unitarioProducto()

class unitarioRubroLinea(osv.Model):
    _name = 'unitario.rubro.linea'
    _columns = dict(
        a_id = fields.many2one('unitario.actividad','Actividad'),
        product_id = fields.many2one('product.product','Rubro'),
        unidad_id = fields.many2one('product.uom','Unidad de medida'),
        cantidad = fields.float('Cantidad'),
        precio_unitario = fields.float('Precio Unitario'),
    )
unitarioRubroLinea()

class unitarioActividad(osv.Model):
    _name = 'unitario.actividad'
    _columns = dict(
        p_id = fields.manyone('unitario.obra.presupuesto','Proyecto'),
        name = fields.char('Nombre Actividad',size=128),
        detalle_ids = fields.one2many('unitario.rubro.linea','a_id','Detalle Rubros'),
    )
unitarioActividad()

class unitarioObraPresupuesto(osv.Model):
    _name = 'unitario.obra.presupuesto'
    _columns = dict(
        obra_id = fields.many2one('obra.obra','Obra Relacionada',required=True),
        name = fields.char('Codigo Presupuesto',size=10),
        partner_id = fields.many2one('res.partner','Institucion Beneficiaria',required=True),
        oferente_id = fields.many2one('res.partner','Oferente',required=True),
        porcentaje_indirecto = fields.float('Porcentaje Costo Indirecto'),
        elaborado_por = fields.many2one('res.users','Elaborado por'),
        fecha = fields.date('Fecha'),
        obra_ids = fields.one2many('unitario.actividad','p_id','Detalle Actividades'),
    )
unitarioObraPresupuesto()
