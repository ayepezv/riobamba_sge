import time
from report import report_sxw

class saldoProducto(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(saldoProducto, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.saldo.producto',
                       'report.saldo.producto', 
                       'addons/gt_stock/report/saldo_producto.mako',
                       parser=saldoProducto)

class saldoProductoDate(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(saldoProductoDate, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.saldo.product.date',
                       'report.saldo.product.date', 
                       'addons/gt_stock/report/saldo_producto_date.mako',
                       parser=saldoProductoDate)

class saldoProductoRml(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(saldoProductoRml, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_total_saldo':self.get_total_saldo,
        })

    def get_total_saldo(self, lines):
        aux_suma = 0 
        for line in lines:
            aux_suma += line.total
        return aux_suma
   
report_sxw.report_sxw('report.saldo.product.rml','report.saldo.product','addons/gt_stock/report/saldo_producto.rml',parser=saldoProductoRml,header=False)


class egresoRml(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(egresoRml, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_total_egreso':self.get_total_egreso,
        })

    def get_total_egreso(self, lines):
        aux_suma = 0 
        for line in lines:
            aux_suma += line.total
        return aux_suma
   
report_sxw.report_sxw('report.egreso.rml','report.egresos','addons/gt_stock/report/egresos.rml',parser=egresoRml,header=False)


class ingresoRml(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ingresoRml, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_ingresos':self.get_ingresos,
        })

    def get_ingresos(self, o):
        picking_obj = self.pool.get('stock.picking')
        picking_ids = picking_obj.search(self.cr, self.uid, [('state','=','done'),('type','=','in'),('date','>=',o.date_start),('date','<=',o.date_end)])
        aux = []
        for pick_id in picking_ids:
            picking = picking_obj.browse(self.cr, self.uid, pick_id)
            aux.append(picking)
        return aux
   
report_sxw.report_sxw('report.ingreso.rml','report.ingresos','addons/gt_stock/report/ingresos.rml',parser=ingresoRml,header=False)
