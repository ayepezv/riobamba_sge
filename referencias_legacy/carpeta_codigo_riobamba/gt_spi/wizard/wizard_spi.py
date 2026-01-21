# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################
from osv import osv, fields
from tools import ustr

class wizardCambiarConcepto(osv.TransientModel):
    _name = 'wizard.cambia.concepto'
    _columns = dict(
        name = fields.char('Nuevo Codigo', size=10),
    )

    def cambiaConceptoSpi(self, cr, uid, ids, context):
        line_obj = self.pool.get('spi.line')
        spi_obj = self.pool.get('account.spi.voucher')
        for this in self.browse(cr, uid, ids):
            line_ids = line_obj.search(cr, uid, [('spi_id','=',context['active_id'])])
            if line_ids:
                line_obj.write(cr, uid, line_ids,{
                    'ref':this.name,
                })
        return {'type':'ir.actions.act_window_close' }

wizardCambiarConcepto()

class wizardNoMove(osv.TransientModel):
    _name = 'wizard.no.move'
    _columns = dict(
        name = fields.many2one('account.move','Comprobante'),
    )

    def loadMoveSpi(self, cr, uid, ids, context):
        move_obj = self.pool.get('account.move')
        for this in self.browse(cr, uid, ids):
            move_obj.write(cr, uid, [this.name.id],{'is_pay':False})
        return {'type':'ir.actions.act_window_close' }

wizardNoMove()
