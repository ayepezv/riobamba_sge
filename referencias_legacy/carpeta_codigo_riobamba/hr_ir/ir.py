# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from time import strftime, strptime
import base64
import xlrd
from XLSWriter import XLSWriter

from osv import osv, fields

class i_renta_line(osv.Model):
   _name = 'i.renta.line'
   _columns = dict(
      r_id = fields.many2one('i.renta','Renta'),
      employee_id = fields.many2one('hr.contract','Funcionario'),
      rmu = fields.float('RMU'),
      meses = fields.integer('Meses'),
      total_rmu = fields.float('Total RMU'),
      iess = fields.float('Aporte Personal'),
      deducciones = fields.float('Deduccciones'),
      total_deducible = fields.float('Total Deducible'),
      base_imponible = fields.float('Base Imponible'),
      renta_anual = fields.float('Renta Anual'),
      renta_mensual = fields.float('Renta Mensual'),
   )
   _defaults = dict(
      meses = 12,
   )

i_renta_line()

class i_renta(osv.Model):
   _name = 'i.renta'
   _columns = dict(
      year_id = fields.many2one('account.fiscalyear','Periodo'),
      line_ids = fields.one2many('i.renta.line','r_id','Detalle'),
   )

i_renta()
