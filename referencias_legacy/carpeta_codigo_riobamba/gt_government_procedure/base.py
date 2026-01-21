# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import osv, fields

class purchase_config_infima(osv.Model):
    _name = 'purchase.config.infima'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = ""
            if record:
                name = record.name.name
            res.append((record.id, name))
        return res

    _columns = dict(
        monto_maximo = fields.float('Monto Máx. Infima',required=True),
        monto_maximo_menor = fields.float('Monto Máx. Menor Cuantia',required=True),
        name = fields.many2one('account.fiscalyear','Periodo Fiscal Contable',required=True),
        activo = fields.boolean('Activa'),
        )

    _sql_constraints=[
        ('unique_activo','unique(activo)','Debe tener una tabla activa')
        ]
purchase_config_infima()

