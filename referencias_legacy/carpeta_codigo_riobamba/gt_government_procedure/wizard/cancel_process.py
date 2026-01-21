# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

import time
from osv import fields, osv

class cancelProcess(osv.TransientModel):

    _name = "cancel.process"

    _columns = dict(
        name = fields.char('Observaciones', size=256,required=True),
        )

    def cancel_process(self, cr, uid, ids, context=None):
        active_id = context['active_id']
        req_obj = self.pool.get('purchase.requisition')
        order_obj = self.pool.get('purchase.order')
        budget_obj = self.pool.get('budget.certificate')
        req = req_obj.browse(cr, uid, active_id)
        this = self.browse(cr, uid, ids[0])
        obs = this.name
        req_obj.write(cr, uid, req.id,{'observation':obs,
                                       'state':'cancel',
                                       'anulant_id':uid,
                                       })
        #anula las ordenes de compra
        if req.purchase_select_ids:
            for oc_line in req.purchase_select_ids:
                order_obj.write(cr, uid, oc_line.id,{'state':'cancel'})
        budget_obj.write(cr, 1, req.presp_ref.id, {'is_lock':False})
        req_obj._generate_log(cr, uid, active_id,'X Anulada')
        return {'type': 'ir.actions.act_window_close'}

cancelProcess()

class finalizaProcess(osv.TransientModel):

    _name = "finaliza.process"

    _columns = dict(
        name = fields.char('Observaciones', size=256,required=True),
        )

    def finaliza_process(self, cr, uid, ids, context=None):
        active_id = context['active_id']
        req_obj = self.pool.get('purchase.requisition')
        req = req_obj.browse(cr, uid, active_id)
        this = self.browse(cr, uid, ids[0])
        obs = this.name
        req_obj.write(cr, uid, req.id,{'observation':obs,
                                       'state':'done',
                                       })
        req_obj._generate_log(cr, uid, active_id,'Finalizada')
        return {'type': 'ir.actions.act_window_close'}

finalizaProcess()
