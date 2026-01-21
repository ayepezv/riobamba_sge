# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP SA (<http://openerp.com>).
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

import time
from osv import fields, osv

class returnState(osv.TransientModel):

    _name = "return.state"

    _columns = dict(
        name = fields.char('Observaciones', size=256,required=True),
        )

    def create_incident(self, cr, uid, ids, context=None):
        active_id = context['active_id']
        req_obj = self.pool.get('purchase.requisition')
        po_obj = self.pool.get('purchase.order')
        req = req_obj.browse(cr, uid, active_id)
        this = self.browse(cr, uid, ids[0])
        state = req.state
        obs = this.name
        req_obj.write(cr, uid, req.id,{'observation':obs,
                                       'revert':True})
        str_aux = ''
        if state=='comprometed':
            req_obj.write(cr, uid, req.id,{'state':'select'})
            req_obj._generate_log(cr, uid, active_id,'<-- Seleccionada')
            str_aux = 'Seleccionar'
        elif state=='select':
            req_obj.write(cr, uid, req.id,{'state':'recomended'})
            req_obj._generate_log(cr, uid, ids[0],'<-- Recomendada')
            str_aux = 'Recomendar'
        elif state=='recomended':
            #aqui se debe borrar todas la cotizaciones select
            for line in req.purchase_select_ids:
                po_obj.unlink(cr, uid, [line.id])
            req_obj.write(cr, uid, req.id,{'state':'aproved'})
            req_obj._generate_log(cr, uid, active_id,'<-- Aprobar')
            str_aux = 'Borrador'
        elif state=='aproved':
            req_obj.write(cr, uid, req.id,{'state':'in_progress'})
            req_obj._generate_log(cr, uid, active_id,'<-- Sol. Ingresada')
            str_aux = 'Sol. Ingresada'
        else: #state=='in_progress':
            req_obj.write(cr, uid, req.id,{'state':'draft'})
            req_obj._generate_log(cr, uid, active_id,'<-- Borrador')
            str_aux = 'Borrador'
        str_2 = '<--Devuelto' + ' ' + str_aux
        return {'type': 'ir.actions.act_window_close'}

returnState()
