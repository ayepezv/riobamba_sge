# -*- coding: utf-8 -*-
#############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

from osv import osv,fields
from dateutil import parser
import time
import unicodedata
from xlrd import open_workbook
from xlutils.copy import copy
import os
from lxml import etree
from time import strftime
from string import upper
import base64
import pooler
import StringIO
import netsvc
import addons

import sys
import zipfile

class hrRubro(osv.Model):
    _name = 'hr.rubro'

    _FIELDS_107 = [('field_301','301'),('field_303','303'),('field_305','305'),('field_307','307'),('field_311','311'),('field_313','313'),
                   ('field_315','315'),('field_317','317'),
                   ('field_351','351'),('field_353','353'),('field_361','361'),('field_363','363'),('field_365','365'),
                   ('field_367','367'),('field_369','369'),('field_371','371'),('field_373','373'),('field_381','381'),
                   ('field_403','403'),('field_405','405'),('field_407','407')]

    _columns = {
        'name':fields.char('Descripción',size=64),
        'valor':fields.float('Valor'),
        'casillero':fields.selection(_FIELDS_107,'Casillero'),
        'contract_id':fields.many2one('hr.contract','Contrato'),
        'period_id':fields.many2one('hr.work.period','Periodo'),
        }
hrRubro()    

class hrContract107(osv.osv):
    _inherit = 'hr.contract'
    _columns = {
        'rubros_ids': fields.one2many('hr.rubro','contract_id','Lineas'),
        }
    
hrContract107()

class empresa_107(osv.osv):
    _name = "empresa.107"
    _columns = {
        'name': fields.char('Descripcion', size=50),
        'name2': fields.many2one('hr.work.period', 'Ejercicio Fiscal'),
        'period_id':fields.many2one('hr.work.period', 'Ejercicio Fiscal'),
        'line_ids': fields.one2many('sri.107', 'head_id', 'Detalle'),
        'archivo_base': fields.binary('Formularios', help="Archivo comprimido con todos los formularios 107"),
        'archivo_rdep': fields.binary('Archivo RDEP', help="RDEP en formato XML"),
        'directorio': fields.char('Directorio destino', size=50),
        'state': fields.selection([('draft','Borrador'),('done','aprobado'),('cancel','Cancelado')],'Estado'),
    }
    
    _defaults = {
        'name': 'rdep.xml',
        'state': 'draft',
    }
    

    def crear_zip(self, folder):
        reffile = zipfile.ZipFile(folder + ".zip", "w")
        for item in os.listdir(folder):
            reffile.write(os.path.join(folder, item), os.path.basename(item), zipfile.ZIP_DEFLATED)
        reffile.close()
        nombre = folder + '.zip'
        return nombre
        '''for item in os.listdir(folder):
            full_path = os.path.join(folder, item)
            if not os.path.isdir(full_path):
                    continue
            dst_filename = item + '.zip'
            dst_item = os.path.join(folder, dst_filename)
            if os.path.exists(dst_item) and os.path.getsize(dst_item) > 0:
                    continue
            output_file = zipfile.ZipFile(dst_item, "w", zipfile.ZIP_DEFLATED)
            for item_file in os.listdir(full_path):
                    output_file.write(os.path.join(full_path, item_file), item_file)
            output_file.close()
        '''
        
    def genera_xml107(self, cr, uid, ids, context=None):
#        usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
        parameter_obj = self.pool.get('ir.config_parameter')
        obj_contract = self.pool.get("hr.contract")
        obj_formulario = self.pool.get("sri.107")
        ids_contract = obj_contract.search(cr, uid, [('activo', '=', True)])
        #archivo del formulario 107
        #aqui tomar el addons que este en los parametros de configuracion
   #     addons_ids = parameter_obj.search(cr, uid, [('key','=','addons')],limit=1)
   #     addons = parameter_obj.browse(cr, uid, addons_ids[0]).value
        xls_path = addons.get_module_resource('gt_hr_sri107','xls','107.xls')
        rb = open_workbook(xls_path,formatting_info=True)
        #print xls_path
        
       
        #file = etree.tostring(rdep, pretty_print=True, encoding='iso-8859-1')
        
        for asistente in self.browse(cr, uid, ids, context):
            #archivo del rdep
            usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
            ruc='001'
            try:
                ruc = usuario.company_id.ruc_company
            except:
                pass
            rdep = etree.Element('rdep')
            etree.SubElement(rdep, 'numRuc').text = ruc.rjust(13,'0')
            etree.SubElement(rdep, 'anio').text = str(asistente.name2.name)[-4:]
            retRelDep = etree.Element('retRelDep')
            #directorio para archivos excel sri
            directorio = os.system("mkdir formularios"+str(asistente.name2.name)[-4:])
            ids_formularios = obj_formulario.search(cr, uid, [('head_id', '=', asistente.id)])
            for id_formulario in ids_formularios:
                formulario = obj_formulario.browse(cr, uid, [id_formulario], context)[0]
                #inicio rdep
                #escritura de datos en el formulario de excel
                wb = copy(rb)
                ws = wb.get_sheet(0)
                #campo 102
                anio = str(formulario.field_102.name)[-4:]
                ws.write(3,14,anio[:1])
                ws.write(3,15,anio[1:2])
                ws.write(3,16,anio[2:3])
                ws.write(3,17,anio[3:4])
                #campo 106
                ws.write(7,15,formulario.field_106)
                #campo 105
                if formulario.field_105:
                    ws.write(7,1,formulario.field_105[:1])
                    ws.write(7,2,formulario.field_105[1:2])
                    ws.write(7,3,formulario.field_105[2:3])
                    ws.write(7,4,formulario.field_105[3:4])
                    ws.write(7,5,formulario.field_105[4:5])
                    ws.write(7,6,formulario.field_105[5:6])
                    ws.write(7,7,formulario.field_105[6:7])
                    ws.write(7,8,formulario.field_105[7:8])
                    ws.write(7,9,formulario.field_105[8:9])
                    ws.write(7,10,formulario.field_105[9:10])
                #campo 201
                ws.write(10,1,formulario.contract_id.employee_id.name)
                #campo 202
                ws.write(10,15,formulario.contract_id.employee_id.complete_name)
                #campos liquidacion de impuestos
                ws.write(13,21,formulario.field_301)
                ws.write(14,21,formulario.field_303)
                ws.write(15,21,formulario.field_305)
                ws.write(16,21,formulario.field_307)
                ws.write(17,21,formulario.field_311)
                ws.write(18,21,formulario.field_313)
                ws.write(19,21,formulario.field_315)
                ws.write(20,21,formulario.field_317)
                ws.write(21,21,formulario.field_351)
                ws.write(22,21,formulario.field_353)
                ws.write(23,21,formulario.field_361)
                ws.write(24,21,formulario.field_363)
                ws.write(25,21,formulario.field_365)
                ws.write(26,21,formulario.field_367)
                ws.write(27,21,formulario.field_369)
                ws.write(28,21,formulario.field_371)
                ws.write(29,21,formulario.field_373)
                ws.write(30,20,formulario.field_381)
                ws.write(31,21,formulario.field_399)
                ws.write(32,21,formulario.field_401)
                ws.write(33,21,formulario.field_403)
                ws.write(34,21,formulario.field_405)
                ws.write(35,21,formulario.field_407)
                ws.write(36,21,formulario.field_349)

                #almacenamiento de datos del formulario en excel

                nombre = "formularios" + str(formulario.field_102.name)[-4:] + "/" + str(formulario.field_102.name)[-4:] + " - " + formulario.contract_id.employee_id.name + ".xls"
                wb.save(nombre)
                out = open(nombre,"rb").read().encode("base64")
                obj_formulario.write(cr, uid, formulario.id, {'archivo':out, 'name':str(formulario.field_102.name)[-4:] + " - " + formulario.contract_id.employee_id.name + ".xls"})

                #creacion rdep
                tipidret='P'
                if formulario.field_202.id_type=='c':
                    tipidret='C'
                #rdep = etree.Element('rdep')
                datRetRelDep = etree.Element('datRetRelDep')
                #etree.SubElement(datRetRelDep, 'numRuc').text = "XXXXXXXXXXXXX"
                #etree.SubElement(datRetRelDep, 'anio').text = str(formulario.field_102.name)[-4:]

                #datRetRelDep = etree.Element('datRetRelDep')
                
                empleado = etree.Element('empleado')
                etree.SubElement( empleado, 'benGalpg' ).text = 'NO'
                etree.SubElement( empleado, 'tipIdRet' ).text = tipidret
                etree.SubElement( empleado, 'idRet' ).text = formulario.field_202.name #estaba ci
                #apellido y nombre unicodedata.normalize('NFKD',cabecera_proveedor).encode('ascii','ignore')
                etree.SubElement(empleado,'apellidoTrab' ).text = unicodedata.normalize('NFKD',formulario.field_202.employee_first_lastname[0:98]).encode('ascii','ignore')
                etree.SubElement(empleado,'nombreTrab' ).text = unicodedata.normalize('NFKD',formulario.field_202.employee_first_name[0:98]).encode('ascii','ignore')
#                etree.SubElement( empleado, 'apellidoTrab' ).text = formulario.field_202.employee_first_lastname
#                etree.SubElement( empleado, 'nombreTrab' ).text = formulario.field_202.employee_first_name
                etree.SubElement( empleado, 'estab' ).text = '001'
                etree.SubElement( empleado, 'residenciaTrab' ).text = '01'
                etree.SubElement( empleado, 'paisResidencia' ).text = '593'
                etree.SubElement( empleado, 'aplicaConvenio' ).text = 'NA'
                aux_disca = '01'
                if formulario.field_202.discapacitado:
                    aux_disca = '02'
                etree.SubElement( empleado, 'tipoTrabajDiscap' ).text = aux_disca
                aux_porcentaje = 0
                if formulario.field_202.porcentaje_discapacidad>0:
                    aux_porcentaje = int(formulario.field_202.porcentaje_discapacidad)
                etree.SubElement( empleado, 'porcentajeDiscap' ).text = str(aux_porcentaje)
                tip_id_discap = 'N'
                etree.SubElement( empleado, 'tipIdDiscap' ).text = tip_id_discap
                id_discap = '999'
                if formulario.field_202.id_conadis:
                    id_discap = formulario.field_202.id_conadis
                etree.SubElement( empleado, 'idDiscap' ).text = '999'
          #      if formulario.field_202.address:
          #          etree.SubElement( empleado, 'dirCal' ).text = formulario.field_202.address.replace("/",'')[:20]
          #      else:
          #          etree.SubElement( empleado, 'dirCal' ).text = 'SN'
          #      etree.SubElement( empleado, 'dirNum' ).text = 'SN'#str(formulario.field_202.num_casa)
          #      etree.SubElement( empleado, 'dirCiu' ).text = formulario.field_202.canton_id.code
          #      etree.SubElement( empleado, 'dirProv' ).text = formulario.field_202.state_id.code
          #      etree.SubElement( empleado, 'tel' ).text = str(formulario.field_202.work_phone).rjust(9,'0')
                #etree.SubElement( empleado, 'sisSalNet' ).text = str(1)
#                etree.SubElement(datRetRelDep, empleado)
                datRetRelDep.append(empleado)
                ####hasta aqui va en el tag de empleado
                etree.SubElement( datRetRelDep, 'suelSal' ).text = str("%0.2f" % abs(formulario.field_301))
                etree.SubElement( datRetRelDep, 'sobSuelComRemu' ).text = str("%0.2f" % abs(formulario.field_303)) 
                etree.SubElement( datRetRelDep, 'partUtil' ).text = str("%0.2f" % abs(formulario.field_305))
                etree.SubElement( datRetRelDep, 'intGrabGen' ).text = str("%0.2f" % abs(formulario.field_307))
                etree.SubElement( datRetRelDep, 'impRentEmpl' ).text = str("%0.2f" % abs(formulario.field_381))
                etree.SubElement( datRetRelDep, 'decimTer' ).text = str("%0.2f" % abs(formulario.field_311))
                etree.SubElement( datRetRelDep, 'decimCuar' ).text = str("%0.2f" % abs(formulario.field_313))
                etree.SubElement( datRetRelDep, 'fondoReserva' ).text = str("%0.2f" % abs(formulario.field_315))
                etree.SubElement( datRetRelDep, 'salarioDigno' ).text = str("%0.2f" % abs(0))
                etree.SubElement( datRetRelDep, 'otrosIngRenGrav' ).text = str("%0.2f" % abs(0))
#                etree.SubElement( datRetRelDep, 'desauOtras' ).text = str("%0.2f" % abs(formulario.field_317))
                etree.SubElement( datRetRelDep, 'ingGravConEsteEmpl' ).text = str("%0.2f" % abs(formulario.field_349))
                etree.SubElement( datRetRelDep, 'sisSalNet' ).text = '1'
                etree.SubElement( datRetRelDep, 'apoPerIess' ).text = str("%0.2f" % abs(formulario.field_351))
                etree.SubElement( datRetRelDep, 'aporPerIessConOtrosEmpls' ).text = str("%0.2f" % abs(formulario.field_353))
                #dedcucciones
                #sql="select * from hr_projection_line l,hr_anual_projection p where l.pl_id=%i'1' and p.fy_id=%i'4' and p.contract_id=%i'1180'" % (,,)
                #cr.execute(sql)
                #res=cr.fetchall()
                etree.SubElement( datRetRelDep, 'deducVivienda' ).text = str("%0.2f" % abs(formulario.field_361))
                etree.SubElement( datRetRelDep, 'deducSalud' ).text = str("%0.2f" % abs(formulario.field_363))
                etree.SubElement( datRetRelDep, 'deducEduca' ).text = str("%0.2f" % abs(formulario.field_365))
                etree.SubElement( datRetRelDep, 'deducAliement' ).text = str("%0.2f" % abs(formulario.field_367))
                etree.SubElement( datRetRelDep, 'deducVestim' ).text = str("%0.2f" % abs(formulario.field_369))
                etree.SubElement( datRetRelDep, 'exoDiscap' ).text = str("%0.2f" % abs(formulario.field_371))
                etree.SubElement( datRetRelDep, 'exoTerEd' ).text = str("%0.2f" % abs(formulario.field_373))
                #etree.SubElement( datRetRelDep, 'impRentEmpl' ).text = str("%0.2f" % abs(formulario.field_381))
                #etree.SubElement( datRetRelDep, 'subTotal' ).text = str("%0.2f" % abs(formulario.field_351))
                #etree.SubElement( datRetRelDep, 'numRet' ).text = str(0)
                #etree.SubElement( datRetRelDep, 'numMesEmplead' ).text = str(int(formulario.field_353))
                etree.SubElement( datRetRelDep, 'basImp' ).text = str("%0.2f" % abs(formulario.field_399))
                #etree.SubElement( datRetRelDep, 'deduccGastosOtrEmpl' ).text = str("%0.2f" % abs(formulario.field_403))
                #etree.SubElement( datRetRelDep, 'otrRebjOtrEmpl' ).text = str("%0.2f" % abs(formulario.field_405))
                
                etree.SubElement( datRetRelDep, 'impRentCaus' ).text = str("%0.2f" % abs(formulario.field_401))
                etree.SubElement( datRetRelDep, 'valRetAsuOtrosEmpls' ).text = str("%0.2f" % abs(0))
                etree.SubElement( datRetRelDep, 'valImpAsuEsteEmpl' ).text = str("%0.2f" % abs(0))
                etree.SubElement( datRetRelDep, 'valRet' ).text = str("%0.2f" % abs(formulario.field_407))
#                etree.SubElement( datRetRelDep, 'valorImpempAnter' ).text = str("%0.2f" % abs(formulario.field_403))
#                etree.SubElement( datRetRelDep, 'anioRet' ).text = str(formulario.field_102.name)[-4:]

                retRelDep.append(datRetRelDep)

                #name = "%s%s.XML" % ("RDEP", strftime("%Y"))
                #self.write(cr, uid, ids, {'archivo': out})
        #file = etree.tostring(datRetRelDep, pretty_print=True, encoding='iso-8859-1')
        #rdep.append(retRelDep)
        rdep.append(retRelDep)
        file = etree.tostring(rdep, pretty_print=True, encoding='iso-8859-1')
        buf=StringIO.StringIO()
        buf.write(file)
        out=base64.encodestring(buf.getvalue())
        buf.close()
        #name = "%s%s.XML" % ("RDEP", strftime("%Y"))
        self.write(cr, uid, ids, {'archivo_rdep': out})

        #n_archivo = self.crear_zip("formularios"+str(asistente.name2.name)[-4:])
    #comprimido = open(n_archivo,"rb").read().encode("base64")
    #return self.write(cr, uid, ids, {'archivo_base':comprimido})    

    def crear_lineas(self, cr, uid, ids, context=None):
#        usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
        parameter_obj = self.pool.get('ir.config_parameter')
        obj_contract = self.pool.get("hr.contract")
        obj_formulario = self.pool.get("sri.107")
        rol_obj = self.pool.get('hr.payslip')
        rule_obj = self.pool.get('hr.salary.rule')
        payslip_line_obj = self.pool.get('hr.payslip.line')
#        ids_contract = obj_contract.search(cr, uid, [('activo', '=', True)])
        #archivo del formulario 107
        #aqui tomar el addons que este en los parametros de configuracion
   #     addons_ids = parameter_obj.search(cr, uid, [('key','=','addons')],limit=1)
   #     addons = parameter_obj.browse(cr, uid, addons_ids[0]).value
        xls_path = addons.get_module_resource('gt_hr_sri107','xls','107.xls')
        rb = open_workbook(xls_path,formatting_info=True)
        #print xls_path
        
       
        #file = etree.tostring(rdep, pretty_print=True, encoding='iso-8859-1')
        
        for asistente in self.browse(cr, uid, ids, context):
            #archivo del rdep
            usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
            ruc='001'
            try:
                ruc = usuario.company_id.ruc_company
            except:
                pass
            rdep = etree.Element('rdep')
            etree.SubElement(rdep, 'numRuc').text = ruc.rjust(13,'0')
            etree.SubElement(rdep, 'anio').text = str(asistente.name2.name)[-4:]
            retRelDep = etree.Element('retRelDep')
            #directorio para archivos excel sri
            directorio = os.system("mkdir formularios"+str(asistente.name2.name)[-4:])
            ids_formularios = obj_formulario.search(cr, uid, [('head_id', '=', asistente.id)])
            if ids_formularios:
                obj_formulario.unlink(cr, uid, ids_formularios)
            #sacar todos los contratos de los roles del periodo no solo los activo
            aux_sql = """select contract_id from hr_payslip where date_from>='%s' and date_to<='%s' group by contract_id"""%(asistente.name2.date_start,asistente.name2.date_stop)
            cr.execute(aux_sql)
            ids_contract = []
            for id_contract in cr.fetchall():
                ids_contract.append(id_contract[0])
            for contrato in obj_contract.browse(cr, uid, ids_contract, context):
                #verificar si hay roles en el anio en curso 
                roles_period = rol_obj.search(cr, uid, [('date_from','>=',asistente.name2.date_start),('date_to','<=',asistente.name2.date_stop),
                                                        ('employee_id','=',contrato.employee_id.id)])
                #if not roles_period:
                #    continue
                #if not aporte personal
                rule_iess = rule_obj.search(cr, uid, [('code','=','IESS_PERSONAL')])
                if rule_iess:
                    payslip_line_iess_ids = payslip_line_obj.search(cr, uid, [('salary_rule_id','in',rule_iess),('employee_id', '=', contrato.employee_id.id),
                                                                              ('slip_id','in',roles_period)])
                #if not payslip_line_iess_ids:
                #    continue
                id_formulario = obj_formulario.create(cr, uid, {'field_102': asistente.name2.id,
                                                                'field_202': contrato.employee_id.id,
                                                                'contract_id':contrato.id,
                                                                'head_id': asistente.id})
                obj_formulario.calcular_formulario(cr, uid, [id_formulario], context)
                
                for formulario in obj_formulario.browse(cr, uid, [id_formulario], context):
                    #inicio rdep
                    
                    
                    #escritura de datos en el formulario de excel
                    wb = copy(rb)
                    ws = wb.get_sheet(0)
                    
                    #campo 102
                    anio = str(formulario.field_102.name)[-4:]
                    ws.write(3,14,anio[:1])
                    ws.write(3,15,anio[1:2])
                    ws.write(3,16,anio[2:3])
                    ws.write(3,17,anio[3:4])
                    #campo 106
                    ws.write(7,15,formulario.field_106)
                    #campo 105
                    if formulario.field_105:
                        ws.write(7,1,formulario.field_105[:1])
                        ws.write(7,2,formulario.field_105[1:2])
                        ws.write(7,3,formulario.field_105[2:3])
                        ws.write(7,4,formulario.field_105[3:4])
                        ws.write(7,5,formulario.field_105[4:5])
                        ws.write(7,6,formulario.field_105[5:6])
                        ws.write(7,7,formulario.field_105[6:7])
                        ws.write(7,8,formulario.field_105[7:8])
                        ws.write(7,9,formulario.field_105[8:9])
                        ws.write(7,10,formulario.field_105[9:10])
                    #campo 201
                    ws.write(10,1,contrato.employee_id.name)
                    #campo 202
                    ws.write(10,15,contrato.employee_id.complete_name)
                    #campos liquidacion de impuestos
                    ws.write(13,21,formulario.field_301)
                    ws.write(14,21,formulario.field_303)
                    ws.write(15,21,formulario.field_305)
                    ws.write(16,21,formulario.field_307)
                    ws.write(17,21,formulario.field_311)
                    ws.write(18,21,formulario.field_313)
                    ws.write(19,21,formulario.field_315)
                    ws.write(20,21,formulario.field_317)
                    ws.write(21,21,formulario.field_351)
                    ws.write(22,21,formulario.field_353)
                    ws.write(23,21,formulario.field_361)
                    ws.write(24,21,formulario.field_363)
                    ws.write(25,21,formulario.field_365)
                    ws.write(26,21,formulario.field_367)
                    ws.write(27,21,formulario.field_369)
                    ws.write(28,21,formulario.field_371)
                    ws.write(29,21,formulario.field_373)
                    ws.write(30,20,formulario.field_381)
                    ws.write(31,21,formulario.field_399)
                    ws.write(32,21,formulario.field_401)
                    ws.write(33,21,formulario.field_403)
                    ws.write(34,21,formulario.field_405)
                    ws.write(35,21,formulario.field_407)
                    ws.write(36,21,formulario.field_349)
                    
                    #almacenamiento de datos del formulario en excel
                    
                    nombre = "formularios" + str(formulario.field_102.name)[-4:] + "/" + str(formulario.field_102.name)[-4:] + " - " + contrato.employee_id.name + ".xls"
                    wb.save(nombre)
                    out = open(nombre,"rb").read().encode("base64")
                    obj_formulario.write(cr, uid, formulario.id, {'archivo':out, 'name':str(formulario.field_102.name)[-4:] + " - " + contrato.employee_id.name + ".xls"})
                    
                    #creacion rdep
                    tipidret='3'
                    if formulario.field_202.id_type=='c':
                        tipidret='2'
                    #rdep = etree.Element('rdep')
                    datRetRelDep = etree.Element('datRetRelDep')
                    #etree.SubElement(datRetRelDep, 'numRuc').text = "XXXXXXXXXXXXX"
                    #etree.SubElement(datRetRelDep, 'anio').text = str(formulario.field_102.name)[-4:]
                    
                    #datRetRelDep = etree.Element('datRetRelDep')
                    etree.SubElement( datRetRelDep, 'tipIdRet' ).text = tipidret
                    etree.SubElement( datRetRelDep, 'idRet' ).text = formulario.field_202.name #estaba ci
                    if formulario.field_202.address:
                        etree.SubElement( datRetRelDep, 'dirCal' ).text = formulario.field_202.address.replace("/",'')[:20]
                    else:
                        etree.SubElement( datRetRelDep, 'dirCal' ).text = 'SN'
                    etree.SubElement( datRetRelDep, 'dirNum' ).text = 'SN'#str(formulario.field_202.num_casa)
                    aux_ccode = "SN"
                    if formulario.field_202.canton_id:
                        if formulario.field_202.canton_id.code:
                            aux_ccode = formulario.field_202.canton_id.code
                    etree.SubElement( datRetRelDep, 'dirCiu' ).text = aux_ccode#formulario.field_202.canton_id.code
                    aux_pcode = "SN"
                    if formulario.field_202.state_id:
                        if formulario.field_202.state_id.code:
                            aux_pcode = formulario.field_202.state_id.code
                    etree.SubElement( datRetRelDep, 'dirProv' ).text = aux_pcode#formulario.field_202.state_id.code
                    etree.SubElement( datRetRelDep, 'tel' ).text = str(formulario.field_202.work_phone).rjust(9,'0')
                    etree.SubElement( datRetRelDep, 'sisSalNet' ).text = str(1)
                    etree.SubElement( datRetRelDep, 'suelSal' ).text = str("%0.2f" % abs(formulario.field_301))
                    etree.SubElement( datRetRelDep, 'sobSuelComRemu' ).text = str("%0.2f" % abs(formulario.field_303)) 
                    etree.SubElement( datRetRelDep, 'decimTer' ).text = str("%0.2f" % abs(formulario.field_311))
                    etree.SubElement( datRetRelDep, 'decimCuar' ).text = str("%0.2f" % abs(formulario.field_313))
                    etree.SubElement( datRetRelDep, 'fondoReserva' ).text = str("%0.2f" % abs(formulario.field_315))
                    etree.SubElement( datRetRelDep, 'salarioDigno' ).text = str("%0.2f" % abs(0))
                    etree.SubElement( datRetRelDep, 'partUtil' ).text = str("%0.2f" % abs(formulario.field_305))
                    etree.SubElement( datRetRelDep, 'intGrabGen' ).text = str("%0.2f" % abs(formulario.field_307))
                    etree.SubElement( datRetRelDep, 'desauOtras' ).text = str("%0.2f" % abs(formulario.field_317))
                    etree.SubElement( datRetRelDep, 'apoPerIess' ).text = str("%0.2f" % abs(formulario.field_351))
                    etree.SubElement( datRetRelDep, 'aporPerIessConOtrosEmpls' ).text = str("%0.2f" % abs(formulario.field_353))
                    #dedcucciones
                    #sql="select * from hr_projection_line l,hr_anual_projection p where l.pl_id=%i'1' and p.fy_id=%i'4' and p.contract_id=%i'1180'" % (,,)
                    #cr.execute(sql)
                    #res=cr.fetchall()
                    etree.SubElement( datRetRelDep, 'deducVivienda' ).text = str("%0.2f" % abs(formulario.field_361))
                    etree.SubElement( datRetRelDep, 'deducSalud' ).text = str("%0.2f" % abs(formulario.field_363))
                    etree.SubElement( datRetRelDep, 'deducEduca' ).text = str("%0.2f" % abs(formulario.field_365))
                    etree.SubElement( datRetRelDep, 'deducAliement' ).text = str("%0.2f" % abs(formulario.field_367))
                    etree.SubElement( datRetRelDep, 'deducVestim' ).text = str("%0.2f" % abs(formulario.field_369))
                    etree.SubElement( datRetRelDep, 'rebEspDiscap' ).text = str("%0.2f" % abs(formulario.field_371))
                    etree.SubElement( datRetRelDep, 'rebEspTerEd' ).text = str("%0.2f" % abs(formulario.field_373))
                    etree.SubElement( datRetRelDep, 'impRentEmpl' ).text = str("%0.2f" % abs(formulario.field_381))
                    #etree.SubElement( datRetRelDep, 'subTotal' ).text = str("%0.2f" % abs(formulario.field_351))
                    #etree.SubElement( datRetRelDep, 'numRet' ).text = str(0)
                    #etree.SubElement( datRetRelDep, 'numMesEmplead' ).text = str(int(formulario.field_353))
                    #etree.SubElement( datRetRelDep, 'deduccGastosOtrEmpl' ).text = str("%0.2f" % abs(formulario.field_403))
                    #etree.SubElement( datRetRelDep, 'otrRebjOtrEmpl' ).text = str("%0.2f" % abs(formulario.field_405))
                    etree.SubElement( datRetRelDep, 'basImp' ).text = str("%0.2f" % abs(formulario.field_399))
                    etree.SubElement( datRetRelDep, 'impRentCaus' ).text = str("%0.2f" % abs(formulario.field_401))
                    etree.SubElement( datRetRelDep, 'valRet' ).text = str("%0.2f" % abs(formulario.field_407))
                    etree.SubElement( datRetRelDep, 'valorImpempAnter' ).text = str("%0.2f" % abs(formulario.field_403))
                    etree.SubElement( datRetRelDep, 'anioRet' ).text = str(formulario.field_102.name)[-4:]
                    
                    retRelDep.append(datRetRelDep)
                    
                    #name = "%s%s.XML" % ("RDEP", strftime("%Y"))
                    #self.write(cr, uid, ids, {'archivo': out})
            #file = etree.tostring(datRetRelDep, pretty_print=True, encoding='iso-8859-1')
            #rdep.append(retRelDep)
            rdep.append(retRelDep)
            file = etree.tostring(rdep, pretty_print=True, encoding='iso-8859-1')
            buf=StringIO.StringIO()
            buf.write(file)
            out=base64.encodestring(buf.getvalue())
            buf.close()
            #name = "%s%s.XML" % ("RDEP", strftime("%Y"))
            self.write(cr, uid, ids, {'archivo_rdep': out})
            
            #n_archivo = self.crear_zip("formularios"+str(asistente.name2.name)[-4:])
        #comprimido = open(n_archivo,"rb").read().encode("base64")
        #return self.write(cr, uid, ids, {'archivo_base':comprimido})
    
empresa_107()




#class wizard_107(osv.osv_memory):
class wizard_107(osv.osv):
    _name = "sri.107"
    
    def get_employee(self, cr, uid, context=None):
        return context['active_id']
    
    def _compute_399(self, cr, uid, ids, a, b, c):
        sri = self.pool.get('sri.107')
        res = {}
        aux = 0
        for t in self.browse(cr, uid, ids):
            aux = t.field_301 + t.field_303 + t.field_305 + t.field_381 + t.field_307 - t.field_351 - t.field_353 - t.field_361 - t.field_363 - t.field_365 - t.field_367 - t.field_369 - t.field_371 - t.field_373
        res[t.id] = aux
        return res

    def _compute_349(self, cr, uid, ids, a, b, c):
        sri = self.pool.get('sri.107')
        res = {}
        aux = 0
        for t in self.browse(cr, uid, ids):
            aux = t.field_301 + t.field_303 + t.field_305 + t.field_381 
        res[t.id] = aux
        return res

    _columns = {
                'name': fields.char('Descripción', size=50),
                'codigo': fields.char('Numero', size=50),
                'head_id': fields.many2one('empresa.107', 'Formulario Empresa'),
                #'employee_id': fields.many2one('hr.employee', 'Empleado'),
                'field_102': fields.many2one('hr.work.period', 'Ejercicio Fiscal - 102'),
                'field_103': fields.date('Fecha - 103'),
                'field_105': fields.char('Empleador - RUC - 105', size=13),
                'field_106': fields.char('Empleador - Nombre - 106', size=50),
                'field_201': fields.char('Empleado - Cedula o Pasaporte - 201', size=15),
                #'field_202': fields.char('Empleado - Nombre - 202', size=50),
                'field_202': fields.many2one('hr.employee', 'Empleado - Nombre - 202'),
        'contract_id':fields.many2one('hr.contract','Contrato'),
                'field_301': fields.float('Sueldos y salarios - 301'),
                'field_303': fields.float('Sobresueldos, comisiones, bonos y otras remuneraciones gravadas - 303'),
                'field_305': fields.float('Participacion de utilidades - 305'),
                'field_307': fields.float('Ingresos gravados generados con otros empleadores - 307'),
                #'field_309': fields.float('Fondos de reserva - 309'),
                'field_311': fields.float('Decimo Tercero - 311'),
                'field_313': fields.float('Decimo Cuarto - 313'),
                'field_315': fields.float('Fondo de Reserva - 315'),
                'field_317': fields.float('Otros ingresos en relacion de dependencia que no constituyen renta gravada - 317'),
                'field_351': fields.float('Aporte Personal IESS con este empleador - 351'),
                'field_353': fields.float('Aporte Personal IESS con otros Empleadores - 353'),
                'field_361': fields.float('Deduccion gastos personales - Vivienda - 361'),
                'field_363': fields.float('Deduccion gastos personales - Salud - 363'),
                'field_365': fields.float('Deduccion gastos personales - Educacion - 365'),
                'field_367': fields.float('Deduccion gastos personales - Alimentacion - 367'),
                'field_369': fields.float('Deduccion gastos personales - Vestimenta - 369'),
                'field_371': fields.float('Exoneracion por discapacidad - 371'),
                'field_373': fields.float('Exoneracion por tercera edad - 373'),
                'field_381': fields.float('Impuesto a la renta asumido por este empleador - 381'),
                'field_399': fields.function(_compute_399,string='Base imponible Gravada - 399',type="float",store=True),
                #fields.float('Base imponible Gravada - 399'),
                'field_401': fields.float('Impuesto a la renta causado - 401'),
                'field_403': fields.float('Impuesto a la renta retenido y asumido por empleadores durante el periodo declarado - 403'),
                'field_405': fields.float('Impuesto a la renta asumido por este empleador - 405'),
                'field_407': fields.float('Impuesto a la renta retenido al trabajador por este empleador - 407'),
                #'field_349': fields.float('Ingresos gravados con este empleador - 349'),
                'field_349':fields.function(_compute_349,string='Base imponible Gravada - 399',type="float",store=True),
                'detalle': fields.text('Detalle'),
                'archivo': fields.binary('Archivo', readonly=True),
                'state': fields.selection([('draft','Borrador'),('done','Aprobado'),('cancel','Cancelado')],'Estado'),
                }
    
    _defaults = {
                 #'employee_id': get_employee,
                 'field_103': time.strftime('%Y-%m-%d'),
                 'state': 'draft',
                 }
    
    def aprobar(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'done'})
    
    def cancelar(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'cancel'})
    
    def calcular_formulario(self, cr, uid, ids, context=None):
        rule_obj = self.pool.get('hr.salary.rule')
        contract_obj = self.pool.get('hr.contract')
        obj_period = self.pool.get('hr.work.period.line')
        tabla_pool = self.pool.get('hr.base.retention')
        line_pool = self.pool.get('hr.base.retention.line')
        obj_provision = self.pool.get('hr.provision.line')
        obj_dec_tercer = self.pool.get('hr.decimo.tercero')
        obj_dec_cuarto = self.pool.get('hr.decimo.cuarto')
        obj_projection = self.pool.get('hr.anual.projection')
        obj_payslip = self.pool.get('hr.payslip')
        payslip_line_obj = self.pool.get('hr.payslip.line')
        obj_renta = self.pool.get('hr.anual.rent.tax')
        
        usuario = self.pool.get('res.users').browse(cr, uid, uid, context)
        
        for formulario in self.browse(cr, uid, ids, context):
            datos = {
                     'codigo': '',
                     'field_105': '',
                     'field_106': '',
                     'field_201': '',
                'field_301': 0.0,
                'field_303': 0.0,
                'field_305': 0.0,
                'field_307': 0.0,
                'field_311': 0.0,
                'field_313': 0.0,
                'field_315': 0.0,
                'field_317': 0.0,
                'field_351': 0.0,
                'field_353': 0.0,
                'field_361': 0.0,
                'field_363': 0.0,
                'field_365': 0.0,
                'field_367': 0.0,
                'field_369': 0.0,
                'field_371': 0.0,
                'field_373': 0.0,
                'field_381': 0.0,
                'field_399': 0.0,
                'field_401': 0.0,
                'field_403': 0.0,
                'field_405': 0.0,
                'field_407': 0.0,
                'field_349': 0.0,
                     'detalle': '',
                     }
            try:
                obj_extras = self.pool.get('hr.rubro')
                ids_extras = obj_extras.search(cr, uid, [('period_id','=',formulario.field_102.id),('contract_id','=',formulario.contract_id.id)])
                for extra in obj_extras.browse(cr, uid, ids_extras):
                    datos[extra.casillero] = datos[extra.casillero] + extra.valor
            except:
                pass
            period_ids = obj_period.search(cr, uid, [('period_id','=',formulario.field_102.id)])
            for period_id in period_ids:
                payslip_ids = obj_payslip.search(cr, uid, [('period_id', '=', period_id),
                                                           ('employee_id', '=', formulario.field_202.id)])
                for payslip in obj_payslip.browse(cr, uid, payslip_ids, context):
                    if usuario.company_id.partner_id.name:
                        datos['field_106'] = usuario.company_id.partner_id.name
                    try:
                        datos['field_105'] = usuario.company_id.partner_id.ced_ruc
                    except:
                        pass
                    datos['field_201'] = payslip.employee_id.name
                    datos['field_301'] = datos['field_301'] + payslip.basic#basic_before_leaves
#                    datos['detalle'] = datos['detalle'] + '\n' + payslip.period_id.name + ' - 301 - SUELDO: ' + str(payslip.basic_before_leaves) 
                    datos['detalle'] = datos['detalle'] + '\n' + payslip.period_id.name + ' - 301 - SUELDO: ' + str(payslip.basic) 
                    for linea in payslip.line_ids:
                        contrato = linea.contract_id
                        #aqui en ves de category_id va salary_rule_id
                        if (linea.category_id.name in ('ING','APT')) and (( "Hora" in linea.salary_rule_id.name)):
                            datos['field_301'] = datos['field_301'] + linea.amount
                            datos['detalle'] = datos['detalle'] + '\n' + payslip.period_id.name + ' - 301 - ' + linea.salary_rule_id.name + ': ' + str(linea.amount)
                        if (linea.category_id.name in ('ING','APT')) and ('RESERVA' not in linea.salary_rule_id.name) and ( "Hora" not in linea.salary_rule_id.name):
                            datos['field_303'] = datos['field_303'] + linea.amount
                            datos['detalle'] = datos['detalle'] + '\n' + payslip.period_id.name + ' - 303 - ' + linea.salary_rule_id.name + ': ' + str(linea.amount)
                        if ('RESERVA' in linea.salary_rule_id.name) or ('Fondos de Reserva' in linea.salary_rule_id.name):
                            datos['field_315'] += linea.amount
                            #datos['field_315'] = datos['field_315'] + linea.amount
                            datos['detalle'] = datos['detalle'] + '\n' + payslip.period_id.name + ' - 315 - ' + linea.salary_rule_id.name + ': ' + str(linea.amount)
                        #if ('IESS' in linea.salary_rule_id.name):
                        #    datos['field_351'] = datos['field_351'] + linea.amount
                        #    datos['detalle'] = datos['detalle'] + '\n' + payslip.period_id.name + ' - 351 - ' + linea.salary_rule_id.name + ': ' + str(linea.amount)
                        #if (linea.category_id.code == 'BALIMENTACION'):
                        #    datos['field_313'] = datos['field_313'] + linea.amount
                        #    datos['detalle'] = datos['detalle'] + '\n' + payslip.period_hr_id.name + ' - 313 - ' + linea.category_id.name + ': ' + str(linea.amount)
                
                    #datos['detalle'] = datos['detalle'] + '\n' + provision.period_id.name + ' - 311 - Decimo tercero: ' + str(tercero.value)
                #    if provision.name=='DECIMO CUARTO':
                #        datos['field_313'] = datos['field_313'] + provision.valor
                #        datos['detalle'] = datos['detalle'] + '\n' + provision.period_id.name + ' - 313 - Decimo cuarto: ' + str(provision.valor)
            projection_ids = obj_projection.search(cr, uid, [('fy_id', '=', formulario.field_102.id),
                                                             ('employee_id', '=', formulario.field_202.id)])  #contract_id
                #print projection_ids
            #toma desde el decimo generado
#            dec_tercer_ids = obj_dec_tercer.search(cr, uid, [('fy_id', '=', formulario.field_102.id),('dec_id','!=',False),
#                                                             ('employee_id', '=', formulario.field_202.id)])
#            if dec_tercer_ids:
#                for tercero in obj_dec_tercer.browse(cr, uid, dec_tercer_ids, context):
#                    datos['field_311'] = datos['field_311'] + tercero.recibir
            #decimo tercero
            dec_tercer_ids = obj_dec_tercer.search(cr, uid, [('fy_id', '=', formulario.field_102.id)],limit=1)
            if dec_tercer_ids:
                total_decimo_3 = 0
                dec_tercer = obj_dec_tercer.browse(cr, uid, dec_tercer_ids[0])
                aux_sql = """select sum(basic),sum(aportable) from hr_payslip where date_from>='%s' and date_to<='%s' and contract_id=%s""" %(dec_tercer.period_start.date_start,dec_tercer.period_end.date_stop,formulario.contract_id.id)
                cr.execute(aux_sql)
                aux_b = aux_ap = 0
                for dec in cr.fetchall():
                    if dec[0]:
                        aux_b = dec[0]
                    if dec[1]:
                        aux_ap = dec[1]
                    total_decimo_3 = (aux_b + aux_ap)/12.00
                datos['field_311'] = datos['field_311'] + total_decimo_3
            #decimo cuarto
            dec_cuarto_ids = obj_dec_cuarto.search(cr, uid, [('fy_id', '=', formulario.field_102.id)],limit=1)
            if dec_cuarto_ids:
                total_decimo_4 = 0
                dec_cuarto = obj_dec_cuarto.browse(cr, uid, dec_cuarto_ids[0])
                roles_emp_ids = obj_payslip.search(cr, uid, [('contract_id','=',formulario.contract_id.id),('date_from','>=',dec_cuarto.period_start.date_start),
                                                             ('date_to','<=',dec_cuarto.period_end.date_stop)])
                if roles_emp_ids:
                    if len(roles_emp_ids)>1:
                        tuple_ids = tuple(roles_emp_ids)
                        operador = 'in'
                    else:
                        tuple_ids = (roles_emp_ids[0])
                        operador = '='
                    aux_sql2="""select sum(number_of_days) from hr_payslip_worked_days where payslip_id %s %s and contract_id=%s"""%(operador,tuple_ids,formulario.contract_id.id)
                    cr.execute(aux_sql2)
                    for dec4 in cr.fetchall():
                        total_decimo_4 = (dec_cuarto.basico*dec4[0])/360.00
                datos['field_313'] = datos['field_313'] + total_decimo_4
            #iess empleado fields_351
            rule_iess = rule_obj.search(cr, uid, [('code','=','IESS_PERSONAL')])
            if rule_iess:
                payslip_line_iess_ids = payslip_line_obj.search(cr, uid, [('salary_rule_id','in',rule_iess),('employee_id', '=', formulario.field_202.id),
                                                                        ('period_id','in',period_ids)])
                if payslip_line_iess_ids:
                    aux_iess = 0
                    for payslip_line_iess_id in payslip_line_iess_ids:
                        payslip_line_iess = payslip_line_obj.browse(cr, uid, payslip_line_iess_id)
                        aux_iess += payslip_line_iess.amount
                    datos['field_351'] = datos['field_351'] + aux_iess
            #decimos 3 cobrados el rol de pagos
#            rule_dec3 = rule_obj.search(cr, uid, [('code','in',('dec3','DEC3'))])
#            if rule_dec3:
#                payslip_line_d3_ids = payslip_line_obj.search(cr, uid, [('salary_rule_id','in',rule_dec3),('employee_id', '=', formulario.field_202.id),
#                                                                        ('period_id','in',period_ids)])
#                if payslip_line_d3_ids:
#                    aux_d3 = 0
#                    for payslip_line_d3_id in payslip_line_d3_ids:
#                        payslip_line_d3 = payslip_line_obj.browse(cr, uid, payslip_line_d3_id)
#                        aux_d3 += payslip_line_d3.amount
#                    datos['field_311'] = datos['field_311'] + aux_d3
#            dec_cuarto_ids = obj_dec_cuarto.search(cr, uid, [('fy_id', '=', formulario.field_102.id),('dec_id','!=',False),
#                                                             ('employee_id', '=', formulario.field_202.id)])
#            if dec_cuarto_ids:
#                for cuarto in obj_dec_cuarto.browse(cr, uid, dec_cuarto_ids, context):
#                    datos['field_313'] = datos['field_313'] + cuarto.recibir
            #decimos 4 cobrados el rol de pagos
#            rule_dec4 = rule_obj.search(cr, uid, [('code','in',('dec4','DEC4'))])
#            if rule_dec4:
#                payslip_line_d4_ids = payslip_line_obj.search(cr, uid, [('salary_rule_id','in',rule_dec4),('employee_id', '=', formulario.field_202.id),
#                                                                        ('period_id','in',period_ids)])
#                if payslip_line_d4_ids:
#                    aux_d4 = 0
#                    for payslip_line_d4_id in payslip_line_d4_ids:
#                        payslip_line_d4 = payslip_line_obj.browse(cr, uid, payslip_line_d4_id)
#                        aux_d4 += payslip_line_d4.amount
#                    datos['field_313'] = datos['field_313'] + aux_d4
            
            for proyeccion in obj_projection.browse(cr, uid, projection_ids, context):
                for linea in proyeccion.line_ids:
                    if linea.projection_id.name=="VIVIENDA":
                        datos['field_361'] = datos['field_361'] + linea.value
                        datos['detalle'] = datos['detalle'] + '\n' + proyeccion.fy_id.name + ' - 361 - Vivienda: ' + str(linea.value)
                    if linea.projection_id.name=="SALUD":
                        datos['field_363'] = datos['field_363'] + linea.value
                        datos['detalle'] = datos['detalle'] + '\n' + proyeccion.fy_id.name + ' - 363 - Salud: ' + str(linea.value)
                    if linea.projection_id.name=="EDUCACION":
                        datos['field_365'] = datos['field_365'] + linea.value
                        datos['detalle'] = datos['detalle'] + '\n' + proyeccion.fy_id.name + ' - 365 - Educacion: ' + str(linea.value)
                    if linea.projection_id.name=="ALIMENTACION":
                        datos['field_367'] = datos['field_367'] + linea.value
                        datos['detalle'] = datos['detalle'] + '\n' + proyeccion.fy_id.name + ' - 367 - Alimentacion: ' + str(linea.value)
                    if linea.projection_id.name=="VESTIMENTA":
                        datos['field_369'] = datos['field_369'] + linea.value
                        datos['detalle'] = datos['detalle'] + '\n' + proyeccion.fy_id.name + ' - 369 - Vestimenta: ' + str(linea.value)
                    if linea.projection_id.name=="ESPECIAL":
                        datos['field_371'] = datos['field_371'] + linea.value
                        datos['detalle'] = datos['detalle'] + '\n' + proyeccion.fy_id.name + ' - 371 - Especial: ' + str(linea.value)
            #Valor retenido
            renta_ids = obj_renta.search(cr, uid, [('fy_id', '=', formulario.field_102.id),
                                                   ('employee_id', '=', formulario.field_202.id)])
            #print renta_ids
            for renta in obj_renta.browse(cr, uid, renta_ids):
                for linea in renta.line_ids:
                    #print linea.valor
                    datos['field_407'] = datos['field_407'] + linea.valor
                    #datos['field_311'] = datos['field_311'] + linea.utilidades
                    datos['field_305'] = datos['field_305'] #+ linea.utilidades
#            datos['field_307'] = 0
#            datos['field_353'] = 0
            datos['field_399'] = datos['field_301'] + datos['field_303'] + datos['field_305'] + datos['field_307'] - datos['field_351'] - datos['field_353'] - datos['field_361'] - datos['field_363'] - datos['field_365'] - datos['field_367'] - datos['field_369'] - datos['field_371'] - datos['field_373'] + datos['field_381']
            #FR
            contract_ids = contract_obj.search(cr, uid, [('employee_id','=',formulario.field_202.id)])
            if not contract_ids:
                continue
                #raise osv.except_osv('Error','No se ha encontrado contrato activo para %s.'%(formulario.field_202.complete_name))
            contrato = contract_obj.browse(cr, uid, contract_ids[0])
            dias = contrato.dias_contrato + contrato.dias_fr
            if dias>=365 and datos['field_315']==0:
                #no cobra en rol los FR toca calcular
                datos['field_315'] = (total_decimo_3) * 0.0833
               # datos['field_315'] = (datos['field_301']) * 0.0833
#                datos['field_315'] = (contrato.wage * 12) * 0.0833
            #calcular meses de trabajo
            date_start = parser.parse(formulario.field_202.contract_id.date_start)
            date_end_form = parser.parse(formulario.field_103)
            dias_contrato = abs(date_end_form - date_start).days
            #meses = (dias_contrato//30.416) + formulario.field_202.contract_id.meses_ant
            meses = (dias_contrato//30.416)
            #if meses>=12:
            #    datos['field_353'] = 12
            #else:
            #    datos['field_353'] = int(meses)
            #301+303+305+381
            datos['field_349'] = datos['field_301'] + datos['field_303'] + datos['field_305'] + datos['field_381']
            #impuesto a la renta
            base = datos['field_399']
            tabla_ids=tabla_pool.search(cr, uid, [('period_id','=',formulario.field_102.id)])
            if tabla_ids:
                for tabla in tabla_ids:
                    linea_ids=line_pool.search(cr, uid,[('retention_id','=',tabla),
                                                        ('basic_fraction','<',datos['field_399']),('excess_to','>',datos['field_399'])])
                    for linea_ in linea_ids:
                        linea=line_pool.browse(cr, uid, linea_)
                        excedente=base-linea.basic_fraction
                        imp_sobre_excedente=excedente*linea.percent/100
                        imp_frac_basica=linea.basic_fraction_tax
                        imp_renta_anual=imp_sobre_excedente+imp_frac_basica
                        datos['field_401'] = imp_renta_anual
                        if datos['field_407']<=0:
                            datos['field_407'] = imp_renta_anual
            datos['codigo'] = self.pool.get('ir.sequence').get(cr, uid, 'sri.107')
            self.write(cr, uid, ids, datos)
            
    def calcular_exportar(self, cr, uid, ids, context=None):
        self.calcular_formulario(cr, uid, ids, context)
        xls_path = addons.get_module_resource('gt_hr_sri107','xls','107.xls')
        rb = open_workbook(xls_path,formatting_info=True)
        directorio = os.system("mkdir formularios")
        for formulario in self.browse(cr, uid, ids, context):
                    #escritura de datos en el formulario de excel
                    wb = copy(rb)
                    ws = wb.get_sheet(0)
                    
                    #campo 102
                    anio = str(formulario.field_102.name)[-4:]
                    ws.write(3,14,anio[:1])
                    ws.write(3,15,anio[1:2])
                    ws.write(3,16,anio[2:3])
                    ws.write(3,17,anio[3:4])
                    #campo 106
                    ws.write(7,15,formulario.field_106)
                    #campo 105
                    if formulario.field_105:
                        ws.write(7,1,formulario.field_105[:1])
                        ws.write(7,2,formulario.field_105[1:2])
                        ws.write(7,3,formulario.field_105[2:3])
                        ws.write(7,4,formulario.field_105[3:4])
                        ws.write(7,5,formulario.field_105[4:5])
                        ws.write(7,6,formulario.field_105[5:6])
                        ws.write(7,7,formulario.field_105[6:7])
                        ws.write(7,8,formulario.field_105[7:8])
                        ws.write(7,9,formulario.field_105[8:9])
                        ws.write(7,10,formulario.field_105[9:10])
                    #campo 201
                    ws.write(10,1,formulario.field_202.name) #estaba ci
                    #campo 202
                    ws.write(10,15,formulario.field_202.complete_name)
                    #campos liquidacion de impuestos
                    ws.write(13,21,formulario.field_301)
                    ws.write(14,21,formulario.field_303)
                    ws.write(15,21,formulario.field_305)
                    ws.write(16,21,formulario.field_307)
                    ws.write(17,21,formulario.field_311)
                    ws.write(18,21,formulario.field_313)
                    ws.write(19,21,formulario.field_315)
                    ws.write(20,21,formulario.field_317)
                    ws.write(21,21,formulario.field_351)
                    ws.write(22,21,formulario.field_353)
                    ws.write(23,21,formulario.field_361)
                    ws.write(24,21,formulario.field_363)
                    ws.write(25,21,formulario.field_365)
                    ws.write(26,21,formulario.field_367)
                    ws.write(27,21,formulario.field_369)
                    ws.write(28,21,formulario.field_371)
                    ws.write(29,21,formulario.field_373)
                    ws.write(30,20,formulario.field_381)
                    ws.write(31,21,formulario.field_399)
                    ws.write(32,21,formulario.field_401)
                    ws.write(33,21,formulario.field_403)
                    ws.write(34,21,formulario.field_405)
                    ws.write(35,21,formulario.field_407)
                    ws.write(36,21,formulario.field_349)
                    
                    #almacenamiento de datos
                    
                    nombre = "formularios/" + str(formulario.field_102.name)[-4:] + " - " + formulario.field_202.name + ".xls"
                    wb.save(nombre)
                    out = open(nombre,"rb").read().encode("base64")
                    self.write(cr, uid, formulario.id, {'archivo':out, 'name':str(formulario.field_102.name)[-4:] + " - " + formulario.field_202.name + ".xls"})

    def regenerar_exportar(self, cr, uid, ids, context=None):
#        self.calcular_formulario(cr, uid, ids, context)
        xls_path = addons.get_module_resource('gt_hr_sri107','xls','107.xls')
        rb = open_workbook(xls_path,formatting_info=True)
        directorio = os.system("mkdir formularios")
        for formulario in self.browse(cr, uid, ids, context):
                    #escritura de datos en el formulario de excel
                    wb = copy(rb)
                    ws = wb.get_sheet(0)
                    
                    #campo 102
                    anio = str(formulario.field_102.name)[-4:]
                    ws.write(3,14,anio[:1])
                    ws.write(3,15,anio[1:2])
                    ws.write(3,16,anio[2:3])
                    ws.write(3,17,anio[3:4])
                    #campo 106
                    ws.write(7,15,formulario.field_106)
                    #campo 105
                    if formulario.field_105:
                        ws.write(7,1,formulario.field_105[:1])
                        ws.write(7,2,formulario.field_105[1:2])
                        ws.write(7,3,formulario.field_105[2:3])
                        ws.write(7,4,formulario.field_105[3:4])
                        ws.write(7,5,formulario.field_105[4:5])
                        ws.write(7,6,formulario.field_105[5:6])
                        ws.write(7,7,formulario.field_105[6:7])
                        ws.write(7,8,formulario.field_105[7:8])
                        ws.write(7,9,formulario.field_105[8:9])
                        ws.write(7,10,formulario.field_105[9:10])
                    #campo 201
                    ws.write(10,1,formulario.field_202.name) #estaba ci
                    #campo 202
                    ws.write(10,15,formulario.field_202.complete_name)
                    #campos liquidacion de impuestos
                    ws.write(13,21,formulario.field_301)
                    ws.write(14,21,formulario.field_303)
                    ws.write(15,21,formulario.field_305)
                    ws.write(16,21,formulario.field_307)
                    ws.write(17,21,formulario.field_311)
                    ws.write(18,21,formulario.field_313)
                    ws.write(19,21,formulario.field_315)
                    ws.write(20,21,formulario.field_317)
                    ws.write(21,21,formulario.field_351)
                    ws.write(22,21,formulario.field_353)
                    ws.write(23,21,formulario.field_361)
                    ws.write(24,21,formulario.field_363)
                    ws.write(25,21,formulario.field_365)
                    ws.write(26,21,formulario.field_367)
                    ws.write(27,21,formulario.field_369)
                    ws.write(28,21,formulario.field_371)
                    ws.write(29,21,formulario.field_373)
                    ws.write(30,20,formulario.field_381)
                    aux_399 = formulario.field_301 + formulario.field_303 + formulario.field_305 + formulario.field_307 - formulario.field_351 - formulario.field_353 - formulario.field_361 - formulario.field_363 - formulario.field_365 - formulario.field_367 - formulario.field_369 - formulario.field_373 - formulario.field_381
                    ws.write(31,21,aux_399)
#                    ws.write(31,21,formulario.field_399)
                    ws.write(32,21,formulario.field_401)
                    ws.write(33,21,formulario.field_403)
                    ws.write(34,21,formulario.field_405)
                    ws.write(35,21,formulario.field_407)
                    ws.write(36,21,formulario.field_349)
                    
                    #almacenamiento de datos
                    
                    nombre = "formularios/" + str(formulario.field_102.name)[-4:] + " - " + formulario.field_202.name + ".xls"
                    wb.save(nombre)
                    out = open(nombre,"rb").read().encode("base64")
                    self.write(cr, uid, formulario.id, {'archivo':out, 'name':str(formulario.field_102.name)[-4:] + " - " + formulario.field_202.name + ".xls"})
            
    def print_107(self, cr, uid, ids, context=None):
        '''
        directorio = os.system("locate ls.107")
        print directorio
        for formulario in self.browse(cr, uid, ids): 
            rb = open_workbook('107.xls',formatting_info=True)
            wb = copy(rb)
            ws = wb.get_sheet(0)
            ws.write(3,14,"2")
            ws.write(3,15,"0")
            ws.write(3,16,"1")
            ws.write(3,17,"2")
            nombre = "107_" + formulario.field_202.name + ".xls"
            wb.save(nombre)
            out = open(nombre,"rb").read().encode("base64")
            return self.write(cr, uid, ids, {'archivo': out})
        return False
        '''
        for formulario in self.browse(cr, uid, ids):
            tipidret='3'
            if formulario.field_202.id_type=='c':
                tipidret='2'
            #rdep = etree.Element('rdep')
            datRetRelDep = etree.Element('datRetRelDep')
            etree.SubElement(datRetRelDep, 'numRuc').text = "XXXXXXXXXXXXX"
            etree.SubElement(datRetRelDep, 'anio').text = str(formulario.field_102.name)[-4:]
            
            #datRetRelDep = etree.Element('datRetRelDep')
            etree.SubElement( datRetRelDep, 'tipIdRet' ).text = tipidret
            etree.SubElement( datRetRelDep, 'idRet' ).text = formulario.field_202.name
            etree.SubElement( datRetRelDep, 'dirCal' ).text = formulario.field_202.address
            etree.SubElement( datRetRelDep, 'dirNum' ).text = str(formulario.field_202.numero)
            etree.SubElement( datRetRelDep, 'dirCiu' ).text = formulario.field_202.canton_id.code
            etree.SubElement( datRetRelDep, 'dirProv' ).text = formulario.field_202.state_id.code
            etree.SubElement( datRetRelDep, 'tel' ).text = str(formulario.field_202.work_phone)
            etree.SubElement( datRetRelDep, 'sisSalNet' ).text = str(formulario.field_202.contract_id.wage)
            etree.SubElement( datRetRelDep, 'suelSal' ).text = str(formulario.field_301)
            cero="000"
            #sacadera de pu, sacar los roles la deduccion de ese anio
            etree.SubElement( datRetRelDep, 'sobSuelComRemu' ).text = str(formulario.field_303) 
            etree.SubElement( datRetRelDep, 'decimTer' ).text = str(formulario.field_311)
            etree.SubElement( datRetRelDep, 'decimCuar' ).text = str(formulario.field_313)
            etree.SubElement( datRetRelDep, 'fondoReserva' ).text = str(formulario.field_315)
            etree.SubElement( datRetRelDep, 'salarioDigno' ).text = cero
            etree.SubElement( datRetRelDep, 'partUtil' ).text = str(formulario.field_305)
            etree.SubElement( datRetRelDep, 'intGrabGen' ).text = str(formulario.field_307)
            etree.SubElement( datRetRelDep, 'desauOtras' ).text = str(formulario.field_317)
            etree.SubElement( datRetRelDep, 'apoPerIess' ).text = str(formulario.field_351)
            etree.SubElement( datRetRelDep, 'aporPerIessConOtrosEmpls' ).text = str("%0.2f" % abs(formulario.field_353))
            #dedcucciones
            #sql="select * from hr_projection_line l,hr_anual_projection p where l.pl_id=%i'1' and p.fy_id=%i'4' and p.contract_id=%i'1180'" % (,,)
            #cr.execute(sql)
            #res=cr.fetchall()
            etree.SubElement( datRetRelDep, 'deducVivienda' ).text = str(formulario.field_361)
            etree.SubElement( datRetRelDep, 'deducSalud' ).text = str(formulario.field_363)
            etree.SubElement( datRetRelDep, 'deducEduca' ).text = str(formulario.field_365)
            etree.SubElement( datRetRelDep, 'deducAliment' ).text = str(formulario.field_367)
            etree.SubElement( datRetRelDep, 'deducVestim' ).text = str(formulario.field_369)
            etree.SubElement( datRetRelDep, 'rebEspDiscap' ).text = str(formulario.field_371)
            etree.SubElement( datRetRelDep, 'rebEspTerEd' ).text = str(formulario.field_373)
            etree.SubElement( datRetRelDep, 'impRentEmpl' ).text = str(formulario.field_381)
            #etree.SubElement( datRetRelDep, 'subTotal' ).text = str(formulario.field_351)
            #etree.SubElement( datRetRelDep, 'numRet' ).text = cero
            #etree.SubElement( datRetRelDep, 'numMesEmpl' ).text = str(formulario.field_353)

            #etree.SubElement( datRetRelDep, 'deduccGastosOtrEmpl' ).text = str(formulario.field_403)
            #etree.SubElement( datRetRelDep, 'otrRebjOtrEmpl' ).text = str(formulario.field_405)
            #formulario.field_361 - formulario.field_363 - formulario.field_365 - formulario.field_367 - formulario.field_369 
            etree.SubElement( datRetRelDep, 'basImp' ).text = str(formulario.field_399)
            etree.SubElement( datRetRelDep, 'impRentCaus' ).text = str(formulario.field_401)
            etree.SubElement( datRetRelDep, 'valRet' ).text = str(formulario.field_407)
            etree.SubElement( datRetRelDep, 'valorImpempAnter' ).text = str(formulario.field_403)
            etree.SubElement( datRetRelDep, 'anioRet' ).text = str(formulario.field_102.name)[-4:]
            
            file = etree.tostring(datRetRelDep, pretty_print=True, encoding='iso-8859-1')
            buf=StringIO.StringIO()
            buf.write(file)
            out=base64.encodestring(buf.getvalue())
            buf.close()
            #name = "%s%s.XML" % ("RDEP", strftime("%Y"))
            self.write(cr, uid, ids, {'archivo': out})
    
wizard_107()

