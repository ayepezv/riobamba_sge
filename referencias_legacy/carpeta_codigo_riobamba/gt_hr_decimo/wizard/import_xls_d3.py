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
#from XLSWriter import XLSWriter
import StringIO
import xlrd
import netsvc

class import_sheet_d3(osv.TransientModel):

    _name='import.sheet.d3'
    
    _columns={
        'name':fields.char('Observaciones',size=128),
        'archivo':fields.binary('Archivo', required=True),
        }

    def _bad_archivo(self, cr, uid, ids, arch,context=None):
        result=True
        emp_obj=self.pool.get('hr.employee')
        arch_xls = base64.b64decode(arch)
        book = xlrd.open_workbook(file_contents=arch_xls)
        sh = book.sheet_by_name(book.sheet_names()[0])
        j=i=0
        for r in range(sh.nrows)[1:]:
            i+=1
            if sh.cell(r,0).value and sh.cell(r,1).value:
                emp_id = emp_obj.search(cr, uid, [('name','=',sh.cell(r,1).value)])
                if emp_id:
                    j+=1
                else:
                    raise osv.except_osv(('Error de archivo!'),'La cedula %s , en la linea numero %d no corresponde a nigun empleado'%((str(sh.cell(r,1).value)),i+1))
            else:
                raise osv.except_osv(('Error de archivo!'),'Existe un campo que esta vacio en la linea %s '%(r))
        if j==sh.nrows:
            result=False
        return result

    def import_sheet_d3(self, cr, uid, ids, context=None):
        emp_obj=self.pool.get('hr.employee')
        data = self.read(cr, uid, ids)[0]
#        self._bad_archivo(cr, uid, ids, data['archivo'],context=context)
 #       if self._bad_archivo(cr, uid, ids, data['archivo'],context=context):
 #           raise osv.except_osv(('Error de archivo!'),'El archivo seleccionado esta incorrecto por favor verifique el mismo.')
        dec_obj = self.pool.get('hr.decimo.tercero')
        dec_line_obj = self.pool.get('hr.decimo.tercero.line')
        if context is None:
            context = {}
        id_activo=context.get('active_id')
        parent=dec_obj.browse(cr, uid, id_activo)
        ids_unlink=[]
        if parent.state!='Borrador':
            raise osv.except_osv(('Error de usuario!'),'No puede importar un archivo cuando el documento ya esta procesado.')
        for l in parent.line_ids:
             ids_unlink.append(l.id)
        dec_line_obj.unlink(cr, uid, ids_unlink,context=context)
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                if sh.cell(r,0).value and sh.cell(r,1).value:
                    emp_id = emp_obj.search(cr, uid, [('name','=',sh.cell(r,1).value)])
                    i = 0
                    if emp_id:
                        i += 1
                        for emp in emp_id:
                            empleado=emp_obj.browse(cr, uid, emp)
                            dec_line_obj.create(cr, uid, {
                                'number':i,
                                'name':empleado.id,
                                'employee_id':empleado.id,
                                'dic':sh.cell(r,2).value and sh.cell(r,2).value or 0.0,
                                'ene':sh.cell(r,3).value and sh.cell(r,3).value or 0.0,
                                'feb':sh.cell(r,4).value and sh.cell(r,4).value or 0.0,
                                'mar':sh.cell(r,5).value and sh.cell(r,5).value or 0.0,
                                'abr':sh.cell(r,6).value and sh.cell(r,6).value or 0.0,
                                'may':sh.cell(r,7).value and sh.cell(r,7).value or 0.0,
                                'jun':sh.cell(r,8).value and sh.cell(r,8).value or 0.0,
                                'jul':sh.cell(r,9).value and sh.cell(r,9).value or 0.0,
                                'ago':sh.cell(r,10).value and sh.cell(r,10).value or 0.0,
                                'sep':sh.cell(r,11).value and sh.cell(r,11).value or 0.0,
                                'oct':sh.cell(r,12).value and sh.cell(r,12).value or 0.0,
                                'nov':sh.cell(r,13).value and sh.cell(r,13).value or 0.0,
                                'dias_lab':sh.cell(r,14).value and sh.cell(r,14).value or 0.0,
#                                'total':sh.cell(r,15).value and sh.cell(r,15).value or 0.0,
#                                'recibir':sh.cell(r,15).value and sh.cell(r,15).value or 0.0,
                                'dec_id':id_activo,
                                'cedula':empleado.name,
                            })
        else:
            raise osv.except_osv(('Error de usuario!'),'No ha seleccionado ningun archivo.')
        return {'type':'ir.actions.act_window_close' }

import_sheet_d3()

