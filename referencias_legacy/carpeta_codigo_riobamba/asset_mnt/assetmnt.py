# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################
import time
from time import strftime, strptime
from osv import osv, fields

class assetMnt(osv.Model):
    _name = 'asset.mnt'
    _order = 'date_ingreso desc,name desc'
    _description = 'Mantenimiento activos'
    _columns = dict(
        name = fields.char('Codigo',size=10),
        asset_id = fields.many2one('account.asset.asset','Activo',required=True),
        date_ingreso = fields.date('Fecha Recepcion'),
        observaciones = fields.text('Observaciones'),
        state = fields.selection([('Receptado','Receptado'),('Mantenimiento','Mantenimiento'),
                                  ('Finalizado','Finalizado')],'Estado'),
        entrega_id = fields.many2one('hr.employee','Entregado por:',required=True),
        responsable_id = fields.many2one('hr.employee','Responsable Mantenimiento',required=True),
    )
    _defaults = dict(
        name = '/',
        date_ingreso = time.strftime('%Y-%m-%d')
    )
assetMnt()    
