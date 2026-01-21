# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################
from openerp.osv import osv, fields
from openerp.addons.edi import EDIMixin
from openerp.tools.translate import _

from werkzeug import url_encode

HR_PAYSLIP_EDI_STRUCT = {
    'name': True,
    'company_id': True, # -> to be changed into partner
    'date_from': True,
    'date_to': True,
    'period_id': True,
    'employee_id': True,
    'net': True,
    'user_id': True,
}

class hr_payslipEdi(osv.osv, EDIMixin):
    _inherit = 'hr.payslip'

    def edi_export(self, cr, uid, records, edi_struct=None, context=None):
        """Exports a payroll"""
        edi_struct = dict(edi_struct or HR_PAYSLIP_EDI_STRUCT)
        res_company = self.pool.get('res.company')
        employee_obj = self.pool.get('hr.employee')
        edi_doc_list = []
        for rol in records:
            # generate the main report
            self._edi_generate_report_attachment(cr, uid, order, context=context)

            # Get EDI doc based on struct. The result will also contain all metadata fields and attachments.
            edi_doc = super(hr_payslipEdi,self).edi_export(cr, uid, [rol], edi_struct, context)[0]
            edi_doc.update({
                    'company_address': res_company.edi_export_address(cr, uid, order.company_id, context=context),
                    'notes': partner.number or False,
            })
            edi_doc_list.append(edi_doc)
        return edi_doc_list
