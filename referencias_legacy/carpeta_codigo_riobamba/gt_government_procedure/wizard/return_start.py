# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

import time
from osv import fields, osv

class returnStart(osv.TransientModel):

    _name = "return.start"

    _columns = dict(
        name = fields.char('Observaciones', size=256,required=True),
        )

    def create_incident_start(self, cr, uid, ids, context=None):
        log_obj = self.pool.get('requisition.log')
        active_id = context['active_id']
        req_obj = self.pool.get('purchase.requisition')
        req = req_obj.browse(cr, uid, active_id)
        for this in self.browse(cr, uid, ids):
            obs = this.name
        req_obj.write(cr, uid, req.id,{'observation':obs,
                                       'revert':True,
                                       'state':'draft'})
        str_2 = '<--Devuelto Inicio' + ' ' + 'Borrador' + ' - ' + obs
        log_obj.create(cr, uid, {
            'name':uid,
            'action':'Borrador',
            'req_log_id':req.id,
            'desc':str_2,
            'date':time.strftime('%Y-%m-%d %H:%M:%S')  
        })
        return {'type': 'ir.actions.act_window_close'}

returnStart()
