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

import time

from osv import osv
from osv import fields
import base64
import pooler
from XLSWriter import XLSWriter
from tools import ustr
import StringIO
import xlrd
import netsvc


class import_category(osv.osv_memory):

    _name='import.category'
    
    _columns={
        'name':fields.char('Observaciones',size=128),
        'archivo':fields.binary('Archivo'),
        }

    def _bad_archivo(self, cr, uid, ids, arch,context=None):
        result=True
        emp_obj=self.pool.get('hr.employee')
        bank_obj=self.pool.get('account.account')
        arch_xls = base64.b64decode(arch)
        book = xlrd.open_workbook(file_contents=arch_xls)
        sh = book.sheet_by_name(book.sheet_names()[0])
        j=i=0
        for r in range(sh.nrows)[1:]:
            i+=1
            if sh.cell(r,0).value and sh.cell(r,1).value:
                try:
                    vals={}
                    prueba=sh.cell(r,0).value
                    vals['name']=self.pool.get('gt.account.asset.type.category').search(cr, uid, [('name','=',prueba.strip())])[0]
                    prueba=sh.cell(r,1).value
                    vals['cuenta_ingreso']=bank_obj.search(cr, uid, [('code','=',prueba.strip())])[0]
                    prueba=sh.cell(r,2).value
                    vals['cuenta_baja']=bank_obj.search(cr, uid, [('code','=',prueba.strip())])[0]
                    prueba=sh.cell(r,3).value
                    vals['tipo_id']=self.pool.get('gt.account.asset.tipo').search(cr, uid, [('name','=',prueba.strip())])[0]
                    prueba=sh.cell(r,4).value
                    vals['subtipo_id']=self.pool.get('gt.account.asset.subtipo').search(cr, uid, [('name','=',prueba.strip()),
                                                                                          ('tipo_id','=', vals['tipo_id'])])[0]
                    prueba=sh.cell(r,5).value
                    vals['journal_id']=self.pool.get('account.journal').search(cr, uid, [('name','=',prueba.strip())])[0]
                    prueba=sh.cell(r,6).value
                    vals['account_asset_id']=bank_obj.search(cr, uid, [('code','=',prueba.strip())])[0]
                    prueba=str(sh.cell(r,7).value)
                    vals['account_depreciation_id']=bank_obj.search(cr, uid, [('code','=',prueba.strip())])[0]
                    prueba=sh.cell(r,8).value
                    vals['account_expense_depreciation_id']=bank_obj.search(cr, uid, [('code','=',prueba.strip())])[0]
                    vals['method_time']=ustr(sh.cell(r,9).value)
                    prueba=sh.cell(r,10).value
                    vals['class_id']=self.pool.get('gt.account.asset.class').search(cr, uid, [('name','=',prueba.strip()),
                                                                                          ('tipo_id','=', vals['tipo_id']),
                                                                                          ('subtipo_id','=', vals['subtipo_id'])])[0]
                    prueba=sh.cell(r,11).value
                    vals['method']=prueba.strip()
                    vals['method_number']=sh.cell(r,12).value
                    vals['method_period']=prueba=sh.cell(r,13).value
                    prueba=sh.cell(r,14).value
                    vals['open_asset']=prueba.strip()     
                    j+=1
                except:
                    raise osv.except_osv(('Error de archivo!'),'Existen errores en la informacion; linea. En la linea: %d del archivo'%i+1)  
            else:
                raise osv.except_osv(('Error de archivo!'),'Existe un campo que esta vacio en la linea %s '%(r))                           

        if j==sh.nrows:
            result=False
        return result

    def import_category(self, cr, uid, ids, context=None):
        categ_obj=self.pool.get('account.asset.category')
        data = self.read(cr, uid, ids)[0]
        bank_obj=self.pool.get('account.account')    
          
        #self._bad_archivo(cr, uid, ids, data['archivo'],context=context)
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                #vals['asset_category_id']
                vals={}
                prueba=sh.cell(r,0).value
                vals['name']=self.pool.get('gt.account.asset.type.category').search(cr, uid, [('name','=',prueba.strip())])[0]
                prueba=sh.cell(r,1).value
                vals['cuenta_ingreso']=bank_obj.search(cr, uid, [('code','=',prueba.strip())])[0]
                prueba=sh.cell(r,2).value
                vals['cuenta_baja']=bank_obj.search(cr, uid, [('code','=',prueba.strip())])[0]
                prueba=sh.cell(r,3).value
                vals['tipo_id']=self.pool.get('gt.account.asset.tipo').search(cr, uid, [('name','=',prueba.strip())])[0]
                prueba=sh.cell(r,4).value
                vals['subtipo_id']=self.pool.get('gt.account.asset.subtipo').search(cr, uid, [('name','=',prueba.strip()),('tipo_id','=',vals['tipo_id'])])[0]
                prueba=sh.cell(r,5).value
                vals['journal_id']=self.pool.get('account.journal').search(cr, uid, [('name','=',prueba.strip())])[0]
                prueba=sh.cell(r,6).value
                vals['account_asset_id']=bank_obj.search(cr, uid, [('code','=',prueba.strip())])[0]
                prueba=str(sh.cell(r,7).value)
                vals['account_depreciation_id']=bank_obj.search(cr, uid, [('code','=',prueba.strip())])[0]
                prueba=sh.cell(r,8).value
                vals['account_expense_depreciation_id']=bank_obj.search(cr, uid, [('code','=',prueba.strip())])[0]
                vals['method_time']=ustr(sh.cell(r,9).value)
                prueba=sh.cell(r,10).value
                vals['class_id']=self.pool.get('gt.account.asset.class').search(cr, uid, [('name','=',prueba.strip()),('tipo_id','=',vals['tipo_id']),('subtipo_id','=',vals['subtipo_id'])])[0]
                prueba=sh.cell(r,11).value
                vals['method']=prueba.strip()
                vals['method_number']=sh.cell(r,12).value
                vals['method_period']=prueba=sh.cell(r,13).value
                prueba=sh.cell(r,14).value
                vals['open_asset']=prueba.strip()
                self.pool.get('account.asset.category').create(cr, uid, vals, context=None)  
                
                #bank_id=bank_obj.search(cr, uid, [('acc_number','=',sh.cell(r,1).value)])
                #emp_id = emp_obj.search(cr, uid, [('ci','=',sh.cell(r,0).value)])
                #if emp_id and bank_id:
                #    empleado=emp_obj.browse(cr, uid, emp_id[0])
                #    banco=bank_obj.browse(cr, uid, bank_id[0])
                #    emp_obj.write(cr, uid, empleado.id,{
                #            'bank_account_id':banco.id,
                #            })
                #    bank_obj.write(cr, uid, banco.id,{
                #            'employee_id':empleado.id,
                #            })
        else:
            raise osv.except_osv(('Error de usuario!'),'No ha seleccionado ningun archivo.')
        return {'type':'ir.actions.act_window_close' }

import_category()



class import_asset(osv.osv_memory):

    _name='import.asset'
    
    _columns={
        'name':fields.char('Observaciones',size=128),
        'archivo':fields.binary('Archivo'),
        }

    def _bad_archivo(self, cr, uid, ids, arch,context=None):
        result=True
        emp_obj=self.pool.get('hr.employee')
        bank_obj=self.pool.get('account.account')
        arch_xls = base64.b64decode(arch)
        book = xlrd.open_workbook(file_contents=arch_xls)
        sh = book.sheet_by_name(book.sheet_names()[0])
        j=i=0
        for r in range(sh.nrows)[1:]:
            i+=1
            if sh.cell(r,0).value and sh.cell(r,1).value:
                vals={}
                try:                       
                    vals['code']=sh.cell(r,20).value
                except:
                    raise osv.except_osv(('Error de archivo!'),'El activo  %s tiene errores en el codigo; linea. En la linea: %d del archivo'%((str(sh.cell(r,20).value)),i+1))
                try: 
                    prueba=sh.cell(r,0).value
                    vals['name']=prueba.strip()
                except:
                    raise osv.except_osv(('Error de archivo!'),'El activo  %s tiene errores en el nombre; linea. En la linea: %d del archivo'%((str(sh.cell(r,20).value)),i+1))
                try:
                    prueba=sh.cell(r,1).value
                    vals['tipo_id']=self.pool.get('gt.account.asset.tipo').search(cr, uid, [('name','=',prueba.strip())])[0]
                except:
                    raise osv.except_osv(('Error de archivo!'),'El activo  %s tiene errores en el tipo; linea. En la linea: %d del archivo'%((str(sh.cell(r,20).value)),i+1))
                try:
                    prueba=sh.cell(r,2).value
                    vals['subtipo_id']=self.pool.get('gt.account.asset.subtipo').search(cr, uid, [('name','=',prueba.strip()),
                                                                                          ('tipo_id','=', vals['tipo_id'])])[0]
                except:
                    raise osv.except_osv(('Error de archivo!'),'El activo  %s tiene errores en el subtipo; linea. En la linea: %d del archivo'%((str(sh.cell(r,20).value)),i+1))
                try:
                    prueba=sh.cell(r,3).value
                    vals['class_id']=self.pool.get('gt.account.asset.class').search(cr, uid, [('name','=',prueba.strip()),
                                                                                          ('tipo_id','=', vals['tipo_id']),
                                                                                          ('subtipo_id','=', vals['subtipo_id'])])[0]
                except:
                    raise osv.except_osv(('Error de archivo!'),'El activo  %s tiene errores en la clase; linea. En la linea: %d del archivo'%((str(sh.cell(r,20).value)),i+1))
                try:
                    prueba=sh.cell(r,4).value
                    gt_categ_id = self.pool.get('gt.account.asset.type.category').search(cr, uid, [('name','=',prueba.strip())])[0]
                    vals['category_id']=self.pool.get('account.asset.category').search(cr, uid, [('name','=',gt_categ_id),
                                                                                              ('tipo_id','=', vals['tipo_id']),
                                                                                              ('subtipo_id','=', vals['subtipo_id']),
                                                                                              ('class_id','=', vals['class_id'])])[0]
                except:
                    raise osv.except_osv(('Error de archivo!'),'El activo  %s tiene errores en la categoria. En la linea: %d del archivo'%((str(sh.cell(r,20).value)),i+1))
                try:                                                                          
                    prueba=sh.cell(r,5).value
                    vals['income_id']=self.pool.get('gt.account.asset.income').search(cr, uid, [('name','=',prueba.strip())])[0]
                except:
                    raise osv.except_osv(('Error de archivo!'),'El activo  %s tiene errores en el tipo de ingreso; linea. En la linea: %d del archivo'%((str(sh.cell(r,20).value)),i+1))
                try:
                    prueba=sh.cell(r,6).value
                    vals['transaction_id']=self.pool.get('gt.account.asset.transaction').search(cr, uid, [('name','=',prueba.strip())])[0]
                except:
                    raise osv.except_osv(('Error de archivo!'),'El activo  %s tiene errores en el tipo de transaccion; linea. En la linea: %d del archivo'%((str(sh.cell(r,20).value)),i+1))
                try:
                    vals['purchase_value']=sh.cell(r,7).value
                    vals['salvage_value']=sh.cell(r,8).value
                    vals['serial_number']=sh.cell(r,9).value
                    prueba=sh.cell(r,10).value
                    partner_id_=self.pool.get('res.partner').search(cr, uid, [('ced_ruc','=',prueba.strip())])
                    if partner_id_:
                        vals['partner_id']=partner_id_[0]
                    vals['purchase_date']=sh.cell(r,11).value
                    prueba=sh.cell(r,12).value
                    vals['method_time']=prueba.strip()
                    prueba=sh.cell(r,13).value
                    vals['method']=prueba.strip()
                    vals['method_number']=sh.cell(r,14).value
                    vals['method_period']=sh.cell(r,15).value
                    prueba=sh.cell(r,16).value
                    department_id_=self.pool.get('hr.department').search(cr, uid, [('name','=',prueba.strip())])
                    if department_id_:
                        vals['department_id']=department_id_[0]
                    prueba=sh.cell(r,17).value
                    vals['employee_id']=self.pool.get('hr.employee').search(cr, uid, [('active','in',('True','False')),
                                                                                      ('name','=',prueba.strip())])[0]
                    prueba=sh.cell(r,18).value
                    vals['note']=prueba.strip()
                    prueba=sh.cell(r,19).value
                    vals['state']=prueba.strip()

                    j+=1
                except:
                    raise osv.except_osv(('Error de archivo!'),'El activo  %s tiene errores en la informacion; linea. En la linea: %d del archivo'%((str(sh.cell(r,20).value)),i+1)) 
            else:
                raise osv.except_osv(('Error de archivo!'),'Existe un campo que esta vacio en la linea %s '%(r))
        if j==sh.nrows:
            result=False
        return result

    def import_asset(self, cr, uid, ids, context=None):
        categ_obj=self.pool.get('account.asset.category')
        data = self.read(cr, uid, ids)[0]
        bank_obj=self.pool.get('account.asset')
        contador = 0
          
        #self._bad_archivo(cr, uid, ids, data['archivo'],context=context)
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                #vals['asset_category_id']
                vals={}
                contador = contador +1
                print contador
                prueba=sh.cell(r,0).value
                vals['name']=prueba.strip()
                prueba=sh.cell(r,1).value
                print prueba
                vals['tipo_id']=self.pool.get('gt.account.asset.tipo').search(cr, uid, [('name','=',prueba.strip())])[0]
                prueba=sh.cell(r,2).value
                vals['subtipo_id']=self.pool.get('gt.account.asset.subtipo').search(cr, uid, [('name','=',prueba.strip()),('tipo_id','=',vals['tipo_id'])])[0]
                prueba=sh.cell(r,3).value
                vals['class_id']=self.pool.get('gt.account.asset.class').search(cr, uid, [('name','=',prueba.strip()),
                                                                                          #('tipo_id','=', vals['tipo_id']),
                                                                                          ('subtipo_id','=', vals['subtipo_id'])])[0]
                prueba=sh.cell(r,4).value
                vals['category_id']=self.pool.get('account.asset.category').search(cr, uid, [('name','=',prueba.strip()),
                                                                                          ('tipo_id','=', vals['tipo_id']),])[0]
                prueba=sh.cell(r,5).value
                vals['income_id']=self.pool.get('gt.account.asset.income').search(cr, uid, [('name','=',prueba.strip())])[0]
                prueba=sh.cell(r,6).value
                vals['transaction_id']=self.pool.get('gt.account.asset.transaction').search(cr, uid, [('name','=',prueba.strip())])[0]
                vals['purchase_value']=sh.cell(r,7).value
                vals['salvage_value']=sh.cell(r,8).value
                vals['serial_number']=sh.cell(r,9).value
                a = sh.cell(r,9).value
                #print "SERIALAAAAAAAAAAAAAaaa",a
                prueba=sh.cell(r,10).value
                partner_id_=self.pool.get('res.partner').search(cr, uid, [('ced_ruc','=',prueba.strip())])
                if partner_id_:
                    vals['partner_id']=partner_id_[0]
                vals['purchase_date']=sh.cell(r,11).value
                prueba=sh.cell(r,12).value
                vals['method_time']=prueba.strip()
                prueba=sh.cell(r,13).value
                vals['method']=prueba.strip()
                vals['method_number']=sh.cell(r,14).value
                vals['method_period']=sh.cell(r,15).value
                prueba=sh.cell(r,16).value
                department_id_=self.pool.get('hr.department').search(cr, uid, [('name','=',prueba.strip())])
                if department_id_:
                    vals['department_id']=department_id_[0]
                prueba=sh.cell(r,17).value
                vals['employee_id']=self.pool.get('hr.employee').search(cr, uid, [('active','in',('True','False')),
                                                                                  ('name','=',prueba.strip())])[0]
                prueba=sh.cell(r,18).value
                vals['reference']=prueba.strip()
                prueba=str(sh.cell(r,19).value)
                vals['note']=prueba.strip()
                prueba=sh.cell(r,20).value
                vals['detalle_baja']=prueba.strip()
                prueba=sh.cell(r,21).value
                vals['code']=prueba.strip()
                prueba=sh.cell(r,22).value
                vals['state']=prueba.strip()
                #print vals
                self.pool.get('account.asset.asset').create(cr, uid, vals, context=None)  
                
                #bank_id=bank_obj.search(cr, uid, [('acc_number','=',sh.cell(r,1).value)])
                #emp_id = emp_obj.search(cr, uid, [('ci','=',sh.cell(r,0).value)])
                #if emp_id and bank_id:
                #    empleado=emp_obj.browse(cr, uid, emp_id[0])
                #    banco=bank_obj.browse(cr, uid, bank_id[0])
                #    emp_obj.write(cr, uid, empleado.id,{
                #            'bank_account_id':banco.id,
                #            })
                #    bank_obj.write(cr, uid, banco.id,{
                #            'employee_id':empleado.id,
                #            })
        else:
            raise osv.except_osv(('Error de usuario!'),'No ha seleccionado ningun archivo.')
        return {'type':'ir.actions.act_window_close' }

import_asset()


class import_class(osv.osv_memory):

    _name='import.class'
    
    _columns={
        'name':fields.char('Observaciones',size=128),
        'archivo':fields.binary('Archivo'),
        }

    def _bad_archivo(self, cr, uid, ids, arch,context=None):
        result=True
        #emp_obj=self.pool.get('hr.employee')
        #bank_obj=self.pool.get('account.account')
        arch_xls = base64.b64decode(arch)
        book = xlrd.open_workbook(file_contents=arch_xls)
        sh = book.sheet_by_name(book.sheet_names()[0])
        j=i=0
        for r in range(sh.nrows)[1:]:
            i+=1
            if sh.cell(r,0).value and sh.cell(r,1).value:
                try:
                    vals={}
                    prueba=sh.cell(r,2).value
                    vals['tipo_id']=self.pool.get('gt.account.asset.tipo').search(cr, uid, [('name','=',prueba.strip())])[0]
                    prueba=sh.cell(r,3).value
                    vals['subtipo_id']=self.pool.get('gt.account.asset.subtipo').search(cr, uid, [('name','=',prueba.strip()),('tipo_id','=',vals['tipo_id'])])[0]
                    j+=1
                except:
                    raise osv.except_osv(('Error de archivo!'),'Existen errores en la informacion; linea. En la linea: %d del archivo'%i+1)  
            else:
                raise osv.except_osv(('Error de archivo!'),'Existe un campo que esta vacio en la linea %s '%(r))                           

        if j==sh.nrows:
            result=False
        return result

    def import_class(self, cr, uid, ids, context=None):
        #categ_obj=self.pool.get('account.asset.category')
        data = self.read(cr, uid, ids)[0]
        #bank_obj=self.pool.get('account.account')    
          
        #self._bad_archivo(cr, uid, ids, data['archivo'],context=context)
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                #vals['asset_category_id']
                vals={}
                prueba=sh.cell(r,0).value
                vals['name'] = prueba.strip()
                prueba=sh.cell(r,1).value
                vals['code'] = prueba.strip()
                prueba=sh.cell(r,2).value
                vals['tipo_id']=self.pool.get('gt.account.asset.tipo').search(cr, uid, [('name','=',prueba.strip())])[0]
                prueba=sh.cell(r,3).value
                #import pdb
                #pdb.set_trace()
                vals['subtipo_id']=self.pool.get('gt.account.asset.subtipo').search(cr, uid, [('name','=',prueba.strip()),('tipo_id','=',vals['tipo_id'])])[0]
                self.pool.get('gt.account.asset.class').create(cr, uid, vals, context=None)
        else:
            raise osv.except_osv(('Error de usuario!'),'No ha seleccionado ningun archivo.')
        return {'type':'ir.actions.act_window_close' }

import_class()

class import_components(osv.osv_memory):

    _name='import.components'
    
    _columns={
        'name':fields.char('Observaciones',size=128),
        'archivo':fields.binary('Archivo'),
        }

    def import_componente(self, cr, uid, ids, context=None):
        #categ_obj=self.pool.get('account.asset.category')
        activo_obj = self.pool.get('account.asset.asset')
        componente_obj = self.pool.get('gt.account.asset.componente')
        
        data = self.read(cr, uid, ids)[0]
        #bank_obj=self.pool.get('account.account')    
          
        #self._bad_archivo(cr, uid, ids, data['archivo'],context=context)
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                #vals['asset_category_id']
                vals={}
                prueba=sh.cell(r,0).value
                activo_id = activo_obj.search(cr, uid, [('code','=',prueba)])
                if not activo_id:
                    raise osv.except_osv('Error de usuario!','No se encuentra el activo con el código ' + prueba)
                vals['asset_id'] = activo_id[0]
                vals['name'] = sh.cell(r,1).value
                vals['value'] = sh.cell(r,2).value
                vals['marca'] = sh.cell(r,3).value
                vals['serie'] = sh.cell(r,4).value
                vals['cantidad'] = sh.cell(r,5).value
                #import pdb
                #pdb.set_trace()
                componente_obj.create(cr, uid, vals, context=None)
        else:
            raise osv.except_osv(('Error de usuario!'),'No ha seleccionado ningun archivo.')
        return {'type':'ir.actions.act_window_close' }

import_components()

class import_propiedades(osv.osv_memory):

    _name='import.propiedades'
    
    _columns={
        'name':fields.char('Observaciones',size=128),
        'archivo':fields.binary('Archivo'),
        }

    def import_propiedades(self, cr, uid, ids, context=None):
        #categ_obj=self.pool.get('account.asset.category')
        activo_obj = self.pool.get('account.asset.asset')
        #componente_obj = self.pool.get('gt.account.asset.componente')
        propiedad_activo_obj = self.pool.get('account.asset.property')
        propiedades_obj = self.pool.get('gt.tipo.properties')
        tipo_obj = self.pool.get('gt.account.asset.tipo')
        contador = 0
        
        data = self.read(cr, uid, ids)[0]
        #bank_obj=self.pool.get('account.account')
          
        #self._bad_archivo(cr, uid, ids, data['archivo'],context=context)
        if context is None:
            context = {}
        if data['archivo']:
            arch = data['archivo']
            arch_xls = base64.b64decode(arch)
            book = xlrd.open_workbook(file_contents=arch_xls)
            sh = book.sheet_by_name(book.sheet_names()[0])
            context={}
            for r in range(sh.nrows)[1:]:
                contador = contador + 1
                #print contador
                #vals['asset_category_id']
                vals={}
                prueba=sh.cell(r,0).value.strip()
                #buscamos el activo
                activo_id = activo_obj.search(cr, uid, [('code','=',prueba)])
                if not activo_id:
                    raise osv.except_osv('Error de usuario!','No se encuentra el activo con el código ' + prueba)
                activo = activo_obj.browse(cr, uid, activo_id[0])
                #buscamos el tipo de propiedad
                prueba=sh.cell(r,1).value.strip()
                tipo_propiedad_id = propiedades_obj.search(cr, uid, [('name','=',prueba),('tipo_id','=',activo.tipo_id.id)])
                if not tipo_propiedad_id:
                    tipo_propiedad_id = propiedades_obj.create(cr, uid, {'name':prueba, 'tipo_id':activo.tipo_id.id})
                else:
                    tipo_propiedad_id = tipo_propiedad_id[0]
                #buscamos la propiedad del activo
                propiedad_activo_id = propiedad_activo_obj.search(cr, uid, [('name','=',tipo_propiedad_id),('asset_id','=',activo.id)])
                if not propiedad_activo_id:
                    propiedad_activo_id = propiedad_activo_obj.create(cr, uid, {'name':tipo_propiedad_id,'asset_id':activo.id})
                    propiedad_activo_id = [propiedad_activo_id]
                propiedad_activo_obj.write(cr, uid, propiedad_activo_id, {'value':sh.cell(r,2).value.strip()})
        else:
            raise osv.except_osv(('Error de usuario!'),'No ha seleccionado ningun archivo.')
        return {'type':'ir.actions.act_window_close' }

import_propiedades()