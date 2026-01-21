# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
import hashlib
import os
import zipfile
try:
    import zlib
    COMPRESSION = zipfile.ZIP_DEFLATED
except:
    COMPRESSION = zipfile.ZIP_STORED

from osv import fields, osv
import decimal_precision as dp
import StringIO
import base64
from tools import ustr
import unicodedata
from string import upper

class resBankSpi(osv.Model):
    _inherit = 'res.bank'
    _columns = dict(
        short_name = fields.char('Desc. Corta',size=5),
        )
resBankSpi()

class journalCta(osv.Model):
    _inherit = 'account.journal'
    _columns = dict(
        cta_number = fields.char('Num. Cta',size=32),
        )
journalCta()

class accountInvoiceDue(osv.Model):
    _inherit = 'account.invoice'
    _columns = {
        'date_due': fields.date('Due Date', states={'paid':[('readonly',True)], 
                                                    'close':[('readonly',True)]}, select=True)
        }
accountInvoiceDue()

class voucherSpi(osv.osv):
    _inherit = 'account.voucher'
    _columns = dict(
        to_pay = fields.boolean('Pagar?'),
        date_aproved = fields.date('Fecha pago'),
        aprobed_id = fields.many2one('res.users','Aprobado por:',readonly=True),
        )

    def aprobar_pago(self, cr, uid, ids,context=None):
        voucher_obj = self.pool.get('account.voucher')
        for this in self.browse(cr, uid, ids):
            if this.date_aproved:
                voucher_obj.write(cr, uid, this.id,{
                        'to_pay':True,
                        'aprobed_id':uid,
                        })
            else:
                raise osv.except_osv(('Error !'), 
                                     'No se puede aprobar pago, debe colocar la fecha de pago')
        return True

#    def proforma_voucher(self, cr, uid, ids, context=None):
#        for this in self.browse(cr, uid, ids):
#            if not this.to_pay:
#                raise osv.except_osv(('Error !'), 
#                                     'No se puede validar el pago, no a sido aprobado por Director Financiero')
#            if not this.date==this.date_aproved:
#                 raise osv.except_osv(('Error !'), 
#                                      'No se puede realizar el pago en fechas diferentes')
#        self.compute_tax(cr, uid, ids, context=context)
#        self.action_move_line_create(cr, uid, ids, context=context)
#        return True

    _defaults = dict(
        date_aproved = time.strftime('%Y-%m-%d'),
        )

voucherSpi()

class spiResume(osv.Model):
    _name = 'spi.resume'
    _columns = dict(
        number = fields.char('Num. Cta.',size=20),
        name = fields.char('Banco',size=20),
        qty = fields.integer('# Pagos'),
        amount = fields.float('USD $ Monto'),
        spi_id = fields.many2one('account.spi.voucher','SPI'),
        )
spiResume()

class spi_voucher(osv.Model):
    _name = 'account.spi.voucher'

    def create(self, cr, uid, vals, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        vals['name'] = obj_sequence.get(cr, uid, 'account.spi.voucher')
        return super(spi_voucher, self).create(cr, uid, vals, context=None)

    def print_resumen(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado
        '''        
        if not context:
            context = {}
        voucher = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [voucher.id], 'model': 'account.spi.voucher'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'spir1',
            'model': 'account.spi.voucher',
            'datas': datas,
            'nodestroy': True,                        
            }

    def print_resumen_(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado
        '''        
        if not context:
            context = {}
        voucher = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [voucher.id], 'model': 'account.spi.voucher'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'spir2',
            'model': 'account.spi.voucher',
            'datas': datas,
            'nodestroy': True,                        
            }            

    def spi_draft(self, cr, uid, ids, context):
        resume_obj = self.pool.get('spi.resume')
        for this in self.browse(cr, uid, ids):
            lista_v = []
            for line in this.resumen_ids:lista_v.append(line.id)
            resume_obj.unlink(cr, uid, lista_v)
            self.write(cr, uid, this.id, {'state':'Borrador',
                                     'total_qty':0,
                                     'total_amount':0})
        return True

    def spi_aprobe(self, cr, uid, ids, context):
        v_obj = self.pool.get('account.voucher')
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                if line.date_aproved:
                    if line.date_aproved!=this.date_done:
                        raise osv.except_osv(('Error !'), 
                                             'No se puede confirmar pago, el pago no tiene autorizacion del director financiero')
                else:
                    raise osv.except_osv(('Error !'), 
                                         'No se puede continuar, el documento no tiene fecha de pago aprobado por el director financiero')
            self.write(cr, uid, this.id, {'state':'Confirmado',
                                         'total_qty':len(this.line_ids)})
        return True

    def spi_generate(self, cr, uid, ids, context):
        comp_obj = self.pool.get('res.company')
        partner_obj = self.pool.get('res.partner')
        line_obj = self.pool.get('spi.resume')
        bank_obj = self.pool.get('res.bank')
        voucher_obj = self.pool.get('account.voucher')
        company_id = comp_obj.search(cr, uid, [],limit=1)[0]
        company = comp_obj.browse(cr, uid, company_id)
        for this in self.browse(cr, uid, ids):
            j = 0
            buf = StringIO.StringIO()
            fecha = time.strftime('%d/%m/%Y')
            if not this.journal_id.cta_number:
                raise osv.except_osv(('No se puede generar el archivo error !'), 
                                     'No existe numero de cuenta en el diario seleccionado')
            num_cta_empresa = this.journal_id.cta_number 
            cabecera = fecha + '\t' + num_cta_empresa + '\t' + company.name +'\r\n'
            cabecera = unicodedata.normalize('NFKD',cabecera).encode('ascii','ignore')
            buf.write(upper(cabecera))
            id_partner = {}
            data2 = {}
            data3 = {}
            data4 = {}
            lines = this.line_ids
            tot_amount = l = 0
            if len(this.line_ids)>0:
                lines.sort(key=lambda x: x.state)
                for line in lines:
                    if line.to_pay:
                        j += 1
                        if not data2.get(line.partner_id.id):
                            data2.update({line.partner_id.id:0})
                        data2[line.partner_id.id] += line.amount
                        tot_amount += line.amount
                        if not data3.get(line.partner_id.bank_ids[0].bank.id):
                            data3.update({line.partner_id.bank_ids[0].bank.id:0})
                            data4.update({line.partner_id.bank_ids[0].bank.id:0})
                        l += 1
                        data3[line.partner_id.bank_ids[0].bank.id] += line.amount
                        data4[line.partner_id.bank_ids[0].bank.id] = l
            else:
                raise osv.except_osv(('No se puede generar el archivo SPI !'), 
                                     'No existen lineas de pago seleccionadas')    
            if len(data2) < 1:
                raise osv.except_osv(('No se puede generar el archivo SPI !'), 
                                     'No existen lineas de pago autorizadas por el Director Financiero')
            for a,b in data3.items():
                #crear una linea de resumen por partner
                #sacar el len por partner
                lista_v = []
#                for line in this.line_ids:lista_v.append(line.id)
#                qty = len(voucher_obj.search(cr, uid, [('partner_id','=',partner.id),('id','in',lista_v)]))   
                bank = bank_obj.browse(cr, uid, a) 
                line_obj.create(cr, uid, {
                        'number':bank.zip,
                        'name':bank.name,
                        'qty':data4[a],
                        'amount':b,
                        'spi_id':this.id,
                        })
            for p,v in data2.items():
                partner = partner_obj.browse(cr, uid, p)
                partner_name = partner.name
                val_1="%.2f"%(v)
                if len(partner_name)<40:
                    partner_cut=partner_name.ljust(30,' ')
                else:
                    partner_cut=partner_name[0:30]
                if len(partner.bank_ids)<1:
                    raise osv.except_osv(('No se puede generar el archivo error !'), 
                                         'No existe cuenta definida para el proveedor')
                cuenta = partner.bank_ids[0]
                numero_cta = int(cuenta.acc_number)
                n_lleno="%018d"%numero_cta
                val_2=val_1.replace(".",'')
                str_val_aux="%09d"%int(val_2)
                str_val = str_val_aux[1:7] + '.' + str_val_aux[7:9]
                bank_code = "%08d"%int(cuenta.bank.zip)
                tipo_cta = '2'
                if cuenta.type_cta == 'aho':
                    tipo_cta = '1'
                detalle = partner.ced_ruc + '\t' + partner_cut + '\t' + n_lleno + '\t' + str_val + '\t' + bank_code + '\t' + tipo_cta +'\r\n'
                detalle = unicodedata.normalize('NFKD',detalle).encode('ascii','ignore')
                buf.write(upper(detalle))
            name = "%s.TXT" % ("SPI-SP_LB")
#            out = base64.encodestring(buf.getvalue())
#            buf.close()
#            self.write(cr, uid, ids, {'archivo': out, 'file_name': name,'total_amount':tot_amount,'state':'Generado'})
            digest_name = 'SPI-SP-LB.md5'
            #checksum
            digest1 = '%s' % (hashlib.md5(buf.getvalue()).hexdigest())
            digest = '%s %s\n' % (hashlib.md5(buf.getvalue()).hexdigest(), name)
            file_digest = open(digest_name, 'w')
            file_digest.write(digest)
            file_digest.close()
            file_spi = open(name, 'w')
            file_spi.write(buf.getvalue())
            file_spi.close()
            #zip file
            zf_name = 'sip-sp %s.zip' % time.strftime('%Y-%m-%d')
            zf = zipfile.ZipFile(zf_name, mode='w')
            zf_buf = StringIO.StringIO()
            try:
                zf.write(digest_name, compress_type=COMPRESSION)
                zf.write(name)
            finally:
                zf.close()
            zf_tmp = open(zf_name, 'rb')
            zf_buf.write(zf_tmp.read())
            out = base64.encodestring(zf_buf.getvalue())
            zf_buf.close()
            self.write(cr, uid, ids, {'dig':digest1,'archivo': out, 'file_name': zf_name,'total_amount':tot_amount,'state':'Generado'})
            return True

    _columns = dict(
        dig = fields.char('dig',size=256),
        total_qty = fields.integer('Total pagos'),
        total_amount = fields.float('Total monto'),
        resumen_ids = fields.one2many('spi.resume','spi_id','Resumen'),
        name = fields.char('Referencia',size=10),
        date = fields.date('Fecha Creacion',readonly=True),
        date_done = fields.date('Fecha Pago'),
        journal_id = fields.many2one('account.journal','Banco'),
        line_ids = fields.many2many('account.voucher','spi_voucher_rel','spi_id','voucher_id','Detalle Pagos'),
        state = fields.selection([('Borrador','Borrador'),('Confirmado','Confirmado'),('Generado','Generado')],'Estado'),
        archivo = fields.binary('Archivo SPI',readonly=True),
        file_name = fields.char('N. archivo', size=32),
        )
    _defaults = dict(
        state = 'Borrador',
        date = time.strftime('%Y-%m-%d'),
        )

spi_voucher()
