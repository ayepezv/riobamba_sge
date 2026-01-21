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

class flowConfig(osv.Model):
    _name = 'flow.config'
    _columns = dict(
        name = fields.char('Descripcion',size=32),
        fuentes_corrientes = fields.many2many('account.account','ft_acc_id',
                                              'Fuentes Corrientes'),
        usos_corrientes = fields.many2many('account.account','us_acc_id',
                                              'Fuentes Corrientes'),
        fuentes_capital = fields.many2many('account.account','ftcp_acc_id',
                                              'Fuentes Capital'),
        usos_produccion = fields.many2many('account.account','usp_acc_id',
                                              'Usos Produccion, Inversion y Capital'),
        fuentes_financiamiento = fields.many2many('account.account','ffinan_acc_id',
                                              'Fuentes Financiamiento'),
        usos_financiamiento = fields.many2many('account.account','ffinanus_acc_id',
                                              'Usos Financiamiento'),
        flujos_no_prep = fields.many2many('account.account','flnoprep_acc_id',
                                              'Flujos No Presupuestarios'),
        variaciones_no_prep = fields.many2many('account.account','vrnoprep_acc_id',
                                              'Variaciones No Presupuestarios'),
        )

flowConfig()

