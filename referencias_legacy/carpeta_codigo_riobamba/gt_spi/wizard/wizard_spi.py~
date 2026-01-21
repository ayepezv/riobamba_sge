# -*- coding: utf-8 -*-
##############################################################################
#
#    HHRR Module
#    Copyright (C) 2009 GnuThink Software  All Rights Reserved
#    info@gnuthink.com
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from XLSWriter import XLSWriter
import StringIO
import xlrd
import time
from osv import osv, fields
import base64
import pooler
from time import strftime
from string import upper
from tools import ustr
import unicodedata

class e_cm(osv.osv_memory):
    _name = 'e.cm'
    _description = 'Exportar'


    _columns = dict(
        period_id = fields.many2one('hr.work.period.line','Periodo'),
        archivo = fields.binary('Archivo',readonly=True),
        name = fields.char('N. archivo', size=32),
    )

    def exportar_archivo(self, cr, uid, ids, context):
        if context is None:
            context = {}
        payroll_obj = self.pool.get('hr.payslip')
        for data in self.browse(cr, uid, ids):
            roles = payroll_obj.search(cr, uid, [('period_id','=',data.period_id.id)])
            if not roles:
                raise osv.except_osv(('Error !'), 'No existen roles generados para ese mes!!!')
            writer = XLSWriter()
            writer.append(["Cedula RUC o Pasaporte","Referencia", "Nombre","INS. Financiera","Cta. Beneficiario","Tipo Cta.","Valor","Concepto","Detalle"])
            periodo = data.period_id.name
            n_archivo = ("SPI" + periodo + ".xls").replace('/','')
            sec = 0
            for rol_id in roles:
                sec += 1
                cadena = ""
                rol = payroll_obj.browse(cr, uid, rol_id)
                if rol.employee_id.active and rol.employee_id.bank_account_id:
                    ced = str(rol.employee_id.ci)
                    ref = sec 
                    nombre = rol.employee_id.employee_lastname+" "+rol.employee_id.name
                    ins_fin = rol.employee_id.bank_account_id.bank.bic
                    cta_ben = rol.employee_id.bank_account_id.acc_number
                    tip_cta = 1
                    if rol.employee_id.bank_account_id.type_cta=="cte":
                        tip_cta = 2
                    val = rol.net
                    concepto = "610101"
                    detalle = "Rol Pagos" + periodo
                    writer.append([ced,ref,nombre,ins_fin,cta_ben,tip_cta,val,concepto,detalle]) 
            writer.save(n_archivo)
            out = open(n_archivo,"rb").read().encode("base64")
            self.write(cr, uid, ids, {'archivo': out, 'name': n_archivo})
        return True
e_cm()
