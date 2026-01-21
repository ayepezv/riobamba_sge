import time
from report import report_sxw
from osv import osv
from gt_tool import amount_to_text_ec


class payment_request_report(report_sxw.rml_parse):
     
    def __init__(self, cr, uid, name, context):
        super(payment_request_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            '_get_letras':self._get_letras,
        })          
      
    def _get_letras(self, valor):
        letra = amount_to_text_ec.amount_to_text_ec(valor)
        return letra
                         
report_sxw.report_sxw('report.payment_request',
                       'payment.request', 
                       'gt_payment_request/report/report_payment_request.mako',
                       parser=payment_request_report, header="True")

