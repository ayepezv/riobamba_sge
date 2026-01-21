# -*- coding: utf-8 -*-
import time
from report import report_sxw


class ReportConsolidate(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportConsolidate, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'process_data': self.process_data
        })

    def process_data(self, data):
        invoices = self.pool.get('account.invoice').browse(self.cr, self.uid, data['invoices'])
        data = []
        datas = {}
        for inv in invoices:
            if not datas.get(inv.partner_id.id):
                datas.update({inv.partner_id.id: {'docs': [],
                                                    'total': 0,
                                                    'type': 'FACT:',
                                                    'partner': inv.partner_id.name }})
            datas[inv.partner_id.id]['total'] += inv.residual
            datas[inv.partner_id.id]['docs'].append(inv)
        for k, v in datas.items():
            data.append(v)
        return data

report_sxw.report_sxw('report.document_consolidate1_report',
                       'document.report.consolidate',
                       'addons/gt_reports_gpa/report/doc_report_consol.mako',
                       parser=ReportConsolidate, header=True)
