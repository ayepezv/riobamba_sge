# -*- coding: utf-8 -*-
##############################################################################
#
#    Author :  Mario Chogllo
#
#
##############################################################################

import time
import base64
import StringIO
from lxml import etree
from lxml.etree import DocumentInvalid
import os
import datetime
import logging

from osv import osv
from osv import fields

tpIdProv = {
    'ruc' : '01',
    'cedula' : '02',
    'pasaporte' : '03',
}

tpIdCliente = {
    'ruc': '04',
    'cedula': '05',
    'pasaporte': '06',
    'consumidor_final':'07',
    }


class wizard_ats(osv.TransientModel):

    _name = 'wizard.ats'
    _description = 'Anexo Transaccional Simplificado'
    __logger = logging.getLogger(_name)

    def _get_period(self, cr, uid, context):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False

    def _get_company(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id.id

    def act_cancel(self, cr, uid, ids, context):
        return {'type':'ir.actions.act_window_close'}

    def process_lines(self, cr, uid, lines):
        """
        @temp: {'332': {baseImpAir: 0,}}
        @data_air: [{baseImpAir: 0, ...}]
        """
        data_air = []
        flag = False
        temp = {}
        for line in lines:
            if line.tax_group in ['ret_ir', 'no_ret_ir']:
                if not temp.get(line.base_code_id.code):
                    temp[line.base_code_id.code] = {'baseImpAir': 0, 'valRetAir': 0}
                temp[line.base_code_id.code]['baseImpAir'] += line.base_amount
                temp[line.base_code_id.code]['codRetAir'] = line.base_code_id.code
                temp[line.base_code_id.code]['porcentajeAir'] = line.percent and float(line.percent) or 0.00
                temp[line.base_code_id.code]['valRetAir'] += abs(line.amount)
        for k,v in temp.items():
            data_air.append(v)
        return data_air

    def process_lines_linea(self, cr, uid, linea):
        """
        @temp: {'332': {baseImpAir: 0,}}
        @data_air: [{baseImpAir: 0, ...}]
        """
        data_air = []
        flag = False
        temp = {}
        for line in linea.invoice_line_tax_id:
            if line.tax_group in ['ret_ir', 'no_ret_ir']:
                if not temp.get(line.base_code_id.code):
                    temp[line.base_code_id.code] = {'baseImpAir': 0, 'valRetAir': 0}
                temp[line.base_code_id.code]['baseImpAir'] += linea.price_subtotal
                temp[line.base_code_id.code]['codRetAir'] = line.base_code_id.code
                temp[line.base_code_id.code]['porcentajeAir'] = line.percent and float(line.percent) or 0.00
#                temp[line.base_code_id.code]['porcentajeAir'] = line.porcentaje and float(line.porcentaje) or 0.00
                temp[line.base_code_id.code]['valRetAir'] += abs(linea.monto_retir)
        for k,v in temp.items():
            data_air.append(v)
        return data_air    

    def convertir_fecha(self, fecha):
        """
        fecha: '2012-12-15'
        return: '15/12/2012'
        """
        f = fecha.split('-')
        date = datetime.date(int(f[0]), int(f[1]), int(f[2]))
        return date.strftime('%d/%m/%Y')


    def _get_ventas_estab(self, cr, period_id, auth_id, journal_id):
        sql_ventas = "SELECT sum(amount_vat+amount_vat_cero+amount_novat) AS base \
                      FROM account_invoice, account_journal j \
                      WHERE account_invoice.journal_id=j.id \
                      AND account_invoice.type = 'out_invoice' \
                      AND account_invoice.state IN ('open','paid') \
                      AND period_id = %s \
                      AND journal_id = %s \
                      AND j.auth_id = %s"  % (period_id, journal_id, auth_id)
        cr.execute(sql_ventas)
        result = cr.fetchone()[0]
        return '%.2f' % (result and result or 0.00)    

    def _get_ventas_siim(self, cr, period_id, wiz):
        import psycopg2
        parameter_obj = self.pool.get('ir.config_parameter')
        #ejecutar el sql para que traiga los datos
#        usuario_ids = parameter_obj.search(self.cr, self.uid, [('key','=','usrsiim')],limit=1)
#        usuario = parameter_obj.browse(self.cr, self.uid, usuario_ids[0]).value
#        clave_ids = parameter_obj.search(self.cr, self.uid, [('key','=','passsiim')],limit=1)
#        clave = parameter_obj.browse(self.cr, self.uid, clave_ids[0]).value
#        base_ids = parameter_obj.search(self.cr, self.uid, [('key','=','basesiim')],limit=1)
#        base = parameter_obj.browse(self.cr, self.uid, base_ids[0]).value
#        server_ids = parameter_obj.search(self.cr, self.uid, [('key','=','serverip')],limit=1)
#        server = parameter_obj.browse(self.cr, self.uid, server_ids[0]).value
#        puerto=5432
#        dbconn_siim = psycopg2.connect(dbname=base, host=server, port=5432, user=usuario, password=clave)
#        cursor = dbconn_siim.cursor()
        str_date_ini = "'" + wiz.period_id.date_start + "'"
        str_date_end = "'" + wiz.period_id.date_stop + "'"
#        aux = """SELECT substr(co."nombreXml", 9,3),substr(co."nombreXml", 13,3),sum(base_impon_cero),sum(base_impon_iva),sum(iva_doce),sum(iva_cero),sum(total) from clave_online co where estado=1 and "fechaActualizacion" BETWEEN %s and %s GROUP BY 1,2""" % (str_date_ini,str_date_end)
#        cursor.execute(aux)
        aux_total = aux_subtotal = 0
#        for row in cursor.fetchall():
#            aux_subtotal += (row[2] + row[3])
#            aux_total += aux_subtotal
        return '%.2f' % (aux_total and aux_total or 0.00)

    def _get_ventas(self, cr, period_id, journal_id=False):
        sql_ventas = "SELECT sum(amount_vat+amount_vat_cero+amount_novat) AS base \
                      FROM account_invoice \
                      WHERE type = 'out_invoice' AND state IN ('open','paid') AND period_id = %s" % period_id
        if journal_id:
            where = " AND journal_id=%s" % journal_id
            sql_ventas += where
        cr.execute(sql_ventas)
        result = cr.fetchone()[0]
        return '%.2f' % (result and result or 0.00)

    def _get_ret_iva2(self, invoice):
        """
        Return (valorRetBien10, valorRetServ20)
        """
        retBien10 = 0
        retServ20 = 0
        retBien30 = 0
        retServ50 = 0
        retServ70 = 0
        retServ100 = 0
        for tax in invoice.tax_line:
            if tax.tax_group == 'ret_vat_srv':
                if tax.percent == '20':
                    retServ20 += abs(tax.tax_amount)
                elif tax.percent == '50':
                    retServ50 += abs(tax.tax_amount)
                elif tax.percent == '70':
                    retServ70 += abs(tax.tax_amount)
                elif tax.percent == '100':
                    retServ100 += abs(tax.tax_amount)
            elif tax.tax_group == 'ret_vat_b':
                if tax.percent == '10':
                    retBien10 += abs(tax.tax_amount)
                elif tax.percent == '30':
                    retBien30 += abs(tax.tax_amount)
        return retBien10, retServ20,retBien30,retServ50,retServ70,retServ100

    def _get_ret_iva(self, invoice):
        """
        Return (valorRetServicios, valorRetServ100)
        """
        retServ = 0
        retServ100 = 0
        for tax in invoice.tax_line:
            if tax.tax_group == 'ret_vat_srv':
                if tax.percent == '100':
                    retServ100 += abs(tax.tax_amount)
                else:
                    retServ += abs(tax.tax_amount)
        return retServ, retServ100

    def _get_ret_iva_linea(self, linea):
        """
        Return (valorRetServicios, valorRetServ100)
        """
        retServ = 0
        retServ100 = 0
        for tax in linea.invoice_line_tax_id:
            if tax.tax_group == 'ret_vat_srv':
                if tax.percent == '100':
                    retServ100 += abs(linea.monto_retserv)
                else:
                    retServ += abs(linea.monto_retserv)
        return retServ, retServ100    

    def act_export_ats(self, cr, uid, ids, context):
        conret = 0
        inv_obj = self.pool.get('account.invoice')
        journal_obj = self.pool.get('account.journal')
        digital_obj = self.pool.get('digital.retention')
        wiz = self.browse(cr, uid, ids)[0]
        period_id = wiz.period_id.id
        period_aux = wiz.period_id
        ruc = wiz.company_id.partner_id.ced_ruc
        ats = etree.Element('iva')
        etree.SubElement(ats, 'TipoIDInformante').text = 'R'
        etree.SubElement(ats, 'IdInformante').text = str(ruc)
        etree.SubElement(ats, 'razonSocial').text = wiz.company_id.name
        period = self.pool.get('account.period').browse(cr, uid, [period_id])[0]
        etree.SubElement(ats, 'Anio').text = time.strftime('%Y',time.strptime(period.date_start, '%Y-%m-%d'))        
        etree.SubElement(ats, 'Mes'). text = time.strftime('%m',time.strptime(period.date_start, '%Y-%m-%d'))
#        total_ventas = self._get_ventas(cr, period_id)
#        total_ventas_siim = self._get_ventas_siim(cr, period_id,wiz)
        import psycopg2
        parameter_obj = self.pool.get('ir.config_parameter')
        #ejecutar el sql para que traiga los datos
#        usuario_ids = parameter_obj.search(cr, uid, [('key','=','usrsiim')],limit=1)
#        usuario = parameter_obj.browse(cr, uid, usuario_ids[0]).value
#        clave_ids = parameter_obj.search(cr, uid, [('key','=','passsiim')],limit=1)
#        clave = parameter_obj.browse(cr, uid, clave_ids[0]).value
#        base_ids = parameter_obj.search(cr, uid, [('key','=','basesiim')],limit=1)
#        base = parameter_obj.browse(cr, uid, base_ids[0]).value
#        server_ids = parameter_obj.search(cr, uid, [('key','=','serverip')],limit=1)
#        server = parameter_obj.browse(cr, uid, server_ids[0]).value
#        puerto=5432
#        dbconn_siim = psycopg2.connect(dbname=base, host=server, port=5432, user=usuario, password=clave)
#        cursor = dbconn_siim.cursor()
        str_date_ini = "'" + wiz.period_id.date_start + "'"
        str_date_end = "'" + wiz.period_id.date_stop + "'"
#        aux = """SELECT substr(co."nombreXml", 9,3),substr(co."nombreXml", 13,3),sum(base_impon_cero),sum(base_impon_iva),sum(iva_doce),sum(iva_cero),sum(total) from clave_online co where estado=1 and "fechaActualizacion" BETWEEN %s and %s GROUP BY 1,2""" % (str_date_ini,str_date_end)
#        cursor.execute(aux)
        aux_total = aux_subtotal = aux_total_estab = 0
#        for row in cursor.fetchall():
#            aux_total_estab += 1
#            if row[2] or row[3]:
#                aux_subtotal = (row[2] + row[3])
#                aux_total += aux_subtotal
        etree.SubElement(ats, 'numEstabRuc').text = '001'#str(aux_total_estab).zfill(3)
        etree.SubElement(ats, 'totalVentas').text = '%.2f' % (aux_total and aux_total or 0.00)
        etree.SubElement(ats, 'codigoOperativo').text = 'IVA'
        compras = etree.Element('compras')
        '''Facturas de Compra con retenciones '''
        inv_ids = []
        #busca por fechas de factura
        if wiz.opt=='Todas':
            inv_ids = inv_obj.search(cr, uid, [('state','in',['open','paid','draft']),
                                   #            ('period_id','=',period_id),
                                               ('date_invoice','>=',period_aux.date_start),('date_invoice','<=',period_aux.date_stop),
                                               ('type','in',['in_invoice','liq_purchase']),
                                               ('company_id','=',wiz.company_id.id)])
#            digital_ids = digital_obj.search(cr, uid, [('state','=','autorizado'),('period_id','=',period_id)])
#            if digital_ids:
#                for digital_id in digital_ids:
#                    digital = digital_obj.browse(cr, uid, digital_id)
#                    inv_ids.append(digital.invoice_id.id)
        else:
            inv_ids = inv_obj.search(cr, uid, [('state','in',['open','paid']),
#                                               ('period_id','=',period_id),
                                               ('date_invoice','>=',period_aux.date_start),('date_invoice','<=',period_aux.date_stop),
                                               ('type','in',['in_invoice','liq_purchase']),
                                               ('company_id','=',wiz.company_id.id)])
        self.__logger.info("Compras registradas: %s" % len(inv_ids))
        for inv in inv_obj.browse(cr, uid, inv_ids):
            detallecompras = etree.Element('detalleCompras')
            #considerar multi factura
            if inv.reference_type == 'invoice_partner':
                #considerar todas las facturas
#                if not inv.retention_id:
#                    continue
#                    if not inv.retention_id.digital_id:
#                        continue
#                        if not inv.retention_id.digital_id.log:
#                            continue
                etree.SubElement(detallecompras, 'codSustento').text = inv.sustento_id.code
                if not inv.partner_id.ced_ruc:
                    raise osv.except_osv('Datos incompletos', 'No ha ingresado toda los datos de %s' % inv.partner_id.name)
                #siempre RUC
                etree.SubElement(detallecompras, 'tpIdProv').text = tpIdProv['ruc']
                aux_ced_ruc = inv.partner_id.ced_ruc
                if len(inv.partner_id.ced_ruc)==10:
                    aux_ced_ruc = inv.partner_id.ced_ruc + '001'
                etree.SubElement(detallecompras, 'idProv').text = aux_ced_ruc
#                etree.SubElement(detallecompras, 'tpIdProv').text = tpIdProv[inv.partner_id.type_ced_ruc]
#                etree.SubElement(detallecompras, 'idProv').text = inv.partner_id.ced_ruc
                if inv.auth_inv_id:
                    tcomp = inv.auth_inv_id.type_id.code
                else:
                    tcomp = '03'
                etree.SubElement(detallecompras, 'tipoComprobante').text = tcomp
                etree.SubElement(detallecompras, 'parteRel').text = 'NO'
                etree.SubElement(detallecompras, 'fechaRegistro').text = self.convertir_fecha(inv.date_invoice)
                #en electronicas no pide serie y emision
                if inv.type == 'in_invoice':
                    if inv.auth_inv_id.serie_entidad or inv.auth_inv_id.serie_emision:
                        se = inv.auth_inv_id.serie_entidad
                        pe = inv.auth_inv_id.serie_emision
                    else:
                        se = '001'
                        pe = '001'
                    #sec = '%09d' % int(inv.reference)
                    if inv.new_number and len(inv.new_number)==15:
                        sec = inv.new_number[6:]
                    else:
                        sec = '%09d' % int(inv.reference)
                    #sec = '%09d' % int(inv.new_number)
                    auth = inv.auth_inv_id.name
                elif inv.type == 'liq_purchase':
                    se = inv.journal_id.auth_id.serie_entidad
                    pe = inv.journal_id.auth_id.serie_emision
                    sec = inv.number[8:]
                    auth = inv.journal_id.auth_id.name
                etree.SubElement(detallecompras, 'establecimiento').text = se
                etree.SubElement(detallecompras, 'puntoEmision').text = pe
                etree.SubElement(detallecompras, 'secuencial').text = sec
                etree.SubElement(detallecompras, 'fechaEmision').text = self.convertir_fecha(inv.date_invoice)
                etree.SubElement(detallecompras, 'autorizacion').text = auth
                etree.SubElement(detallecompras, 'baseNoGraIva').text = inv.amount_novat==0 and '0.00' or '%.2f'%inv.amount_novat
                etree.SubElement(detallecompras, 'baseImponible').text = '%.2f'%inv.amount_vat_cero
                etree.SubElement(detallecompras, 'baseImpGrav').text = '%.2f'%inv.amount_vat
                etree.SubElement(detallecompras, 'baseImpExe').text = '0.00'
                etree.SubElement(detallecompras, 'montoIce').text = '0.00'
                etree.SubElement(detallecompras, 'montoIva').text = '%.2f'%inv.amount_tax
                #cambiado
                valRetBien10,valRetServ20,valRetBienes30,valRetServicios50,valRetServicios70,valRetServ100 = self._get_ret_iva2(inv)
                etree.SubElement(detallecompras, 'valRetBien10').text = '%.2f'%valRetBien10
                etree.SubElement(detallecompras, 'valRetServ20').text = '%.2f'%valRetServ20
                etree.SubElement(detallecompras, 'valorRetBienes').text = '%.2f'%valRetBienes30
                etree.SubElement(detallecompras, 'valRetServ50').text = '%.2f'%valRetServicios50
                etree.SubElement(detallecompras, 'valorRetServicios').text = '%.2f'%valRetServicios70
                etree.SubElement(detallecompras, 'valRetServ100').text = '%.2f'%valRetServ100
                etree.SubElement(detallecompras, 'totbasesImpReemb').text = '0.00'
#                etree.SubElement(detallecompras, 'valorRetBienes').text = '%.2f'%abs(inv.taxed_ret_vatb)
#                valorRetServicios, valorRetServ100 = self._get_ret_iva(inv)
#                etree.SubElement(detallecompras, 'valorRetServicios').text = '%.2f'%valorRetServicios
#                etree.SubElement(detallecompras, 'valRetServ100').text = '%.2f'%valorRetServ100
                ########
                pagoExterior = etree.Element('pagoExterior')
                etree.SubElement(pagoExterior, 'pagoLocExt').text = '01'
                etree.SubElement(pagoExterior, 'paisEfecPago').text = 'NA'
                etree.SubElement(pagoExterior, 'aplicConvDobTrib').text = 'NA'
                etree.SubElement(pagoExterior, 'pagExtSujRetNorLeg').text = 'NA'
                detallecompras.append(pagoExterior)

                if inv.amount_pay >= wiz.pay_limit:
                    formasDePago = etree.Element('formasDePago')
                    etree.SubElement(formasDePago, 'formaPago').text = '01'
                    detallecompras.append(formasDePago)
                if inv.retention_ir or inv.no_retention_ir:
                    air = etree.Element('air')
                    data_air = self.process_lines(cr, uid, inv.tax_line)
                    for da in data_air:
                        detalleAir = etree.Element('detalleAir')
                        etree.SubElement(detalleAir, 'codRetAir').text = da['codRetAir']
                        etree.SubElement(detalleAir, 'baseImpAir').text = '%.2f' % da['baseImpAir']
                        etree.SubElement(detalleAir, 'porcentajeAir').text = '%.2f' % da['porcentajeAir']
                        etree.SubElement(detalleAir, 'valRetAir').text = '%.2f' % da['valRetAir']
                        air.append(detalleAir)
                    detallecompras.append(air)

                flag = False            
                if inv.retention_ir or inv.retention_vat:
#                    flag = True
#                    etree.SubElement(detallecompras, 'estabRetencion1').text = flag and inv.journal_id.auth_ret_id.serie_entidad or '000'
#                    etree.SubElement(detallecompras, 'ptoEmiRetencion1').text = flag and inv.journal_id.auth_ret_id.serie_emision or '000'
#                    if inv.retention_id:
#                        etree.SubElement(detallecompras, 'secRetencion1').text = flag and inv.retention_id.number[6:] or '%09d'%0
#                    else:
#                        etree.SubElement(detallecompras, 'secRetencion1').text= '0'
                    if inv.retention_id:
                        if inv.retention_id.digital_id:
                            flag = True
                            etree.SubElement(detallecompras, 'estabRetencion1').text = flag and inv.journal_id.auth_ret_id.serie_entidad or '000'
                            etree.SubElement(detallecompras, 'ptoEmiRetencion1').text = flag and inv.journal_id.auth_ret_id.serie_emision or '000'
                            if inv.retention_id:
                                etree.SubElement(detallecompras, 'secRetencion1').text = flag and inv.retention_id.number[6:] or '%09d'%0
                            else:
                                etree.SubElement(detallecompras, 'secRetencion1').text= '0'
                            if inv.retention_id.digital_id.autorizacion:
                                #si no es digit toma de la  manual o cero
                                if inv.retention_id.digital_id.autorizacion_manual:
                                    if len(inv.retention_id.digital_id.autorizacion_manual)>1:
                                        etree.SubElement(detallecompras, 'autRetencion1').text = flag and inv.retention_id.digital_id.autorizacion_manual
                                else:
                                    etree.SubElement(detallecompras, 'autRetencion1').text = flag and inv.retention_id.digital_id.autorizacion
                            elif inv.retention_id.digital_id.log:
                                aux_text = inv.retention_id.digital_id.log
                                lista=aux_text.splitlines()
                                etree.SubElement(detallecompras, 'autRetencion1').text = flag and lista[4]
                            etree.SubElement(detallecompras, 'fechaEmiRet1').text = flag and self.convertir_fecha(inv.retention_id.date)
                        else:
                            etree.SubElement(detallecompras, 'autRetencion1').text = '000'
                    #else:
                    #    etree.SubElement(detallecompras, 'autRetencion1').text = '000'
                    #if inv.retention_id:
                    #    etree.SubElement(detallecompras, 'fechaEmiRet1').text = flag and self.convertir_fecha(inv.retention_id.date)
                    #else:
                    #    etree.SubElement(detallecompras, 'fechaEmiRet1').text = '00/00/0000'
                etree.SubElement(detallecompras, 'docModificado').text = '000'
                etree.SubElement(detallecompras, 'estabModificado').text = '000'
                etree.SubElement(detallecompras, 'ptoEmiModificado').text = '000'
                etree.SubElement(detallecompras, 'secModificado').text = '000000000'
                etree.SubElement(detallecompras, 'autModificado').text = '0000000000000000000000000000000000000000000000000'
#                etree.SubElement(detallecompras, 'baseImpExeReemb').text = '0.00'
                #etree.SubElement(detallecompras, 'reembolso').text = '0.00'
                aux_total_bases = inv.amount_vat + inv.amount_vat_cero
                #etree.SubElement(detallecompras, 'totbasesImpReemb').text = '%.2f'%aux_total_bases 
                compras.append(detallecompras)                                                  
            elif inv.reference_type == 'multi_invoice':
                for linv in inv.invoice_line:
                    detallecompras = etree.Element('detalleCompras')
                    etree.SubElement(detallecompras, 'codSustento').text = linv.sustento_id.code
                    if not inv.partner_id.ced_ruc:
                        raise osv.except_osv('Datos incompletos', 'No ha ingresado toda los datos de %s' % inv.partner_id.name)
                    #siempre RUC
                    etree.SubElement(detallecompras, 'tpIdProv').text = tpIdProv['ruc']
                    aux_ced_ruc = inv.partner_id.ced_ruc
                    if len(inv.partner_id.ced_ruc)==10:
                        aux_ced_ruc = inv.partner_id.ced_ruc + '001'
#                    etree.SubElement(detallecompras, 'tpIdProv').text = tpIdProv[linv.invoice_id.partner_id.type_ced_ruc]
#                    etree.SubElement(detallecompras, 'idProv').text = linv.invoice_id.partner_id.ced_ruc
                    if linv.auth_id:
                        tcomp = inv.auth_inv_id.type_id.code
                    else:
                        tcomp = '03'
                    etree.SubElement(detallecompras, 'tipoComprobante').text = tcomp
                    etree.SubElement(detallecompras, 'fechaRegistro').text = self.convertir_fecha(linv.date_invoice)
                    se = linv.auth_id.serie_entidad
                    pe = linv.auth_id.serie_emision
                    sec = linv.invoice_number_complete[6:]
                    auth = linv.auth_id.name
                    etree.SubElement(detallecompras, 'establecimiento').text = se
                    etree.SubElement(detallecompras, 'puntoEmision').text = pe
                    etree.SubElement(detallecompras, 'secuencial').text = sec
                    etree.SubElement(detallecompras, 'fechaEmision').text = self.convertir_fecha(linv.date_invoice)
                    etree.SubElement(detallecompras, 'autorizacion').text = auth
                    etree.SubElement(detallecompras, 'baseNoGraIva').text = linv.base_noiva==0 and '0.00' or '%.2f'%linv.base_noiva
                    etree.SubElement(detallecompras, 'baseImponible').text = '%.2f' % linv.base_cero
                    etree.SubElement(detallecompras, 'baseImpGrav').text = '%.2f' % linv.base_doce
                    etree.SubElement(detallecompras, 'baseImpExe').text = '0.00'
                    etree.SubElement(detallecompras, 'montoIce').text = '0.00'
                    etree.SubElement(detallecompras, 'montoIva').text = '%.2f' % linv.monto_iva
                    
                    etree.SubElement(detallecompras, 'valorRetBienes').text = '%.2f' % abs(linv.monto_retbienes)
                    valorRetServicios, valorRetServ100 = self._get_ret_iva_linea(linv)
                    etree.SubElement(detallecompras, 'valorRetServicios').text = '%.2f'%valorRetServicios
                    etree.SubElement(detallecompras, 'valRetServ100').text = '%.2f'%valorRetServ100
                    pagoExterior = etree.Element('pagoExterior')
                    etree.SubElement(pagoExterior, 'pagoLocExt').text = '01'
                    etree.SubElement(pagoExterior, 'paisEfecPago').text = 'NA'
                    etree.SubElement(pagoExterior, 'aplicConvDobTrib').text = 'NA'
                    etree.SubElement(pagoExterior, 'pagExtSujRetNorLeg').text = 'NA'
                    detallecompras.append(pagoExterior)
                    
                    if linv.price_subtotal * 1.12  >= wiz.pay_limit: # dirty hack suponer retencion
                        formasDePago = etree.Element('formasDePago')
                        etree.SubElement(formasDePago, 'formaPago').text = '01'
                        detallecompras.append(formasDePago)
                    if linv.has_retention:
                        air = etree.Element('air')
                        data_air = self.process_lines_linea(cr, uid, linv)
                        for da in data_air:
                            detalleAir = etree.Element('detalleAir')
                            etree.SubElement(detalleAir, 'codRetAir').text = da['codRetAir']
                            etree.SubElement(detalleAir, 'baseImpAir').text = '%.2f' % da['baseImpAir']
                            etree.SubElement(detalleAir, 'porcentajeAir').text = '%.2f' % da['porcentajeAir']
                            etree.SubElement(detalleAir, 'valRetAir').text = '%.2f' % da['valRetAir']
                            air.append(detalleAir)
                        detallecompras.append(air)
                        etree.SubElement(detallecompras, 'estabRetencion1').text = flag and linv.invoice_id.journal_id.auth_ret_id.serie_entidad or '000'
                        etree.SubElement(detallecompras, 'ptoEmiRetencion1').text = flag and linv.invoice_id.journal_id.auth_ret_id.serie_emision or '000'
                        etree.SubElement(detallecompras, 'secRetencion1').text = flag and linv.invoice_id.retention_id.number[6:] or '%09d'%0
                        if linv.invoice_id.retention_id.digital_id.autorizacion:
                            if linv.invoice_id.retention_id.digital_id.autorizacion_manual:
                                if len(linv.invoice_id.retention_id.digital_id.autorizacion_manual)>1:
                                    etree.SubElement(detallecompras, 'autRetencion1').text = flag and linv.invoice_id.retention_id.digital_id.autorizacion_manual
                            else:
                                etree.SubElement(detallecompras, 'autRetencion1').text = flag and linv.invoice_id.retention_id.digital_id.autorizacion
                        else:
                            aux_text = linv.invoice_id.retention_id.digital_id.log
                            lista=aux_text.splitlines()
                            etree.SubElement(detallecompras, 'autRetencion1').text = flag and lista[4]
                        etree.SubElement(detallecompras, 'fechaEmiRet1').text = flag and self.convertir_fecha(linv.invoice_id.retention_id.date)

                    compras.append(detallecompras)                                        

        ats.append(compras)
        total_ventas_erp = 0
        total_ventas = 0
        if float(total_ventas) > 0:
            aux = '''SELECT identificador_cliente,tipo_identificador_cliente,nombres,direccion,telefono,concepto_venta,base_impon_cero,base_impon_iva,iva_doce,iva_cero,total,num_autorizacion,"fechaActualizacion","fechaActualizacion","claveAcceso" from clave_online co where estado=1 and "fechaActualizacion" BETWEEN %s and %s GROUP BY identificador_cliente,tipo_identificador_cliente,nombres,direccion,telefono,concepto_venta,base_impon_cero,base_impon_iva,iva_doce,iva_cero,total ,num_autorizacion ,"fechaActualizacion","fechaActualizacion","claveAcceso",id_factura''' % (str_date_ini,str_date_end)
            cursor.execute(aux)
            ventas = etree.Element('ventas')
            pdata = {}
            for row in cursor.fetchall():
                if not pdata.get(row[0], False):
                    if row[0]:
                        aux_idCliente = row[0]
                        if row[1]:
                            aux_tpIdCliente = str(row[1]).zfill(2)
                            if len(row[0])>10:
                                aux_tpIdCliente = '04'
                            elif len(row[0])<10:
                                aux_tpIdCliente = '06'
                        else:
                            aux_tpIdCliente = '06'
                    else:
                        aux_idCliente = '9999999999'
                        aux_tpIdCliente = '06'
                    partner_data = {row[0]: {'tpIdCliente': aux_tpIdCliente,
                                             'idCliente': aux_idCliente,
                                             'numeroComprobantes': 0,
                                             'basenoGraIva': 0,
                                             'baseImponible': 0,
                                             'baseImpGrav': 0,
                                             'montoIva': 0,
                                             'valorRetRenta': 0,
                                             'valorRetIva': 0}}
                    pdata.update(partner_data)
                pdata[row[0]]['numeroComprobantes'] += 1
                pdata[row[0]]['basenoGraIva'] += 0#inv.amount_novat
                if row[6]:
                    pdata[row[0]]['baseImponible'] += row[6]
                if row[7]:
                    pdata[row[0]]['baseImpGrav'] += row[7]
                if row[8]:
                    pdata[row[0]]['montoIva'] += row[8]
                pdata[row[0]]['tipoComprobante'] = '18'
            for k, v in pdata.items():
                detalleVentas = etree.Element('detalleVentas')
                etree.SubElement(detalleVentas, 'tpIdCliente').text = str(v['tpIdCliente'])#tpIdCliente[v['tpIdCliente']]
                if v['idCliente']:
                    etree.SubElement(detalleVentas, 'idCliente').text = v['idCliente']
                else:
                    etree.SubElement(detalleVentas, 'idCliente').text = '9999999999'
                etree.SubElement(detalleVentas, 'parteRelVtas').text = 'NO'
                etree.SubElement(detalleVentas, 'tipoComprobante').text = v['tipoComprobante']
                etree.SubElement(detalleVentas, 'numeroComprobantes').text = str(v['numeroComprobantes'])
                etree.SubElement(detalleVentas, 'baseNoGraIva').text = '%.2f' % v['basenoGraIva']
                etree.SubElement(detalleVentas, 'baseImponible').text = '%.2f' % v['baseImponible']
                etree.SubElement(detalleVentas, 'baseImpGrav').text = '%.2f' % v['baseImpGrav']
                etree.SubElement(detalleVentas, 'montoIva').text = '%.2f' % v['montoIva']
                etree.SubElement(detalleVentas, 'valorRetIva').text = '%.2f' % v['valorRetIva']
                etree.SubElement(detalleVentas, 'valorRetRenta').text = '%.2f' % v['valorRetRenta']
                ventas.append(detalleVentas)
            ats.append(ventas)
        if float(total_ventas_erp) > 0:
            """VENTAS DECLARADAS"""
            ventas = etree.Element('ventas')
            inv_ids = inv_obj.search(cr, uid, [('state','in',['open','paid']),
                                               ('period_id','=',period_id),
                                               ('type','=','out_invoice'),
                                               ('company_id','=',wiz.company_id.id)])
            pdata = {}
            self.__logger.info("Ventas registradas: %s" % len(inv_ids))
            for inv in inv_obj.browse(cr, uid, inv_ids):
                if not pdata.get(inv.partner_id.id, False):
                    partner_data = {inv.partner_id.id: {'tpIdCliente': inv.partner_id.type_ced_ruc,
                                                        'idCliente': inv.partner_id.ced_ruc,
                                                        'numeroComprobantes': 0,
                                                        'basenoGraIva': 0,
                                                        'baseImponible': 0,
                                                        'baseImpGrav': 0,
                                                        'montoIva': 0,
                                                        'valorRetRenta': 0,
                                                        'valorRetIva': 0}}
                    pdata.update(partner_data)
                pdata[inv.partner_id.id]['numeroComprobantes'] += 1
                pdata[inv.partner_id.id]['basenoGraIva'] += inv.amount_novat
                pdata[inv.partner_id.id]['baseImponible'] += inv.amount_vat_cero
                pdata[inv.partner_id.id]['baseImpGrav'] += inv.amount_vat
                pdata[inv.partner_id.id]['montoIva'] += inv.amount_tax
                pdata[inv.partner_id.id]['tipoComprobante'] = inv.journal_id.auth_id.type_id.code
                if inv.retention_ir:
                    data_air = self.process_lines(cr, uid, inv.tax_line)
                    for dt in data_air:
                        pdata[inv.partner_id.id]['valorRetRenta'] += dt['valRetAir']
                pdata[inv.partner_id.id]['valorRetIva'] += abs(inv.taxed_ret_vatb) + abs(inv.taxed_ret_vatsrv)

            for k, v in pdata.items():
                detalleVentas = etree.Element('detalleVentas')
                etree.SubElement(detalleVentas, 'tpIdCliente').text = tpIdCliente[v['tpIdCliente']]
                etree.SubElement(detalleVentas, 'idCliente').text = v['idCliente']
                etree.SubElement(detalleVentas, 'tipoComprobante').text = v['tipoComprobante']
                etree.SubElement(detalleVentas, 'numeroComprobantes').text = str(v['numeroComprobantes'])
                etree.SubElement(detalleVentas, 'baseNoGraIva').text = '%.2f' % v['basenoGraIva']
                etree.SubElement(detalleVentas, 'baseImponible').text = '%.2f' % v['baseImponible']
                etree.SubElement(detalleVentas, 'baseImpGrav').text = '%.2f' % v['baseImpGrav']
                etree.SubElement(detalleVentas, 'montoIva').text = '%.2f' % v['montoIva']
                etree.SubElement(detalleVentas, 'valorRetIva').text = '%.2f' % v['valorRetIva']
                etree.SubElement(detalleVentas, 'valorRetRenta').text = '%.2f' % v['valorRetRenta']
                ventas.append(detalleVentas)
            ats.append(ventas)
        """  VENTAS ESTABLECIMIENTO """
#        ventasEstablecimiento = etree.Element('ventasEstablecimiento')
#        aux = """SELECT substr(co."nombreXml", 9,3),substr(co."nombreXml", 13,3),sum(base_impon_cero),sum(base_impon_iva),sum(iva_doce),sum(iva_cero),sum(total) from clave_online co where estado=1 and "fechaActualizacion" BETWEEN %s and %s GROUP BY 1,2""" % (str_date_ini,str_date_end)
#        cursor.execute(aux)
#        for row in cursor.fetchall():
#            ventaEst = etree.Element('ventaEst')
#            etree.SubElement(ventaEst, 'codEstab').text = row[1]
#            if row[2] or row[3]:
#                etree.SubElement(ventaEst, 'ventasEstab').text = '%.2f' % (row[2] + row[3])
#            else:
#                aux = 0
#                etree.SubElement(ventaEst, 'ventasEstab').text = '%.2f' % aux
#            ventasEstablecimiento.append(ventaEst)
#        ats.append(ventasEstablecimiento)
        """ Ventas establecimiento
        ventasEstablecimiento = etree.Element('ventasEstablecimiento')
        jour_ids = journal_obj.search(cr, uid, [('type','=','sale')])
        for j in journal_obj.browse(cr, uid, jour_ids):
            if not j.auth_id:
                continue
            ventaEst = etree.Element('ventaEst')
            etree.SubElement(ventaEst, 'codEstab').text = j.auth_id.serie_emision
            etree.SubElement(ventaEst, 'ventasEstab').text = self._get_ventas(cr, period_id, j.id)
            ventasEstablecimiento.append(ventaEst)
        ats.append(ventasEstablecimiento) """
        """ Documentos Anulados """
        anulados = etree.Element('anulados')
        inv_ids = inv_obj.search(cr, uid, [('state','=','cancel'),
                                            ('period_id','=',period_id),
                                            ('type','=','out_invoice'),
                                            ('company_id','=',wiz.company_id.id)])
        self.__logger.info("Ventas Anuladas: %s" % len(inv_ids))        
        for inv in inv_obj.browse(cr, uid, inv_ids):
            detalleAnulados = etree.Element('detalleAnulados')
            etree.SubElement(detalleAnulados, 'tipoComprobante').text = inv.journal_id.auth_id.type_id.code
            etree.SubElement(detalleAnulados, 'establecimiento').text = inv.journal_id.auth_id.serie_entidad
            etree.SubElement(detalleAnulados, 'puntoEmision').text = inv.journal_id.auth_id.serie_emision
            etree.SubElement(detalleAnulados, 'secuencialInicio').text = str(int(inv.number[8:]))
            etree.SubElement(detalleAnulados, 'secuencialFin').text = str(int(inv.number[8:]))
            etree.SubElement(detalleAnulados, 'autorizacion').text = inv.journal_id.auth_id.name
            anulados.append(detalleAnulados)
        liq_ids = inv_obj.search(cr, uid, [('state','=','cancel'),
                                            ('period_id','=',period_id),
                                            ('type','=','liq_purchase'),
                                            ('company_id','=',wiz.company_id.id)])
        for inv in inv_obj.browse(cr, uid, liq_ids):
            detalleAnulados = etree.Element('detalleAnulados')
            etree.SubElement(detalleAnulados, 'tipoComprobante').text = inv.journal_id.auth_id.type_id.code
            etree.SubElement(detalleAnulados, 'establecimiento').text = inv.journal_id.auth_id.serie_entidad
            etree.SubElement(detalleAnulados, 'puntoEmision').text = inv.journal_id.auth_id.serie_emision
            etree.SubElement(detalleAnulados, 'secuencialInicio').text = str(int(inv.number[8:]))
            etree.SubElement(detalleAnulados, 'secuencialFin').text = str(int(inv.number[8:]))
            etree.SubElement(detalleAnulados, 'autorizacion').text = inv.journal_id.auth_id.name
            anulados.append(detalleAnulados)
        retention_obj = self.pool.get('account.retention')
        ret_ids = retention_obj.search(cr, uid, [('state','=','cancel'),
                                                 ('in_type','=','ret_out_invoice'),
                                                 ('date','>=',wiz.period_id.date_start),
                                                 ('date','<=',wiz.period_id.date_stop)])
        for ret in retention_obj.browse(cr, uid, ret_ids):
            detalleAnulados = etree.Element('detalleAnulados')
            etree.SubElement(detalleAnulados, 'tipoComprobante').text = ret.auth_id.type_id.code
            etree.SubElement(detalleAnulados, 'establecimiento').text = ret.auth_id.serie_entidad
            etree.SubElement(detalleAnulados, 'puntoEmision').text = ret.auth_id.serie_emision
            etree.SubElement(detalleAnulados, 'secuencialInicio').text = str(int(ret.number[8:]))
            etree.SubElement(detalleAnulados, 'secuencialFin').text = str(int(ret.number[8:]))
            etree.SubElement(detalleAnulados, 'autorizacion').text = ret.auth_id.name
            anulados.append(detalleAnulados)
        ats.append(anulados)
        file_path = os.path.join(os.path.dirname(__file__), 'XSD/ats.xsd')
        schema_file = open(file_path)
        file_ats = etree.tostring(ats, pretty_print=True, encoding='iso-8859-1')
        #validata schema
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        if not wiz.no_validate:
            try:
                xmlschema.assertValid(ats)
            except DocumentInvalid as e:
                raise osv.except_osv('Error de Datos', """El sistema generó el XML pero los datos no pasan la validación XSD del SRI.
                \nLos errores mas comunes son:\n* RUC,Cédula o Pasaporte contiene caracteres no válidos.\n* Números de documentos están duplicados.\n\nEl siguiente error contiene el identificador o número de documento en conflicto:\n\n %s""" % str(e))
        buf = StringIO.StringIO()
        buf.write(file_ats)
        out=base64.encodestring(buf.getvalue())
        buf.close()
        name = "%s%s%s.XML" % ("AT", wiz.period_id.name[:2], wiz.period_id.name[3:8])
        return self.write(cr, uid, ids, {'state': 'export', 'data': out, 'name': name, 'filename': name})
        
    _columns = {
        'opt' : fields.selection([('Todas','Todas')],'Opcion',help="Si usted selecciona retenciones el ats se genera en base a las retenciones electronicas autorizas por el SRI, caso contrario se basa en las facturas validadas"),
        'name' : fields.char('Nombre de Archivo', size=50, readonly=True),
        'fy_id': fields.many2one('account.fiscalyear', 'Ejercicio Fiscal', required=True),
        'period_id' : fields.many2one('account.period', 'Periodo', domain=[('special','=',False)]),
        'company_id': fields.many2one('res.company', 'Compania'),
        'num_estab_ruc': fields.char('Num. de Establecimientos', size=3, required=True),
        'pay_limit': fields.float('Limite de Pago'),
        'data' : fields.binary('Archivo XML'),
        'no_validate': fields.boolean('No Validar'),
        'state' : fields.selection((('choose', 'choose'),
                                    ('export', 'export'))),
        'filename': fields.char('Nombre de Archivo', size=64),
        }

    def _get_fy(self, cr, uid, context=None):
        res = self.pool.get('account.fiscalyear').find(cr, uid)
        return res

    _defaults = {
        'state' : 'choose',
        'period_id': _get_period,
        'company_id': _get_company,
        'fy_id': _get_fy,
        'pay_limit': 1000.00,
        'num_estab_ruc': '001',
        'no_validate':True,
        'opt':'Todas',
    }    

wizard_ats()


class wizard_reoc(osv.TransientModel):

    _name = 'wizard.reoc'
    _description = 'REOC'
    __logger = logging.getLogger(_name)

    def _get_period(self, cr, uid, context):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False

    def _get_company(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id.id

    def act_cancel(self, cr, uid, ids, context):
        return {'type':'ir.actions.act_window_close'}

    def process_lines(self, cr, uid, lines):
        """
        @temp: {'332': {baseImpAir: 0,}}
        @data_air: [{baseImpAir: 0, ...}]
        """
        data_air = []
        flag = False
        temp = {}
        for line in lines:
            if line.tax_group in ['ret_ir', 'no_ret_ir']:
                if not temp.get(line.base_code_id.code):
                    temp[line.base_code_id.code] = {'baseImpAir': 0, 'valRetAir': 0}
                temp[line.base_code_id.code]['baseImpAir'] += line.base_amount
                temp[line.base_code_id.code]['codRetAir'] = line.base_code_id.code
                temp[line.base_code_id.code]['porcentajeAir'] = line.percent and float(line.percent) or 0.00
                temp[line.base_code_id.code]['valRetAir'] += abs(line.amount)
        for k,v in temp.items():
            data_air.append(v)
        return data_air

    def process_lines_linea(self, cr, uid, linea):
        """
        @temp: {'332': {baseImpAir: 0,}}
        @data_air: [{baseImpAir: 0, ...}]
        """
        data_air = []
        flag = False
        temp = {}
        for line in linea.invoice_line_tax_id:
            if line.tax_group in ['ret_ir', 'no_ret_ir']:
                if not temp.get(line.base_code_id.code):
                    temp[line.base_code_id.code] = {'baseImpAir': 0, 'valRetAir': 0}
                temp[line.base_code_id.code]['baseImpAir'] += linea.price_subtotal
                temp[line.base_code_id.code]['codRetAir'] = line.base_code_id.code
                temp[line.base_code_id.code]['porcentajeAir'] = line.percent and float(line.percent) or 0.00
#                temp[line.base_code_id.code]['porcentajeAir'] = line.porcentaje and float(line.porcentaje) or 0.00
                temp[line.base_code_id.code]['valRetAir'] += abs(linea.monto_retir)
        for k,v in temp.items():
            data_air.append(v)
        return data_air    

    def convertir_fecha(self, fecha):
        """
        fecha: '2012-12-15'
        return: '15/12/2012'
        """
        f = fecha.split('-')
        date = datetime.date(int(f[0]), int(f[1]), int(f[2]))
        return date.strftime('%d/%m/%Y')


    def _get_ventas_estab(self, cr, period_id, auth_id, journal_id):
        sql_ventas = "SELECT sum(amount_vat+amount_vat_cero+amount_novat) AS base \
                      FROM account_invoice, account_journal j \
                      WHERE account_invoice.journal_id=j.id \
                      AND account_invoice.type = 'out_invoice' \
                      AND account_invoice.state IN ('open','paid') \
                      AND period_id = %s \
                      AND journal_id = %s \
                      AND j.auth_id = %s"  % (period_id, journal_id, auth_id)
        cr.execute(sql_ventas)
        result = cr.fetchone()[0]
        return '%.2f' % (result and result or 0.00)    


    def _get_ventas(self, cr, period_id, journal_id=False):
        sql_ventas = "SELECT sum(amount_vat+amount_vat_cero+amount_novat) AS base \
                      FROM account_invoice \
                      WHERE type = 'out_invoice' AND state IN ('open','paid') AND period_id = %s" % period_id
        if journal_id:
            where = " AND journal_id=%s" % journal_id
            sql_ventas += where
        cr.execute(sql_ventas)
        result = cr.fetchone()[0]
        return '%.2f' % (result and result or 0.00)

    def _get_ret_iva(self, invoice):
        """
        Return (valorRetServicios, valorRetServ100)
        """
        retServ = 0
        retServ100 = 0
        for tax in invoice.tax_line:
            if tax.tax_group == 'ret_vat_srv':
                if tax.percent == '100':
                    retServ100 += abs(tax.tax_amount)
                else:
                    retServ += abs(tax.tax_amount)
        return retServ, retServ100

    def _get_ret_iva_linea(self, linea):
        """
        Return (valorRetServicios, valorRetServ100)
        """
        retServ = 0
        retServ100 = 0
        for tax in linea.invoice_line_tax_id:
            if tax.tax_group == 'ret_vat_srv':
                if tax.percent == '100':
                    retServ100 += abs(linea.monto_retserv)
                else:
                    retServ += abs(linea.monto_retserv)
        return retServ, retServ100    

    def act_export_reoc(self, cr, uid, ids, context):
        conret = 0
        inv_obj = self.pool.get('account.invoice')
        journal_obj = self.pool.get('account.journal')
        digital_obj = self.pool.get('digital.retention')
        wiz = self.browse(cr, uid, ids)[0]
        period_id = wiz.period_id.id
        ruc = wiz.company_id.partner_id.ced_ruc
        reoc = etree.Element('reoc')
        etree.SubElement(reoc, 'numeroRuc').text = str(ruc)
        period = self.pool.get('account.period').browse(cr, uid, [period_id])[0]
        etree.SubElement(reoc, 'Anio').text = time.strftime('%Y',time.strptime(period.date_start, '%Y-%m-%d'))        
        etree.SubElement(reoc, 'Mes'). text = time.strftime('%m',time.strptime(period.date_start, '%Y-%m-%d'))
        compras = etree.Element('compras')
        '''Facturas de Compra con retenciones '''
        inv_ids = []
        if wiz.opt=='Todas':
            inv_ids = inv_obj.search(cr, uid, [('state','in',['open','paid','draft']),
                                               ('period_id','=',period_id),
                                               ('type','in',['in_invoice','liq_purchase']),
                                               ('company_id','=',wiz.company_id.id)])
        else:
            inv_ids = inv_obj.search(cr, uid, [('state','in',['open','paid']),
                                               ('period_id','=',period_id),
                                               ('type','in',['in_invoice','liq_purchase']),
                                               ('company_id','=',wiz.company_id.id)])
        self.__logger.info("Compras registradas: %s" % len(inv_ids))
        for inv in inv_obj.browse(cr, uid, inv_ids):
            detallecompras = etree.Element('detalleCompras')
            #considerar multi factura
            if inv.reference_type == 'invoice_partner':
                if not inv.partner_id.ced_ruc:
                    raise osv.except_osv('Datos incompletos', 'No ha ingresado toda los datos de %s' % inv.partner_id.name)
                #siempre RUC
                etree.SubElement(detallecompras, 'tpIdProv').text = tpIdProv['ruc']
                aux_ced_ruc = inv.partner_id.ced_ruc
                if len(inv.partner_id.ced_ruc)==10:
                    aux_ced_ruc = inv.partner_id.ced_ruc + '001'
#                etree.SubElement(detallecompras, 'tpIdProv').text = tpIdProv[inv.partner_id.type_ced_ruc]
#                etree.SubElement(detallecompras, 'idProv').text = inv.partner_id.ced_ruc
                if inv.auth_inv_id:
                    tcomp = inv.auth_inv_id.type_id.code
                else:
                    tcomp = '03'
                etree.SubElement(detallecompras, 'tipoComp').text = tcomp
                etree.SubElement(detallecompras, 'fechaRegistro').text = self.convertir_fecha(inv.date_invoice)
                if inv.type == 'in_invoice':
                    se = inv.auth_inv_id.serie_entidad
                    pe = inv.auth_inv_id.serie_emision
                    sec = '%09d' % int(inv.reference)
                    auth = inv.auth_inv_id.name
                elif inv.type == 'liq_purchase':
                    se = inv.journal_id.auth_id.serie_entidad
                    pe = inv.journal_id.auth_id.serie_emision
                    sec = inv.number[8:]
                    auth = inv.journal_id.auth_id.name
                etree.SubElement(detallecompras, 'aut').text = auth
                etree.SubElement(detallecompras, 'estab').text = se
                etree.SubElement(detallecompras, 'ptoEmi').text = pe
                etree.SubElement(detallecompras, 'secuencial').text = sec
                etree.SubElement(detallecompras, 'fechaEmiCom').text = self.convertir_fecha(inv.date_invoice)
                if inv.retention_ir or inv.no_retention_ir:
                    air = etree.Element('air')
                    data_air = self.process_lines(cr, uid, inv.tax_line)
                    for da in data_air:
                        detalleAir = etree.Element('detalleAir')
                        etree.SubElement(detalleAir, 'codRetAir').text = da['codRetAir']
                        etree.SubElement(detalleAir, 'porcentajeAir').text = '%.2f' % da['porcentajeAir']
                        etree.SubElement(detalleAir, 'baseCero').text = '%.2f' % da['baseImpAir']
                        etree.SubElement(detalleAir, 'baseGrav').text = '%.2f' % da['baseImpAir']
                        etree.SubElement(detalleAir, 'baseNoGrav').text = '%.2f' % da['baseImpAir']
                        etree.SubElement(detalleAir, 'valRetAir').text = '%.2f' % da['valRetAir']
                        air.append(detalleAir)
                    detallecompras.append(air)

                flag = False            
                if inv.retention_ir or inv.retention_vat:
                    flag = True
                    if inv.retention_id.digital_id.autorizacion:
                        etree.SubElement(detallecompras, 'autRet').text = flag and inv.retention_id.digital_id.autorizacion
                    else:
                        aux_text = inv.retention_id.digital_id.log
                        lista=aux_text.splitlines()
                        etree.SubElement(detallecompras, 'autRet').text = flag and lista[4]
                    etree.SubElement(detallecompras, 'estabRet').text = flag and inv.journal_id.auth_ret_id.serie_entidad or '000'
                    etree.SubElement(detallecompras, 'ptoEmiRet').text = flag and inv.journal_id.auth_ret_id.serie_emision or '000'
                    etree.SubElement(detallecompras, 'secRet').text = flag and inv.retention_id.number[6:] or '%09d'%0
                    etree.SubElement(detallecompras, 'fechaEmiRet').text = flag and self.convertir_fecha(inv.retention_id.date)
                compras.append(detallecompras)                                                  
        reoc.append(compras)
        file_path = os.path.join(os.path.dirname(__file__), 'XSD/reoc.xsd')
        schema_file = open(file_path)
        file_reoc = etree.tostring(reoc, pretty_print=True, encoding='iso-8859-1')
        #validata schema
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        if not wiz.no_validate:
            try:
                xmlschema.assertValid(reoc)
            except DocumentInvalid as e:
                raise osv.except_osv('Error de Datos', """El sistema generó el XML pero los datos no pasan la validación XSD del SRI.
                \nLos errores mas comunes son:\n* RUC,Cédula o Pasaporte contiene caracteres no válidos.\n* Números de documentos están duplicados.\n\nEl siguiente error contiene el identificador o número de documento en conflicto:\n\n %s""" % str(e))
        buf = StringIO.StringIO()
        buf.write(file_reoc)
        out=base64.encodestring(buf.getvalue())
        buf.close()
        name = "%s%s%s.XML" % ("REOC", wiz.period_id.name[:2], wiz.period_id.name[3:8])
        return self.write(cr, uid, ids, {'state': 'export', 'data': out, 'name': name, 'filename': name})
        
    _columns = {
        'opt' : fields.selection([('Todas','Todas')],'Opcion',help="Si usted selecciona retenciones el reoc se genera en base a las retenciones electronicas autorizas por el SRI, caso contrario se basa en las facturas validadas"),
        'name' : fields.char('Nombre de Archivo', size=50, readonly=True),
        'fy_id': fields.many2one('account.fiscalyear', 'Ejercicio Fiscal', required=True),
        'period_id' : fields.many2one('account.period', 'Periodo', domain=[('special','=',False)]),
        'company_id': fields.many2one('res.company', 'Compania'),
        'num_estab_ruc': fields.char('Num. de Establecimientos', size=3, required=True),
        'pay_limit': fields.float('Limite de Pago'),
        'data' : fields.binary('Archivo XML'),
        'no_validate': fields.boolean('No Validar'),
        'state' : fields.selection((('choose', 'choose'),
                                    ('export', 'export'))),
        'filename': fields.char('Nombre de Archivo', size=64),
        }

    def _get_fy(self, cr, uid, context=None):
        res = self.pool.get('account.fiscalyear').find(cr, uid)
        return res

    _defaults = {
        'state' : 'choose',
        'period_id': _get_period,
        'company_id': _get_company,
        'fy_id': _get_fy,
        'pay_limit': 1000.00,
        'num_estab_ruc': '001',
        'no_validate':True,
    }    

wizard_reoc()


class wizard_iva(osv.TransientModel):

    _name = 'wizard.iva'
    _description = 'DEVOLUCOIN IVA'
    __logger = logging.getLogger(_name)

    def _get_period(self, cr, uid, context):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False

    def _get_company(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id.id

    def act_cancel(self, cr, uid, ids, context):
        return {'type':'ir.actions.act_window_close'}

    def process_lines(self, cr, uid, lines):
        """
        @temp: {'332': {baseImpAir: 0,}}
        @data_air: [{baseImpAir: 0, ...}]
        """
        data_air = []
        flag = False
        temp = {}
        for line in lines:
            if line.tax_group in ['ret_ir', 'no_ret_ir']:
                if not temp.get(line.base_code_id.code):
                    temp[line.base_code_id.code] = {'baseImpAir': 0, 'valRetAir': 0}
                temp[line.base_code_id.code]['baseImpAir'] += line.base_amount
                temp[line.base_code_id.code]['codRetAir'] = line.base_code_id.code
                temp[line.base_code_id.code]['porcentajeAir'] = line.percent and float(line.percent) or 0.00
                temp[line.base_code_id.code]['valRetAir'] += abs(line.amount)
        for k,v in temp.items():
            data_air.append(v)
        return data_air

    def process_lines_linea(self, cr, uid, linea):
        """
        @temp: {'332': {baseImpAir: 0,}}
        @data_air: [{baseImpAir: 0, ...}]
        """
        data_air = []
        flag = False
        temp = {}
        for line in linea.invoice_line_tax_id:
            if line.tax_group in ['ret_ir', 'no_ret_ir']:
                if not temp.get(line.base_code_id.code):
                    temp[line.base_code_id.code] = {'baseImpAir': 0, 'valRetAir': 0}
                temp[line.base_code_id.code]['baseImpAir'] += linea.price_subtotal
                temp[line.base_code_id.code]['codRetAir'] = line.base_code_id.code
                temp[line.base_code_id.code]['porcentajeAir'] = line.percent and float(line.percent) or 0.00
#                temp[line.base_code_id.code]['porcentajeAir'] = line.porcentaje and float(line.porcentaje) or 0.00
                temp[line.base_code_id.code]['valRetAir'] += abs(linea.monto_retir)
        for k,v in temp.items():
            data_air.append(v)
        return data_air    

    def convertir_fecha(self, fecha):
        """
        fecha: '2012-12-15'
        return: '15/12/2012'
        """
        f = fecha.split('-')
        date = datetime.date(int(f[0]), int(f[1]), int(f[2]))
        return date.strftime('%d/%m/%Y')


    def _get_ventas_estab(self, cr, period_id, auth_id, journal_id):
        sql_ventas = "SELECT sum(amount_vat+amount_vat_cero+amount_novat) AS base \
                      FROM account_invoice, account_journal j \
                      WHERE account_invoice.journal_id=j.id \
                      AND account_invoice.type = 'out_invoice' \
                      AND account_invoice.state IN ('open','paid') \
                      AND period_id = %s \
                      AND journal_id = %s \
                      AND j.auth_id = %s"  % (period_id, journal_id, auth_id)
        cr.execute(sql_ventas)
        result = cr.fetchone()[0]
        return '%.2f' % (result and result or 0.00)    

    def _get_ventas(self, cr, period_id, journal_id=False):
        return 0

    def _get_ventas_erp(self, cr, period_id, journal_id=False):
        sql_ventas = "SELECT sum(amount_vat+amount_vat_cero+amount_novat) AS base \
                      FROM account_invoice \
                      WHERE type = 'out_invoice' AND state IN ('open','paid') AND period_id = %s" % period_id
        if journal_id:
            where = " AND journal_id=%s" % journal_id
            sql_ventas += where
        cr.execute(sql_ventas)
        result = cr.fetchone()[0]
        return '%.2f' % (result and result or 0.00)

    def _get_ret_iva(self, invoice):
        """
        Return (valorRetServicios, valorRetServ100)
        """
        retServ = 0
        retServ100 = 0
        for tax in invoice.tax_line:
            if tax.tax_group == 'ret_vat_srv':
                if tax.percent == '100':
                    retServ100 += abs(tax.tax_amount)
                else:
                    retServ += abs(tax.tax_amount)
        return retServ, retServ100

    def _get_ret_iva_linea(self, linea):
        """
        Return (valorRetServicios, valorRetServ100)
        """
        retServ = 0
        retServ100 = 0
        for tax in linea.invoice_line_tax_id:
            if tax.tax_group == 'ret_vat_srv':
                if tax.percent == '100':
                    retServ100 += abs(linea.monto_retserv)
                else:
                    retServ += abs(linea.monto_retserv)
        return retServ, retServ100    

    def act_export_iva(self, cr, uid, ids, context):
        conret = 0
        ats_sustento = self.pool.get('account.ats.sustento')
        inv_obj = self.pool.get('account.invoice')
        journal_obj = self.pool.get('account.journal')
        digital_obj = self.pool.get('digital.retention')
        wiz = self.browse(cr, uid, ids)[0]
        period_id = wiz.period_id.id
        period_aux = wiz.period_id
        ruc = wiz.company_id.partner_id.ced_ruc
        reoc = etree.Element('devIva')
        etree.SubElement(reoc, 'numeroRuc').text = str(ruc)
        period = self.pool.get('account.period').browse(cr, uid, [period_id])[0]
        etree.SubElement(reoc, 'anio').text = time.strftime('%Y',time.strptime(period.date_start, '%Y-%m-%d'))        
        etree.SubElement(reoc, 'mes'). text = time.strftime('%m',time.strptime(period.date_start, '%Y-%m-%d'))
        compras = etree.Element('compras')
        '''Facturas de Compra con retenciones '''
        inv_ids = []
#        sustento_ids = ats_sustento.search(cr, uid, [('code','in',('01','03','06'))])
        sustento_ids = ats_sustento.search(cr, uid, [])
        if wiz.opt=='Todas':
            inv_ids = inv_obj.search(cr, uid, [('state','in',['open','paid','draft']),
                                               ('sustento_id','in',sustento_ids),
                                               ('type','in',['in_invoice','liq_purchase']),
                                               ('date_invoice','>=',period_aux.date_start),('date_invoice','<=',period_aux.date_stop),
                                               ('company_id','=',wiz.company_id.id)])
        else:
            inv_ids = inv_obj.search(cr, uid, [('state','in',['open','paid']),
                                               ('date_invoice','>=',period_aux.date_start),('date_invoice','<=',period_aux.date_stop),
                                               ('sustento_id','in',sustento_ids),
                                               ('type','in',['in_invoice','liq_purchase']),
                                               ('company_id','=',wiz.company_id.id)])
        self.__logger.info("Compras registradas: %s" % len(inv_ids))
        for inv in inv_obj.browse(cr, uid, inv_ids):
            detallecompras = etree.Element('detalleCompras')
            #considerar multi factura
            if inv.reference_type == 'invoice_partner':
                etree.SubElement(detallecompras, 'codSustento').text = inv.sustento_id.code
                if not inv.partner_id.ced_ruc:
                    raise osv.except_osv('Datos incompletos', 'No ha ingresado toda los datos de %s' % inv.partner_id.name)
                etree.SubElement(detallecompras, 'tpIdProv').text = tpIdProv[inv.partner_id.type_ced_ruc]
                etree.SubElement(detallecompras, 'idProv').text = inv.partner_id.ced_ruc
                if inv.auth_inv_id:
                    tcomp = inv.auth_inv_id.type_id.code
                else:
                    tcomp = '03'
                etree.SubElement(detallecompras, 'tipoComprobante').text = tcomp
                etree.SubElement(detallecompras, 'fechaRegistro').text = self.convertir_fecha(inv.date_invoice)
                if inv.type == 'in_invoice':
                    se = inv.auth_inv_id.serie_entidad
                    pe = inv.auth_inv_id.serie_emision
                    sec = '%09d' % int(inv.reference)
                    auth = inv.auth_inv_id.name
                elif inv.type == 'liq_purchase':
                    se = inv.journal_id.auth_id.serie_entidad
                    pe = inv.journal_id.auth_id.serie_emision
                    sec = inv.number[8:]
                    auth = inv.journal_id.auth_id.name
                etree.SubElement(detallecompras, 'establecimiento').text = se
                etree.SubElement(detallecompras, 'puntoEmision').text = pe
                etree.SubElement(detallecompras, 'secuencial').text = sec
                etree.SubElement(detallecompras, 'autorizacion').text = auth
                etree.SubElement(detallecompras, 'baseImponible').text = '%.2f'%inv.amount_vat
                etree.SubElement(detallecompras, 'montoIva').text = '%.2f'%inv.amount_tax
                #ojo aqui segun retenido
                etree.SubElement(detallecompras, 'ivaSolicitado').text = '%.2f'%inv.amount_tax
                compras.append(detallecompras)                                                  
        reoc.append(compras)
        file_path = os.path.join(os.path.dirname(__file__), 'XSD/iva.xsd')
        schema_file = open(file_path)
        file_reoc = etree.tostring(reoc, pretty_print=True, encoding='iso-8859-1')
        #validata schema
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        if not wiz.no_validate:
            try:
                xmlschema.assertValid(reoc)
            except DocumentInvalid as e:
                raise osv.except_osv('Error de Datos', """El sistema generó el XML pero los datos no pasan la validación XSD del SRI.
                \nLos errores mas comunes son:\n* RUC,Cédula o Pasaporte contiene caracteres no válidos.\n* Números de documentos están duplicados.\n\nEl siguiente error contiene el identificador o número de documento en conflicto:\n\n %s""" % str(e))
        buf = StringIO.StringIO()
        buf.write(file_reoc)
        out=base64.encodestring(buf.getvalue())
        buf.close()
        name = "%s%s%s.XML" % ("DEVIVA", wiz.period_id.name[:2], wiz.period_id.name[3:8])
        return self.write(cr, uid, ids, {'state': 'export', 'data': out, 'name': name, 'filename': name})
        
    _columns = {
        'opt' : fields.selection([('Todas','Todas')],'Opcion',help="Si usted selecciona retenciones el reoc se genera en base a las retenciones electronicas autorizas por el SRI, caso contrario se basa en las facturas validadas"),
        'name' : fields.char('Nombre de Archivo', size=50, readonly=True),
        'fy_id': fields.many2one('account.fiscalyear', 'Ejercicio Fiscal', required=True),
        'period_id' : fields.many2one('account.period', 'Periodo', domain=[('special','=',False)]),
        'company_id': fields.many2one('res.company', 'Compania'),
        'num_estab_ruc': fields.char('Num. de Establecimientos', size=3, required=True),
        'pay_limit': fields.float('Limite de Pago'),
        'data' : fields.binary('Archivo XML'),
        'no_validate': fields.boolean('No Validar'),
        'state' : fields.selection((('choose', 'choose'),
                                    ('export', 'export'))),
        'filename': fields.char('Nombre de Archivo', size=64),
        }

    def _get_fy(self, cr, uid, context=None):
        res = self.pool.get('account.fiscalyear').find(cr, uid)
        return res

    _defaults = {
        'state' : 'choose',
        'period_id': _get_period,
        'company_id': _get_company,
        'fy_id': _get_fy,
        'pay_limit': 1000.00,
        'num_estab_ruc': '001',
        'no_validate':True,
    }    

wizard_iva()
