# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################
from osv import osv, fields
from tools import ustr

class wizardCambiarConcepto(osv.TransientModel):
    _inherit = 'wizard.cambia.concepto'
    _columns = dict(
        name = fields.many2one('spi.concepto','Nuevo Concepto'),
    )

    def cambiaConceptoSpi(self, cr, uid, ids, context):
        line_obj = self.pool.get('spi.line')
        spi_obj = self.pool.get('account.spi.voucher')
        for this in self.browse(cr, uid, ids):
            line_ids = line_obj.search(cr, uid, [('spi_id','=',context['active_id'])])
            if line_ids:
                line_obj.write(cr, uid, line_ids,{
                    'concepto_id':this.name.id,
                })
        return {'type':'ir.actions.act_window_close' }

wizardCambiarConcepto()
