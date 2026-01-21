# -*- coding: utf-8 -*-
##############################################################################
#    
# Mario Chogllo
#
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler

class requisitionCuadro(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(requisitionCuadro, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_solicitud_value':self.get_solicitud_value,
            'get_select':self.get_select,
            'get_in_stock':self.get_in_stock,
        })

    def get_in_stock(self, po):
        aux = 'No'
        if po.in_stock:
            aux = 'Si'
        return aux

    def get_select(self, po):
        aux = ''
        if po.select_item:
            aux = 'Seleccionada'
        return aux

    def get_solicitud_value(self, order, linea, desc, position):
        aux = ''
        descripcion = ''
        aux_desc = ''
        purchase_line_obj = self.pool.get('purchase.order.line')
        ids = order.purchase_ids[0:3]
        aux = '0'
        if ids[position]:
            if linea.product_id:
                line_oc_ids = purchase_line_obj.search(self.cr, self.uid, [('order_id','=',ids[position].id),('product_id','=',linea.product_id.id)],limit=1)
                if not line_oc_ids:
                    if linea.product_id.code:
                        if linea.desc:
                            descripcion = '[' + linea.product_id.code + '] ' + linea.product_id.name + ' ' + linea.desc
                        else:
                            descripcion = '[' + linea.product_id.code + '] ' + linea.product_id.name + ' ' 
                    elif linea.desc:
                        descripcion = linea.product_id.name[0:256] + ' ' + linea.desc
                        aux_desc = linea.desc
                    else:
                        descripcion = linea.product_id.name[0:256] + ' '
                    line_oc_ids = purchase_line_obj.search(self.cr, self.uid, [('order_id','=',ids[position].id),('name','in',[descripcion,aux_desc])],limit=1)
            else:
                if linea.desc:
                    descripcion = linea.desc 
                    aux_desc = linea.desc
                    descripcion = descripcion[:256]
                    line_oc_ids = purchase_line_obj.search(self.cr, self.uid, [('order_id','=',ids[position].id),('name','in',[descripcion,aux_desc])],limit=1)
            if line_oc_ids:
                purchase_line = purchase_line_obj.browse(self.cr, self.uid, line_oc_ids[0])
                total = purchase_line.price_subtotal + purchase_line.amount_tax
                aux = str(purchase_line.price_subtotal) + '+' + str(purchase_line.amount_tax) +' IMP' + ' = ' + str(total) 
        return aux
   
report_sxw.report_sxw('report.purchase.req.cuadro','purchase.requisition','addons/gt_government_procedure/report/cuadro.rml',parser=requisitionCuadro)

class requisitionCuadro5(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(requisitionCuadro5, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_solicitud_value_mk':self.get_solicitud_value_mk,
            'get_select_mk':self.get_select_mk,
            'get_in_stock_mk':self.get_in_stock_mk,
        })

    def get_in_stock_mk(self, po):
        aux = 'No'
        if po.in_stock:
            aux = 'Si'
        return aux

    def get_select_mk(self, po):
        aux = ''
        if po.select_item:
            aux = 'Seleccionada'
        return aux

    def get_solicitud_value_mk(self, order, linea, desc, position):
        aux = ''
        descripcion = ''
        aux_desc = ''
        purchase_line_obj = self.pool.get('purchase.order.line')
        ids = order.purchase_ids[0:5]
        aux = '0'
        if ids[position]:
            if linea.product_id:
                line_oc_ids = purchase_line_obj.search(self.cr, self.uid, [('order_id','=',ids[position].id),('product_id','=',linea.product_id.id)],limit=1)
                if not line_oc_ids:
                    if linea.product_id.code:
                        if linea.desc:
                            descripcion = '[' + linea.product_id.code + '] ' + linea.product_id.name + ' ' + linea.desc
                        else:
                            descripcion = '[' + linea.product_id.code + '] ' + linea.product_id.name + ' ' 
                    elif linea.desc:
                        descripcion = linea.product_id.name[0:256] + ' ' + linea.desc
                        aux_desc = linea.desc
                    else:
                        descripcion = linea.product_id.name[0:256] + ' '
                    line_oc_ids = purchase_line_obj.search(self.cr, self.uid, [('order_id','=',ids[position].id),('name','in',[descripcion,aux_desc])],limit=1)
            else:
                if linea.desc:
                    descripcion = linea.desc 
                    aux_desc = linea.desc
                    descripcion = descripcion[:256]
                    line_oc_ids = purchase_line_obj.search(self.cr, self.uid, [('order_id','=',ids[position].id),('name','in',[descripcion,aux_desc])],limit=1)
            if line_oc_ids:
                purchase_line = purchase_line_obj.browse(self.cr, self.uid, line_oc_ids[0])
                total = purchase_line.price_subtotal + purchase_line.amount_tax
                aux = str(purchase_line.price_subtotal) + '+' + str(purchase_line.amount_tax) +' IMP' + ' = ' + str(total) 
        return aux
   
report_sxw.report_sxw('report.purchase.req.cuadro5','purchase.requisition','addons/gt_government_procedure/report/cuadro5.mako',parser=requisitionCuadro5)

class requisitionCuadroAut5(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(requisitionCuadroAut5, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_solicitud_value_mk':self.get_solicitud_value_mk,
            'get_select_mk':self.get_select_mk,
            'get_in_stock_mk':self.get_in_stock_mk,
        })

    def get_in_stock_mk(self, po):
        aux = 'No'
        if po.in_stock:
            aux = 'Si'
        return aux

    def get_select_mk(self, po):
        aux = ''
        if po.select_item:
            aux = 'Seleccionada'
        return aux

    def get_solicitud_value_mk(self, order, linea, desc, position):
        aux = ''
        descripcion = ''
        aux_desc = ''
        purchase_line_obj = self.pool.get('purchase.order.line')
        ids = order.purchase_ids[0:5]
        aux = '0'
        if ids[position]:
            if linea.product_id:
                line_oc_ids = purchase_line_obj.search(self.cr, self.uid, [('order_id','=',ids[position].id),('product_id','=',linea.product_id.id)],limit=1)
                if not line_oc_ids:
                    if linea.product_id.code:
                        if linea.desc:
                            descripcion = '[' + linea.product_id.code + '] ' + linea.product_id.name + ' ' + linea.desc
                        else:
                            descripcion = '[' + linea.product_id.code + '] ' + linea.product_id.name + ' ' 
                    elif linea.desc:
                        descripcion = linea.product_id.name[0:256] + ' ' + linea.desc
                        aux_desc = linea.desc
                    else:
                        descripcion = linea.product_id.name[0:256] + ' '
                    line_oc_ids = purchase_line_obj.search(self.cr, self.uid, [('order_id','=',ids[position].id),('name','in',[descripcion,aux_desc])],limit=1)
            else:
                if linea.desc:
                    descripcion = linea.desc 
                    aux_desc = linea.desc
                    descripcion = descripcion[:256]
                    line_oc_ids = purchase_line_obj.search(self.cr, self.uid, [('order_id','=',ids[position].id),('name','in',[descripcion,aux_desc])],limit=1)
            if line_oc_ids:
                purchase_line = purchase_line_obj.browse(self.cr, self.uid, line_oc_ids[0])
                total = purchase_line.price_subtotal + purchase_line.amount_tax
                aux = str(purchase_line.price_subtotal) + '+' + str(purchase_line.amount_tax) +' IMP' + ' = ' + str(total) 
        return aux
   
report_sxw.report_sxw('report.purchase.req.cuadroAut5','purchase.requisition','addons/gt_government_procedure/report/cuadro_aut5.mako',parser=requisitionCuadroAut5)
