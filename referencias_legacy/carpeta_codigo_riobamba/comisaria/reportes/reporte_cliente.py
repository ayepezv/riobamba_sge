
from report import report_sxw
from osv import osv

class reportes_clientes(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(reportes_clientes, self).__init__(cr, uid, name, context)

		

class reporte_clientes(osv.AbstractModel):
    _name="report.comisaria.comisaria_cliente"
    _inherit = "report.abstract_report"
    _template="comisaria.comisaria_cliente"
    _wrapped_report_class=reportes_clientes






