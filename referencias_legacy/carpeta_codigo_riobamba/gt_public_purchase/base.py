# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Gnuthink Software Labs Cia. Ltda.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class purchaseValueLine(osv.Model):
    _name = 'purchase.value.line'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = ""
            if record.objeto:
                name = record.objeto.name + ' - ' + record.name.name + ' (' + str(record.desde) + '-' + str(record.hasta) + ')'
            res.append((record.id, name))
        return res

    _OBJ_CONTRACT = [('b','Bienes'),('s','Servicios'),('bienes','Bienes y Servicios'),
                     ('obras','Obras'),('consultoria','Consultoría')]

    _columns = dict(
        p_id = fields.many2one('purchase.config','Configuración'),
        name = fields.many2one('purchase.contract.type','Tipo Compra',required=True),
        desde = fields.float('Monto Desde'),
        hasta = fields.float('Monto Hasta'),
        )
purchaseValueLine()

class purchaseConfig(osv.Model):
    _name = 'purchase.config'
    _description = 'Configuración'

    _columns = dict(
        name = fields.many2one('account.fiscalyear','Periodo Fiscal Contable',required=True),
        line_ids = fields.one2many('purchase.value.line','p_id','Tipos de procesos'),
        activo = fields.boolean('Activa'),
        )
    
    _sql_constraints=[
        ('unique_activo','unique(activo)','Debe tener una tabla activa')
        ]

purchaseConfig()
