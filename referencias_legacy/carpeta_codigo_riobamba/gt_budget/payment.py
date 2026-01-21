# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from osv import osv, fields

class paymentRequestBudget(osv.Model):
    _inherit = "payment.request"

    _columns = dict(
        certificate_id = fields.many2one('budget.certificate','Certificacion Presupuestaria'),
    )
    
paymentRequestBudget()
