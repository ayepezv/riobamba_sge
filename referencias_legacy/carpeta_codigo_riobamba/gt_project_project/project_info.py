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

__author__ = 'Cristian Salamea'

import time
import logging

from osv import osv, fields
from tools.translate import _


class ProjectBuildProgram(osv.Model):
    _name = 'project.build.program'
    _columns= {
        'name': fields.char('Nombre', size=64, required=True),
        }
    _sql_constraints = [('unique_name','unique(name)', u'El nombre debe ser único.')]


class ProjectBuildType(osv.Model):
    _name = 'project.build.type'
    _columns = {
        'name': fields.char('Nombre', size=64, required=True),
        'program_id': fields.many2one('project.build.program', 'Programa', required=True),
        }
    _sql_constraints = [('unique_name','unique(name)', u'El nombre debe ser único.')]


class ProjectBuildIndole(osv.Model):
    _name = 'project.build.indole'
    _columns = {
        'name': fields.char('Nombre', size=64, required=True),
        }
    _sql_constraints = [('unique_name','unique(name)', u'El nombre debe ser único.')]


class ProjectBuildMode(osv.Model):
    _name = 'project.build.mode'
    _columns = {
        'name': fields.char('Nombre', size=64, required=True),
        }
    _sql_constraints = [('unique_name','unique(name)', u'El nombre debe ser único.')]

