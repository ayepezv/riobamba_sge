# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
#
##############################################################################

import time

from osv import osv
from osv import fields
import base64
import pooler
from XLSWriter import XLSWriter
import StringIO
import xlrd
import netsvc

class import_sheet(osv.osv_memory):

    _name='import.sheet'
    
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
                    raise osv.except_osv(('Error de archivo!'),'La cedula %s , en la linea numero %d no corresponde a ningun empleado'%((str(sh.cell(r,1).value)),i+1))
            else:
                raise osv.except_osv(('Error de archivo!'),'Existe un campo que esta vacio en la linea %s '%(r))
        if j==sh.nrows:
            result=False
        return result

    def import_sheet_(self, cr, uid, ids, context=None):
        emp_obj=self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        data = self.read(cr, uid, ids)[0]
        h_ad=self.pool.get('hr.ie.line')
        self._bad_archivo(cr, uid, ids, data['archivo'],context=context)
 #       if self._bad_archivo(cr, uid, ids, data['archivo'],context=context):
 #           raise osv.except_osv(('Error de archivo!'),'El archivo seleccionado esta incorrecto por favor verifique el mismo.')
        obj=self.pool.get('hr.ie.head')
        if context is None:
            context = {}
        id_activo=context.get('active_id')
        parent=obj.browse(cr, uid, id_activo)
        ids_unlink=[]
        if parent.state!='draft':
            raise osv.except_osv(('Error de usuario!'),'No puede importar un archivo cuando el documento ya esta procesado.')
        for l in parent.line_ids:
             ids_unlink.append(l.id)
        h_ad.unlink(cr, uid, ids_unlink,context=context)
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                if sh.cell(r,0).value and sh.cell(r,1).value and sh.cell(r,2).value:
                    emp_id = emp_obj.search(cr, uid, [('name','=',sh.cell(r,1).value)])
                    if emp_id:
                        for emp in emp_id:
                            empleado=emp_obj.browse(cr, uid, emp)
                            aux_valor = 0
                            if parent.valor>0 and parent.valor>=1:
                                aux_valor = parent.valor
                            elif parent.valor>0 and parent.valor<1:
                                contrato_ids = contract_obj.search(cr, uid, [('employee_id','=',empleado.id),('activo','=',True)])
                                if contrato_ids:
                                    contrato = contract_obj.browse(cr, uid, contrato_ids[0])
                                    aux_valor = contrato.wage * parent.valor 
                            else:
                                aux_valor = sh.cell(r,2).value
                            h_ad.create(cr, uid, {
                                    'name':empleado.name,
                                    'employee_id':empleado.id,
                                    'valor':aux_valor,
                                    'categ_id':parent.name.id,
                                    'head_id':parent.id,
                                    'period_id':parent.period_id.id,
                                    })
                elif sh.cell(r,0).value and sh.cell(r,1).value:
                    emp_id = emp_obj.search(cr, uid, [('name','=',sh.cell(r,1).value)])
                    if emp_id:
                        for emp in emp_id:
                            empleado=emp_obj.browse(cr, uid, emp)
                            aux_valor = 0
                            if parent.valor>0 and parent.valor>=1:
                                aux_valor = parent.valor
                            elif parent.valor>0 and parent.valor<1:
                                contrato_ids = contract_obj.search(cr, uid, [('employee_id','=',empleado.id),('activo','=',True)])
                                if contrato_ids:
                                    contrato = contract_obj.browse(cr, uid, contrato_ids[0])
                                    aux_valor = contrato.wage * parent.valor 
                            else:
                                aux_valor = sh.cell(r,2).value
                            h_ad.create(cr, uid, {
                                    'name':empleado.name,
                                    'employee_id':empleado.id,
                                    'valor':aux_valor,
                                    'categ_id':parent.name.id,
                                    'head_id':parent.id,
                                    'period_id':parent.period_id.id,
                                    })
                        
        else:
            raise osv.except_osv(('Error de usuario!'),'No ha seleccionado ningun archivo.')
        return {'type':'ir.actions.act_window_close' }

import_sheet()

class export_sheet(osv.osv_memory):
    _name='export.sheet'
    _columns={
        'archivo':fields.binary('Archivo',readonly=True),
        'name':fields.char('N. archivo', size=32),
        }

    def exportar_emp(self, cr, uid, ids, context):
        #crear el archivo de excel
        emp_obj=self.pool.get('hr.employee')
        writer = XLSWriter()
        writer.append(["NOMBRE","CEDULA", "VALOR"])
        record_id = context and context.get('active_id', False) or False
        head_obj = self.pool.get('hr.ie.head')
        head = head_obj.browse(cr, uid, record_id)
        if head:
            if head.department_id:
                emp_ids=emp_obj.search(cr, uid, [('department_id','=',head.department_id.id)])
                n_archivo = ("Empleados" + str(head.institute_id.name) + ".xls").replace('/','')
                for empleado_ in emp_ids:
                    empleado=emp_obj.browse(cr, uid, empleado_)
                    nombre=empleado.apellido + ' ' + empleado.name
                    writer.append([nombre,empleado.ci,0]) 
            else:
                n_archivo = ("Empleados" + ".xls").replace('/','')
                writer.append(["Alvear Jaramillo Luis Mario","0103898896",0])
        writer.save("Empleados.xls")
        out = open("Empleados.xls","rb").read().encode("base64")
        self.write(cr, uid, ids, {'archivo': out, 'name': n_archivo})


export_sheet()


