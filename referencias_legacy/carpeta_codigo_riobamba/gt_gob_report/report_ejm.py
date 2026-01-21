# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from osv import osv, fields

class ejmReport(osv.Model):
    _name = 'ejm.report'
    _columns = dict(
        name = fields.char('Nombre',size=2),
        )
ejmReport()
