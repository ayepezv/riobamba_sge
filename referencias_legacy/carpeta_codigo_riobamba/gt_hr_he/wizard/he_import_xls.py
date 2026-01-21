# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

import time

from osv import osv
from osv import fields
import base64
import pooler
from gt_tool import XLSWriter
import StringIO
import xlrd
import netsvc

class he_import_sheet(osv.osv_memory):

    _name='he.import.sheet'
    
    _columns={
        'name':fields.char('Observaciones',size=128),
        'period_id':fields.many2one('hr.work.period.line','Periodo',required=True),
        'archivo':fields.binary('Archivo', required=True),
        }

    def _bad_archivo(self, cr, uid, ids, arch,context=None):
        result=True
        emp_obj=self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        arch_xls = base64.b64decode(arch)
        book = xlrd.open_workbook(file_contents=arch_xls)
        sh = book.sheet_by_name(book.sheet_names()[0])
        j=i=0
        for r in range(sh.nrows)[1:]:
            i+=1
            if sh.cell(r,1).value and sh.cell(r,2).value:
                emp_id = emp_obj.search(cr, uid, [('name','=',sh.cell(r,2).value)],limit=1)
                if emp_id:
                    contract_ids = contract_obj.search(cr, uid, [('employee_id','=',emp_id[0])])
                    if contract_ids:
                        j+=1
                    else:
                        raise osv.except_osv(('Error de archivo!'),'La cedula %s , en la linea numero %d no corresponde a nigun empleado con contrato activo'%((str(sh.cell(r,2).value)),i+1))
                else:
                    raise osv.except_osv(('Error de archivo!'),'La cedula %s , en la linea numero %d no corresponde a nigun empleado'%((str(sh.cell(r,2).value)),i+1))
            else:
                raise osv.except_osv(('Error de archivo!'),'Existe un campo que esta vacio en la linea %s '%(r))
        if j!=sh.nrows:
            result=False
        return result

    def import_sheet_(self, cr, uid, ids, context=None):
        emp_obj=self.pool.get('hr.employee')
        contract_obj=self.pool.get('hr.contract')
        data = self.read(cr, uid, ids)[0]
        h_ad=self.pool.get('hr.he.register.alone')
        line_obj=self.pool.get('hr.he.register.alone.line')
        if context is None:
            context = {}
        self._bad_archivo(cr, uid, ids, data['archivo'],context=context)
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                emp_id = emp_obj.search(cr, uid, [('name','=',sh.cell(r,2).value)],limit=1)
                contract_id = contract_obj.search(cr, uid, [('employee_id','=',emp_id[0])],limit=1)[0]
                hr_25 = hr_50 = hr_60 = hr_100 = 0
                if sh.cell(r,3).value:
                    hr_25 = sh.cell(r,3).value
                if sh.cell(r,4).value:
                    hr_50 = sh.cell(r,4).value
                if sh.cell(r,5).value:
                    hr_60 = sh.cell(r,5).value
                if sh.cell(r,6).value:
                    hr_100 = sh.cell(r,6).value
                head_id = h_ad.create(cr, uid, {
                        'contract_id': contract_id,
                        'period_id': data['period_id'][0],
                        })
                line_obj.create(cr, uid, {
                        'h_25':hr_25,
                        'h_50':hr_50,
                        'h_60':hr_60,
                        'h_100':hr_100,
                        'registro_id':head_id,
                        })
        else:
            raise osv.except_osv(('Error de usuario!'),'No ha seleccionado ningun archivo.')
        return {'type':'ir.actions.act_window_close' }

he_import_sheet()
