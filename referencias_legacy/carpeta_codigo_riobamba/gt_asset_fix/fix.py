# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################
import time
from tools import ustr
from osv import fields, osv


class assetFix(osv.Model):
    _name='asset.fix'
    _description = 'Mantenimiento Activos'
    _columns = dict(
        name = fields.char('Codigo',size=10,required=True),
        asset_id = fields.many2one('account.asset.asset','Activo',required=True),
        desc = fields.text('Descripcion'),
        state = fields.selection([('Borrador','Borrador'),('Revision','Revision'),('Reparado','Reparado'),('Para Baja','Para Baja')],'Estado'),
    )

assetFix()
