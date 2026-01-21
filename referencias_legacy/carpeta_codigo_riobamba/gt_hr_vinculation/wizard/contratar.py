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

class contratarLine(osv.TransientModel):
    _name = 'contratar.line'
    _columns = dict(
        c_id = fields.many2one('contratar','Proceso'),
        job_id = fields.many2one('hr.job',readonly=True),
        select = fields.boolean('Seleccionado'),
        )
contratarLine()

class contratar(osv.TransientModel):
    _name = "contratar"

    def _jobs(self, cr, uid, job):
        job_ = {
            'c_id' : job.id,
            'job_id' : job.job_id.id,
        }
        return job_

    def default_get(self, cr, uid, fields, context=None):
        vinc_obj = self.pool.get('hr.vinculation')
        if context is None: context = {}
        res = super(contratar, self).default_get(cr, uid, fields, context=context)
        vinculation_ids = context.get('active_ids', [])
        vinculation_id, = vinculation_ids 
#        for this in self.browse(cr, uid, parent_ids):            
        solicitud = self.pool.get('hr.vinculation').browse(cr, uid, vinculation_id)
            #sacar los puestos de la solicitud
        if solicitud.has_sol:
                #tiene solicitud
            jobs = [self._jobs(cr, uid, m) for m in solicitud.solicitud_id.job_ids]
            res.update(line_ids=jobs)
        else:
            print "VELE"
                #sacar los jobs disponibles
        return res

    _columns = dict(
        line_ids = fields.one2many('contratar.line','c_id','Cargos/Puestos de trabajo'),
        )

    def contratar(self, cr, uid, ids, context=None):
        print "CONTRATADO"
        return {'type': 'ir.actions.act_window_close'}

contratar()
