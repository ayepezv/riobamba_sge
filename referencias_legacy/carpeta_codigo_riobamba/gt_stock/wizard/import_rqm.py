# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

import netsvc

from osv import fields, osv

class import_rqm(osv.TransientModel):
    _name = 'import.rqm'
    
    _columns = {
        'rqm_id': fields.many2one('stock.requisition', 'Requerimiento', required=True),
    }

    def import_rqm(self, cr, uid, ids, context=None):
        pick_obj = self.pool.get('stock.picking')
        move_line_obj = self.pool.get('stock.move')
        location_obj = self.pool.get('stock.location')
        for this in self.browse(cr, uid, ids):
            picking_id = context and context.get('active_id', False) or False
            picking = pick_obj.browse(cr, uid, picking_id)
            if picking.state!='draft' or picking.type!='out':
                raise osv.except_osv(('Error de usuario!'), ('Este asistente es solo para egresos o documentos aun no procesados'))
            for line in this.rqm_id.move_lines:
                location_ids = location_obj.search(cr, uid, [('usage','=','customer')],limit=1)
                if not location_ids:
                    raise osv.except_osv(('Error de configuración'), ('No tiene una ubicación tipo cliente definida, configure una por favor'))
                move_id = move_line_obj.create(cr, uid, {
                    'name':line.product_id.name,
#                    'date':picking.document_date,
#                    'date_expected':picking.date_done,
                    'product_id':line.product_id.id,
                    'product_qty':line.qty,
                    'product_uom':line.uom_id.id,
                    'product_uos':line.uom_id.id,
                    'location_id':picking.bodega_id.id,
                    'location_dest_id':location_ids[0],
                    'picking_id':picking.id,
                })
                pick_obj.write(cr, uid, picking.id,{
                    'number':this.rqm_id.name,
                })
        return {'type':'ir.actions.act_window_close' }


import_rqm()


