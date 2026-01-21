# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
#
##############################################################################

import time
import logging
from operator import itemgetter
from lxml import etree
import csv
from osv import osv, fields
from tools import config
from tools.translate import _
from tools import ustr
from decimal import *
import decimal_precision as dp
import netsvc
from openerp.osv.orm import setup_modifiers
import shutil
import os
import base64
from datetime import datetime as dt
import unicodedata

balance = False
cedula = False

class wizard_load_certificado(osv.TransientModel):
    _name = 'wizard.load.certificado'
    _columns = dict(
        certificate_id = fields.many2one('budget.certificate','Compromiso'),
    )

    def action_load_certificado(self, cr, uid, ids, context=None):
        print "LOAD"

wizard_load_certificado()

class noPartida(osv.Model):
    _name = 'no.partida'
    _columns = dict(
        name = fields.char('Codigo',size=12),
        desc = fields.char('Descripcion',size=256),
    )
noPartida()

class DigitalRetentionProcess(osv.TransientModel):
    _name = 'digital.retention.process'

    _columns = {
        'log_error': fields.text('Documentos con errores'),
        'log_procesadas': fields.text('Documentos procesados'),
    }

    def processFile(self, cr, uid, ids, context={}):
        for doc_ride in os.listdir(carpetaRE+'/autorizados/'):
            if doc_ride.endswith(".xml") and retencion in doc_ride:
                texto_file = open(carpetaRE+'/autorizados/'+doc_ride, 'r')
                texto = texto_file.read()
                l = texto.find('numeroAutorizacion')
                aux_aut = texto[l+19:l+19+37]
                m = texto.find('claveAcceso')
                aux_clave = texto[m+15:m+15+49]
                name = doc_ride.replace('COMPROBANTE DE RETENCION_','')
                name = name.replace('.xml','')
                digital_ret_ids = digital_retention_obj.search(cr, uid, [('name','=',name)])
                if digital_ret_ids:
                    if "AUTORIZADO" in texto and "NO AUTORIZADO" not in texto:
                        nombre_archivo = doc_ride
                        nombre_pdf = nombre_archivo.replace('xml','pdf')
                        nombre_xml = nombre_pdf.replace('pdf','xml')
                        log_procesadas += "\n"+doc_ride
                        fpdf = open(carpetaRE+'/autorizados/'+nombre_pdf, 'r')
                        fxml = open(carpetaRE+'/autorizados/'+nombre_xml, 'r')
                        buf_pdf = base64.encodestring(fpdf.read())
                        buf_xml = base64.encodestring(fxml.read())
                        email_from_ids = parameter_obj.search(cr, uid, [('key','=','email_from')],limit=1)
                        if email_from_ids:
                            email_from = parameter_obj.browse(cr, uid, email_from_ids[0]).value
                        else:
                            raise osv.except_osv('Error','No ha configurado la direccion de correo para envio de retenciones.')
                        email_copy_ids = parameter_obj.search(cr, uid, [('key','=','email_copy')],limit=1)
                        email_copy = False
                        if email_copy_ids:
                            email_copy = parameter_obj.browse(cr, uid, email_copy_ids[0]).value
                        else:
                            raise osv.except_osv('Error','No ha configurado la direccion de correo para envio de retenciones.')
                        digitaldoc = digital_retention_obj.browse(cr, uid, digital_ret_ids[0], context)
                        #mando el correo con el pdf
                        razonSocial = user.company_id.name
                        msg = " Estimado  %s, \n\n Adjunto sirvase encontrar el detalle de su retencion electronica. \n\n Saludos\n%s,"  %(digitaldoc.retention_id.partner_id.name,razonSocial)
                        vals_msg = {
                            'subject': 'Retencion electronica - ' + razonSocial,
                            'body_text': msg,
                            'email_from': email_from,
                            'email_bcc' : email_copy,
                            'email_to': digitaldoc.email_a_enviar,
                            'state': 'outgoing',
                        }
                        email_msg_id = mail_message.create(cr, uid, vals_msg, context)
                        attachment_ids = []
                        attachment_pdf = {
                            'name': nombre_pdf,
                            'datas_fname': nombre_pdf,
                            'datas': buf_pdf,
                            'res_model': 'mail.message',
                            'res_id': email_msg_id,
                        }
                        attachment_xml = {
                            'name': nombre_xml,
                            'datas_fname': nombre_xml,
                            'datas': buf_xml,
                            'res_model': 'mail.message',
                            'res_id': email_msg_id,
                        }
                        attachment_ids.append(attachment_obj.create(cr, uid, attachment_pdf, context))
                        attachment_ids.append(attachment_obj.create(cr, uid, attachment_xml, context))
                        if attachment_ids:
                            mail_message.write(cr, uid, email_msg_id, { 'attachment_ids': [(6, 0, attachment_ids)]}, context=context)
                        try:
                            mail_message.send(cr, uid, [email_msg_id])
#                            respuestas.append(doc_ride)
#                            respuestas.append(respuesta.replace('resultado-','ca-'))
                            autorizadas.append(nombre_pdf)
                            autorizadas.append(nombre_xml)
                            text_new = 'RECIBIDA' + '\n' + 'AUTORIZADO' + '\n' + 'PRODUCCION' + '\n' + ustr(aux_clave) + '\n' + ustr(aux_aut)
                            vals = {
                                'autorizacion':aux_aut,
                                'state': 'autorizado',
                                'state_email': 'enviado',
                                'pdf': buf_pdf,
                                'fnpdf': nombre_pdf,
                                'xml': buf_xml,
                                'fnxml': nombre_xml,
                                'log': text_new,
                                'mail_id': email_msg_id,
                            }
                        except:
                            pass
                        digital_retention_obj.write(cr, uid, digital_ret_ids[0], vals, context)
#                    digital_retention_obj.write(cr, uid, digital_ret_ids[0], vals, context)
                else:
                    raise osv.except_osv('Error','No se ha encontrado la retention digital %s.'%(name))

    def process(self, cr, uid, ids, context={}):
        if context.get('one_retention',False):
            retencion = context['retencion']
        else:
            retencion=""
        attachment_obj = self.pool.get('ir.attachment')
        mail_message = self.pool.get('mail.message')
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        digital_retention_obj = self.pool.get('digital.retention')
        parameter_obj = self.pool.get('ir.config_parameter')
        carpetaRE_ids = parameter_obj.search(cr, uid, [('key','=','RE')],limit=1)
        if carpetaRE_ids:
            carpetaRE = parameter_obj.browse(cr, uid, carpetaRE_ids[0]).value
        else:
            raise osv.except_osv('Error','No ha configurado la carpeta para retenciones autorizadas.')

        formulario = self.browse(cr, uid, ids[0],context)
        # Mando un correo por cada retencion autorizada
        autorizadas = []
        respuestas = []
        log_error = ""
        log_procesadas = ""
        for respuesta in os.listdir(carpetaRE+'/respuestas/'):
            if respuesta.endswith(".txt") and "resultado" in respuesta and retencion in respuesta:
                texto_file = open(carpetaRE+'/respuestas/'+respuesta, 'r')
                texto = texto_file.read()
                texto = ustr(texto)
                name = respuesta.replace('resultado-codDoc07-docNo','')
                name = name.replace('.txt','')
                digital_ret_ids = digital_retention_obj.search(cr, uid, [('name','=',name)])
                if digital_ret_ids:
                    if "AUTORIZADO" in texto and "NO AUTORIZADO" not in texto:
                        nombre_archivo = respuesta.replace('resultado-','COMPROBANTE DE RETENCION_')
                        nombre_archivo = nombre_archivo.replace('codDoc07-docNo','')
                        nombre_pdf = nombre_archivo.replace('txt','pdf')
                        nombre_xml = nombre_pdf.replace('pdf','xml')
                        log_procesadas += "\n"+name
                        fpdf = open(carpetaRE+'/autorizados/'+nombre_pdf, 'r')
                        fxml = open(carpetaRE+'/autorizados/'+nombre_xml, 'r')
                        buf_pdf = base64.encodestring(fpdf.read())
                        buf_xml = base64.encodestring(fxml.read())
                        email_from_ids = parameter_obj.search(cr, uid, [('key','=','email_from')],limit=1)
                        if email_from_ids:
                            email_from = parameter_obj.browse(cr, uid, email_from_ids[0]).value
                        else:
                            raise osv.except_osv('Error','No ha configurado la direccion de correo para envio de retenciones.')
                        email_copy_ids = parameter_obj.search(cr, uid, [('key','=','email_copy')],limit=1)
                        email_copy = False
                        if email_copy_ids:
                            email_copy = parameter_obj.browse(cr, uid, email_copy_ids[0]).value
                        else:
                            raise osv.except_osv('Error','No ha configurado la direccion de correo para envio de retenciones.')
                        digitaldoc = digital_retention_obj.browse(cr, uid, digital_ret_ids[0], context)
                        #mando el correo con el pdf
                        razonSocial = user.company_id.name
                        msg = " Estimado  %s, \n\n Adjunto sirvase encontrar el detalle de su retencion electronica. \n\n Saludos\n%s,"  %(digitaldoc.retention_id.partner_id.name,razonSocial)
                        vals_msg = {
                            'subject': 'Retencion electronica - ' + razonSocial,
                            'body_text': msg,
                            'email_from': email_from,
                            'email_bcc' : email_copy,
                            'email_to': digitaldoc.email_a_enviar,
                            'state': 'outgoing',
                        }
                        email_msg_id = mail_message.create(cr, uid, vals_msg, context)
                        attachment_ids = []
                        attachment_pdf = {
                            'name': nombre_pdf,
                            'datas_fname': nombre_pdf,
                            'datas': buf_pdf,
                            'res_model': 'mail.message',
                            'res_id': email_msg_id,
                        }
                        attachment_xml = {
                            'name': nombre_xml,
                            'datas_fname': nombre_xml,
                            'datas': buf_xml,
                            'res_model': 'mail.message',
                            'res_id': email_msg_id,
                        }
                        attachment_ids.append(attachment_obj.create(cr, uid, attachment_pdf, context))
                        attachment_ids.append(attachment_obj.create(cr, uid, attachment_xml, context))
                        if attachment_ids:
                            mail_message.write(cr, uid, email_msg_id, { 'attachment_ids': [(6, 0, attachment_ids)]}, context=context)
                        try:
                            mail_message.send(cr, uid, [email_msg_id])
                            respuestas.append(respuesta)
                            respuestas.append(respuesta.replace('resultado-','ca-'))
                            autorizadas.append(nombre_pdf)
                            autorizadas.append(nombre_xml)
                            vals = {
                                'state': 'autorizado',
                                'state_email': 'enviado',
                                'pdf': buf_pdf,
                                'fnpdf': nombre_pdf,
                                'xml': buf_xml,
                                'fnxml': nombre_xml,
                                'log': texto,
                                'mail_id': email_msg_id,
                            }
                        except:
                            pass
                        #digital_retention_obj.write(cr, uid, digital_ret_ids[0], vals, context)
                    else:
                        texto = name + '\n' + ustr(texto)
                        vals = {
                            'log': texto,
                            'state': 'noautorizado',
                        }
                        log_error+='\n'+texto
                    digital_retention_obj.write(cr, uid, digital_ret_ids[0], vals, context)
                else:
                    raise osv.except_osv('Error','No se ha encontrado la retention digital %s.'%(name))
        self.write(cr, uid, [formulario.id], {'log_error': log_error, 'log_procesadas': log_procesadas})
        for autorizada in autorizadas:
            shutil.move(carpetaRE+'/autorizados/'+autorizada,carpetaRE+'/autorizados_siim/'+autorizada)
        for respuesta in respuestas:
            shutil.move(carpetaRE+'/respuestas/'+respuesta,carpetaRE+'/respuestas_siim/'+respuesta)
        return True
    
DigitalRetentionProcess()

class DigitalDocument(osv.Model):
    _name = 'digital.document'

    def load_retention(self, cr, uid, ids, context):
        print "HACE"
        return True

    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if uid!=1:
                raise osv.except_osv('Aviso','No se permite borrar documentos firmados digitalmente.')
        res = super(DigitalDocument, self).unlink(cr, uid, ids, context)
        return res
    
    def _get_autorizacion(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for digital in self.browse(cr, uid, ids):
            if digital.log:
                aux_text = digital.log
                lista=aux_text.splitlines()
                if lista[4]:
                    res[digital.id] = lista[4]
        return res

    _columns = dict(
        name = fields.char('Nombre del documento', required=True, size=64, readonly=True),
        date = fields.datetime('Fecha de generacion', required=True, readonly=True),
        pdf = fields.binary('PDF', readonly=True),
        fnpdf = fields.char('filenamepdf', size=256),
        xml = fields.binary('XML', readonly=True),
        fnxml = fields.char('filenamexml', size=256),
        email_a_enviar = fields.char('Enviar a:', size=128, readonly=True),
        tipo = fields.selection([('retention','Retencion')],'Tipo'),
        state = fields.selection([('proceso','En proceso'),('autorizado','Autorizado'),('noautorizado','No autorizado')],'Estado'),
        state_email = fields.selection([('noenviado','No enviado'),('enviado','Enviado')],'Estado de envio de correo'),
        mail_id = fields.many2one('mail.message','Correo electronico'),
        log = fields.text('Log', readonly=True),
        invoice_id = fields.related('retention_id','invoice_id',type='many2one',relation='account.invoice',string='Factura'),
        period_id = fields.related('invoice_id','period_id',type='many2one',relation='account.period',string='Periodo'),
        autorizacion = fields.function(_get_autorizacion, method=True, string="Num. Autorizacion", store=True, type="char", size=256), 
        autorizacion_manual = fields.char('Autorizacion Corregida',size=40,help="Si coloca numero en este campo en el ATS se cagara este valor y no el de autorizacion del SRI"),
    )
DigitalDocument()

class DigitalRetention(osv.Model):
    _name = 'digital.retention'
    _inherit = 'digital.document'
    _order = 'name desc, date desc'

    _columns = dict(
        retention_id = fields.many2one('account.retention', 'Retencion', readonly=True, ondelete='cascade'),
    )
DigitalRetention()

class preAsientoLine(osv.Model):
    _name = 'pre.asiento.line'
    _columns = dict(
        pre_id = fields.many2one('pre.asiento','Asiento'),
        budget_id = fields.many2one('budget.item','Partida',required=True),
        cert_line = fields.many2one('budget.certificate.line','Linea cert'),
        account_id = fields.many2one('account.account','Contra Cuenta',required=True),
        account2_id = fields.many2one('account.account','Cuenta x pagar'),
        monto = fields.float('Monto'),
    )
preAsientoLine()
class preAsiento(osv.Model):
    _name = 'pre.asiento'

    def preDevengado(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        account_obj = self.pool.get('account.account')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
        if not journal_ids:
            raise osv.except_osv('Error configuracion','No existe diario de egresos, por favor crear uno')
        for this in self.browse(cr, uid, ids):
            cp = this.name
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            name_aux = 'Pago'
            date_aux = cp.date_commited
            move_id = move_obj.create(cr, uid, {
                'partner':cp.partner_id.id,
                'certificate_id':cp.id,
                'narration':cp.notes,
                'journal_id':journal_ids[0],
                'afectacion':True,
                'partner_id':1,
                'ref':cp.notes,
            })
            move = move_obj.browse(cr, uid, move_id)
            aux_total = 0
            for line in this.line_ids:
                aux_total += line.monto
                account_ids = account_obj.search(cr, uid, [('budget_id','=',line.budget_id.budget_post_id.id)])
                account = account_obj.browse(cr, uid, account_ids[0])
                if account.account_rec_id.id:
                    cxp = account.account_rec_id.id
                else:
                    cxp = account.account_pay_id.id
                monto = line.monto
                certificate = certificate_line_obj.browse(cr, uid, line.cert_line.id)
                b_id = certificate.budget_id.id
                p_id = certificate.budget_post.id
                #entrada cxp haber
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,certificate.id,b_id,p_id,name_aux,False))
                #linea  entrada cxp debe
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,name,migrado) VALUES (%s,%s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,cxp,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,certificate.id,b_id,p_id,name_aux,False))
                #linea  entrada cta patrimonial 621
                cr.execute('''
                INSERT INTO account_move_line (
                move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,budget_id_cert,budget_id,budget_post,budget_paid,budget_accrued,name,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account.id,monto,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,certificate.id,b_id,p_id,True,True,name_aux,False))
            cr.execute('''
            INSERT INTO account_move_line (
            move_id,account_id,credit,journal_id,period_id,state,company_id,currency_id,date,name,migrado) VALUES (%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s)''',(move_id,this.journal_id.default_debit_account_id.id,aux_total,move.journal_id.id,move.period_id.id,state_aux,company_aux,currency_aux,date_aux,name_aux,False))
        return True

    def onchange_cp(self, cr, uid, ids, cp):
        line_obj = self.pool.get('pre.asiento.line')
        account_obj = self.pool.get('account.account')
        certificate_obj = self.pool.get('budget.certificate')
        post_obj = self.pool.get('budget.post')
        result = {}
        value = []
        cp = certificate_obj.browse(cr, uid, cp)
        for line in cp.line_ids:
            account_aux_ids = account_obj.search(cr, uid, [('budget_id','=',line.budget_id.budget_post_id.id)])
            if not account_aux_ids:
                aux_6 = line.budget_id.budget_post_id.code[0:6]
                aux_budget_6_ids = post_obj.search(cr, uid, [('code','=',aux_6)])
                if aux_budget_6_ids:
                    account_aux_ids = account_obj.search(cr, uid, [('budget_id','=',aux_budget_6_ids[0])])
            if len(account_aux_ids)>0:
                #cambiado por mario, aqui debe ser pero la patrimonial no la primera
                for account_id in account_aux_ids:
                    account = account_obj.browse(cr, uid, account_id)
                    if account.account_rec_id or account.account_pay_id:
                        continue
                if account.account_rec_id:
                    account_aux2 = account.account_rec_id.id
                elif account.account_pay_id:
                    account_aux2 = account.account_pay_id.id
                else:
                    if account.account_p_ids:
                        account_aux2 = account.account_p_ids[0].id
                    else:
                        aux_name_cuenta = account.code + ' - ' + account.name
                        MSG = 'La cuenta %s de la partida %s no tiene configurada la cuenta por pagar' % (aux_name_cuenta,line.budget_id.budget_post_id.name)
                        raise osv.except_osv('Error', MSG)
            else:
                aux_msg_contra = line.budget_id.budget_post_id.code + ' - ' + line.budget_id.budget_post_id.name
                MSG = 'La partida %s no tiene configurada la contra cuenta' % (aux_msg_contra)
                raise osv.except_osv('Error', MSG)
            id_creado = line_obj.create(cr, uid, {
       #         'pre_id':this.id,
                'budget_id':line.budget_id.id,
                'account_id':account.id,
                'account2_id':account_aux2,
                'monto':line.amount_commited,
                'cert_line':line.id,
            })
            value.append(id_creado)
        result['line_ids'] = value
        return {'value': result}

    _columns = dict(
        name = fields.many2one('budget.certificate','Compromiso Presupuestario',required=True),
        journal_id = fields.many2one('account.journal','Banco',required=True),
        line_ids = fields.one2many('pre.asiento.line','pre_id','Detalle'),
    )
preAsiento()

class account_code_ret(osv.osv):
    _name= 'account.code.ret'

    _columns = {
        'name': fields.char('Codigo', size=10),
        'descripcion':fields.text('Descripcion'),
    }
account_code_ret()

class account_retention(osv.osv):
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.name
            res.append((record.id, name))
        return res        

    def _get_type(self, cr, uid, context):
        if context.has_key('type') and \
        context['type'] in ['in_invoice', 'out_invoice']:
            return 'in_invoice'
        else:
            return 'liq_purchase'

    def _get_in_type(self, cr, uid, context):
        if context.has_key('type') and \
        context['type'] in ['in_invoice', 'liq_purchase']:
            return 'ret_in_invoice'
        else:
            return 'ret_in_invoice'

    def _amount_total(self, cr, uid, ids, field_name, args, context):
        res = {}
        retentions = self.browse(cr, uid, ids, context)
        for ret in retentions:
            total = 0
            for tax in ret.tax_ids:
                total += tax.amount
            res[ret.id] = abs(total)
        return res

    def _get_period(self, cr, uid, ids, fields, args, context):
        res = {}
        period_obj = self.pool.get('account.period')
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = period_obj.find(cr, uid, obj.date)[0]
        return res

    STATES_VALUE = {'draft': [('readonly', False)]}

    _name = 'account.retention'
    _description = 'Documentos de Retención'
    _order = 'date desc, number desc'

    
    
    _columns = {
        'name': fields.char('Número', size=64, readonly=True,
                            required=True,
                            states=STATES_VALUE),
        'number': fields.char('Número', size=64, readonly=True,
                              required=True),
        'manual': fields.boolean('Numeración Manual', readonly=True,
                                 states=STATES_VALUE),
        'num_document': fields.char('Num. Comprobante', size=50,
                                    readonly=True,
                                    states=STATES_VALUE),
        'auth_id': fields.many2one('account.authorisation', 'Autorización',
                                   readonly=True,
                                   states=STATES_VALUE,
                                   domain=[('in_type','=','interno')]),
        'auth_id2': fields.related('digital_id', 'autorizacion', type='char', size=128,
                                  string='Autorizacion Retencion Electronica',
                                  readonly=True),
#        'address_id': fields.many2one('res.partner.address', 'Direccion',
#                                      readonly=True,
#                                      states=STATES_VALUE,
#                                      domain="[('partner_id','=',partner_id)]"),
        'address_id': fields.many2one('res.partner.address', 'Direccion',
                                      readonly=True,
                                      states=STATES_VALUE,
                                      domain="[('partner_id','=',partner_id)]"),
        'type': fields.selection([('in_invoice','Factura'),
                                  ('liq_purchase','Liquidacion Compra')],
                                 string='Tipo Comprobante',
                                 readonly=True, states=STATES_VALUE),
        'in_type': fields.selection([('ret_in_invoice',
                                      'Retencion a Proveedor'),
                                     ('ret_out_invoice',
                                      'Retencion de Cliente')],
                                    string='Tipo', states=STATES_VALUE, readonly=True),
        'date': fields.date('Fecha Emision', readonly=True,
                            states={'draft': [('readonly', False)]}, required=True),
#        'period_id': fields.function(_get_period, method=True, type='many2one', store=True, relation='account.period', string='Periodo'),
        'tax_ids': fields.one2many('account.invoice.tax', 'retention_id',
                                   'Detalle de Impuestos', readonly=True,
                                   states=STATES_VALUE),
        'invoice_id': fields.many2one('account.invoice', string='Documento',
                                      required=False,
                                      readonly=True, states=STATES_VALUE,domain=[('state','=','open')]),
        'partner_id': fields.related('invoice_id', 'partner_id', type='many2one',
                                     relation='res.partner', string='Empresa',
                                     readonly=True),
        'move_id': fields.related('invoice_id', 'move_id', type='many2one',
                                  relation='account.move',
                                  string='Asiento Contable',
                                  readonly=True),
        'move_cancel_id': fields.many2one('account.move',
                                          'Asiento de Cancelacion',
                                          readonly=True),
        'state': fields.selection([('draft', 'Borrador'),
                                   ('early', 'Anticipado'),
                                   ('done', 'Validado'),
                                   ('cancel', 'Anulado')],
                                  readonly=True, string='Estado'),
        'amount_total': fields.function( _amount_total, string='Total',
                                         method=True, store=True,
                                         digits_compute=dp.get_precision('Account')),
        'to_cancel': fields.boolean('Para anulación',readonly=True, states=STATES_VALUE),
        'digital_id': fields.many2one('digital.retention', 'Retencion Digital',readonly=True)
        }

    _defaults = {
        'state': 'draft',
        'in_type': _get_in_type,
        'type': _get_type,
        'name': '/',
        'number': '/',
        'manual': True,
        'date': time.strftime('%Y-%m-%d'),
        }

    _sql_constraints = [('unique_number', 'unique(number)', u'El número de retención es único.')]

    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if obj.state in ['done']:
                raise osv.except_osv('Aviso','No se permite borrar retenciones validadas.')
        res = super(account_retention, self).unlink(cr, uid, ids, context)
        return res

    def onchange_invoice(self, cr, uid, ids, invoice_id):
        res = {'value': {'num_document': ''}}
        if not invoice_id:
            return res
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if not invoice.auth_inv_id:
            return res
        num_document = '%s%s%s'% (invoice.auth_inv_id.serie_entidad, invoice.auth_inv_id.serie_emision, invoice.reference.zfill(9))
        res['value']['num_document'] = num_document
        res['value']['type'] = invoice.type
        return res

    def button_validate(self, cr, uid, ids, context=None):
        """
        Botón de validación de Retención que se usa cuando
        se creó una retención manual, esta se relacionará
        con la factura seleccionada.
        """
        invoice_obj = self.pool.get('account.invoice')
        if context is None:
            context = {}
        for ret in self.browse(cr, uid, ids, context):
            if ret.manual:
                self.action_validate(cr, uid, [ret.id], ret.name)
                invoice_obj.write(cr, uid, ret.invoice_id.id, {'retention_id': ret.id})
            else:
                self.action_validate(cr, uid, [ret.id])
        return True

    def action_verify_sri(self, cr, uid, ids, context={}):
        process_obj = self.pool.get('digital.retention.process')
        retencion = self.browse(cr, uid, ids[0], context)
        ret_number = '%09d'%(int(retencion.name))
        ctx = context.copy()
        ctx.update({'one_retention': True, 'retencion': ret_number })
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'retention', 'retention_process_form')
        return {
            'name':"Verificar estado",
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'digital.retention.process',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx
        }
    
    def action_send_sri(self,cr, uid, ids, context={}):
        #leo de ir.config_parameter las carpetas de la integracion de la firma digital
        #Genero los archivos csv en una carpeta temporal, luego de creados los muevo a carpeta_pendiente
        process_obj = self.pool.get('digital.retention.process')
        digital_obj = self.pool.get('digital.retention')
        mail_obj = self.pool.get('mail.message')
        parameter_obj = self.pool.get('ir.config_parameter')
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        period_obj = self.pool.get('account.period')
        
        carpeta_RE_ids = parameter_obj.search(cr, uid, [('key','=','RE')],limit=1)
        if carpeta_RE_ids:
            carpeta_RE = parameter_obj.browse(cr, uid, carpeta_RE_ids[0]).value
        else:
            raise osv.except_osv('Error','No ha configurado una carpeta para generacion de retenciones.')
    
        establecimiento_ids = parameter_obj.search(cr, uid, [('key','=','establecimiento')],limit=1)
        if establecimiento_ids: 
            establecimiento = parameter_obj.browse(cr, uid, establecimiento_ids[0]).value
        else:
            raise osv.except_osv('Error','No ha configurado un establecimiento para la generacion de retenciones.')

        punto_emision_ids = parameter_obj.search(cr, uid, [('key','=','punto_emision')],limit=1)
        if punto_emision_ids:
            punto_emision = parameter_obj.browse(cr, uid, punto_emision_ids[0]).value
        else:
            raise osv.except_osv('Error','No ha configurado un punto de emision para la generacion de retenciones.')

        ambiente_ids = parameter_obj.search(cr, uid, [('key','=','ambiente')],limit=1)
        if ambiente_ids:
            ambiente = parameter_obj.browse(cr, uid, ambiente_ids[0]).value
        else:
            raise osv.except_osv('Error','No ha configurado un ambiente para la generacion de retenciones.')
        for ret in self.browse(cr, uid, ids, context):
            ret_number = '%09d'%(int(ret.name))
            if ret.digital_id:
                #Ya existe una retencion digital creada, primero verifico si ya se encuentra autorizada
                if ret.digital_id.state == 'autorizado':
                    raise osv.except_osv('Error','La retencion digital ya se encuentra autorizada por el SRI')
                elif ret.digital_id.state == 'proceso':
                    raise osv.except_osv('Error','La retencion se encuentra en proceso, por favor primero verifique el estado de la misma')
            if ret.partner_id.email:
                email = ret.partner_id.email
            else:
                raise osv.except_osv('Error','Proveedor sin correo electronico, por favor configure el correo electronico')

            if user.company_id.ruc_company:
                RUC = user.company_id.ruc_company
            else:
                raise osv.except_osv('Error','No se ha configurado el RUC de la Institucion')

            cont_especial = ""
            if user.company_id.cont_especial!="":
                cont_especial= user.company_id.cont_especial
            detalle_csv = open(carpeta_RE+'/pendientes_siim/'+"detalle-codDoc07-docNo"+establecimiento+'-'+punto_emision+'-'+ret_number+'.csv','w')
            writer_detalle = csv.writer(detalle_csv, delimiter=';')
            titulo_detalle = ["codigo","codigoRetencion","baseImponible","porcentajeRetener","valorRetenido","codDocSustento","numDocSustento","fechaEmisionDocSustento"]
            writer_detalle.writerow(titulo_detalle)
            for tax in ret.tax_ids:
                codigo_retencion = tax.tax_code_id.code
                if tax.tax_group in ['ret_vat_b','ret_vat_srv']:
                    codigo = '2'
                    if tax.percent == '10':
                        codigo_retencion = '9'
                    elif tax.percent == '20':
                        codigo_retencion = '10'
                    elif tax.percent == '30':
                        codigo_retencion = '1'
                    elif tax.percent == '70':
                        codigo_retencion = '2'
                    elif tax.percent == '100':
                        codigo_retencion = '3'
                    elif tax.percent == '0':
                        codigo_retencion = '7'
                elif tax.tax_group == 'ret_ir':
                    codigo = '1'
                    codigo_retencion = tax.base_code_id.code
                baseImponible = '{:.2f}'.format(tax.base)
                porcentajeRetener = tax.percent
                valorRetenido = '{:.2f}'.format(abs(tax.amount))
                codDocSustento = '01'
                if not len(ret.num_document)==15:
                    raise osv.except_osv('Error', 'El número de la factura proveedor debe ser 15 digitos.')
                numDocSustento = ret.num_document
                fechaEmisionDocSustento = dt.strptime(ret.invoice_id.date_invoice,'%Y-%m-%d').strftime('%d/%m/%Y')
                linea = [codigo,codigo_retencion,baseImponible,porcentajeRetener,valorRetenido,codDocSustento,numDocSustento,fechaEmisionDocSustento]
                writer_detalle.writerow(linea)
            detalle_csv.close()
            razonSocial = user.company_id.name
            razonSocial = unicodedata.normalize('NFKD',razonSocial).encode('ascii','ignore')
            nombreComercial = user.company_id.name
            nombreComercial = unicodedata.normalize('NFKD',nombreComercial).encode('ascii','ignore')
            direccionMatriz= ustr(user.company_id.street)
            dirEstablecimiento = ustr(user.company_id.street)
            tipoIdentificaconSujetoRetenido = '04'
            if len(ret.partner_id.ced_ruc) == 10:
                tipoIdentificaconSujetoRetenido = '05'
            razonSocialSujetoRetenido = ret.partner_id.name
            razonSocialSujetoRetenido = unicodedata.normalize('NFKD',razonSocialSujetoRetenido).encode('ascii','ignore')
            identificacionSujetoRetenido = ret.partner_id.ced_ruc
            cabecera_csv = open(carpeta_RE+'/pendientes_siim/'+"cabecera-codDoc07-docNo"+establecimiento+'-'+punto_emision+'-'+ret_number+'.csv','w')
            writer = csv.writer(cabecera_csv, delimiter=';')
            titulo_cabecera = ["ambiente","tipoEmision","razonSocial","nombreComercial","RUC","claveAcceso","codDoc","estab","ptoEmi","secuencial","direccionMatriz","fechaDeEmision","dirEstablecimiento","contribuyenteEspecial","obligadoContabilidad","tipoIdentficaconSujetoRetenido","razonSocialSujetoRetenido","identificacionSujetoRetenido","periodoFiscal","campoAdicional:email"]
            writer.writerow(titulo_cabecera)
            
            datos_cabecera = [ambiente,1,razonSocial,nombreComercial,RUC,'','07',establecimiento,punto_emision,ret_number,direccionMatriz,dt.strptime(ret.date,'%Y-%m-%d').strftime('%d/%m/%Y'),dirEstablecimiento,cont_especial,"SI",tipoIdentificaconSujetoRetenido,razonSocialSujetoRetenido,identificacionSujetoRetenido,ret.invoice_id.period_id.name,email]
            writer.writerow(datos_cabecera)
            cabecera_csv.close()
            source_cab = carpeta_RE+'/pendientes_siim/'+"cabecera-codDoc07-docNo"+establecimiento+'-'+punto_emision+'-'+ret_number+'.csv'
            dest_cab = carpeta_RE+'/ficheroscsvpendientes/'+"cabecera-codDoc07-docNo"+establecimiento+'-'+punto_emision+'-'+ret_number+'.csv'
            
            source_det = carpeta_RE+'/pendientes_siim/'+"detalle-codDoc07-docNo"+establecimiento+'-'+punto_emision+'-'+ret_number+'.csv'
            dest_det = carpeta_RE+'/ficheroscsvpendientes/'+"detalle-codDoc07-docNo"+establecimiento+'-'+punto_emision+'-'+ret_number+'.csv'
            #muevo los archivos a la carpeta pendientes
            shutil.move(source_det,dest_det)
            shutil.move(source_cab,dest_cab)
            #genero el documento digital en estado en proceso
            if ret.digital_id:
                digital_obj.unlink(cr,uid,[ret.digital_id.id])
            vals = {
                'name': establecimiento+'-'+punto_emision+'-'+ret_number,
                'date': ret.date,
                'email_a_enviar': email,
                'tipo': 'retention',
                'state': 'proceso',
                'state_email': 'noenviado',
                'retention_id': ret.id,
            }
            doc_id = digital_obj.create(cr, uid, vals)
            self.write(cr, uid, [ret.id], {'digital_id': doc_id})
        return True
        
    def action_validate(self, cr, uid, ids, number=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado
        number: Numero posible para usar en el documento

        Metodo que valida el documento, su principal
        accion es numerar el documento segun el parametro number
        '''
        seq_obj = self.pool.get('ir.sequence')
        inv_obj = self.pool.get('account.invoice')
        retentions = self.browse(cr, uid, ids)
        for ret in retentions:
            seq_id = ret.invoice_id.journal_id.auth_ret_id.sequence_id.id
            seq = seq_obj.browse(cr, uid, seq_id)
            ret_num = number
            if number is None:
                ret_number = seq_obj.get(cr, uid, seq.code)
                ret_num = ret_number
                inv_obj.write(cr, uid, [ret.invoice_id.id],{'manual_ret_num': ret_num})
            else:
                padding = seq.padding
                ret_number = str(number).zfill(padding)
            self._amount_total(cr, uid, [ret.id], [], {}, {})                
            number = ret.auth_id.serie_entidad + ret.auth_id.serie_emision + ret_number
            self.write(cr, uid, ret.id, {'state': 'done', 'name': ret_num, 'number': number })
            self.log(cr, uid, ret.id, _("La retención %s fue generada.") % number)
        return True



    
    def action_cancel(self, cr, uid, ids, *args):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para cambiar de estado a cancelado
        el documento
        '''
        for ret in self.browse(cr, uid, ids):
            data = {'state': 'cancel'}
            if ret.to_cancel:
                if len(ret.name) == 9:
                    number = ret.auth_id.serie_entidad + ret.auth_id.serie_emision + ret.name
                    data.update({'number': number, 'name': number})
                else:
                    raise osv.except_osv('Error', 'El número debe ser de 9 dígitos.')
            if ret.digital_id:
#                if ret.digital_id.state == 'autorizado':
#                    raise osv.except_osv('Error','La retencion digital ya se encuentra autorizada por el SRI')
#                elif ret.digital_id.state == 'proceso':
#                    raise osv.except_osv('Error','La retencion se encuentra en proceso, por favor primero verifique el estado de la misma')
                if ret.digital_id.state == 'noautorizado':
                    self.pool.get('digital.retention').unlink(cr, 1, [ret.digital_id.id])
                    
            self.write(cr, uid, ret.id, data)
        return True

    def action_early(self, cr, uid, ids, *args):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para cambiar de estado a cancelado
        el documento
        '''        
        self.write(cr, uid, ids, {'state': 'early'})
        return True        

account_retention()


class account_invoice_tax(osv.osv):

    _name = 'account.invoice.tax'
    _inherit = 'account.invoice.tax'
   
    _columns = {
        'pay':fields.boolean('Pagado'),
        'partner_id': fields.many2one('res.partner', 'SRI'),
        'partner_id2':fields.related('invoice_id','partner_id',type='many2one',relation='res.partner',string='Proveedor',store=True),
        'ruc': fields.related('partner_id2','ced_ruc',type='char',size=15,string='Identificador',store=True),        
        'cedula': fields.related('partner_id','ced_ruc',type='char',size=15,string='Identificador',store=True),        
        'fiscal_year' : fields.char('Ejercicio Fiscal', size = 4),
        'tax_group' : fields.selection([('vat','IVA Diferente de 0%'),
                                        ('vat0','IVA 0%'),
                                        ('novat','No objeto de IVA'),
                                        ('ret_vat_b', 'Retención de IVA (Bienes)'),
                                        ('ret_vat_srv', 'Retención de IVA (Servicios)'),
                                        ('ret_ir', 'Ret. Imp. Renta'),
                                        ('no_ret_ir', 'No sujetos a Ret. de Imp. Renta'), 
                                        ('imp_ad', 'Imps. Aduanas'),
                                        ('ice', 'ICE'),
                                        ('other','Other')], 'Grupo', required=True),        
        'percent' : fields.char('Porcentaje', size=20),
        'num_document': fields.char('Num. Comprobante', size=50),
        'retention_id': fields.many2one('account.retention', 'Retención', select=True),
        'date':fields.related('invoice_id','date_invoice',type='date',string='Fecha',store=True),
        'base': fields.float('Base'),
        'amount': fields.float('Amount'),
        'base_amount': fields.float('Base Code Amount'),
        'tax_amount': fields.float('Tax Code Amount'),
        'budget_id':fields.many2one('budget.certificate.line','Partida'),
        }

    #metodo q crea las lineas de impuestos y retenciones, la base imponible de IVA saca mal
    def compute(self, cr, uid, invoice_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        tax_map_obj = self.pool.get('account.tax.map')
        cur_obj = self.pool.get('res.currency')
        company_obj = self.pool.get('res.company')
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id
        compania = company_obj.browse(cr, uid, 1)
        for line in inv.invoice_line:
            aux = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, inv.address_invoice_id.id, line.product_id, inv.partner_id)['taxes']
            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, inv.address_invoice_id.id, line.product_id, inv.partner_id)['taxes']:
                partner_id = line.partner_id.id
                if tax['tax_group'] in ['ret_vat_b', 'ret_vat_srv','ret_ir']:
                    if compania.tax_company_id:
                        partner_id = compania.tax_company_id.id
                tax['price_unit'] = cur_obj.round(cr, uid, cur, tax['price_unit'])
                val={}
                tax_group = self.pool.get('account.tax').read(cr, uid, tax['id'],['tax_group', 'amount', 'porcentaje','partner_id'])
                #num_document para account.invoice.tax
                if line.invoice_id.reference_type == 'multi_invoice':
                    val['num_document'] = line.invoice_number
                elif line.invoice_id.reference_type == 'invoice_partner':
                    val['num_document'] = line.invoice_id.reference
                    val['invoice_id'] = inv.id
                    val['name'] = tax['name']
                    val['tax_group'] = tax_group['tax_group']
                    val['percent'] = tax_group['porcentaje']
                    val['partner_id'] = partner_id 
                    val['amount'] = tax['amount']
                    val['manual'] = False
                    val['sequence'] = tax['sequence']
                    val['base'] = tax['price_unit'] * line['quantity']
                    val['budget_id'] = line.budget_id.id
                if tax_group['tax_group'] in ['ret_vat_b', 'ret_vat_srv']:
                    ret = float(str(tax_group['porcentaje'])) / 100.0
                    bi = tax['price_unit'] * line['quantity']
                    if ret!=0:
                        imp = (abs(tax['amount']) / (ret * bi)) * 100.0
                        val['base'] = (tax['price_unit'] * line['quantity']) * imp / 100.0
                    else:
                        imp = (abs(tax['amount']) / (bi)) * 100.0    
                        val['base'] = (bi * 0.14)
                else:
                    val['base'] = tax['price_unit'] * line['quantity']
                if inv.type in ('out_invoice','in_invoice', 'liq_purchase'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = val['base'] * tax['base_sign']
                    val['tax_amount'] = val['amount'] * tax['tax_sign']
                    val['budget_id'] = line.budget_id.id
#                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
#                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    #aqui seria de mandarse el cambio de cuenta de taxes en base a la tabla y pasar tambien la partida presupuestaria
                    impuesto = tax_obj.browse(cr, uid, tax['id'])
                    if inv.aux_invoice:
                        if inv.certificate_id:
                            if impuesto.tax_map_ids:
                                if not line.budget_id:
                                    raise osv.except_osv('Error de Usuario', 'El detalle de la factura no tiene partida prespuestaria, seleccione uno.')
                                partida = line.budget_id.budget_post.code[0:2]
                                budget_det_ids = tax_map_obj.search(cr, uid, [('budget','=',partida),('tax_id','=',impuesto.id)])
                                if budget_det_ids:
                                    budget_det = tax_map_obj.browse(cr, uid, budget_det_ids[0])
                                    val['account_id'] = budget_det.account_id.id
                                else:
                                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                            else:
                                val['account_id'] = tax['account_collected_id'] or line.account_id.id
                                val['budget_id'] =  line.budget_id.id
                        else:
                            val['account_id'] = tax['account_collected_id'] or line.account_id.id
                            val['budget_id'] = line.budget_id.id
                    else:
                        if impuesto.tax_map_ids:
                            if not line.budget_id:
                                raise osv.except_osv('Error de Usuario', 'El detalle de la factura no tiene partida prespuestaria, seleccione uno.')
                            partida = line.budget_id.budget_post.code[0:2]
                            budget_det_ids = tax_map_obj.search(cr, uid, [('budget','=',partida),('tax_id','=',impuesto.id)])
                            if budget_det_ids:
                                budget_det = tax_map_obj.browse(cr, uid, budget_det_ids[0])
                                val['account_id'] = budget_det.account_id.id
                            else:
                                val['account_id'] = tax['account_collected_id'] or line.account_id.id
                                val['budget_id'] = line.budget_id.id
                        else:
                            val['account_id'] = tax['account_collected_id'] or line.account_id.id
                            val['budget_id'] = line.budget_id.id
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = val['base'] * tax['ref_base_sign']
                    val['tax_amount'] = val['amount'] * tax['ref_tax_sign']
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['budget_id'] =  line.budget_id.id
#                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                key = (val['tax_code_id'], val['base_code_id'], val['account_id'],val['budget_id'])
#                tax_grouped[key] = val
#                tax_grouped[key]['amount'] = val['amount']
#                tax_grouped[key]['base'] = val['base']
#                tax_grouped[key]['base_amount'] = val['base_amount']
#                tax_grouped[key]['tax_amount'] = val['tax_amount']
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']
        for t in tax_grouped:
            tax_grouped[t]['amount'] = cur_obj.round(cr, uid, cur, tax_grouped[t]['amount'])
            tax_grouped[t]['tax_amount'] = cur_obj.round(cr, uid, cur, tax_grouped[t]['tax_amount'])
            tax_grouped[t]['base_amount'] = cur_obj.round(cr, uid, cur, tax_grouped[t]['base_amount'])
        for t in tax_grouped.values():
            t['base'] = t['base']
            t['amount'] = t['amount']
            t['base_amount'] = t['base_amount']
            t['tax_amount'] = t['tax_amount']
        return tax_grouped

    def move_line_get(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_tax WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            if not t['amount'] \
                    and not t['tax_code_id'] \
                    and not t['tax_amount']:
                continue
            res.append({
                'tax_group':t['tax_group'],
                'type':'tax',
                'name':t['name'],
                'price_unit': t['amount'],
                'quantity': 1,
                'price': t['amount'] or 0.0,
                'account_id': t['account_id'],
                'tax_code_id': t['tax_code_id'],
                'tax_amount': t['tax_amount'],
                'budget_id_cert':t['budget_id'],
            })
        return res    

    _defaults = dict(
        fiscal_year = time.strftime('%Y'),
        pay = False,
    )    

account_invoice_tax()


class Invoice(osv.osv):
    
    _inherit = 'account.invoice'
    __logger = logging.getLogger(_inherit)

    def create1(self, cr, uid, vals, context):
        period_obj = self.pool.get('account.period')
        if vals.has_key('reference'):
            if vals['reference']:
                vals['new_number'] = vals['reference']
        if vals.has_key('new_number'):
            vals['reference'] = vals['new_number']
        if vals.has_key('date_invoice'):
            aux_date = vals['date_invoice']
            period_ids = period_obj.find(cr, uid, aux_date)
            if period_ids:
                vals['period_id'] = period_ids[0]
        return super(Invoice, self).create(cr, uid, vals, context=None)

    def write(self, cr, uid, ids,vals,context=None):
        if vals.has_key('new_number'):
            vals['reference'] = vals['new_number']
        return super(Invoice, self).write(cr, uid, ids, vals,context=None)    

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoices = self.read(cr, uid, ids, ['state','internal_number'], context=context)
        unlink_ids = []
        for t in invoices:
            if t['state'] in ('draft', 'cancel'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('You can not delete an invoice which is open or paid. We suggest you to refund it instead.'))
        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True

    def action_cancel(self, cr, uid, ids, *args):
        context = {} # TODO: Use context from arguments
        account_move_obj = self.pool.get('account.move')
        invoices = self.read(cr, uid, ids, ['move_id', 'payment_ids'])
        move_ids = [] # ones that we will need to remove
        for i in invoices:
            if i['move_id']:
                move_ids.append(i['move_id'][0])
            if i['payment_ids']:
                account_move_line_obj = self.pool.get('account.move.line')
                pay_ids = account_move_line_obj.browse(cr, uid, i['payment_ids'])
                for move_line in pay_ids:
                    if move_line.reconcile_partial_id and move_line.reconcile_partial_id.line_partial_ids:
                        raise osv.except_osv(_('Error !'), _('You can not cancel an invoice which is partially paid! You need to unreconcile related payment entries first!'))

        # First, set the invoices as cancelled and detach the move ids
        self.write(cr, uid, ids, {'state':'cancel', 'move_id':False})
        if move_ids:
            # second, invalidate the move(s)
            move_aux = account_move_obj.browse(cr, uid, move_ids[0])
            if move_aux.state=='posted':
                account_move_obj.button_cancel(cr, uid, move_ids, context=context)
                account_move_obj.write(cr, uid, [move_aux.id],{'state':'anulado'})
            elif move_aux.state=='draft':
                account_move_obj.unlink(cr, uid, move_ids, 1,context=context)
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            #si el move esta ya validaddo
#            if move_aux.state=='draft':
 #               account_move_obj.unlink(cr, uid, move_ids, 1,context=context)
        self._log_event(cr, uid, ids, -1.0, 'Cancel Invoice')
        return True

    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        result = {}
        cxp_ids = self.pool.get('config.cxp').search(cr, uid, [])
        config_acc_ids = [a.account_id.id for a in self.pool.get('config.cxp').browse(cr, uid, cxp_ids, context)]
        for invoice in self.browse(cr, uid, ids, context=context):
            checked_partial_rec_ids = []
            result[invoice.id] = 0.0
            if invoice.move_id:
                for move_line in invoice.move_id.line_id:
                    if move_line.account_id.type in ('receivable','payable') and move_line.partner_id.id == invoice.partner_id.id:
#                    if move_line.account_id.id in config_acc_ids or move_line.account_id.type in ('receivable'):#type in ('receivable','payable'):
                        if move_line.reconcile_partial_id:
                            partial_reconcile_id = move_line.reconcile_partial_id.id
                            if partial_reconcile_id in checked_partial_rec_ids:
                                continue
                            checked_partial_rec_ids.append(partial_reconcile_id)
                        result[invoice.id] += move_line.amount_residual_currency
        return result    

    def move_line_id_payment_gets(self, cr, uid, ids, *args):
        """
        redefinicion para considerar las cuentas de la tabla de configuracion
        de cuentas por pagar
        """
        cxp_obj = self.pool.get('config.cxp')
        cxp_ids = cxp_obj.search(cr, uid, [])
        acc_ids = cxp_obj.read(cr, uid, cxp_ids, ['account_id'])
        acc_ids = [i['account_id'][0] for i in acc_ids]
#        if not acc_ids:
#            raise osv.except_osv('Error de configuracion', 
#                                 'No se ha configurado las cuentas por pagar para la aplicacion presupuestaria')
#        res = {}
#        if not ids: return res
#        if len(ids)==1:
#            invs = '(%s)' % ids[0]
#        else:
#            invs = str(tuple(ids))
#        aux = '(' + str(acc_ids[0]) + ')'
#        sql = 'SELECT i.id, l.id FROM account_move_line l LEFT JOIN account_invoice i ON (i.move_id=l.move_id) WHERE i.id IN %s AND (l.account_id in %s OR l.account_id=i.account_id)' % (invs, tuple(acc_ids))
#vale        sql = 'SELECT i.id, l.id FROM account_move_line l LEFT JOIN account_invoice i ON (i.move_id=l.move_id) WHERE i.id IN %s AND (l.account_id in %s OR l.account_id=i.account_id)' % (invs, aux)
#        cr.execute(sql)
        res = {}
        if not ids: return res
        cr.execute('SELECT i.id, l.id '\
                   'FROM account_move_line l '\
                   'LEFT JOIN account_invoice i ON (i.move_id=l.move_id) '\
                   'WHERE i.id IN %s '\
                   'AND l.account_id=i.account_id',
                   (tuple(ids),))
        for r in cr.fetchall():
            res.setdefault(r[0], [])
            res[r[0]].append( r[1] )
        return res    

    def invoice_pay_customer_1(self, cr, uid, ids, context=None):
        """
        Redefinicion para cargar por defecto el compromiso
        presupuestario en el voucher
        """
        if not ids: return []
        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'context': {
                'default_partner_id': inv.partner_id.id,
                'default_amount': inv.residual,
                'default_name':inv.name,
                'close_after_process': True,
                'invoice_type':inv.type,
                'invoice_id':inv.id,
                'narration':inv.certificate_id.notes,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'default_certificate_id': inv.certificate_id.id
                }
        }    

    def _get_analytic_lines_1(self, cr, uid, id, context=None):
        """
        Redefinicion para incluir en la afectacion de costos
        el IVA
        """
        acc_obj = self.pool.get('account.analytic.account')
        tax_obj = self.pool.get('account.tax')
        if context is None:
            context = {}
        inv = self.browse(cr, uid, id)
        cur_obj = self.pool.get('res.currency')

        company_currency = inv.company_id.currency_id.id
        if inv.type in ('out_invoice', 'in_refund'):
            sign = 1
        else:
            sign = -1

        iml = self.pool.get('account.invoice.line').move_line_get(cr, uid, inv.id, context=context)
        amt = 0
        for il in iml:
            if il['account_analytic_id']:
                if inv.type in ('in_invoice', 'in_refund'):
                    ref = inv.reference
                else:
                    ref = self._convert_ref(cr, uid, inv.number)
                if not inv.journal_id.analytic_journal_id:
                    raise osv.except_osv(_('No Analytic Journal !'),_("You have to define an analytic journal on the '%s' journal!") % (inv.journal_id.name,))
                taxes = [tax for tax in il['taxes'] if tax.tax_group not in ['ret_vat_b','ret_vat_srv','ret_ir', 'other'] and tax.amount>0] #no es mejor in ['vat']
                taxes = tax_obj.compute_all(cr, uid, taxes, il['price'], 1)['taxes']
                il['tax_computed'] = sum([t['amount'] for t in taxes])
                amt = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, il['price'], context={'date': inv.date_invoice}) * sign
                il['analytic_lines'] = [(0,0, {
                    'name': il['name'],
                    'date': inv['date_invoice'],
                    'account_id': il['account_analytic_id'],
                    'unit_amount': il['quantity'],
                    'amount': il['price'],
                    'product_id': il['product_id'],
                    'product_uom_id': il['uos_id'],
                    'general_account_id': il['account_id'],
                    'journal_id': inv.journal_id.analytic_journal_id.id,
                    'ref': ref,
                    'budget_id_cert':il['budget_id_cert'],
                    'budget_accrued':True,
                })]
        return iml    


    def create_expedient_task(self, cr, uid, ids, context=None):
        """
        Definicion de metodo para cracion de tarea de tramite
        """
        raise NotImplementedError

    def action_budget_apply(self, cr, uid, ids, context=None):
        """
        Definicion de metodo para la aplicacion presupuestaria - DEVENGADO
        """
        return True

    def onchange_sustento(self, cr, uid, ids, sustento_id):
        res = {'value': {}}
        if not sustento_id:
            return res
        sustento = self.pool.get('account.ats.sustento').browse(cr, uid, sustento_id)
        res['value']['name'] = sustento.type
        return res

    def button_reset_taxes(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ait_obj = self.pool.get('account.invoice.tax')
        invoice_obj = self.pool.get('account.invoice')
        for id in ids:
            cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s", (id,))
            partner = self.browse(cr, uid, id, context=ctx).partner_id
            if partner.lang:
                ctx.update({'lang': partner.lang})
            invoice_aux =  invoice_obj.browse(cr, uid, id)
            if context.has_key('caja_fondo'):
                if context['caja_fondo']:
                    invoice_line = invoice_aux.invoice_line[0]
                    if invoice_line.cxp_id:
                        cxp_aux = invoice_line.cxp_id.id
                        self.pool.get('account.invoice').write(cr, uid, ids, {'account_id':cxp_aux}, context=ctx)
            #aux = ait_obj.compute(cr, uid, id, context=ctx)
            for taxe in ait_obj.compute(cr, uid, id, context=ctx).values():
#                taxe['tax_amount'] = float(Decimal(str(taxe['tax_amount'])).quantize(Decimal('.01'), rounding=ROUND_DOWN)) 
#                taxe['base_amount'] = float(Decimal(str(taxe['base_amount'])).quantize(Decimal('.01'), rounding=ROUND_DOWN)) 
#                taxe['amount'] = float(Decimal(str(taxe['amount'])).quantize(Decimal('.01'), rounding=ROUND_DOWN)) 
##                taxe['base'] = float(Decimal(str(taxe['base'])).quantize(Decimal('.01'), rounding=ROUND_DOWN))
                id_creado = ait_obj.create(cr, uid, taxe)
        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, ids, {'invoice_line':[]}, context=ctx)
        return True

    def button_compute(self, cr, uid, ids, context=None, set_total=True):
        self.button_reset_taxes(cr, uid, ids, context)
        for inv in self.browse(cr, uid, ids, context=context):
            if set_total:
                self.pool.get('account.invoice').write(cr, uid, [inv.id], {'check_total': inv.amount_total})
        return True

    def renumerate_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        seq_obj = self.pool.get('ir.sequence')
        for inv in self.browse(cr, uid, ids, context):
            context.update({'new_number': inv.new_number})
            self.action_number(cr, uid, ids, context)
        return True
    
    def print_invoice(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de liquidacion de compra
        '''        
        if not context:
            context = {}
        invoice = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [invoice.id], 'model': 'account.invoice'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'invoice_report',
            'model': 'account.invoice',
            'datas': datas,
            'nodestroy': True,                        
            }        

    def print_liq_purchase(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de liquidacion de compra
        '''        
        if not context:
            context = {}
        invoice = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [invoice.id], 'model': 'account.invoice'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_liq_purchase',
            'model': 'account.invoice',
            'datas': datas,
            'nodestroy': True,                        
            }

    def print_retention(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de retencion
        '''                
        if not context:
            context = {}
        invoice = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [invoice.retention_id.id],
                 'model': 'account.retention'}
        if invoice.retention_id:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.retention',
                'model': 'account.retention',
                'datas': datas,
                'nodestroy': True,            
                }

    def print_move(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de diario
        '''       
        if not context:
            context = {}
        if 'advance' in context:
            datas = {'ids' : ids,'model': 'account.move'}
        else: 
            invoice = self.browse(cr, uid, ids, context)[0]        
            datas = {'ids' : [invoice.move_id.id],
                     'model': 'account.move'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.move',
            'model': 'account.move',
            'datas': datas,
            'nodestroy': True,            
            }
    
    def _get_type(self, cr, uid, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        context: Variable goblal del sistema
        
        Metodo que devuelve el tipo basado en el contexto
        '''
        if context is None:
            context = {}
        return context.get('type', 'out_invoice')    

    def _amount_all(self, cr, uid, ids, fields, args, context=None):
        """
        Compute all total values in invoice object
        params:
        @cr cursor to DB
        @uid user id logged
        @ids active object ids
        @fields used fields in function, severals if use multi arg
        """
        res = {}
        cur_obj = self.pool.get('res.currency')

        invoices = self.browse(cr, uid, ids, context=context)
        for invoice in invoices:
            cur = invoice.currency_id
            res[invoice.id] = {
                'amount_vat': 0.0,
                'amount_untaxed': 0.0, 
                'amount_tax': 0.0,
                'amount_tax_retention': 0.0,
                'amount_tax_ret_ir': 0.0,
                'taxed_ret_ir': 0.0, 
                'amount_tax_ret_vatb': 0.0,
                'amount_tax_ret_vatsrv': 0.00,
                'taxed_ret_vatb': 0.0,
                'taxed_ret_vatsrv': 0.00,
                'amount_vat_cero': 0.0,
                'amount_novat': 0.0, 
                'amount_noret_ir': 0.0,
                'amount_total': 0.0,
                'amount_pay': 0.0,
                'invoice_discount': 0,
                'amount_discounted': 0.0,
            }

            #Total General
            not_discounted = 0
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
                if not line.invoice_line_tax_id:
                    res[invoice.id]['amount_vat_cero'] += line.price_subtotal                        
            for line in invoice.tax_line:
                if line.tax_group == 'vat':
                    res[invoice.id]['amount_vat'] += line.base
                    res[invoice.id]['amount_tax'] += line.amount                    
                elif line.tax_group == 'vat0':
                    res[invoice.id]['amount_vat_cero'] += line.base
                elif line.tax_group == 'novat':
                    res[invoice.id]['amount_novat'] += line.base
                elif line.tax_group == 'no_ret_ir':
                    res[invoice.id]['amount_noret_ir'] += line.base
                elif line.tax_group in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']:
                    res[invoice.id]['amount_tax_retention'] += line.amount
                    if line.tax_group == 'ret_vat_b':#in ['ret_vat_b', 'ret_vat_srv']:
                        res[invoice.id]['amount_tax_ret_vatb'] += line.base
                        res[invoice.id]['taxed_ret_vatb'] += line.amount
                    elif line.tax_group == 'ret_vat_srv':
                        res[invoice.id]['amount_tax_ret_vatsrv'] += line.base
                        res[invoice.id]['taxed_ret_vatsrv'] += line.amount                        
                    elif line.tax_group == 'ret_ir':
                        res[invoice.id]['amount_tax_ret_ir'] += line.base
                        res[invoice.id]['taxed_ret_ir'] += line.amount
                elif line.tax_group == 'ice':
                    res[invoice.id]['amount_ice'] += line.amount

            # base vat not defined, amount_vat_cero by default
            if res[invoice.id]['amount_vat'] == 0 and res[invoice.id]['amount_vat_cero'] == 0:
                res[invoice.id]['amount_vat_cero'] = res[invoice.id]['amount_untaxed']

            res[invoice.id]['amount_pay']  = res[invoice.id]['amount_vat'] + res[invoice.id]['amount_vat_cero'] \
                                             + res[invoice.id]['amount_tax']
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_pay'] + res[invoice.id]['amount_tax_retention']
        self.__logger.info('Calculado valores de factura')
        return res

    def _get_reference_type(self, cr, uid, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para crear la lista de tipos de referencia en el documento
        '''                        
        return [('invoice_partner','Factura Proveedor'),
                ('multi_invoice','Multi-Factura'),
                ('liq_purchase', 'Referencia'),
                ('retention', 'Retencion Cliente'),
                ('in_refund', 'Nota de Credito'),
                ('guia', 'Guía de Remisión'),
                ('out_refund', 'Nota de Débito'),
                ('none', 'Ninguna')]

    def _get_ref_type(self, cr, uid, context):
        self.__logger.debug("contexto para referencia %s", context)
        if context.has_key('type'):
            if context['type'] == 'in_invoice':
                return 'invoice_partner'
            elif context['type'] == 'out_invoice':
                return 'guia'
            elif context['type'] == 'liq_purchase':
                return 'liq_purchase'
            elif context['type'] == 'out_refund':
                return 'out_refund'
            else:
                return 'in_refund'
        return 'invoice_partner'

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()        

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            if record.new_number:
                name = str(record.new_number) + ' - ' + str(record.manual_ret_num)
            else:
                name = str(record.reference) + ' - ' + str(record.manual_ret_num)
            res.append((record.id, name))
        return res        

    def _check_retention(self, cr, uid, ids, field_name, context, args):
        res = {}
        for inv in self.browse(cr, uid, ids, context):
            res[inv.id] = {
                'retention_ir': False,
                'retention_vat': False,
                'no_retention_ir': False,
                }
            for tax in inv.tax_line:
                if tax.tax_group in ['ret_vat_b', 'ret_vat_srv']:
                    res[inv.id]['retention_vat'] = True
                elif tax.tax_group == 'ret_ir':
                    res[inv.id]['retention_ir'] = True
                elif tax.tax_group == 'no_ret_ir':
                    res[inv.id]['no_retention_ir'] = True
        return res

    def _get_num_retentions(self, cr, uid, context=None):
        if context is None:
            context = {}
        numbers = self.pool.get('account.retention.cache')
        num_ids = numbers.search(cr, uid, [('active','=',True)])
        res = numbers.read(cr, uid, num_ids, ['name', 'id'])
        res = [(r['id'], r['name']) for r in res]
        return res

    def _get_num_to_use(self, cr, uid, ids, field_name, args, context):
        res = {}
        invoices = self.browse(cr, uid, ids, context)
        for inv in invoices:
            if inv.type in ['out_invoice', 'liq_purchase']:
                if inv.journal_id.auth_id and inv.journal_id.auth_id.sequence_id:
                    res[inv.id] = str(inv.journal_id.auth_id.sequence_id.number_next)
                elif inv.state in ['cancel', 'open', 'paid']:
                    return res
                else:
                    raise osv.except_osv('Error', 'No se ha configurado una autorización en el diario.')
        return res

    def _get_supplier_number(self, cr, uid, ids, fields, args, context):
        res = {}
        for inv in self.browse(cr, uid, ids, context):
            number = '/'
            if inv.aux_invoice:
                number = inv.new_number
            else:
                if inv.type == 'in_invoice' and inv.auth_inv_id:
                    n = inv.reference and inv.reference.zfill(9) or '*'
                    number = ''.join([inv.auth_inv_id.serie_entidad,inv.auth_inv_id.serie_emision,n])
            res[inv.id] = number
        return res

    def create_move_nc_supp(self, cr, uid, ids, context):
        """
        Crear asiento contable de nota de credito
        sobre facturas de proveedor
        """
        #pasar en el context en 'novalidate' True
        config_obj = self.pool.get('config.cxp')
        invoice_obj = self.pool.get('account.invoice')
        acc_move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        lines_data = {}
        for this in self.browse(cr, uid, ids):
            numero = this.name
            context['novalidate'] = True
            move_credit = {
                    'name':this.name,
                    'journal_id':this.journal_id.id,
                    'period_id':this.period_id.id,
                    'date':this.date_invoice,
                    'line_id': []
                    }
            for line in this.invoice_line:
                #Cuentas por pagar / por cobrar
                res = config_obj.search(cr, uid, [('budget','=',line.categ_id.budget)], limit=1)
                ctaxp = config_obj.browse(cr, uid, res[0])
                if not lines_data.get(ctaxp.account_id.id):
                    lines_data[ctaxp.account_id.id] = {
                        'account_id': ctaxp.account_id.id,
                        'credit': 0,
                        'budget_id': line.budget_id.id,
                        'partner_id': line.invoice_id.partner_id.id,
                        'name': 'NOTA DE CREDITO'
                        }
                lines_data[ctaxp.account_id.id]['credit'] -= line.price_total
                # Cuentas de gasto
                if not lines_data[line.account_id.id]:
                    lines_data[line.account_id.id] = {'account_id': line.account_id.id,
                                                      'debit': 0,
                                                      'budget_accrued': True,
                                                      'partner_id': line.invoice_id.partner_id.id
                                                      }
        return True

    def create_move_nc(self, cr, uid, ids, context):
#        """Creates invoice related analytics and financial move lines"""
        #clonar el asiento y cambiar los signos nada mas
        invoice_obj = self.pool.get('account.invoice')
        acc_move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        for this in self.browse(cr, uid, ids):
            numero = this.name
            move_copy = acc_move_obj.copy_data(cr, uid,this.related_invoice_id.move_id.id)
            move_creado_id = acc_move_obj.create(cr, uid, {
                    'name':this.name,
                    'journal_id':this.journal_id.id,
                    'period_id':this.period_id.id,
                    'date':this.date_invoice,
                    })
            invoice_obj.write(cr, uid, this.id, {
                    'move_id':move_creado_id,
                    })
        i = 0
        for line in move_copy['line_id']:
            move_copy['line_id'][i][2]['credit'] =  (move_copy['line_id'][i][2]['credit']) * (-1)
            move_copy['line_id'][i][2]['debit'] =  (move_copy['line_id'][i][2]['debit']) * (-1)
#line[2]['credit']
            move_copy['line_id'][i][2]['name'] = numero
            move_copy['line_id'][i][2]['move_id'] = move_creado_id
            line_id = move_line_obj.create(cr, uid, move_copy['line_id'][i][2])
            i += 1
        return True        

    def line_get_convert_1(self, cr, uid, x, part, date, context=None):
        company_obj = self.pool.get('res.company')
        compania = company_obj.browse(cr, uid, 1)
        partner_id = x.get('partner_id') and x['partner_id'] or part
        if x.has_key('tax_group'):
            if x['tax_group'] in ['ret_vat_b', 'ret_vat_srv','ret_ir']:
                if compania.tax_company_id:
                    partner_id = compania.tax_company_id.id
        return {
            'date_maturity': x.get('date_maturity', False),
            'partner_id': partner_id,#x.get('partner_id') and x['partner_id'] or part,
            'name': x['name'][:64],
            'date': date,
            'debit': x['price']>0 and x['price'],
            'credit': x['price']<0 and -x['price'],
            'account_id': x['account_id'],
            'analytic_lines': x.get('analytic_lines', []),
            'amount_currency': x['price']>0 and abs(x.get('amount_currency', False)) or -abs(x.get('amount_currency', False)),
            'currency_id': x.get('currency_id', False),
            'tax_code_id': x.get('tax_code_id', False),
            'tax_amount': x.get('tax_amount', False),
            'ref': x.get('ref', False),
            'quantity': x.get('quantity',1.00),
            'product_id': x.get('product_id', False),
            'product_uom_id': x.get('uos_id', False),
            'analytic_account_id': x.get('account_analytic_id', False),
            'budget_id_cert': x.get('budget_id_cert', False),
            'budget_accrued': x.get('budget_accrued', False),
            'tax_computed': x.get('tax_computed', 0)
        }    

    def compute_invoice_totals(self, cr, uid, inv, company_currency, ref, invoice_move_lines):
        total = 0
        total_currency = 0
        cur_obj = self.pool.get('res.currency')
        for i in invoice_move_lines:
            if inv.currency_id.id != company_currency:
                i['currency_id'] = inv.currency_id.id
                i['amount_currency'] = i['price']
#                i['price'] = cur_obj.compute(cr, uid, inv.currency_id.id,
#                        company_currency, i['price'],
#                        context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
            else:
                i['amount_currency'] = False
                i['currency_id'] = False
            i['ref'] = ref
            if inv.type in ('out_invoice','in_refund'):
                total += i['price']
                total_currency += i['amount_currency'] or i['price']
                i['price'] = - i['price']
            else:
                total -= i['price']
                total_currency -= i['amount_currency'] or i['price']
        return total, total_currency, invoice_move_lines

    def check_tax_lines(self, cr, uid, inv, compute_taxes, ait_obj):
        return True
        if not inv.tax_line:
            for tax in compute_taxes.values():
                ait_obj.create(cr, uid, tax)
        else:
            tax_key = []
            for tax in inv.tax_line:
                if tax.manual:
                    continue
                key = (tax.tax_code_id.id, tax.base_code_id.id, tax.account_id.id)
                tax_key.append(key)
                if not key in compute_taxes:
                    raise osv.except_osv(_('Warning !'), _('Global taxes defined, but they are not in invoice lines !'))
                base = compute_taxes[key]['base']
                if abs(base - tax.base) > inv.company_id.currency_id.rounding:
                    raise osv.except_osv(_('Warning !'), _('Tax base different!\nClick on compute to update the tax base.'))
            for key in compute_taxes:
                if not key in tax_key:
                    raise osv.except_osv(_('Warning !'), _('Taxes are missing!\nClick on compute button.'))

    def action_move_create_1(self, cr, uid, ids, context=None):
#        """Creates invoice related analytics and financial move lines"""
#        import pdb
#        pdb.set_trace()
        tax_obj = self.pool.get('account.tax')
        account_obj = self.pool.get('account.account')
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        config_obj = self.pool.get('config.cxp')
        bitem_obj = self.pool.get('budget.item')
        post_obj = self.pool.get('budget.post')
        cert_line_obj = self.pool.get('budget.certificate.line')
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.certificate_id.state=='commited' and type=='in_invoice':
                raise osv.except_osv(_('Error !'), _('El presupuesto referencial debe estar comprometido.'))
            if inv.type == 'out_refund':
                self.create_move_nc(cr, uid, ids, context=context)
                return True
            elif inv.type== 'in_refund':
                self.create_move_nc_supp(cr, uid, ids, context=context)
                return True
        for inv in self.browse(cr, uid, ids, context=context):
            #llamar automatico al calcular impuestos
            self.button_reset_taxes(cr, uid, ids, context)
            if inv.type=='in_invoice':
                for line_aux in inv.invoice_line:
                    if not line_aux.budget_id:
                        raise osv.except_osv(_('Error de usuario !'), _('Verifique que las las lineas de factura tengan la partida presupuestaria.'))
            part = inv.partner_id.id
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error !'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines !'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue
            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            #ojo aqui debe ser por cada linea las ctas delos impuestos
#            for line_inV in inv.invoice_line:
            categ_line = inv.invoice_line[0].categ_id
#            ctx.update({'budget_type': categ_line.budget, 'aplic_id': categ_line.presp_aplic_id.id})
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
            company_currency = inv.company_id.currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
            # check if taxes are all computed
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)
            # I disabled the check_total feature
            #if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0):
            #    raise osv.except_osv(_('Bad total !'), _('Please verify the price of the invoice !\nThe real total does not match the computed total.'))
            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise osv.except_osv(_('Error !'), _("Can not create the invoice !\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. The latest line of your payment term must be of type 'balance' to avoid rounding issues."))
            # one move line per tax line
            iml += ait_obj.move_line_get(cr, uid, inv.id)  ##ojo este metodo
            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = self._convert_ref(cr, uid, inv.number)
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'

            diff_currency_p = inv.currency_id.id <> company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            #este metodo carga la linea de impuesto
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml)
            acc_id = inv.account_id.id

            name = inv['name'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = payment_term_obj.compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False, context=ctx)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                ctx.update({'date': inv.date_invoice})
                for t in totlines:
                    if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)
                    else:
                        amount_currency = False

                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': acc_id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency_p \
                                and amount_currency or False,
                        'currency_id': diff_currency_p \
                                and inv.currency_id.id or False,
                        'ref': ref,
                    })
            else:
                #aqui iterar por cada linea, leer la tabla de cxp en base a aplicacion presupuestaria
                #y mandar la linea
                for invoice_line in inv.invoice_line:
                    part = inv.partner_id.id
#                    config_ids = config_obj.search(cr, uid, [('budget','=',invoice_line.budget_id.budget_type_id.id)],limit=1)
#                    if len(config_ids)>0:
                        #toma la cuenta de la tabla
#                        config_ = config_obj.browse(cr, uid, config_ids)[0]
                    #tomar la cuenta x pagar de la linea
                    acc_id = inv.account_id.id#config_.account_id.id
                    if invoice_line.cxp_id:
                        acc_id = invoice_line.cxp_id.id
                    #calcular los impuestos + el subtotal para mandar en el campo total
                    valor_inc_iva = 0
                    price = invoice_line.price_unit * (1-(invoice_line.discount or 0.0)/100.0)
                    taxes = tax_obj.compute_all(cr, uid, invoice_line.invoice_line_tax_id, price, invoice_line.quantity, product=invoice_line.product_id, address_id=invoice_line.invoice_id.address_invoice_id, partner=invoice_line.invoice_id.partner_id)
                    for tax in taxes['taxes']:
                        if tax['tax_group'] in ['vat', 'vat0', 'novat']:
                            valor_inc_iva += taxes['total'] + tax['amount']
                        if tax['tax_group'] in ['ret_vat_b','ret_vat_srv','ret_ir','no_ret_ir','other']:
                            valor_inc_iva += tax['amount']
                    if len(taxes['taxes'])<1:
                        valor_inc_iva = taxes['total']
                    if inv.type in ('out_invoice'):
                        valor_inc_iva = valor_inc_iva * (-1)
                    aux_budget_id = invoice_line.budget_id.id
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': valor_inc_iva * (-1),#total,
                        'account_id': acc_id,
                        'date_maturity': inv.date_due or False,
                        'amount_currency': diff_currency_p \
                        and total_currency or False,
                        'currency_id': diff_currency_p \
                        and inv.currency_id.id or False,
                        'ref': ref,
                        'budget_id_cert':invoice_line.budget_id.id,
#                        'budget_accrued':True,
                            })
                #=======================================
#                iml.append({
#                        'type': 'dest',
#                        'name': name,
#                        'price': total,
#                        'account_id': acc_id,
#                        'date_maturity': inv.date_due or False,
#                        'amount_currency': diff_currency_p \
#                            and total_currency or False,
#                        'currency_id': diff_currency_p \
#                            and inv.currency_id.id or False,
#                        'ref': ref
#                        })
            date = inv.date_invoice or time.strftime('%Y-%m-%d')
#            part = inv.partner_id.id #este es el proveedor
            ctx['inv_type'] = inv.type
            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part, date, context=ctx)),iml)
#            line = self.group_lines(cr, uid, iml, line, inv) quitado mario
            journal_id = inv.journal_id.id
            journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
            if journal.centralisation:
                raise osv.except_osv(_('UserError'),
                        _('You cannot create an invoice on a centralised journal. Uncheck the centralised counterpart box in the related journal from the configuration menu.'))
            line = self.finalize_invoice_move_lines(cr, uid, inv, line)
            m = 0
            line_2 = []
            for line_aux in line:
                b_aux = False
                if line_aux[2]['debit']==0 and line_aux[2]['credit']==0:
                    b_aux = True
                elif line_aux[2]['debit']=='False' and line_aux[2]['credit']=='False':
                    b_aux= True
                if not b_aux:
                    line_2.append(line_aux)
            line = []
            line=line_2
            for line_aux in line:
                if line_aux[2]['debit']>0:
                    line_aux[2]['budget_accrued'] = True
#                    account_aux_id = line_aux[2]['account_id']
#                    account_aux = account_obj.browse(cr, uid, account_aux_id)
#                    if account_aux.budget_id:
#                        for cert_line in inv.certificate_id.line_ids:
#                            if cert_line.budget_id.budget_post_id==account_aux.budget_id:
#                                line_aux[2]['budget_id_cert']=cert_line.id
#                                line_aux[2]['budget_accrued']=True
#                            else:
#                                aux_code_post = cert_line.budget_id.budget_post_id.code[0:6]
#                                post_ids = post_obj.search(cr, uid, [('code','=',aux_code_post)])
#                                if account_aux.budget_id.id in post_ids:
#                                    line_aux[2]['budget_id_cert']=cert_line.id
#                                    line_aux[2]['budget_accrued']=True
#                    else:
#                        line_aux[2]['budget_id_cert']=aux_budget_id
#                        line_aux[2]['budget_accrued']=True
#                else:
#                    line_aux[2]['budget_id_cert']=aux_budget_id
            if inv.certificate_id:
                move = {
                    'ref': inv.reference and inv.reference or inv.name,
                    'line_id': line,
                    'journal_id': journal_id,
                    'date': date,
                    'narration':inv.comment,
                    'certificate_id':inv.certificate_id.id,
                    'partner_id':inv.partner_id.id,
                    'reposition':inv.reposition,
                    'to_check':True,
                    'afectacion':True,
                }
            else:
                move = {
                    'ref': inv.reference and inv.reference or inv.name,
                    'line_id': line,
                    'journal_id': journal_id,
                    'date': date,
                    'narration':inv.comment,
                    'reposition':inv.reposition,
                    'to_check':True,
                }
            period_id = inv.period_id and inv.period_id.id or False
            ctx.update(company_id=inv.company_id.id,
                       account_period_prefer_normal=True)
            if not period_id:
                period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
                period_id = period_ids and period_ids[0] or False
            if period_id:
                move['period_id'] = period_id
                for i in line:
                    i[2]['period_id'] = period_id
            if inv.certificate_id:
                move['narration']=inv.certificate_id.notes
            move_id = move_obj.create(cr, uid, move, context=ctx)
            new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            ctx.update({'invoice':inv})
            #quitado la validacion automatica
#            move_obj.post(cr, uid, [move_id], context=ctx)
        self._log_event(cr, uid, ids)
        return True
    
    def finalize_invoice_move_lines_1(self, cr, uid, invoice_browse, move_lines):
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines) -> move_lines
        Hook method to be overridden in additional modules to verify and possibly alter the
        move lines to be created by an invoice, for special cases.
        :param invoice_browse: browsable record of the invoice that is generating the move lines
        :param move_lines: list of dictionaries with the account.move.lines (as for create())
        :return: the (possibly updated) final move_lines to create for this invoice
        """
        account_obj = self.pool.get('account.account')
        tax_obj = self.pool.get('account.tax')
        for line in invoice_browse.invoice_line:
            inv_type = line.invoice_id.type
            if inv_type in ['in_refund','out_refund']:
                continue
            if not line.account_id.in_stock and line.account_id.account_comp_id and line.account_id.account_comp_id.account_comp_id:
                #los items de factura in_invoice van al debe
                comp1 = line.account_id.account_comp_id
                comp2 = line.account_id.account_comp_id.account_comp_id
                price = line.price_unit * (1-(line.discount or 0.0)/100.0)
                valor_inc_iva = 0
                taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
                for tax in taxes['taxes']:
                    if tax['tax_group'] in ['vat', 'vat0', 'novat']:
                        valor_inc_iva += taxes['total'] + tax['amount']
                data_line = {
                    'partner_id': line.partner_id.id,
                    'name': comp1.name,
                    'account_id': comp1.id,
#                    'credit': inv_type=='in_invoice' and (line.price_total or line.price_subtotal) or 0,
#                    'debit': inv_type=='out_invoice' and (line.price_total or line.price_subtotal) or 0,
                    'credit': inv_type=='in_invoice' and (valor_inc_iva or valor_inc_iva) or 0,
                    'debit': inv_type=='out_invoice' and (valor_inc_iva or valor_inc_iva) or 0,
                    'product_id': line.product_id.id,
                    'ref': line.invoice_id.reference,
                    'date': line.invoice_id.date_invoice
                    }
                data_line2 = {
                    'partner_id': line.partner_id.id,
                    'name': comp2.name,
                    'account_id': comp2.id,
#                    'debit': inv_type=='in_invoice' and (line.price_total or line.price_subtotal) or 0,
#                    'credit': inv_type=='out_invoice' and (line.price_total or line.price_subtotal) or 0,
                    'debit': inv_type=='in_invoice' and (valor_inc_iva or valor_inc_iva) or 0,
                    'credit': inv_type=='out_invoice' and (valor_inc_iva or valor_inc_iva) or 0,
                    'product_id': line.product_id.id,
                    'ref': line.invoice_id.reference,
                    'date': line.invoice_id.date_invoice                    
                    }
                move_lines.append((0, 0, data_line))
                move_lines.append((0, 0, data_line2))
        #order by debit, credit move lines
        temp_list = [line[2] for line in move_lines]
        newlist = sorted(temp_list, key=itemgetter('debit'))
        move_lines = [(0,0,line) for line in newlist]
        return move_lines

    def _get_invoice_from_line(self, cr, uid, ids, context=None):
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids    

    def _get_invoice_from_reconcile(self, cr, uid, ids, context=None):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids, context=context):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True

        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids    

    HELP_RET_TEXT = '''Automatico: El sistema identificara los impuestos y creara la retencion automaticamente, \
    Manual: El usuario ingresara el numero de retencion \
    Agrupar: Podra usar la opcion para agrupar facturas del sistema en una sola retencion.'''

    VAR_STORE = {
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            }

    PRECISION_DP = dp.get_precision('Account')    

    _columns = {
        'supplier_invoice_number':fields.char('Num. Factura',size=15),
        'id_ext':fields.char('Id. Ext',size=10),
        'tipo_codigo':fields.selection([('2','Iva 12'),('3','Iva 14')],'Tipo Impuesto'),
        'period_id': fields.many2one('account.period','Periodo'),
        'address_invoice_id': fields.many2one('res.partner.address', 'Invoice Address', 
                                              readonly=True, states={'draft':[('readonly',False)]}),
        'certificate_id':fields.many2one('budget.certificate','Compromiso Presupuestario'),
        'residual': fields.function(_amount_residual, digits_compute=dp.get_precision('Account'), string='Balance',
                                    store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line','move_id'], 50),
                'account.invoice.tax': (_get_invoice_tax, None, 50),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 50),
                'account.move.line': (_get_invoice_from_line, None, 50),
                'account.move.reconcile': (_get_invoice_from_reconcile, None, 50),
                },
            help="Remaining amount due."),        
        'supplier_number': fields.function(_get_supplier_number, method=True, type='char', size=32,
                                           string='Factura de Proveedor', store=True),
        'amount_ice': fields.function(_amount_all, method=True, digits_compute=PRECISION_DP, string='ICE',
                                      store=VAR_STORE, multi='all'),
        'amount_vat': fields.function(_amount_all, method=True,
                                      digits_compute=PRECISION_DP, string='Base 12 %', 
                                      store=VAR_STORE,
                                      multi='all'),
        'amount_untaxed': fields.function(_amount_all, method=True,
                                          digits_compute=PRECISION_DP, string='Untaxed',
                                          store=VAR_STORE,
                                          multi='all'),
        'amount_tax': fields.function(_amount_all, method=True,
                                      digits_compute=PRECISION_DP, string='Tax',
                                      store=VAR_STORE,
                                      multi='all'),
        'amount_total': fields.function(_amount_all, method=True,
                                        digits_compute=PRECISION_DP, string='Total a Pagar',
                                        store=VAR_STORE,
                                        multi='all'), 
        'amount_pay': fields.function(_amount_all, method=True,
                                      digits_compute=PRECISION_DP, string='Total',
                                      store=VAR_STORE,
                                      multi='all'),
        'amount_noret_ir': fields.function(_amount_all, method=True,
                                           digits_compute=PRECISION_DP, string='Monto no sujeto a IR',
                                           store=VAR_STORE,
                                           multi='all'),
        'amount_tax_retention': fields.function(_amount_all, method=True,
                                                digits_compute=PRECISION_DP, string='Total Retencion',
                                                store=VAR_STORE,
                                                multi='all'),
        'amount_tax_ret_ir': fields.function( _amount_all, method=True,
                                              digits_compute=PRECISION_DP, string='Base IR',
                                              store=VAR_STORE,
                                              multi='all'),
        'taxed_ret_ir': fields.function( _amount_all, method=True,
                                         digits_compute=PRECISION_DP, string='Impuesto IR',
                                         store=VAR_STORE,
                                         multi='all'),
        'amount_tax_ret_vatb' : fields.function( _amount_all,
                                                 method=True,
                                                 digits_compute=PRECISION_DP,
                                                 string='Base Ret. IVA',
                                                 store=VAR_STORE,
                                                 multi='all'),
        'taxed_ret_vatb' : fields.function( _amount_all,
                                            method=True,
                                            digits_compute=PRECISION_DP,
                                            string='Retencion en IVA',
                                            store=VAR_STORE,
                                            multi='all'),
        'amount_tax_ret_vatsrv' : fields.function( _amount_all,
                                                   method=True,
                                                   digits_compute=PRECISION_DP, string='Base Ret. IVA',
                                                   store=VAR_STORE,
                                                   multi='all'),
        'taxed_ret_vatsrv' : fields.function( _amount_all, method=True,
                                              digits_compute=PRECISION_DP,
                                              string='Retencion en IVA',
                                              store=VAR_STORE,
                                              multi='all'),        
        'amount_vat_cero' : fields.function( _amount_all, method=True,
                                             digits_compute=PRECISION_DP, string='Base IVA 0%',
                                             store=VAR_STORE,
                                             multi='all'),
        'amount_novat' : fields.function( _amount_all, method=True,
                                          digits_compute=PRECISION_DP, string='Base No IVA',
                                          store=VAR_STORE,
                                          multi='all'),
        'invoice_discount': fields.function(_amount_all, method=True,
                                            digits_compute=dp.get_precision('Account'),
                                            string='Desc (%)',
                                            store=VAR_STORE,
                                            multi='all'),
        'amount_discounted': fields.function(_amount_all,
                                             method=True,
                                             digits_compute=dp.get_precision('Account'),
                                             string='Descuento',
                                             store=VAR_STORE,
                                             multi='all'),
        'create_retention_type': fields.selection([('normal','Automatico'),
                                                   ('manual', 'Manual'),
                                                   ('reserve','Num Reservado'),
                                                   ('no_retention', 'No Generar')],
                                                  string='Numerar Retención',
                                                  readonly=True,
                                                  help=HELP_RET_TEXT,
                                                  states = {'draft': [('readonly', False)]}),        
        
        'auth_inv_id' : fields.many2one('account.authorisation', 'Autorización',
                                        help = 'Autorización del SRI para documento recibido',
                                        readonly=True,
                                        states={'draft': [('readonly', False)]}),
        'reference': fields.char('Invoice Reference', size=15,
                                 readonly=True,
                                 states={'draft':[('readonly',False)]},
                                 help="The partner reference of this invoice."),
        'reference_type': fields.selection(_get_reference_type, 'Reference Type',
                                           required=True, readonly=False),
        'retention_id': fields.many2one('account.retention', store=True,
                                        string='Retencion de Impuestos',
                                        readonly=True),
        'retention_ir': fields.function( _check_retention, store=True,
                                         string="Tiene Retencion en IR",
                                         method=True, type='boolean',
                                         multi='ret'),
        'retention_vat': fields.function( _check_retention, store=True,
                                          string='Tiene Retencion en IVA',
                                          method=True, type='boolean',
                                          multi='ret'),
        'no_retention_ir': fields.function( _check_retention, store=True,
                                          string='No objeto de Retencion',
                                          method=True, type='boolean',
                                          multi='ret'),        
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ('liq_purchase','Liquidacion de Compra')
            ],'Type', readonly=True, select=True, change_default=True),
        'retention_numbers': fields.selection(_get_num_retentions,
                                              readonly=True,
                                              string='Num. de Retención',
                                              help='Lista de Números de Retención reservados',
                                              states = {'draft': [('readonly', False)]}),
        'manual_ret_num': fields.integer('Num. Retencion', readonly=True,
                                         states = {'draft': [('readonly', False)]}),
        'num_to_use': fields.function( _get_num_to_use,
                                       string='Núm a Usar',
                                       method=True,
                                       type='char',
                                       help='Num. de documento a usar'),
        'new_number': fields.char('Nuevo Número', size=15, readonly=True, states = {'draft': [('readonly', False)]}),
        'sustento_id': fields.many2one('account.ats.sustento',
                                       'Sustento del Comprobante'),        
        'related_invoice_id' : fields.many2one('account.invoice','Factura Relacionada',readonly=True),
        'reposition' : fields.char('Reposicion Referencia',size=32,readonly=True,
                                   states={'draft': [('readonly', False)]}),
        'has_responsable': fields.boolean('Responsable?', help="El compromiso se emitio a un responsable."),
        'responsable_id': fields.many2one('res.partner', 'Responsable', help="Responsable de Caja Chica / Fondo Rotativo"),
        'aux_invoice': fields.boolean('Fact auxiliar solo para ret electronica'),
        'caja_fondo': fields.boolean('Fondo Rotativo/Caja Chica'),
        }

    def _get_period_invoice(self, cr, uid, ids,context=None):
        period_obj = self.pool.get('account.period')
        aux_date = time.strftime('%d-%m-%Y')
        period_ids = period_obj.find(cr, uid, aux_date)
        if period_ids:
            return period_ids[0]


    _defaults = {
        'type':'in_invoice',
        'create_retention_type': 'manual',
        'reference_type': _get_ref_type,
        'date_invoice': time.strftime('%Y-%m-%d'),
#        'period_id':_get_period_invoice,
        }

    # constraint stuff
    def check_in_reference(self, cr, uid, ids):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo que revisa la referencia a
        tener en cuenta en documentos que se recibe
        '''
        res = False
        for inv in self.browse(cr, uid, ids):
            if inv.partner_id.type_ced_ruc == 'pasaporte':
                return True
            elif inv.reference == '0' and inv.state == 'draft':
                return True
            elif inv.state == 'cancel':
                return True
            elif inv.create_retention_type == 'early' or inv.type in ['liq_purchase']:
                return True
            elif not inv.auth_inv_id:
                return True
            elif inv.auth_inv_id.is_electronic:
                return True
            elif inv.type in ['out_refund', 'in_refund']:
                return True
            elif inv.reference_type == 'multi_invoice':
                return True
            elif inv.aux_invoice==True:
                if len(inv.new_number)==15:
                    if inv.auth_inv_id.num_start <= int(inv.new_number[7:]) <= inv.auth_inv_id.num_end:
                        return True
                else:
                    raise osv.except_osv('Error', 'El numero de la factura proveedor debe ser 15 digitos.')
            elif inv.type == 'in_invoice' or (inv.type == 'out_invoice' and (inv.retention_vat or inv.retention_ir)):
                if inv.auth_inv_id.num_start <= int(inv.reference) <= inv.auth_inv_id.num_end:
                    res = True
            elif inv.type == 'out_invoice':
                res = True
            return res

    def check_retention_number(self, cr, uid, ids):
        """
        Metodo que verifica el numero de retencion
        asignada a la factura cuando es manual la numeracion.
        """
        res = False
        auth_obj = self.pool.get('account.authorisation')
        for obj in self.browse(cr, uid, ids):
            if obj.type == 'in_invoice' and (obj.retention_ir or obj.retention_vat):
#                if obj.create_retention_type == 'manual' and not auth_obj.is_valid_number(cr, uid, obj.journal_id.auth_ret_id.id, obj.manual_ret_num):
#                    raise osv.except_osv('Error', u'El número de retención no pertenece a la secuencia activa.')
                if obj.create_retention_type == 'manual':# and not auth_obj.is_valid_number(cr, uid, obj.journal_id.auth_ret_id.id, obj.manual_ret_num):
                    return True
        return True

    def check_invoice_number(self, cr, uid, ids):
        return True
        auth_obj = self.pool.get('account.authorisation')
        for obj in self.browse(cr, uid, ids):
            if obj.new_number:
                if obj.aux_invoice:
                    if len(obj.new_number) == 15 and obj.new_number.isdigit():
                        return True
                if obj.type != 'out_invoice':
                    return True
                if obj.new_number:
                    if len(obj.new_number) != 15 or not obj.new_number.isdigit():
                        return False
                    if auth_obj.is_valid_number(cr, uid, obj.journal_id.auth_id.id, int(obj.new_number[6:15])):
                        return True
            else:
                return True
        return False

    def _checkInvoiceDate(self, cr, uid, ids):
        return True
        #OJO mover al compute sino no corre el duplicar
        band = True
        year_obj = self.pool.get('account.fiscalyear')
        invoice_obj = self.pool.get('account.invoice')
        for obj in self.browse(cr, uid, ids):
            invoice_ids = invoice_obj.search(cr, uid, [('new_number','=',obj.new_number),('partner_id','=',obj.partner_id.id)])
            if len(invoice_ids)>1:
                raise osv.except_osv('Error de usuario', 'El numero de factura es unico por proveedor')
            if obj.auth_inv_id:
                if obj.auth_inv_id.emision_date:
                    if not (obj.date_invoice >= obj.auth_inv_id.emision_date and obj.date_invoice <= obj.auth_inv_id.expiration_date):
                        band=False
                        raise osv.except_osv('Error de usuario', 'Verifique la fecha de factura no esta dentro de las fechas de autorizacion')
            year_ids = year_obj.search(cr, uid, [('date_start','<=',obj.date_invoice),('date_stop','>=',obj.date_invoice)],limit=1)
            if year_ids:
                year = year_obj.browse(cr, uid, year_ids[0])
            else:
                raise osv.except_osv('Error de configuracion', 'No hay anio fiscal para la fecha de factura.')
            if obj.certificate_id:
                if not (obj.certificate_id.date_commited>=year.date_start and obj.certificate_id.date_commited<=year.date_stop):
                    band = False
        return band

    _constraints = [
        (_checkInvoiceDate,
         ustr('La fecha de factura no corresponde al periodo o la fecha del compromiso presupuestario.'),[ustr('Fecha'), 'Fecha']),
        (check_in_reference,
         ustr('El # de fact. no pertenece a la aut. seleccionada.'),
         [ustr('Factura Proveedor'), 'Aut.']),
         (check_invoice_number, ustr('Número de factura no pertenece a la autorización activa configurada en el diario'),
         ['Factura Cliente', 'Nro. Factura'])
        ]
    
    _sql_constraints = [
         ('number_uniq', 'unique(new_number, partner_id, type)', 'Invoice Number must be unique per Company!'),
         ('newnumber_uniq', 'unique(new_number, partner_id, type)', 'Invoice Number must be unique per Company!'),
#         ('unique_inv_supplier', 'unique(reference,type,partner_id)', u'El numero de factura es unico.'),
    ]

    def _refund_cleanup_lines(self, cr, uid, lines):
        """
        Redefinido metodo de limpiar lineas para campos M2O
        y considerar tambien budget_id
        """
        for line in lines:
            del line['id']
            del line['invoice_id']
            for field in ('company_id', 'partner_id', 'account_id', 'product_id',
                          'uos_id', 'account_analytic_id', 'tax_code_id', 'base_code_id', 'budget_id', 'categ_id'):
                if line.get(field):
                    line[field] = line[field][0]
            if 'invoice_line_tax_id' in line:
                line['invoice_line_tax_id'] = False#[(6,0, line.get('invoice_line_tax_id', [])) ]
        return map(lambda x: (0,0,x), lines)    

    def refund(self, cr, uid, ids, date=None, period_id=None, description=None, journal_id=None):
        """
        Redefinido metodo para actualizar el campo reference utilizado para numero de referencia
        numero de factura reembolsada, guia de remision.
        """
        invoices = self.read(cr, uid, ids, ['name', 'type', 'number', 'reference', 'comment', 'date_due', 'partner_id', 'address_contact_id', 'address_invoice_id', 'partner_contact', 'partner_insite', 'partner_ref', 'payment_term', 'account_id', 'currency_id', 'invoice_line', 'tax_line', 'journal_id', 'user_id', 'fiscal_position'])
        obj_invoice_line = self.pool.get('account.invoice.line')
        obj_invoice_tax = self.pool.get('account.invoice.tax')
        obj_journal = self.pool.get('account.journal')
        new_ids = []
        for invoice in invoices:
            del invoice['id']

            type_dict = {
                'out_invoice': 'out_refund', # Customer Invoice
                'in_invoice': 'in_refund',   # Supplier Invoice
                'out_refund': 'out_invoice', # Customer Refund
                'in_refund': 'in_invoice',   # Supplier Refund
            }

            invoice_lines = obj_invoice_line.read(cr, uid, invoice['invoice_line'])
            invoice_lines = self._refund_cleanup_lines(cr, uid, invoice_lines)

            tax_lines = obj_invoice_tax.read(cr, uid, invoice['tax_line'])
            tax_lines = filter(lambda l: l['manual'], tax_lines)
            tax_lines = self._refund_cleanup_lines(cr, uid, tax_lines)
            if journal_id:
                refund_journal_ids = [journal_id]
            elif invoice['type'] == 'in_invoice':
                refund_journal_ids = obj_journal.search(cr, uid, [('type','=','purchase_refund')])
            else:
                refund_journal_ids = obj_journal.search(cr, uid, [('type','=','sale_refund')])

            if not date:
                date = time.strftime('%Y-%m-%d')
            invoice.update({
                'type': type_dict[invoice['type']],
                'date_invoice': date,
                'state': 'draft',
                'number': False,
                'invoice_line': invoice_lines,
                'tax_line': tax_lines,
                'journal_id': refund_journal_ids,
                'reference_type': type_dict[invoice['type']],
                'reference': invoice['number'][8:],
            })
            if period_id:
                invoice.update({
                    'period_id': period_id,
                })
            if description:
                invoice.update({
                    'name': description,
                })
            # take the id part of the tuple returned for many2one fields
            for field in ('address_contact_id', 'address_invoice_id', 'partner_id',
                    'account_id', 'currency_id', 'payment_term', 'journal_id',
                    'user_id', 'fiscal_position'):
                invoice[field] = invoice[field] and invoice[field][0]
            # create the new invoice
            new_ids.append(self.create(cr, uid, invoice))

        return new_ids

    def copy_data(self, cr, uid, id, default=None, context=None):
        res = super(Invoice, self).copy_data(cr, uid, id, default, context=context)
        res.update({'reference': '0',
                    'auth_inv_id': False,
                    'retention_id': False,
                    'retention_numbers': False,
                    'manual_ret_num': '',
                    'number': '',
                    'invoice_number': ''})
        return res

    def onchange_certificate_id(self, cr, uid, ids, certificate_id):
        cert_obj = self.pool.get('budget.certificate')
        line_obj = self.pool.get('budget.certificate.line')
        account_obj = self.pool.get('account.account')
        post_obj = self.pool.get('budget.post')
        certificado = cert_obj.browse(cr, uid, certificate_id)
        lines = line_obj.search(cr, uid, [('certificate_id','=',certificate_id)],order='amount_commited desc')
        cxp = '0'
        if lines:
            line = line_obj.browse(cr, uid, lines[0])
            #aqui considerar solo los 6 del codigo
            post_ids = post_obj.search(cr, uid, [('code','=',line.budget_post.code[0:6])],limit=1)
            #budget_post = line.budget_post.id
            account_ids = account_obj.search(cr, uid, [('budget_id','=',line.budget_post.id),('type','!=','view')])
            if not account_ids:
                account_ids = account_obj.search(cr, uid, [('budget_id','=',post_ids[0]),('type','!=','view')])
            if account_ids:
                for account_id in account_ids:
                    account = account_obj.browse(cr, uid, account_id)
                    if account.account_pay_id:
                        cxp = account.account_pay_id.id
                        return {'value':{'account_id': cxp}}
                    else:
                        if account.account_rec_id:
                            cxp = account.account_rec_id.id
                            return {'value':{'account_id': cxp}}
                if cxp=='0':
                    raise osv.except_osv(('Error de Configuracion !'),
                                         ("No existe configuracion contable para la partida '%s'") % (line.budget_post.code))
            else:
                #verificar este proceso
                budget_post = line.budget_post.parent_id.id
                account_ids = account_obj.search(cr, uid, [('budget_id','=',budget_post),('type','!=','view')],limit=1)
                if account_ids:
                    account = account_obj.browse(cr, uid, account_ids[0])
                    if account.account_pay_id:
                        cxp = account.account_pay_id.id
                    else:
                        if account.account_rec_id:
                            cxp = account.account_rec_id.id
                        else:
                            raise osv.except_osv(('Error de Configuracion !'),
                                                 ("No existe configuracion contable para la partida '%s'") % (line.budget_post.code))
                else:
                    raise osv.except_osv(('Error de Configuracion !'),
                                         ("No existe configuracion contable para la partida '%s'") % (line.budget_post.code))
        return {'value':{'account_id': cxp}}

    def onchange_partner_aux_id(self, cr, uid, ids, partner_id, date_invoice):
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        period_obj = self.pool.get('account.period')
        account_obj = self.pool.get('account.account')
        period_id = period_obj.find(cr, uid, date_invoice)
        account_ids = account_obj.search(cr, uid, [('type','=','payable')],limit=1)
        if partner.property_account_payable:
            res = {'value': {'period_id':period_id, 'account_id': partner.property_account_payable.id, 'type':'in_invoice', 'aux_invoice':True, 'create_retention_type':'manual'}}
        else:
            res = {'value': {'period_id':period_id, 'account_id': account_ids[0], 'type':'in_invoice', 'aux_invoice':True, 'create_retention_type':'manual'}}
        return res

    def onchange_supplier_number(self, cr, uid, ids, sn):
        res = {'value': {'new_number': sn}}
        return res
    
    def onchange_partner_id3(self, cr, uid, ids, type, partner_id,\
                        date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        invoice_addr_id = False
        contact_addr_id = False
        partner_payment_term = False
        acc_id = False
        bank_id = False
        fiscal_position = False

        opt = [('uid', str(uid))]
        if partner_id:
            opt.insert(0, ('id', partner_id))
            res = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact', 'invoice'])
            contact_addr_id = res['contact']
            invoice_addr_id = res['invoice']
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if company_id:
                if p.property_account_receivable.company_id.id != company_id and p.property_account_payable.company_id.id != company_id:
                    property_obj = self.pool.get('ir.property')
                    rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = property_obj.read(cr,uid,rec_pro_id,['name','value_reference','res_id'])
                    pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
                    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not rec_res_id and not pay_res_id:
                        raise osv.except_osv(_('Configuration Error !'),
                            _('Can not find a chart of accounts for this company, you should create one.'))
                    account_obj = self.pool.get('account.account')
                    rec_obj_acc = account_obj.browse(cr, uid, [rec_res_id])
                    pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
                    p.property_account_receivable = rec_obj_acc[0]
                    p.property_account_payable = pay_obj_acc[0]

            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
            else:
                acc_id = p.property_account_payable.id
            fiscal_position = p.property_account_position and p.property_account_position.id or False
            partner_payment_term = p.property_payment_term and p.property_payment_term.id or False
            if p.bank_ids:
                bank_id = p.bank_ids[0].id

        result = {'value': {
            'address_contact_id': contact_addr_id,
            'address_invoice_id': invoice_addr_id,
            #'account_id': acc_id,
            'payment_term': partner_payment_term,
            'fiscal_position': fiscal_position
            }
        }

        if type in ('in_invoice', 'in_refund'):
            result['value']['partner_bank_id'] = bank_id

        if payment_term != partner_payment_term:
            if partner_payment_term:
                to_update = self.onchange_payment_term_date_invoice(
                    cr, uid, ids, partner_payment_term, date_invoice)
                result['value'].update(to_update['value'])
            else:
                result['value']['date_due'] = False

        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(cr, uid, ids, bank_id)
            result['value'].update(to_update['value'])
        return result

    def onchange_partner_id(self, cr, uid, ids, type_doc, partner_id, \
                            date_invoice=False, payment_term=False, \
                            partner_bank_id=False, company_id=False):
        auth_obj = self.pool.get('account.authorisation')
        partner_obj = self.pool.get('res.partner')
        res1 = {'value': {
            }
        }
        if res1['value'].has_key('reference_type'):
            res1['value'].pop('reference_type')
        res = auth_obj.search(cr, uid, [('partner_id','=',partner_id),('in_type','=','externo')], limit=1)
        if res:
            res1['value']['auth_inv_id'] = res[0]
        res1['value']['certificate_id']=''
        partner = partner_obj.browse(cr, uid, partner_id)
        res1['value']['fiscal_position']=partner.property_account_position.id
        return res1

    #workflow stuff

    def action_cancel_draft(self, cr, uid, ids, context=None):
        retention_obj = self.pool.get('account.retention')
        for inv in self.browse(cr, uid, ids, context):
            if inv.retention_id:
                if inv.retention_id.digital_id:
                    if inv.retention_id.digital_id.state=='noautorizado':
                        retention_obj.unlink(cr, uid, [inv.retention_id.id], context)
        super(Invoice, self).action_cancel_draft(cr, uid, ids, context)
        return True    

    def action_retention_create(self, cr, uid, ids, *args):
        return True
        '''
        @cr: DB cursor
        @uid: active ID user
        @ids: active IDs objects

        Este metodo genera el documento de retencion en varios escenarios
        considera casos de:
        * Generar retencion automaticamente
        * Generar retencion de reemplazo
        * Cancelar retencion generada
        '''
        context = args and args[0] or {}
        invoices = self.browse(cr, uid, ids)
        ret_obj = self.pool.get('account.retention')
        invtax_obj = self.pool.get('account.invoice.tax')
        ret_cache_obj = self.pool.get('account.retention.cache')
        ir_seq_obj = self.pool.get('ir.sequence')
        for inv in invoices:
            if inv.type=='out_invoice':
                return True
            if inv.partner_id.type_ced_ruc!='ruc' or len(inv.partner_id.ced_ruc)<13:
                raise osv.except_osv('Error de usuario', 'Solo se puede registrar facturas con RUC, verifique la informacion del proveedor')
            if inv.retention_id and inv.retention_id.digital_id and inv.retention_id.digital_id.state=="autorizado":
                continue
            num_ret = False
            if inv.create_retention_type == 'no_retention':
                continue
            if inv.retention_id and not inv.retention_vat and not inv.retention_ir:
                num_next = inv.journal_id.auth_ret_id.sequence_id.number_next
                seq = inv.journal_id.auth_ret_id.sequence_id
                if num_next - 1 == int(inv.retention_id.name):
                    ir_seq_obj.write(cr, uid, seq.id, {'number_next': num_next-1})
                else:
                    ret_cache_obj.create(cr, uid, {'name': inv.retention_id.name})
            if inv.type in ['in_invoice', 'liq_purchase'] and (inv.retention_ir or inv.retention_vat):
                if inv.journal_id.auth_ret_id.sequence_id:
                    #verificar si hay retenciones sino True
                    k = 0
                    for tax_line in inv.tax_line:
                        if tax_line.tax_group in ('ret_vat_b','ret_vat_srv','ret_ir'):
                            k+=1
#                            if tax_line.amount!=0:
#                                k+=1
                    if k==0:
                        return True
                    if inv.aux_invoice:
                        num_document = inv.new_number
                    else:
                        num_document = '%s%s%09d' % (inv.auth_inv_id.serie_entidad, inv.auth_inv_id.serie_emision, int(inv.reference))
                    if inv.retention_id:
                        if inv.retention_id.state == "cancel":
                            ret_obj.unlink(cr, 1, [inv.retention_id.id])
                            ret_data = {'name':'/',
                                        'number': '/',
                                        'invoice_id': inv.id,
                                        'num_document': num_document,
                                        'auth_id': inv.journal_id.auth_ret_id.id,
                                        'address_id': inv.address_invoice_id.id,
                                        'type': inv.type,
                                        'in_type': 'ret_in_invoice',
                                        'date': inv.date_invoice,
#                                        'date': time.strftime('%Y-%m-%d'),
                                    }
                            ret_id = ret_obj.create(cr, uid, ret_data)
                        else:
                            ret_id = inv.retention_id.id
                    else:
                        ret_data = {'name':'/',
                                    'number': '/',
                                    'invoice_id': inv.id,
                                    'num_document': num_document,
                                    'auth_id': inv.journal_id.auth_ret_id.id,
                                    'address_id': inv.address_invoice_id.id,
                                    'type': inv.type,
                                    'in_type': 'ret_in_invoice',
#                                    'date': time.strftime('%Y-%m-%d'),
                                    'date': inv.date_invoice,
                                }
                        ret_id = ret_obj.create(cr, uid, ret_data)
                    for line in inv.tax_line:
                        if line.tax_group in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']:
                            num = inv.supplier_number
                            invtax_obj.write(cr, uid, line.id, {'retention_id': ret_id})
                    if num_ret:
                        ret_obj.action_validate(cr, uid, [ret_id], num_ret)
                    elif inv.create_retention_type == 'normal':
                        ret_obj.action_validate(cr, uid, [ret_id])
                    elif inv.create_retention_type == 'manual':
                        if inv.manual_ret_num != 0:
                            ret_obj.action_validate(cr, uid, [ret_id], inv.manual_ret_num)
                        else:
                            ret_obj.action_validate(cr, uid, [ret_id])
                    elif inv.create_retention_type == 'reserve':
                        if inv.retention_numbers:
                            ret_num = ret_cache_obj.get_number(cr, uid, inv.retention_numbers)
                            ret_obj.action_validate(cr, uid, [ret_id], ret_num)
                        else:
                            raise osv.except_osv('Error', 'Corrija el método de numeración de la retención')
                    if inv.reference:
                        ref_aux = inv.reference
                    else:
                        ref_aux = inv.new_number[6:]
                    self.write(cr, uid, [inv.id], {'retention_id': ret_id,'reference':ref_aux, 'fiscal_position':inv.partner_id.property_account_position.id})
                else:
                    raise osv.except_osv('Error de Configuracion',
                                         'No se ha configurado una secuencia para las retenciones en Compra')
        self._log_event(cr, uid, ids)
        return True

    def recreate_retention(self, cr, uid, ids, context=None):
        '''
        Metodo que implementa la recreacion de la retención
        TODO: recibir el numero de retención del campo manual
        '''
        if context is None:
            context = {}
        context.update({'recreate_retention': True})
        for inv in self.browse(cr, uid, ids, context):
            self.action_retention_cancel(cr, uid, [inv.id], context)
            self.action_retention_create(cr, uid, [inv.id], context)
        return True

    def action_retention_cancel(self, cr, uid, ids, *args):
        invoices = self.browse(cr, uid, ids)
        ret_obj = self.pool.get('account.retention')
        for inv in invoices:
            if inv.retention_id:
                ret_obj.action_cancel(cr, uid, [inv.retention_id.id])
        return True

Invoice()


class AccountInvoiceLine(osv.osv):
    _inherit = 'account.invoice.line'
    
    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(AccountInvoiceLine, self).move_line_get_item(cr, uid, line, context)
        if line.budget_id:
            res.update({'budget_id_cert': line.budget_id.id, 'budget_accrued': True})
        return res


    def onchange_name_aux(self, cr, uid, ids, name):
        res = {}
        account_obj = self.pool.get('account.account')
        cuentas = account_obj.search(cr, uid, [])
        res['value'] = {'account_id': cuentas[0]}
        return res


    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        """
        Redefinicion de metodo para almacenar el total incluido iva
        en casos cuando el tipo de impuestos es de tipo IVA,IVA 0, NO Obj IVA
        """
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            cur = line.invoice_id.currency_id
            res[line.id] = {'price_subtotal': 0,
                            'price_total': 0,
                            'base_doce': 0,
                            'base_cero': 0,
                            'base_noiva': 0,
                            'monto_iva': 0,
                            'monto_retbienes': 0,
                            'monto_retserv': 0,
                            'monto_retir': 0,
                            'has_retention': False}
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
            res[line.id]['price_subtotal'] = taxes['total']
            for tax in taxes['taxes']:
                if tax['tax_group'] in ['vat', 'vat0', 'novat']:
                    res[line.id]['price_total'] += taxes['total'] + tax['amount']
                if tax['tax_group'] == 'vat':
                    res[line.id]['base_doce'] += taxes['total']
                    res[line.id]['monto_iva'] += tax['amount']
                elif tax['tax_group'] == 'novat':
                    res[line.id]['base_noiva'] += tax['price_unit']
                elif tax['tax_group'] == 'vat0':
                    res[line.id]['base_cero'] += tax['price_unit']
                elif tax['tax_group'] == 'ret_vat_b':
                    res[line.id]['has_retention'] = True
                    res[line.id]['monto_retbienes'] += tax['amount']
                elif tax['tax_group'] == 'ret_vat_srv':
                    res[line.id]['monto_retserv'] += tax['amount']
                    res[line.id]['has_retention'] = True
                elif tax['tax_group'] == 'ret_ir':
                    res[line.id]['monto_retir'] += tax['amount']
                
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id]['price_subtotal'] = cur_obj.round(cr, uid, cur, res[line.id]['price_subtotal'])
                res[line.id]['price_total'] = cur_obj.round(cr, uid, cur, res[line.id]['price_subtotal'])
                res[line.id]['monto_iva'] = cur_obj.round(cr, uid, cur, res[line.id]['monto_iva'])
                res[line.id]['base_doce'] = cur_obj.round(cr, uid, cur, res[line.id]['base_doce'])
        return res

    def move_line_get_1(self, cr, uid, invoice_id, context=None):
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        company_currency = inv.company_id.currency_id.id

        for line in inv.invoice_line:
            mres = self.move_line_get_item(cr, uid, line, context)
            if not mres:
                continue
            res.append(mres)
            tax_code_found= False
            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id,
                    (line.price_unit * (1.0 - (line['discount'] or 0.0) / 100.0)),
                    line.quantity, inv.address_invoice_id.id, line.product_id,
                    inv.partner_id)['taxes']:
                #if type=='tax' and tax_code_id es de SRI: OJOOOOOOOOOOOOOOOOOOOOOOOOO
                if inv.type in ('out_invoice', 'in_invoice', 'liq_purchase'):
                    tax_code_id = tax['base_code_id']
                    tax_amount = line.price_subtotal * tax['base_sign']
                else:
                    tax_code_id = tax['ref_base_code_id']
                    tax_amount = line.price_subtotal * tax['ref_base_sign']

                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(self.move_line_get_item(cr, uid, line, context))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True

                res[-1]['tax_code_id'] = tax_code_id
                #res[-1]['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, tax_amount, context={'date': inv.date_invoice})
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(AccountInvoiceLine, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)        
        doc = etree.XML(res['arch'])
        if context.get('type') == 'in_invoice':
            #lo que esta adentrito quite lo ultimo
         #   if not context.get('certificate_id'):
         #       raise osv.except_osv('Error', 'No ha seleccionado un compromiso presupuestario.')
         #   for node in doc.xpath("//field[@name='account_id']"):
         #       cert = self.pool.get('budget.certificate').browse(cr, uid, context.get('certificate_id'))
         #       accounts = []
         #       node.set('domain',"[('company_id', '=', parent.company_id),('type', '!=', 'view')]")
#                for l in cert.line_ids:
#                    accounts += [acc.id for acc in l.budget_line_id.general_budget_id.account_ids]
#                node.set('domain',"[('company_id', '=', parent.company_id),('type', '!=', 'view'),('id','in',%s)]" % accounts)
            for node in doc.xpath("//field[@name='product_id']"):                              
                node.set('domain',"[('categ_id', '=', categ_id)]")
        if context.get('type') == 'out_invoice':
            for node in doc.xpath("//field[@name='categ_id']"):
                doc.remove(node)
            for node in doc.xpath("//field[@name='product_id']"):
                node.set('on_change','product_id_change(product_id, uos_id, quantity, name, parent.type, parent.partner_id, parent.fiscal_position, price_unit, parent.address_invoice_id, parent.currency_id, context, parent.company_id)')
            for node in doc.xpath("//field[@name='account_id']"):
                node.set('on_change','onchange_account_id(product_id, parent.partner_id, parent.type, parent.fiscal_position,account_id,parent.certificate_id)')                  
                node.set('domain',"[('company_id', '=', parent.company_id), ('journal_id', '=', parent.journal_id), ('type', '!=', 'view'),('user_type.code','=','income')]")                
        if context.get('reference_type') != 'multi_invoice' or context.get('type')=='out_invoice':
            if view_type == 'form':
                for node in doc.xpath("//field[@name='invoice_number']"):
                    doc.remove(node)
                for node in doc.xpath("//field[@name='auth_id']"):
                    doc.remove(node)
                for node in doc.xpath("//field[@name='date_invoice']"):
                    doc.remove(node)
                for node in doc.xpath("//field[@name='sustento_id']"):
                    doc.remove(node)
        res['arch'] = etree.tostring(doc)
        return res

    def _get_supplier_number(self, cr, uid, ids, fields, args, context):
        res = {}
        for inv in self.browse(cr, uid, ids, context):
            number = '/'
            if inv.invoice_id.reference_type == 'multi_invoice':
                n = inv.invoice_number.zfill(9)
                number = ''.join([inv.auth_id.serie_entidad,inv.auth_id.serie_emision,n])
            res[inv.id] = number
        return res    

    _columns = {
        'cxp_id':fields.many2one('account.account','Cuenta por pagar'),
        'auth_id': fields.many2one('account.authorisation', 'Autorización'),
        'date_invoice': fields.date('Fecha de Factura'),
        'invoice_number': fields.char('Nro. Factura', size=9),
        'invoice_number_complete': fields.function(_get_supplier_number, method=True, string='Factura Proveedor'),
        'account_number': fields.char('Cuenta', size=32),
        'categ_id': fields.many2one('product.category', 'Línea de Bien / Servicio'),
        'sustento_id': fields.many2one('account.ats.sustento', 'Sustento'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', type="float",
                                          digits_compute= dp.get_precision('Account'), store=True, multi='line'),
        'base_doce': fields.function(_amount_line, string='Base Imponible', type="float",
                                    digits_compute= dp.get_precision('Account'), store=True, multi='line'),
        'base_cero': fields.function(_amount_line, string='Base Iva 0%', type="float",
                                    digits_compute= dp.get_precision('Account'), store=True, multi='line'),
        'base_noiva': fields.function(_amount_line, string='Base No Iva', type="float",
                                    digits_compute= dp.get_precision('Account'), store=True, multi='line'),
        'monto_iva': fields.function(_amount_line, string='IVA', type="float",
                                    digits_compute= dp.get_precision('Account'), store=True, multi='line'),
        'monto_retbienes': fields.function(_amount_line, string='Ret. Bienes', type="float",
                                            digits_compute= dp.get_precision('Account'), store=True, multi='line'),
        'monto_retserv': fields.function(_amount_line, string='Ret. Servicios', type="float",
                                            digits_compute= dp.get_precision('Account'), store=True, multi='line'),
        'monto_retir': fields.function(_amount_line, string='Ret. IR', type="float",
                                            digits_compute= dp.get_precision('Account'), store=True, multi='line'),               
        'has_retention': fields.function(_amount_line, string='A Pagar', type="boolean", store=True, multi='line'),
        'price_total': fields.function(_amount_line, string='Total',
                                       digits_compute=dp.get_precision('Account'), store=True, multi='line'),
        'type_desc': fields.selection([('none','Ninguno'),
                                       ('base0','Base 0'),
                                       ('base12','Base 12')], string='Tipo'),
#        'budget_id': fields.many2one('budget.post', 'Aplicación Presupuestaria'),
        'budget_id': fields.many2one('budget.certificate.line', 'Aplicación Presupuestaria'),
        'cambiar_partida' :fields.boolean('Cambiar/Seleccionar partida manual'),
        'obra_programa': fields.selection([('obra', 'OBRA'),
                                           ('programa', 'PROGRAMA'),
                                           ('corriente', 'CORRIENTE')], string='Obra / Programa'),
        'project_code': fields.many2one('account.analytic.account', 
                                        string='Centro de Costos', domain=[('usage','in',['project','cost'])]),
        'seq' : fields.integer('Secuencia'),
    }


    _defaults = {
        'type_desc': 'none',
        'obra_programa': 'corriente',
        
        }
    
    def onchange_account_id(self, cr, uid, ids, product_id, partner_id, inv_type, fposition_id, account_id,certificate_id):
        id=[]   
        if not account_id:
            return {}
        budget_obj = self.pool.get('budget.certificate.line')
        certificate_obj = self.pool.get('budget.certificate')
        post_obj = self.pool.get('account.budget.post')
        account_obj = self.pool.get('account.account')
        account = account_obj.browse(cr, uid, account_id)
        res = post_obj.search(cr, uid, [('account_ids','in',[account_id])])
        #'budget_line_id.general_budget_id.account_ids','in',[account_id])
        if not res:
            return {}        
        # leer detalle de certificate_id y ver cual tiene el post de la cta
        certificate = certificate_obj.browse(cr, uid, certificate_id)
        for lines_cert in certificate.line_ids:
            for accounts in lines_cert.budget_line_id.general_budget_id.account_ids:
                if accounts.id==account_id:
                    id=[lines_cert.id]
                    break
        #line_ids = [line.id for line in certificate.line_ids]
        partida = budget_obj.search(cr, uid, [('certificate_id','=',certificate.id),('id','in',id)])
        if partida:
            budget_id_id=budget_obj.browse(cr,uid,partida[0]).id
        else:
            budget_id_id=[]  
        return {'value':{'budget_id': budget_id_id}}    

    def onchange_bud_id(self, cr, uid, ids, budget_id):
        account_obj = self.pool.get('account.account')
        cert_line_obj = self.pool.get('budget.certificate.line')
        post_obj = self.pool.get('budget.post')
        invoice_obj = self.pool.get('account.invoice')
        partner_account_obj = self.pool.get('partner.account')
        cert_line = cert_line_obj.browse(cr, uid, budget_id)
        budget_post = cert_line.budget_post.id
        budget_aux = cert_line.budget_post.name
        account_ids1 = account_obj.search(cr, uid, [('budget_id','=',budget_post),('type','!=','view')])
        #busca por el codigo de la partida de mayor
        aux_code = cert_line.budget_post.code[0:6]
        post_ids = post_obj.search(cr, uid, [('code','=',aux_code)],limit=1)
        account_ids2 = []
        if post_ids:
            account_ids2 = account_obj.search(cr, uid, [('budget_id','=',post_ids[0]),('type','!=','view')])
        account_ids = account_ids1 + account_ids2
        for this in self.browse(cr, uid, ids):
            parent_account_ids = partner_account_obj.search(cr, uid, [('name','=',aux_code[0:2]),('p_id','=',this.invoice_id.partner_id.id)])
            if parent_account_ids:
                p_account = partner_account_obj.browse(cr, uid, parent_account_ids[0])
                if not account_ids:
                    raise osv.except_osv(('Error de Configuracion !'),
                                         ("No existe configuracion contable patrimonial para la partida '%s'") % (aux_code))
                return {'value':{'account_id': account_ids[0],'cxp_id':p_account.account_id.id}}
            if account_ids:
                for account_id in account_ids:
                    account = account_obj.browse(cr, uid, account_id)
                    if account.account_pay_id:
                        cxp = account.id
                        #invoice_obj.write(cr, uid, this.id,{'account_id':account.account_pay_id.id})
                        return {'value':{'account_id': cxp,'cxp_id':account.account_pay_id.id}}
                    else:
                        if account.account_rec_id:
                            cxp = account.id
                            #invoice_obj.write(cr, uid, this.id,{'account_id':account.account_rec_id.id})
                            return {'value':{'account_id': cxp,'cxp_id':account.account_rec_id.id}}
            else:
                raise osv.except_osv(('Error de Configuracion !'),
                                     ("No existe configuracion contable para la partida '%s'") % (budget_aux))
        return {'value':{'account_id': account_ids[0]}}

    def onchange_account_id_categ(self, cr, uid, ids, product_id, partner_id, inv_type, fposition_id, account_id, categ_id, obra_programa, certificate_id):
        id=[]
        if not account_id:
            return {}
        budget_obj = self.pool.get('budget.certificate.line')
        certificate_obj = self.pool.get('budget.certificate')
        account_obj = self.pool.get('account.account')
        account = account_obj.browse(cr, uid, account_id)
        #line_ids = [line.id for line in certificate.line_ids]
        unique_tax_ids = []
        fpos = fposition_id and self.pool.get('account.fiscal.position').browse(cr, uid, fposition_id) or False
        account = self.pool.get('account.account').browse(cr, uid, account_id)
        if not product_id:
            #que no quite los taxes
            print "no p"
            #taxes = account.tax_ids
            #unique_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)
        else:
            # force user choosen account in context to allow product_id_change()
            # to fallback to the this accounts in case product has no taxes defined.
            context = {'account_id': account_id}
            product_change_result = self.product_id_change_categ(cr, uid, ids, product_id, categ_id, obra_programa, False, type=inv_type,
                partner_id=partner_id, fposition_id=fposition_id, context=context,
                company_id=account.company_id.id)
            if product_change_result and 'value' in product_change_result and 'invoice_line_tax_id' in product_change_result['value']:
                unique_tax_ids = product_change_result['value']['invoice_line_tax_id']
        return {'value':{}}
#        return {'value':{'invoice_line_tax_id': unique_tax_ids}}
#                         'budget_id': ''}}    

    def product_id_change_categ(self, cr, uid, ids, product, categ_id, obra_programa, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, invoice_address_id=False, currency_id=False, context=None, company_id=None):
        if context is None:
            context = {}
        categ_obj = self.pool.get('product.category')
        product_obj = self.pool.get('product.product')
        company_id = company_id if company_id != None else context.get('company_id',False)
        context = dict(context)
        context.update({'company_id': company_id})
        if not partner_id:
            raise osv.except_osv(_('No Partner Defined !'),_("You must first select a partner !") )
        if not categ_id:
            result = {'warning': {'title':'No seleccionó una categoría', 'message': 'Debe selecionar primero la línea de producto.'},
                      'value': {'product_id': False}}
            return result
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {}, 'domain':{'product_uom':[]}}
            else:
                return {'value': {'price_unit': 0.0}, 'domain':{'product_uom':[]}}
        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        fpos_obj = self.pool.get('account.fiscal.position')
        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False

        if part.lang:
            context.update({'lang': part.lang})
        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=context)
#        categ = res.categ_id
        #CAMBIO PARA CTA CONTABLE DE CATEG DE PRODUCTO
        #TODO: REVISAR SI LOS ITEMS DE INVENTARIO SON POR BODEGA
        #Revisar la tabla de cuentas para eleccion de cta contable ctas.categ
        ctas_categ_obj = self.pool.get('ctas.categ')
        categ = categ_obj.browse(cr, uid, categ_id, context=context)
        if type in ('out_invoice','out_refund'):
            a = categ.property_account_income_categ.id#res.product_tmpl_id.property_account_income.id
            if not a:
                a = res.categ_id.property_account_income_categ.id
        else:
            ##agregado para q si es servicio tome directo la cta de la categoria
            if res.type in ['service', 'asset']: #muestre todas loco
                if res.product_tmpl_id.property_account_expense.id:
                    a = res.product_tmpl_id.property_account_expense.id
                else:
                    a = res.categ_id.property_account_expense_categ.id
            ##
            else: ##de aqui hacia abajo estaba a la izquierda
#                a = ctas_categ_obj.get_by_category(cr, uid, categ_id, categ.budget, obra_programa)
#                if not a:
                a = res.product_tmpl_id.property_account_expense.id #res.categ_id.property_account_expense_categ.id

#        if context.get('account_id',False):
            # this is set by onchange_account_id() to force the account choosen by the
            # user - to get defaults taxes when product have no tax defined.
#            a = context['account_id']

#        a = fpos_obj.map_account(cr, uid, fpos, a)
        if a:
            result['account_id'] = a        
            result['account_number'] = a
        if type in ('out_invoice', 'out_refund'):
            taxes = res.taxes_id and res.taxes_id or categ.taxes_id and categ.taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        else:
            taxes = res.supplier_taxes_id and res.supplier_taxes_id or categ.supplier_taxes_id and categ.supplier_taxes_id \
                    or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        context.update({'budget_type': categ.budget, 'aplic_id': categ.presp_aplic_id.id})
        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes, context)
        if type in ('in_invoice', 'in_refund'):
            result.update( {'price_unit': price_unit or res.standard_price,'invoice_line_tax_id': tax_id} )
        else:
            result.update({'price_unit': res.list_price, 'invoice_line_tax_id': tax_id})
        result['name'] = res.partner_ref

        domain = {}
        result['uos_id'] = res.uom_id.id or uom or False
        result['note'] = res.description
        if result['uos_id']:
            res2 = res.uom_id.category_id.id
            if res2:
                domain = {'uos_id':[('category_id','=',res2 )]}

        res_final = {'value':result, 'domain':domain}

        if not company_id or not currency_id:
            return res_final

        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)

        if company.currency_id.id != currency.id:
            if type in ('in_invoice', 'in_refund'):
                res_final['value']['price_unit'] = res.standard_price
            new_price = res_final['value']['price_unit'] * currency.rate
            res_final['value']['price_unit'] = new_price

        if uom:
            uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
            if res.uom_id.category_id.id == uom.category_id.id:
                new_price = res_final['value']['price_unit'] * uom.factor_inv
                res_final['value']['price_unit'] = new_price
        return res_final

    def onchange_category(self, cr, uid, ids, categ_id, certificate_id):
        if not categ_id:
            return {}
        res = self.pool.get('product.category').read(cr, uid, categ_id, ['budget'])
        if res['budget'] == 'corriente':
            return {'value': {'obra_programa': 'corriente'} }
        elif res['budget'] in ['ogastos', 'opublica']:
            return {'value': {'obra_programa': 'obra'}}
        else:
            return {'value': {'obra_programa': 'programa'}}

    def onchange_op(self, cr, uid, ids, categ_id, obra_programa):
        if not categ_id:
            return {}
        res = self.pool.get('product.category').read(cr, uid, categ_id, ['budget'])
        if res['budget'] == 'corriente' and obra_programa=='corriente':
            return {'value': {'obra_programa': obra_programa} }
        elif res['budget'] in ['ogastos', 'opublica', 'inversion', 'ginversion'] and obra_programa in ['obra','programa']:
            return {'value': {'obra_programa': obra_programa}}
        else:
            return {'value': {'obra_programa': False}, 'warning': {'title': 'Aviso', 'message': 'No corresponde al tipo de categoria.'}}

AccountInvoiceLine()


class AccountInvoiceRefund(osv.TransientModel):

    _inherit = 'account.invoice.refund'

    def _get_description(self, cr, uid, context=None):
        number = '/'
        if not context.get('active_id'):
            return number
        invoice = self.pool.get('account.invoice').browse(cr, uid, context.get('active_id'))
        if invoice.type == 'out_invoice':
            number = invoice.number
        else:
            number = invoice.reference
        return number

    _defaults = {
        'description': _get_description,
        }
            
class accountMove(osv.Model):
    _inherit = 'account.move'
    _order = 'date desc, numero desc,name desc'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            if record.narration:
                name = record.name + " - " + record.narration
            else:
                name = record.name
            res.append((record.id, name))
        return res    

    def write2(self, cr, uid, ids, vals, context=None):
        move_obj = self.pool.get('stock.move')
        period_obj = self.pool.get('account.period')
        for this in self.browse(cr, uid, ids):
            if this.period_id.state=='done':
                raise osv.except_osv('Error de usuario','No se puede modificar comprobantes de meses cerrados.')
        return super(accountMove, self).write(cr, uid, ids, vals, context)    

#    def create(self, cr, uid, vals, context):
#        if vals.has_key('partner_id'):
#            if 'line_id' in vals:
#                c = context.copy()
#                c['novalidate'] = True
#                result = super(account_move, self).create(cr, uid, vals, c)
#                self.validate(cr, uid, [result], context)
#            else:
#                result = super(account_move, self).create(cr, uid, vals, context)
#            return result

    def crear_padre(self, data, data_suma, res):
        if data['post'].parent_id:
            data['padre'] = data['post'].parent_id
            if res.get(data['post'].parent_id.code,False):
                res[data['post'].parent_id.code]['planned_amount'] += data_suma['planned_amount']
                res[data['post'].parent_id.code]['devengado_amount'] += data_suma['devengado_amount']
                res[data['post'].parent_id.code]['devengado_balance'] += data_suma['devengado_balance']
                res[data['post'].parent_id.code]['paid_amount'] += data_suma['paid_amount']
                res[data['post'].parent_id.code]['codif_amount'] += data_suma['codif_amount']
                res[data['post'].parent_id.code]['reform_amount'] += data_suma['reform_amount']
                res[data['post'].parent_id.code]['commited_amount'] += data_suma['commited_amount']
                res[data['post'].parent_id.code]['commited_balance'] += data_suma['commited_balance']
            else:
                res[data['post'].parent_id.code] = {
                    'post': data['post'].parent_id,
                    'padre': False, 
                    'code':data['post'].parent_id.code,
#                    'program':data['post'].parent_id.code,
                    'general_budget_name':data['post'].parent_id.name,
                    'planned_amount':data['planned_amount'],
                    'devengado_amount':data['devengado_amount'],
                    'devengado_balance':data['devengado_balance'],
                    'paid_amount':data['paid_amount'],     
                    'codif_amount':data['codif_amount'],
                    'reform_amount':data['reform_amount'],
                    'commited_amount':data['commited_amount'],
                    'commited_balance':data['commited_balance'],
                    'final': False,
                    'tipo': data['tipo'],
                    
                }
            self.crear_padre(res[data['post'].parent_id.code], data_suma,res)
    
    def get_cedula_data(self,cr, uid, move_ids, context):
        res = { }
        res_line = { }
        result = []
        move_ids = context['move_ids']
        items = context['item_ids']
        c_b_lines_obj = self.pool.get('budget.item')
        poa_obj = self.pool.get('budget.poa')
        move_obj = self.pool.get('account.move')
        
        move = move_obj.browse(cr, uid, move_ids[0])
        fiscalyear = move.period_id.fiscalyear_id

        poa_ids = poa_obj.search(cr, uid, [('date_start','=',fiscalyear.date_start),('date_end','=',fiscalyear.date_stop)])
        if not poa_ids:
            raise osv.except_osv('Error de usuario','No hay presupuesto definido para la fecha o periodo contable seleccionado.')
        ids_lines=c_b_lines_obj.search(cr, uid,[('poa_id','=',poa_ids[0]),('id','in',items)])
        contexto = {'move_ids':move_ids, 'poa_id': poa_ids[0]}          
        parameter_obj = self.pool.get('ir.config_parameter')
        codificacion_ids = parameter_obj.search(cr, uid, [('key','=','codigopartida')],limit=1)
        aux='No'
        if codificacion_ids:
            code_budget = parameter_obj.browse(cr, uid, codificacion_ids[0]).value
            if code_budget=='Si':
                aux='Si'
                for line in c_b_lines_obj.browse(cr, uid, ids_lines, context=contexto):
                    if res_line.has_key(line.code)==False:
                        res_line[line.code]={
                            'post': line.budget_post_id,
                            'program': line.program_id.id,
                            'padre': False, 
                            'code':line.code,
                            'general_budget_name':line.budget_post_id.name,
                            'planned_amount':line.planned_amount,
                            'commited_amount':line.commited_amount,
                            'devengado_amount':round(line.devengado_amount,2),
                            'paid_amount':round(line.paid_amount,2),
                            'devengado_balance':line.devengado_balance,
                            'commited_balance':line.commited_balance,
                            'codif_amount':line.codif_amount,
                            'reform_amount':line.reform_amount,
                            'final': False,
                            'tipo': line.type_budget,
                        }
                        if res_line.has_key(line.budget_post_id.code)==False:
                            res_line[line.budget_post_id.code]={
                                'post': line.budget_post_id,
                                'program': line.program_id.id,
                                'padre': False, 
                                'code': line.budget_post_id.code,
                                'general_budget_name':line.budget_post_id.name,
                                'planned_amount':line.planned_amount,
                                'commited_amount':line.commited_amount,
                                'devengado_amount':round(line.devengado_amount,2),
                                'paid_amount':round(line.paid_amount,2),
                                'devengado_balance':line.devengado_balance,
                                'commited_balance':line.commited_balance,
                                'codif_amount':line.codif_amount,
                                'reform_amount':line.reform_amount,
                                'final': True,
                                'tipo': line.type_budget,
                            }
                        else:
                            res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
                            res_line[line.budget_post_id.code]['reform_amount']+=line.reform_amount
                            res_line[line.budget_post_id.code]['codif_amount']+=line.codif_amount
                            res_line[line.budget_post_id.code]['commited_amount']+=line.commited_amount
                            res_line[line.budget_post_id.code]['devengado_amount']+=round(line.devengado_amount,2)
                            res_line[line.budget_post_id.code]['paid_amount']+=round(line.paid_amount,2)
                            res_line[line.budget_post_id.code]['commited_balance']+=line.commited_balance
                            res_line[line.budget_post_id.code]['devengado_balance']+=line.devengado_balance
                        self.crear_padre(res_line[line.code], res_line[line.code],res_line)
                    else:              
                        res_line[line.code[4:]]['planned_amount']+=line.planned_amount
                        res_line[line.code[4:]]['reform_amount']+=line.reform_amount
                        res_line[line.code[4:]]['codif_amount']+=line.codif_amount
                        res_line[line.code[4:]]['commited_amount']+=line.commited_amount
                        res_line[line.code[4:]]['devengado_amount']+=round(line.devengado_amount,2)
                        res_line[line.code[4:]]['paid_amount']+=round(line.paid_amount,2)
                        res_line[line.code[4:]]['commited_balance']+=line.commited_balance
                        res_line[line.code[4:]]['devengado_balance']+=line.devengado_balance
#                        res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
#                        res_line[line.budget_post_id.id+line.program_id.id]['reform_amount']+=line.reform_amount
#                        res_line[line.budget_post_id.id+line.program_id.id]['codif_amount']+=line.codif_amount
#                        res_line[line.budget_post_id.id+line.program_id.id]['commited_amount']+=line.commited_amount
#                        res_line[line.budget_post_id.id+line.program_id.id]['devengado_amount']+=round(line.devengado_amount,2)
#                        res_line[line.budget_post_id.id+line.program_id.id]['paid_amount']+=round(line.paid_amount,2)
#                        res_line[line.budget_post_id.id+line.program_id.id]['commited_balance']+=line.commited_balance
#                        res_line[line.budget_post_id.id+line.program_id.id]['devengado_balance']+=line.devengado_balance
        else:
            for line in c_b_lines_obj.browse(cr, uid, ids_lines, context=contexto):
                if res_line.has_key(line.code)==False:
                    res_line[line.code]={
                        'post': line.budget_post_id,
                        'program': line.program_id.id,
                        'padre': False, 
                        'code':line.code,
                        'general_budget_name':line.budget_post_id.name,
                        'planned_amount':line.planned_amount,
                        'commited_amount':line.commited_amount,
                        'devengado_amount':round(line.devengado_amount,2),
                        'paid_amount':round(line.paid_amount,2),
                        'devengado_balance':line.devengado_balance,
                        'commited_balance':line.commited_balance,
                        'codif_amount':line.codif_amount,
                        'reform_amount':line.reform_amount,
                        'final': False,
                        'tipo': line.type_budget,
                    }
                    if res_line.has_key(line.budget_post_id.code)==False:
                        res_line[line.budget_post_id.code]={
                            'post': line.budget_post_id,
                            'program': line.program_id.id,
                            'padre': False, 
                            'code': line.budget_post_id.code,
                            'general_budget_name':line.budget_post_id.name,
                            'planned_amount':line.planned_amount,
                            'commited_amount':line.commited_amount,
                            'devengado_amount':round(line.devengado_amount,2),
                            'paid_amount':round(line.paid_amount,2),
                            'devengado_balance':line.devengado_balance,
                            'commited_balance':line.commited_balance,
                            'codif_amount':line.codif_amount,
                            'reform_amount':line.reform_amount,
                            'final': True,
                            'tipo': line.type_budget,
                        }
                    else:
                        res_line[line.budget_post_id.code]['planned_amount']+=line.planned_amount
                        res_line[line.budget_post_id.code]['reform_amount']+=line.reform_amount
                        res_line[line.budget_post_id.code]['codif_amount']+=line.codif_amount
                        res_line[line.budget_post_id.code]['commited_amount']+=line.commited_amount
                        res_line[line.budget_post_id.code]['devengado_amount']+=round(line.devengado_amount,2)
                        res_line[line.budget_post_id.code]['paid_amount']+=round(line.paid_amount,2)
                        res_line[line.budget_post_id.code]['commited_balance']+=line.commited_balance
                        res_line[line.budget_post_id.code]['devengado_balance']+=line.devengado_balance
                    self.crear_padre(res_line[line.code], res_line[line.code],res_line)
                else:              
                    res_line[line.budget_post_id.id+line.program_id.id]['planned_amount']+=line.planned_amount
                    res_line[line.budget_post_id.id+line.program_id.id]['reform_amount']+=line.reform_amount
                    res_line[line.budget_post_id.id+line.program_id.id]['codif_amount']+=line.codif_amount
                    res_line[line.budget_post_id.id+line.program_id.id]['commited_amount']+=line.commited_amount
                    res_line[line.budget_post_id.id+line.program_id.id]['devengado_amount']+=round(line.devengado_amount,2)
                    res_line[line.budget_post_id.id+line.program_id.id]['paid_amount']+=round(line.paid_amount,2)
                    res_line[line.budget_post_id.id+line.program_id.id]['commited_balance']+=line.commited_balance
                    res_line[line.budget_post_id.id+line.program_id.id]['devengado_balance']+=line.devengado_balance

        return res_line

    
    def get_balance_data(self, cr, uid, ids, context):
        move_ids = context['move_ids']
        accounts = context['account_ids']
        result = {}
        move_line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')

        move = move_obj.browse(cr, uid, move_ids[0])
        fiscalyear = move.period_id.fiscalyear_id        
        
        account_ids = account_obj.search(cr, uid, [('id','in', accounts)])
        #Buscar lineas de asientos de asiento de inicio

        ctx2 = {}
        ctx2.update({'fiscalyear': fiscalyear.id})
        ctx2.update({'move_ids': move_ids})
        accounts_flujo = account_obj.read(cr, uid, account_ids, ['code','name','debit','credit', 'balance','level'], ctx2)

        accounts_flujo_dict = {}
        for account_data in accounts_flujo:
            accounts_flujo_dict[account_data['code']] = {
                'code': account_data['code'],
                'desc': account_data['name'],
                'nivel': account_data['level'],
                'debit': round(account_data['debit'],2),
                'credit': round(account_data['credit'],2)
            }
        
        accounts_final_dict = {}
        for code in accounts_flujo_dict:
            accounts_final_dict[code] = {
                'code': accounts_flujo_dict[code]['code'],
                'desc': accounts_flujo_dict[code]['desc'],
                'nivel': accounts_flujo_dict[code]['nivel'],
                'debe_inicial': 0,
                'haber_inicial': 0,
                'debe_flujo': round(accounts_flujo_dict[code]['debit'],2),
                'haber_flujo': round(accounts_flujo_dict[code]['credit'],2),
                'debe_suma': 0,
                'haber_suma': 0,
                'debe_final': 0,
                'haber_final': 0
            }
        return accounts_final_dict
        
    def evalRegla(self,regla,cedula,balance):
        return eval(regla.regla)
    
    def get_esigef_values(self, cr, uid, move_id, context={}):
        mensajes = ""
        account_obj = self.pool.get('account.account')
        account_move_obj = self.pool.get('account.move')
        regla_line_obj = self.pool.get('regla.line')
        for move in account_move_obj.browse(cr, uid, move_id):
            accounts = []
            items = []
            for line in move.line_id:
                if line.account_id:
                    accounts.append(line.account_id.id)
                    seguir = True
                    cuenta_aux = line.account_id.id
                    while seguir==True:
                        parent_data = account_obj.read(cr, uid, cuenta_aux, ['parent_id'])
                        if parent_data['parent_id']:
                            accounts.append(parent_data['parent_id'][0])
                            cuenta_aux = parent_data['parent_id'][0]
                        else:
                            seguir=False
                    
                if line.budget_id:
                    items.append(line.budget_id.id)
            context1 = context.copy()
            context2 = context.copy()
            context1.update({'move_ids': [move.id], 'account_ids': accounts})
            context2.update({'move_ids': [move.id], 'item_ids': items})
            balance = self.get_balance_data(cr, uid, [move.id], context1)
            cedula = self.get_cedula_data(cr, uid, [move.id], context2)
            regla_ids = regla_line_obj.search(cr, uid, [])
            for regla in regla_line_obj.browse(cr, uid, regla_ids):
                resultline = self.evalRegla(regla,cedula,balance)
                if resultline != True:
                    #pdb esigef
                    if cedula.has_key('51') and balance.has_key('21351'):
                        print 'CEDULA 51', cedula['51']['devengado_amount'],balance['21351']['haber_flujo'],cedula['51']['paid_amount'],balance['21351']['debe_flujo']
                    if cedula.has_key('71') and balance.has_key('21371'):
                        print 'CEDULA 71', cedula['71']['devengado_amount'],balance['21371']['haber_flujo'],cedula['71']['paid_amount'],balance['21371']['debe_flujo']
                    mensajes += "Regla "+ str(regla.name) + ".- " + "Tipo " + ustr(regla.agrupa) + ". \nDescripcion: "+ ustr(regla.texto)+"\n"
                else:
                    if cedula.has_key('51') and balance.has_key('21351'):
                        print 'CEDULA 51', cedula['51']['devengado_amount'],balance['21351']['haber_flujo'],cedula['51']['paid_amount'],balance['21351']['debe_flujo']
                    if cedula.has_key('71') and balance.has_key('21371'):
                        print 'CEDULA 71', cedula['71']['devengado_amount'],balance['21371']['haber_flujo'],cedula['71']['paid_amount'],balance['21371']['debe_flujo']
        return mensajes

    def call_esigef_values(self, cr, uid, ids, context={}):
        for id in ids:
            mensajes = self.get_esigef_values(cr, uid, [id], context)
            if mensajes!="":
                raise osv.except_osv('Error', mensajes)
        return True
    
    def onchange_line_id(self, cr, uid, ids, line_ids, context=None):
        balance = 0.0
#        line_ids = [ line for line in line_ids if not (isinstance(line, (tuple, list)) and line and line[0] == 2) ]
#        line_ids = self.resolve_o2m_commands_to_record_dicts(cr, uid, 'line_id', line_ids, context=context)
#        for line in line_ids:
#            balance += (line['debit'] or 0.00)- (line['credit'] or 0.00)
        return {'value': {'balance': balance}}

    def onchange_opago(self, cr, uid, ids, p_id):
        result = {}
        value = []
        pago_obj = self.pool.get('payment.request')
        pago = pago_obj.browse(cr, uid, p_id)
        result['narration'] = pago.concepto
        return {'value': result}

    def onchange_cp(self, cr, uid, ids, cp, period=False, date=False,journal=False):
        result = {}
        value = []
        move_obj = self.pool.get('account.move')
        certificate_obj = self.pool.get('budget.certificate')
        company_obj = self.pool.get('res.company')
        cert = certificate_obj.browse(cr, uid, cp)
        result['narration'] = cert.notes
        move_ids = move_obj.search(cr, uid, [('certificate_id','=',cert.id),('state','=','posted')])
        if move_ids:
            MSG = 'El documento presupuestario esta ya relacionado en otro(s) comprobante(s)'
#            raise osv.except_osv('Error', MSG)
        #######################
        post_obj = self.pool.get('budget.post')
        line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        certificate_obj = self.pool.get('budget.certificate')
        result = {}
        value = []
        if not period:
            MSG = 'Debe seleccionar un periodo'
            raise osv.except_osv('Error', MSG)
        if not date:
            MSG = 'Debe seleccionar una fecha'
            raise osv.except_osv('Error', MSG)
        if not journal:
            MSG = 'Debe seleccionar un diario'
            raise osv.except_osv('Error', MSG)
        account_aux = '0'
        #si hay lineas en el move elimina las lineas
        for move in self.browse(cr, uid, ids):
            if move.state=='draft':
                line_ant_ids = line_obj.search(cr, uid, [('move_id','=',move.id)])
                if line_ant_ids:
                    line_obj.unlink(cr, uid, line_ant_ids)
        compania = company_obj.browse(cr, uid, 1)
        for line in cert.line_ids:
            partner_id = line.certificate_id.partner_id.id
            budget_id = line.budget_id
            account_aux_ids = account_obj.search(cr, uid, ['|',('budget_id','=',budget_id.budget_post_id.id),('budget_haber_id','=',budget_id.budget_post_id.id)])
            if not account_aux_ids:
                aux_6 = line.budget_id.budget_post_id.code[0:6]
                aux_budget_6_ids = post_obj.search(cr, uid, [('code','=',aux_6)])
                if aux_budget_6_ids:
                    account_aux_ids = account_obj.search(cr, uid, ['|',('budget_id','=',aux_budget_6_ids[0]),('budget_haber_id','=',aux_budget_6_ids[0])])
            if len(account_aux_ids)>0:
                #cambiado por mario, aqui debe ser pero la patrimonial no la primera
                for account_id in account_aux_ids:
                    account = account_obj.browse(cr, uid, account_id)
                    if account.account_rec_id or account.account_pay_id:
                        account_aux = account.id
                        continue
                if account_aux=='0':
                    aux_nocxp = budget_id.code + ' - ' + budget_id.name
                    MSG = 'La partida %s no tiene configurada la cuenta por pagar' % (aux_nocxp)
                    raise osv.except_osv('Error', MSG)
                account = account_obj.browse(cr, uid, account_aux)
                if account.account_rec_id:
                    account_aux2 = account.account_rec_id.id
                elif account.account_pay_id:
                    account_aux2 = account.account_pay_id.id
                else:
                    if account.account_p_ids:
                        account_aux2 = account.account_p_ids[0].id
                    else:
                        aux_name_cuenta = account.code + ' - ' + account.name
                        MSG = 'La cuenta %s de la partida %s no tiene configurada la cuenta por pagar' % (aux_name_cuenta,budget_id.budget_post_id.name)
                        raise osv.except_osv('Error', MSG)
            else:
                aux_msg_contra = budget_id.budget_post_id.code + ' - ' + budget_id.budget_post_id.name
                MSG = 'La partida %s no tiene configurada la contra cuenta' % (aux_msg_contra)
                raise osv.except_osv('Error', MSG)
            if line.budget_accrued < line.amount_commited:
                amount_aux = line.amount_commited - line.budget_accrued
                if line.tipo_invoice:
                    if line.tipo_invoice in ('Iva','IvaServicios','SRI'):
                        partner_id = compania.tax_company_id.id
                    elif line.tipo_invoice=='Iess':
                        partner_id = compania.iess_id.id
                    aux_name2 = line.tipo_invoice
                else:
                    aux_name2 = 'REF'
                id_creado_pat = line_obj.create(cr, uid, {
                    'journal_id': journal,
                    'budget_id_cert':line.id,
                    'account_id':account_aux,
                    'partner_id':partner_id,
                    'debit':amount_aux,
                    'period_id': period,
                    'date': date,
                    'budget_accrued':True,
                    'name':aux_name2,
                })
                value.append(id_creado_pat)
                linea_aux = line_obj.browse(cr, uid, id_creado_pat)
            if line.budget_paid < line.amount_commited:
                amount_aux = line.amount_commited - line.budget_paid
                if line.tipo_invoice:
                    if line.tipo_invoice in ('Iva','IvaServicios'):
                        partner_id = compania.tax_company_id.id
                    elif line.tipo_invoice=='Iess':
                        partner_id = compania.iess_id.id
                    aux_name2 = line.tipo_invoice
                else:
                    aux_name2 = 'REF'
                id_creado_pp = line_obj.create(cr, uid, {
                    'journal_id': journal,
                    'period_id': period,
                    'date': date,
                    'budget_id_cert':line.id,
                    'account_id':account_aux2,
                    'credit':amount_aux,
                    'name':aux_name2,
                    'partner_id':partner_id,
                })
                value.append(id_creado_pp)
                linea_aux = line_obj.browse(cr, uid, id_creado_pp)
        result['line_id'] = value
        result['narration'] = cert.notes
        result['ref'] = cert.notes
        return {'value': result}

    def unlink(self, cr, uid, ids, aux,context=None):
        for obj in self.browse(cr, uid, ids, context):
            if obj.to_unlink==True:
                aux = 1
            if obj.name=='/' and obj.state in ('draft','anulado'):
                aux = 1
            if aux != 1:
                raise osv.except_osv('Aviso','No se permite borrar asientos contables.')
        res = super(accountMove, self).unlink(cr, uid, ids, context)
        return res

    def buttonAnular(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        for this in self.browse(cr, uid, ids):
            move_obj.write(cr, uid, [this.id], {
                'state':'anulado'
            })
            for line in this.line_id:
                cr.execute('UPDATE account_move_line '\
                           'SET state=%s,to_pay=%s '\
                           'WHERE id = %s', ('draft',False, line.id,))
        return True

    def button_cancel(self, cr, uid, ids, context=None):
        item_obj = self.pool.get('budget.item')
        log_obj = self.pool.get('budget.item.log')
        move_line_obj = self.pool.get('account.move.line')
        for line in self.browse(cr, uid, ids, context=context):
            if line.period_id.state == 'done':
                raise osv.except_osv(('Error !'), ('No se puede modificar asientos de periodos cerrados'))
            elif not line.journal_id.update_posted:
                raise osv.except_osv(_('Error !'), _('You can not modify a posted entry of this journal !\nYou should set the journal to allow cancelling entries if you want to do that.'))
        if ids:
            cr.execute('UPDATE account_move '\
                       'SET state=%s '\
                       'WHERE id IN %s', ('draft', tuple(ids),))
        for move in self.browse(cr, uid, ids, context=context):
            for line in move.line_id:
                cr.execute('UPDATE account_move_line '\
                           'SET state=%s '\
                           'WHERE id = %s', ('draft', line.id,))
        return True

    def validate_esigef(self, cr, uid, ids, context=None):
        MSG = False
        line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        journal_obj = self.pool.get('account.journal')
        post_obj = self.pool.get('budget.post')
        partida_obj = self.pool.get('budget.item')
        period_obj = self.pool.get('account.period')
        no_obj = self.pool.get('no.partida')
        self.test_budget(cr, uid, ids)
        self.apply_budget(cr, uid, ids)
        patrimoniales = []
        lista_banco = [] 
        partida_debe = {}
        partida_haber = {}
        aux_debit = s = aux_anticipo = 0
        for move in self.browse(cr, uid, ids):
            #poner el mismo partner del encabezado en las lineas si estan null
          aux_sql = '''select id from account_move_line where move_id=%s and partner_id is null''' % (move.id)
          cr.execute(aux_sql)
          ids_linea_null = cr.fetchall()
          if ids_linea_null:
              for id_linea_null in ids_linea_null:
                  aux_sql2 = '''update account_move_line set partner_id=%s where id=%s''' % (move.partner_id.id,id_linea_null[0])
                  cr.execute(aux_sql2)
          period_date = period_obj.find(cr, uid, move.date)
          if period_date and period_date[0] != move.period_id.id:
              MSG = 'La fecha %s del comprobante %s no corresponde con el periodo %s' % (move.date, move.name, move.period_id.name)
              return MSG
          if move.afectacion: #and move.type != 'Recaudacion':
                if not (move.date >= move.period_id.date_start and move.date<=move.period_id.date_stop):
                    MSG = 'La fecha del comprobante %s no corresponde al periodo del comprobante' % (move.name)
                    return MSG
                if move.validar_cp == False and move.certificate_id and move.date < move.certificate_id.date_commited:
                    if move.type!='Recaudacion':
                        MSG = 'La fecha de compromiso %s no puede ser mayor a la fecha del movimiento %s' % (move.certificate_id.name,move.name)
                        return MSG
                for line in move.line_id:
                    #valdar que corresponda la partida en la linea en las cxp 
                    if line.budget_id_cert:
                        if not line.budget_post:
                            line_obj.write(cr, uid, line.id,{
                                'name':'CC',
                            })
                        code_partida_2 = line.budget_id_cert.budget_post.code[0:2]
                        code_cuenta_2 = line.account_id.code[3:5]
                        if line.account_id.code[0:3]=='213':
                            if code_partida_2!=code_cuenta_2:
                                if line.account_id.code[0:5]!='21398':
                                    MSG = 'La cuenta seleccionada %s no corresponde con la partida %s' % (line.account_id.code,line.budget_id.code)
                                    return MSG
                    if line.credit==0 and line.debit==0:
                        line_obj.unlink(cr, uid, [line.id])
                        continue
                    #validar que este la partida en todas las lineas a excepcion si hay de banco
                    sql = """select default_debit_account_id from account_journal where type in ('cash','bank')"""
#                    sql = 'select default_debit_account_id from account_journal'
                    cr.execute(sql)
                    data = cr.fetchall()
                    for id_bk in data:
                        lista_banco.append(id_bk[0])
                    no_partida = False
                    is_anticipo = False
                    is_anterior = False
                    is_inversion = False
                    is_not = False
                    no_partida_ids = no_obj.search(cr, uid, [('name','=',line.account_id.code[0:3])])
                    no_partida_ids2 = no_obj.search(cr, uid, [('name','=',line.account_id.code[0:5])])
                    if no_partida_ids or no_partida_ids2:
                        no_partida=True
                    if line.account_id.code[0:3]=='112':
                        is_anticipo=True
                        aux_anticipo = line.credit
                    if line.account_id.code[0:3] in ('124','639'):
                        is_anterior=True
                    if line.account_id.code[0:3] in ('631'):
                        is_inversion = True
                    if line.account_id.code[0:5] in ('15198','15199','21281'):
                        is_not = True
                    #aqui tambien agreagar las cuentas de anticipo 112
                    if not line.account_id.id in lista_banco:
                        if no_partida:
                            continue
                        if is_not:
                            continue
                        if is_inversion:
                            continue
                        if is_anterior:
                            continue
                        if is_anticipo:
                            if line.budget_accrued or line.budget_paid:
                                MSG = 'La cuenta %s de anticipo no tiene afectacion presupuestaria devangado o pagado, y estan con afectacion devengado o pagado' % (line.account_id.code)
                                return MSG
                            continue
                        if not line.budget_id_cert:
                            MSG = 'La cuenta %s seleccionada no esta relacionada con la partida en el asiento' % (line.account_id.code)
                            return MSG
                        account = line.account_id
                        if account.budget_id:
                            if not account.account_rec_id:
                                continue
                            if line.budget_post and line.account_id.account_rec_id:                                
                                patrimoniales.append(account.id)
                                #aqui seria la post padre [0:6]
                                post_ids_1 = post_obj.search(cr, uid, [('code','=',line.budget_post.code[0:6])],limit=1)
                                post_aux_1 = post_obj.browse(cr, uid, post_ids_1[0])
                                if post_aux_1.code != account.budget_id.code[0:6]:
                                    account_ids = account_obj.search(cr, uid, [('budget_id','=',post_ids_1[0])],limit=1)
                                    if not account_ids:
                                        MSG = 'La partida %s , No tiene asociacion contable ' % (line.budget_post.code)
                                        return MSG
                                    account_aux = account_obj.browse(cr, uid, account_ids[0])
                                    MSG = 'La cuenta %s seleccionada no corresponde con la partida %s , La cuenta que corresponde a la partida seleccionada es %s ' % (account.code,line.budget_post.code,account_aux.code)
                                    return MSG
                        elif account.parent_id.budget_id:
                            if not account.account_rec_id:
                                continue
                            if line.budget_post:
                                patrimoniales.append(account.id)
                                if line.budget_post != account.budget_id:
                                    account_ids = account_obj.search(cr, uid, [('budget_id','=',line.budget_post.id)],limit=1)
                                    if not account_ids:
                                        MSG = 'La partida %s , No tiene asociacion contable ' % (line.budget_post.code)
                                        return MSG
                                    account_aux = account_obj.browse(cr, uid, account_ids[0])
                                    MSG = 'La cuenta %s seleccionada no corresponde con la partida %s , La cuenta que corresponde a la partida seleccionada es %s ' % (account.code,line.budget_post.code,account_aux.code)
                                    return MSG
                        else:
                            #es cxp: busco en donde esta cuenta este con partida y sea cxp y esta debe estar en la lista de patromoniales
                            account_ids = account_obj.search(cr, uid, [('account_rec_id','=',account.id)])
                            if account_ids:
                                #valido la partida
                                for acc_id in account_ids:
                                    account_aux = account_obj.browse(cr, uid, acc_id)
                                    if line.budget_id.budget_post_id == account_aux.budget_id:
                                        s += 1
                                if s<=0:
                                    MSG = 'La cuenta %s seleccionada no corresponde con la partida %s ' % (account.code,line.budget_id.budget_post_id.code)
                                    return MSG
                            else:
                                #podria ser retenciones, aqui validar si es 73 o 53 etc [0:2] con cuenta [4:6] sin puntos
                                code_acc_aux = (account.code).replace(".",'')[3:5]
                                budget_acc_aux = line.budget_id.budget_post_id.code[0:2]
                                if code_acc_aux != budget_acc_aux:
                                    code_acc_aux = (account.code).replace(".",'')[3:4]
                                    budget_acc_aux = line.budget_id.budget_post_id.code[0:1]
                                    if code_acc_aux != budget_acc_aux:
                                        MSG = 'La cuenta %s seleccionada no corresponde con la partida %s' % (account.code,line.budget_id.budget_post_id.code)
                                        return MSG
                        #no aplicable ahora en pagos si aplicaria, por que se deberia separar estos
#                        if line.debit:
#                            if line.debit>0:
#                                if not line.budget_accrued:
#                                    MSG = 'La cuenta %s afecta al devengado de la partida, debe seleccionar el campo devengado ' % (account.code)
#                                    raise osv.except_osv('Error', MSG)
                        #validar que las lineas de las partidas haber sumen lo mismo que las partidas del debe: diccionario partida:debe = partida haber
                        if line.debit:
                            if line.debit>0:
                                if not line.budget_id in partida_debe:
                                    partida_debe[line.budget_id.id] = line.debit
                                else:
                                    partida_debe[line.budget_id.id] += line.debit
                        if line.credit:
                            if line.credit>0:
                                if not line.budget_id in partida_haber:
                                    partida_haber[line.budget_id.id] = line.credit
                                else:
                                    partida_haber[line.budget_id.id] += line.credit
                    else:
                        if line.budget_accrued or line.budget_paid:
                            MSG = 'La cuenta %s de banco no tiene afectacion presupuestaria devangado o pagado y estan con devengado o pagado' % (line.account_id.code)
                            return MSG
                    if (line.budget_accrued or line.budget_paid) and (line.move_id.type!='Recaudacion'):
                        MSG1 = False
                        MSG2 = False
                        commited_aux = line.budget_id_cert.amount_commited
                        accrued_aux = line.budget_id_cert.amount_paid
                        paid_aux = line.budget_id_cert.budget_paid
                        if line.debit == None or line.debit == 0:
                            dato = line.credit
                        else:
                            dato = line.debit
                        if line.budget_accrued:
                            #Validar que lo devengado no pueda ser mayor que lo comprometido
                            if commited_aux < accrued_aux:
                                MSG1 = 'El valor total de devengado %s + %s no puede ser mayor que el comprometido %s' % (accrued_aux, dato ,commited_aux)
                            else:
                                accrued_aux = accrued_aux + dato
                        if line.budget_paid:
                            #Validar que el valor pagado no pueda ser mayor que el valor devengado
                            print "PARQ FU"
#                            if accrued_aux < paid_aux + dato:
#                                MSG2 = 'El valor total de pagado %s + %s no puede ser mayor que el devengado %s' % (str(accrued_aux), str(paid_aux))
                        if MSG1!=False and MSG2!=False:
                            MSG = MSG1 + " - " + MSG2
                        elif MSG1!=False:
                            MSG = MSG1
                        elif MSG2!=False:
                            MSG = MSG2
                        if MSG!=False:
                            return MSG
                for pdebe in partida_debe:
                    if partida_debe.get(pdebe,False) and partida_haber.get(pdebe,False):
                        if partida_debe[pdebe] != partida_haber[pdebe]:
                            if is_anticipo:
                                print "anticipo"
#                            else:
#                                partida = partida_obj.browse(cr, uid, pdebe)
#                                partida_suma = post_obj.browse(cr, uid, partida.budget_post_id.id)
#                                aux_pdebe = partida_suma.code + ' - ' + partida_suma.name
#                                aux_abs = abs(aux_pdebe)
#                                if not (aux_abs < 10 ** -4):                                        
#                                    MSG = 'El todal del valor debe y haber para la partida %s debe ser igual ' % (aux_pdebe)
#                                    raise osv.except_osv('Error', MSG)
                #message = self.check_esigef_msg(cr, uid, [move.id], context)
                #if message:
                #    MSG = message
                #    return MSG
        return MSG

    def validate_budget(self, cr, uid, ids, context=None):
        #revisar este metodo
        #return True
        MSG = False
        line_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        post_obj = self.pool.get('budget.post')
        partida_obj = self.pool.get('budget.item')
        migrated_obj = self.pool.get('budget.item.migrated')
        poa_obj = self.pool.get('budget.poa')
        move_obj = self.pool.get('account.move')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        partidas = []
        for move in self.browse(cr, uid, ids):
            if move.type2_id in ('Ajuste','Cierre','Inventario'):
                return True
            if move.type=='Recaudacion':
                return True
            poa_ids = poa_obj.search(cr, uid, [('date_start','>=',move.period_id.fiscalyear_id.date_start),('date_end','<=',move.period_id.fiscalyear_id.date_stop)])
            context = {'by_date':True,'date_start':move.period_id.fiscalyear_id.date_start, 'date_end': move.date,
                       'poa_id':poa_ids[0]}            
            for line in move.line_id:
                if line.budget_id:
                    if not line.budget_id.id in partidas:
                        partidas.append(line.budget_id.id)
            total_comprometido = total_devengado = total_pagado = 0
            for partida_id in partidas:
                lines_compromiso_ids = certificate_line_obj.search(cr, uid, [('certificate_id','=',move.certificate_id.id),('budget_id','=',partida_id)])
                if lines_compromiso_ids:
                    for line_compromiso_id in lines_compromiso_ids:
                        line_compromiso = certificate_line_obj.browse(cr, uid, line_compromiso_id)
                        total_comprometido += line_compromiso.amount_commited
                #lineas de reajuste
                migrated_ids = migrated_obj.search(cr, uid, [('certificate_id','=',move.certificate_id.id),('budget_item_id','=',partida_id)])
                if migrated_ids:
                    for migrated_id in migrated_ids:
                        migrated = migrated_obj.browse(cr, uid, migrated_id)
                        total_comprometido += migrated.commited_amount
                partida = partida_obj.browse(cr, uid, partida_id, context)
                if partida.type_budget=='ingreso':
                    continue
                lineas_devengado = line_obj.search(cr, uid, [('move_id','=',move.id),('budget_id','=',partida_id),('budget_accrued','=',True)])
                aux_devengado = 0 
                if lineas_devengado:
                    for linea_devengado_id in lineas_devengado:
                        linea_devengado = line_obj.browse(cr, uid, linea_devengado_id)
                        if linea_devengado.debit>0:
                            aux_devengado += linea_devengado.debit
                        elif linea_devengado.credit>0:
                            aux_devengado += linea_devengado.credit
                lineas_pagado = line_obj.search(cr, uid, [('move_id','=',move.id),('budget_id','=',partida_id),('budget_paid','=',True)])
                aux_pagado = 0 
                if lineas_pagado:
                    for linea_pagado_id in lineas_pagado:
                        linea_pagado = line_obj.browse(cr, uid, linea_pagado_id)
                        if linea_pagado.debit>0:
                            aux_pagado += linea_pagado.debit
                        elif linea_pagado.credit>0:
                            aux_pagado += linea_pagado.credit
                #primero validar mas pago, devengado etc pero del compromiso
                extra_devengado = extra_pagado = 0
                if move.certificate_id and move.type not in ('Nomina','Recaudacion','Impuestos'):
                    moves_extra_ids = move_obj.search(cr, uid, [('certificate_id','=',move.certificate_id.id),('id','!=',move.id),('state','=','posted')])
                    if moves_extra_ids:
                        lineas_extra_devengado_ids = line_obj.search(cr,uid, [('move_id.state','=','posted'),('move_id','in',moves_extra_ids),
                                                                              ('budget_accrued','=',True),('budget_id','=',partida_id)])
                        lineas_extra_pagado_ids = line_obj.search(cr,uid, [('move_id.state','=','posted'),('move_id','in',moves_extra_ids),
                                                                           ('budget_paid','=',True),('budget_id','=',partida_id)])
                        if lineas_extra_devengado_ids:
                            for line_extra_id in lineas_extra_devengado_ids:
                                linea = line_obj.browse(cr, uid, line_extra_id)
                                extra_devengado += (linea.debit+linea.credit)
                        if lineas_extra_pagado_ids:
                            for line_extra_id in lineas_extra_pagado_ids:
                                linea = line_obj.browse(cr, uid, line_extra_id)
                                extra_pagado += (linea.debit+linea.credit)
                    ####################################
                    devengado_asientos = extra_devengado + aux_devengado
                    if total_comprometido>0:
                        if devengado_asientos > total_comprometido:
                            diferencia = abs(devengado_asientos - total_comprometido)
                            if diferencia > 0.01:
                                raise osv.except_osv('Error de usuario',
                                                     'EL devengado no puede ser mayor al comprometido en la partida %s diferencia %s.'%(partida.code,str(diferencia)))
                    pagado_asientos = extra_pagado + aux_pagado
                    if pagado_asientos > devengado_asientos:
                        diferencia = abs(devengado_asientos - pagado_asientos)
                        if diferencia > 0.01:
                            raise osv.except_osv('Error de usuario',
                                                 'EL pagado no puede ser mayor al devengado en la partida %s diferencia %s.'%(partida.code,str(diferencia)))
                #luego el global de todo
                total_comprometido = partida.commited_amount
                total_pagado = partida.paid_amount + aux_pagado
                total_devengado = partida.devengado_amount + aux_devengado
                if (total_pagado - total_devengado) > 0.001:
                    diferencia = abs(total_pagado - total_devengado)
                #    raise osv.except_osv('Error de usuario',
                #                         'EL pagado no puede ser mayor al devengado en la partida %s diferencia %s.'%(partida.code,str(diferencia)))
                if (total_devengado - total_comprometido)>0.001:
                    diferencia = abs(total_comprometido - total_devengado)
                #    raise osv.except_osv('Error de usuario',
                #                         'EL devengado no puede ser mayor al comprometido en la partida %s diferencia %s.'%(partida.code,str(diferencia)))
        return True

    def post(self, cr, uid, ids, context=None):
        """
        Redefinicion de metodo para validar partidas
        y su relacion contable
        """
        MSG_TOTAL = ""
        move_obj = self.pool.get('account.move')
        obj_move_line = self.pool.get('account.move.line')
        pago_obj = self.pool.get('payment.request')
        moves = []
        for move in self.read(cr, uid, ids, ['id','line_id','type2_id'],context):
            #validar q debe = haber
            sql_aux = '''select sum(debit),sum(credit) from account_move_line where move_id=%s'''%move['id']
            cr.execute(sql_aux)
            for suma in cr.fetchall():
                aux_dif = suma[0] - suma[1]
                if abs(aux_dif)>0.01:
                    raise osv.except_osv(('Error de usuario!'), ('La suma del debe no es igual a la suma del haber'))
            move_obj._checkMoveDate(cr, uid, [move['id']])
            movimiento = move_obj.browse(cr, uid, [move['id']])
            if movimiento[0].certificate_id and movimiento[0].type!='Recaudacion':
                if not movimiento[0].certificate_id.state=='commited':
                    raise osv.except_osv(('Error de usuario!'), ('No puede ejecutar la contabilizacion sin el compromiso presupuestario, primero debe comprometer'))
            if movimiento[0].period_id.state == 'done' and movimiento[0].type2_id!='Cierre':
                raise osv.except_osv(('Error !'), ('No se puede modificar asientos de periodos cerrados'))
            if movimiento[0].pago_id.id:
                pago_obj.write(cr, uid, [movimiento[0].pago_id.id],{
                    'state':'Contabilizado',
                })
            if movimiento[0].certificate_id:
                if movimiento[0].certificate_id.payment_id:
                    pago_obj.write(cr, uid, [movimiento[0].certificate_id.payment_id.id],{
                        'state':'Contabilizado',
                    })  
#            MSG = self.validate_esigef(cr, uid, [move['id']], context) quitado el 30 dic 2016
            MSG_ESIGEF = self.get_esigef_values(cr, uid,[move['id']], context)
            if MSG_ESIGEF:
                if move['type2_id'] not in ('Baja','Inventario','Cierre','Simultaneo'):
                    raise osv.except_osv('Error', MSG_ESIGEF)
            if MSG_ESIGEF:
                MSG_TOTAL = MSG_TOTAL #+ MSG
                moves.append(move['id'])
            else:
                obj_move_line.write(cr, uid, move['line_id'], {
                    'state': 'valid'
                }, context, check=False)
            if move['type2_id'] in ('Baja','Inventario','Cierre','Simultaneo'):
                MSG_TOTAL=""
        cr.commit()
        if MSG_TOTAL!="":
            for move in moves:
                line_ids = obj_move_line.search(cr, uid, [('move_id','=',move)])
                obj_move_line.write(cr, uid, line_ids, {'state': 'draft'}, context, check=False)
            cr.commit()
            raise osv.except_osv('Error', MSG_TOTAL)
        #pasar el estado del orden de pago a contabilizado
        #validar que no haya mas pagado que devengado, mas devengado que comprometido y comprometido que codificado
        MSG_more = self.validate_budget(cr, uid, ids, context)
        ##elimina los asientos creado y lineas creadas ficticias
        move_ids = move_obj.search(cr, uid, [('name','=','/'),('afectacion','=',False),('partner_id','=',False)])
        if move_ids:
            line_ids_unlink = obj_move_line.search(cr, uid, [('move_id','in',move_ids)])
            if line_ids_unlink:
                obj_move_line.unlink(cr, uid, line_ids_unlink)
            move_obj.unlink(cr, uid, move_ids, context)
        move_obj.write(cr, uid, [move['id']],{'contabilizado_id':uid})
        return super(accountMove, self).post(cr, uid, ids, context)

    def validate(self, cr, uid, ids, context=None):
        if context and ('__last_update' in context):
            del context['__last_update']
        valid_moves = [] #Maintains a list of moves which can be responsible to create analytic entries
        obj_analytic_line = self.pool.get('account.analytic.line')
        obj_move_line = self.pool.get('account.move.line')
        for move in self.browse(cr, uid, ids, context):          
            # Unlink old analytic lines on move_lines
            for obj_line in move.line_id:
                for obj in obj_line.analytic_lines:
                    obj_analytic_line.unlink(cr,uid,obj.id)

            journal = move.journal_id
            amount = 0
            line_ids = []
            line_draft_ids = []
            company_id = None
            for line in move.line_id:
                amount += line.debit - line.credit
                line_ids.append(line.id)
                if line.state=='draft':
                    line_draft_ids.append(line.id)

                if not company_id:
                    company_id = line.account_id.company_id.id
                if not company_id == line.account_id.company_id.id:
                    raise osv.except_osv(_('Error'), _("Couldn't create move between different companies"))

                if line.account_id.currency_id and line.currency_id:
                    if line.account_id.currency_id.id != line.currency_id.id and (line.account_id.currency_id.id != line.account_id.company_id.currency_id.id):
                        raise osv.except_osv(_('Error'), _("""Couldn't create move with currency different from the secondary currency of the account "%s - %s". Clear the secondary currency field of the account definition if you want to accept all currencies.""") % (line.account_id.code, line.account_id.name))
            if line_ids:
                if len(line_ids)>1:
                    tuple_ids = tuple(line_ids)
                    operador = 'in'
                else:
                    tuple_ids = (line_ids[0])
                    operador = '='
                cr.execute('''update account_move_line set state='valid' where id %s %s'''%(operador,tuple_ids))            
            if abs(amount) < 10 ** -3:
                # If the move is balanced
                # Add to the list of valid moves
                # (analytic lines will be created later for valid moves)
                valid_moves.append(move)

                # Check whether the move lines are confirmed

                if not line_draft_ids:
                    continue
                # Update the move lines (set them as valid)
                #cambiado mario 1 enero 2017 hecho con sql
                if len(line_draft_ids)>1:
                    tuple_ids = tuple(line_draft_ids)
                    operador = 'in'
                else:
                    tuple_ids = (line_draft_ids[0])
                    operador = '='
                cr.execute('''update account_move_line set state='valid' where id %s %s'''%(operador,tuple_ids))
                #obj_move_line.write(cr, uid, line_draft_ids, {
                #    'state': 'valid'
                #}, context, check=False)

                account = {}
                account2 = {}
                if journal.type in ('purchase','sale'):
                    for line in move.line_id:
                        code = amount = 0
                        key = (line.account_id.id, line.tax_code_id.id)
                        if key in account2:
                            code = account2[key][0]
                            amount = account2[key][1] * (line.debit + line.credit)
                        elif line.account_id.id in account:
                            code = account[line.account_id.id][0]
                            amount = account[line.account_id.id][1] * (line.debit + line.credit)
                        if (code or amount) and not (line.tax_code_id or line.tax_amount):
#                            cr.execute('''update account_move_line set tax_code_id=%s,tax_amount=%s where id=%s'''%(line.id,code,amount))
                            obj_move_line.write(cr, uid, [line.id], {
                                'tax_code_id': code,
                                'tax_amount': amount
                            }, context, check=False)
            elif journal.centralisation:
                # If the move is not balanced, it must be centralised...

                # Add to the list of valid moves
                # (analytic lines will be created later for valid moves)
                valid_moves.append(move)

                #
                # Update the move lines (set them as valid)
                #
                self._centralise(cr, uid, move, 'debit', context=context)
                self._centralise(cr, uid, move, 'credit', context=context)
                if len(line_draft_ids)>1:
                    tuple_ids = tuple(line_draft_ids)
                    operador = 'in'
                else:
                    tuple_ids = (line_draft_ids[0])
                    operador = '='
                cr.execute('''update account_move_line set state='valid' where id %s %s'''%(operador,tuple_ids))                
#                obj_move_line.write(cr, uid, line_draft_ids, {
#                    'state': 'valid'
#                }, context, check=False)
            else:
                if len(line_ids)>1:
                    tuple_ids = tuple(line_ids)
                    operador = 'in'
                else:
                    tuple_ids = (line_ids[0])
                    operador = '='
                cr.execute('''update account_move_line set state='valid' where id %s %s'''%(operador,tuple_ids))
                # We can't validate it (it's unbalanced)
                # Setting the lines as draft
             #   obj_move_line.write(cr, uid, line_ids, {
             #       'state': 'draft'
             #   }, context, check=False)
        # Create analytic lines for the valid moves
        for record in valid_moves:
            obj_move_line.create_analytic_lines(cr, uid, [line.id for line in record.line_id], context)

        valid_moves = [move.id for move in valid_moves]
        ###### solo para migrar
#        if not valid_moves:
#            valid_moves = [] 
#            valid_moves.append(move.id)
        ######
        return len(valid_moves) > 0 and valid_moves or False

    def test_budget(self, cr, uid, ids):
        """
        Metodo que valida si la partida presupuestaria
        aplicada es correcta con la cuenta contable.
        Quitado por el momento siempre TRUE
        """
        return True    

    def apply_budget(self, cr, uid, ids):
        """
        Metodo que valida si la partida presupuestaria
        aplicada es correcta con la cuenta contable.
        Quitado por el momento siempre TRUE
        """
        item_obj = self.pool.get('budget.item')
        log_obj = self.pool.get('budget.item.log')
        monto = 0
        return True    
 
    def button_imprimir(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        states = self.read(cr, uid, ids, ['state'])
        for state in states:
            if state['state'] != 'posted':
                raise osv.except_osv(_('Error !'), _('No puede imprimir un comprobante en borrador'))
        datas = {'ids': ids, 'model': 'account.move'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.move',
            'model': 'account.move',
            'datas': datas,
            'nodestroy': True,                          
            }

    def button_addpost(self, cr, uid, ids, context=None):
        cert_line = self.pool.get('budget.certificate.line')
        project_obj = self.pool.get('project.project')
        item_obj = self.pool.get('budget.item')
        for this in self.browse(cr, uid, ids):
            if this.budget_post_id:
                project_ids = project_obj.search(cr, uid, [('type_budget','=','ingreso')],limit=1)
                if project_ids:
                    item_ids = item_obj.search(cr, uid, [('budget_post_id','=',this.budget_post_id.id)],limit=1)
                    if item_ids:
                        project = project_obj.browse(cr, uid, project_ids[0])
                        cert_line_id = cert_line.create(cr, uid, {
                            'project_id':project.id,
                            'task_id':project.tasks[0].id,
                            'budget_id':item_ids[0],
                            'certificate_id':this.certificate_id.id,
                            'amount':0,
                            'amount_certified':0,
                            'amount_commited':0,
                        })
        return True

    def button_imprimir_detalle(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        states = self.read(cr, uid, ids, ['state'])
        for state in states:
            if state['state'] not in ('posted','anulado'):
                raise osv.except_osv(_('Error !'), _('No puede imprimir un comprobante en borrador'))
        datas = {'ids': ids, 'model': 'account.move'}
        #unlink
        sql = "delete from account_move where partner_id is null and name='/'"
        cr.execute(sql)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.move',
            'model': 'account.move',
            'datas': datas,
            'nodestroy': True,                          
            }

    def button_imprimir_detalle_ingreso(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        states = self.read(cr, uid, ids, ['state'])
        for state in states:
            if state['state'] != 'posted':
                raise osv.except_osv(_('Error !'), _('No puede imprimir un comprobante en borrador'))
        datas = {'ids': ids, 'model': 'account.move'}
        #unlink
        sql = "delete from account_move where partner_id is null and name='/'"
        cr.execute(sql)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.move.detalle',
            'model': 'account.move',
            'datas': datas,
            'nodestroy': True,                          
            }
    
    def check_esigef_msg(self, cr, uid, ids, context={}):
        cta_obj = self.pool.get('cta.partida')
        account_obj = self.pool.get('account.account')
        cta_ids = cta_obj.search(cr, uid, [])
        cta_objs = cta_obj.read(cr, uid, cta_ids, [])
        valid = {}
        MSG = ""
        for move in self.browse(cr, uid, ids, context):
            for cta in cta_objs:
                valid[cta['cta']] = {
                    'cta':cta['cta'],
                    'partida': cta['partida'],
                    'debe':0,
                    'haber':0,
                    'devengado':0,
                    'pagado':0
                }
            for line in move.line_id:
                for cta in valid:
                    if line.account_id.code[0:len(cta)]==cta:
                        valid[cta]['debe'] = valid[cta]['debe'] + line.debit
                        valid[cta]['haber'] = valid[cta]['haber'] + line.credit
                        break
                for cta in valid:
                    if line.budget_id and line.budget_id.code[0:len(valid[cta]['partida'])]==valid[cta]['partida']:
                        if line.budget_accrued:
                            valid[cta]['devengado'] = valid[cta]['devengado'] + abs(line.debit-line.credit)
                        if line.budget_paid:
                            valid[cta]['pagado'] = valid[cta]['pagado'] + abs(line.debit-line.credit)
                        break
            for cta in valid:
                aux_abs = 0
#                if abs(valid[cta]['debe'] - valid[cta]['pagado'])>0.001:
                if valid[cta]['pagado'] > 0:
                    if abs(valid[cta]['debe'] - valid[cta]['pagado'])>0.01:
                        aux_abs = abs(valid[cta]['debe'] - valid[cta]['pagado'])
                        MSG += '\nEl total debe de la cuenta %s no es igual al pagado de la partida %s . Revise el movimiento %s, Es %s' % (cta,valid[cta]['partida'],move.name,aux_abs)
    #                    raise osv.except_osv('Error', MSG)
                if abs(valid[cta]['haber'] - valid[cta]['devengado'])>0.01:
                    aux_abs = abs(valid[cta]['haber'] - valid[cta]['devengado'])
                    MSG += '\nEl total haber de la cuenta %s no es igual al devengado de la partida %s . Revise el movimiento %s, Es %s' % (cta,valid[cta]['partida'], move.name,aux_abs)
#                    raise osv.except_osv('Error', MSG)
        return MSG

    def _compute_numero_comp(self, cr, uid, ids, a, b, c):
        po = self.pool.get('purchase.order')
        res = {}
        aux = 0
        for this in self.browse(cr, uid, ids):
            if this.state=='posted':
                aux = this.name.encode('utf-8')
                if aux.isdigit():
                    res[this.id] = int(this.name)
                else:
                    res[this.id] = -1
        return res

    def _compute_total_banco(self, cr, uid, ids, a, b, c):
        res = {}
        aux = 0
        journal_obj = self.pool.get('account.journal')
        aux_total_banco = 0
        for this in self.browse(cr, uid, ids):
            for line in this.line_id:
                if line.credit>0:
                    aux_account_id = line.account_id
                    journal_ids = journal_obj.search(cr, uid, [('type','=','bank'),('default_credit_account_id','=',line.account_id.id)])
                    if journal_ids:
                        aux_total_banco += line.credit
            res[this.id] = aux_total_banco
        return res
                        
    _columns = dict(
        contabilizado_id = fields.many2one('res.users','Contabilizado por'),
        active = fields.boolean('Activo'),
        numero_aux = fields.integer('Num. Aux'),
        archivado = fields.boolean('Archivado'),
        total_banco = fields.function(_compute_total_banco,string='Total Banco',type="float",store=True),
        numero = fields.function(_compute_numero_comp,string='NUMERO COMPROBANTE',type="integer",store=True),
        fiscalyear_id = fields.related('period_id', 'fiscalyear_id', type='many2one',
                                      relation='account.fiscalyear', string='A. Fiscal',store=True,
                                      readonly=True),
        aux_update = fields.char('aux gob_implementation', size=1),
        no_cp = fields.boolean('NO CP'),
        pago_id = fields.many2one('payment.request','Orden Pago'),
        to_unlink = fields.boolean('Borrar'),
        partner_id = fields.many2one('res.partner','Empresa'),
        afectacion = fields.boolean('Afectacion'),
        state = fields.selection([('draft','Unposted'), ('posted','Posted'),('anulado','Anulado')], 'State', required=True, readonly=True),
        certificate_id = fields.many2one('budget.certificate',
                                         string='Compromiso Presupuestario'),
        reposition = fields.char('Reposicion',size=32,readonly=True),
        migrado = fields.boolean('Es migrado'),
        migrado2 = fields.boolean('Migrado Ant'),
        type = fields.selection([('Factura','Factura'),('Anticipo','Anticipo'),('Liquidacion','Liquidacion'),('Impuestos','Impuestos'),
                                 ('Recaudacion','Recaudacion'),('Otros','Otros'),('Baja','Baja'),('Nomina','Nomina')],'Tipo Asiento'),
        is_pay = fields.boolean('Es pago'),
        is_start = fields.boolean('Es Inicial'),
        validar_cp = fields.boolean('Validar CP'),
        budget_post_id = fields.many2one('budget.post','Partida'),
        type2_id = fields.selection([('Financiero','Financiero'),('Ajuste','Ajuste'),('Simultaneo','Simultaneo'),('Cierre','Cierre'),('Inventario','Inventario'),
                                     ('Presupuestario','Presupuestario'),('Cuenta de orden','Cuenta de orden'),('Baja','Baja')],'Tipo Transaccion'),
        )

    def _checkMoveDate(self, cr, uid, ids):
        #debe ser en el contabilizar
        band = True
        year_obj = self.pool.get('account.fiscalyear')
        for obj in self.browse(cr, uid, ids):
            year_ids = year_obj.search(cr, uid, [('date_start','<=',obj.date),('date_stop','>=',obj.date)],limit=1)
            if year_ids:
                year = year_obj.browse(cr, uid, year_ids[0])
            else:
                raise osv.except_osv('Error de configuracion', 'No hay anio fiscal para la fecha del comprobante.')
            if not (obj.date>=obj.period_id.date_start and obj.date<=obj.period_id.date_stop):
                raise osv.except_osv('Error de usuario', 'La fecha del comprobante no corresponde con el periodo seleccionado.')
            if obj.certificate_id:
                if obj.certificate_id.date_commited:
                    if not (obj.certificate_id.date_commited>=year.date_start and obj.certificate_id.date_commited<=year.date_stop):
                        raise osv.except_osv('Error de usuario', 'La fecha del compromiso no corresponde con el periodo seleccionado.')
                    #validar el anio de las partidas usadas en el compromiso
                    for certificate_line in obj.certificate_id.line_ids:
                        year_line_ids = year_obj.search(cr, uid, [('date_start','<=',certificate_line.date_commited),
                                                                  ('date_stop','>=',certificate_line.date_commited)],limit=1) 
                        if year_line_ids:
                            if year_ids[0]!=year_line_ids[0]:
                                raise osv.except_osv('Error de usuario', 'Las partidas de compromiso no corresponden al anio de la fecha de comprobante.')
        return band

    def _checkMoveNumber(self, cr, uid, ids):
        return True
        result = True
        move_obj = self.pool.get('account.move')
        for this in self.browse(cr, uid, ids):
            if this.name!='/':
                #aqui considerar el diario para riobamba
                parameter_obj = self.pool.get('ir.config_parameter')
                separasec_ids = parameter_obj.search(cr, uid, [('key','=','separasec')],limit=1)
                separasec = 'No'
                if separasec_ids:
                    separasec = parameter_obj.browse(cr, uid, separasec_ids[0]).value
                if separasec=='Si':
                    move_ids = move_obj.search(cr, uid, [('journal_id','=',this.journal_id.id),('name','=',this.name),
                                                         ('state','=','posted'),('fiscalyear_id','=',this.fiscalyear_id.id)])
                else:
                    move_ids = move_obj.search(cr, uid, [('name','=',this.name),('state','=','posted'),('fiscalyear_id','=',this.fiscalyear_id.id)])
                    #limon considerar anulados
#                    move_ids = move_obj.search(cr, uid, [('name','=',this.name),('state','in',('posted','anulado')),('fiscalyear_id','=',this.fiscalyear_id.id)])
                if len(move_ids)>1:
                    result = False
        return result

    def _checkCambioFecha(self, cr, uid, ids):
        band = True
        for obj in self.browse(cr, uid, ids):
            if obj.name!='/':
                if obj.fiscalyear_id:
                    if obj.date:
                        if not (obj.date>=obj.fiscalyear_id.date_start and obj.date<=obj.fiscalyear_id.date_stop):
                            mensaje = ustr('La fecha debe estar dentro del mismo anio fiscal en el cual tomo secuencia %s' %(obj.fiscalyear_id.name))
                            raise osv.except_osv('Error', mensaje)
                    if obj.period_id:
                        if obj.period_id.fiscalyear_id.id!=obj.fiscalyear_id.id:
                            mensaje = ustr('La fecha debe estar dentro del mismo anio fiscal en el cual tomo secuencia %s' %(obj.fiscalyear_id.name))
                            raise osv.except_osv('Error', mensaje)
        return True

    _defaults = dict(
        state = 'draft',
        migrado = False,
        validar_cp = False,
        no_cp = False,
        type2_id = 'Financiero',
        active = True,
    )

    _constraints = [
#        (_checkMoveDate,
 #        ustr('La fecha de comprobante no corresponde al periodo o la fecha del compromiso presupuestario. Verifique las fechas'),[ustr('Fecha'), 'Fecha']),
        (_checkMoveNumber,
         ustr('El numero de comprobante es unico. Verifique el numero'),[ustr('Numero'), 'Numero']),
        (_checkCambioFecha,
         ustr('El comprobante ya tiene numero en el periodo'),[ustr('Fecha'), 'Fecha']),
        ]
    
accountMove()

class moveLinePago(osv.Model):
    _name = 'move.line.pago'
    _columns = dict(
        line_id = fields.many2one('account.move.line','Cuenta por pagar'),
        line_move_id = fields.many2one('account.move.line','Detalle Pago'),
        monto_pagado = fields.float('Monto Pago'),
    )
moveLinePago()

class AccountMoveLine(osv.Model):
    _inherit = 'account.move.line'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.name + ' - ' + record.account_id.code + ' DEBE: ' + str(record.debit) + ' HABER: ' + str(record.credit)
            res.append((record.id, name))
        return res

    def _check_company_id(self, cr, uid, ids, context=None):
        lines = self.browse(cr, uid, ids, context=context)
        for l in lines:
            if l.company_id != l.account_id.company_id or l.company_id != l.period_id.company_id:
                return False
        return True

    def _get_cuenta_aux(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            if line.account_id:
                res[line.id] = line.account_id.code[0:5]
        return res

    def _get_partida_aux(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            if line.budget_post:
                res[line.id] = line.budget_post.code[0:2]
        return res

    def _amount_pagar(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        move_line_obj = self.pool.get('account.move.line')
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'monto_pagado': 0.0,
                'saldo': 0.0,
                }
            move_line_ids = move_line_obj.search(cr, uid, [('move_line_cxp','=',line.id),('move_id','=',line.move_id.id)])
            move_line_ids2 = move_line_obj.search(cr, uid, [('move_line_cxp','=',line.id),('move_id','!=',line.move_id.id),('move_id.state','=','posted')])
            move_line_ids3 = move_line_ids + move_line_ids2
            total_pagado = saldo = 0
            if move_line_ids3:
                for move_line_id in move_line_ids3:
                    move_line = move_line_obj.browse(cr, uid, move_line_id)
                    total_pagado += move_line.debit
            saldo = line.credit - total_pagado
            res[line.id]['monto_pagado'] = total_pagado
            res[line.id]['saldo'] = saldo
        return res

    def _spi_pago(self, cr, uid, ids, a, b, c):
        res = {}
        aux_numero = 0
        line_obj = self.pool.get('spi.line')
        for this in self.browse(cr, uid, ids):
            line_ids = line_obj.search(cr, uid, [('move_id','=',this.move_id.id)])
            if line_ids:
                line = line_obj.browse(cr, uid, line_ids[0])
                aux_numero = line.spi_id.ref
            res[this.id] = aux_numero
        return res

    _columns = {
        'judicial_decimo':fields.float('Desc. Judicial (DECIMOS)'),
        'spi_numero':fields.integer('Num.SPI'),#fields.function(_spi_pago,string='Num. SPI',type="integer",store=True),
        'updated':fields.boolean('AuxUpdt'),
        'move_line_cxp':fields.many2one('account.move.line','Cta. por pagar'),#esto seria el move q se esta pagando con este pago
        'is_ingreso_gad':fields.boolean('Es ingreso GAD'),
        'cuenta_aux':fields.function(_get_cuenta_aux, store=True, string='Cuenta Aux',type='char',size=5),
        'partida_aux':fields.function(_get_partida_aux, store=True, string='Partida Aux',type='char',size=2),
        'is_ingreso_anticipo':fields.boolean('Es anticipo ingreso(vacaciones)'),
        'is_anticipo':fields.boolean('Es anticipo'),
        'tax_aux_id':fields.many2one('account.invoice.tax','Impuesto factura'),
        'p_id':fields.many2one('account.payment.sri','Impuestos'),
        'wcxp_id':fields.many2one('wizard.pagar.cxp','Detalle'),
        'pay_ids':fields.one2many('move.line.pago','line_id','Pagos'),
        'pay_id' : fields.many2one('make.pay','Pago'),
        'account_id2':fields.many2one('account.account','Cuenta por pagar tercero'),
        'to_pay': fields.boolean('Pagar'),
        'to_pay2': fields.boolean('Pagar'),
        'monto': fields.float('Monto a Pagar'),
        #'saldo':fields.float('Saldo'),
        'monto_pagado':fields.function(_amount_pagar, string='Pagado', multi="topay",store=True,digits_compute= dp.get_precision('Account')),
        'saldo':fields.function(_amount_pagar, string='Saldo', multi="topay",store=True,digits_compute= dp.get_precision('Account')),
        'date': fields.related('move_id','date', type='date', relation="account.move", string="Fecha", store=True, readonly=True),
        'is_start': fields.related('move_id', 'is_start', type='boolean',
                                     string='Inicial',store=True,
                                     readonly=True),
        'budget_id_cert': fields.many2one('budget.certificate.line', 'Partida Prespuestaria'),
        'budget_post': fields.related('budget_id_cert', 'budget_post', type='many2one',
                                     relation='budget.post', string='Partida Catalogo',store=True,
                                     readonly=True),
        'financia_id': fields.related('budget_id_cert', 'financia_id', type='many2one',
                                      relation='budget.financiamiento', string='Cta. Financiera',store=True,
                                      readonly=True),
        'budget_id': fields.related('budget_id_cert', 'budget_id', type='many2one',
                                     relation='budget.item', string='Partida',store=True,
                                     readonly=True),#many2one('budget.item', 'Partida Prespuestaria'),
        'budget_certificate_id':fields.related('budget_id_cert', 'certificate_id', type='many2one',
                                     relation='budget.certificate', string='Certificacion',store=True,
                                     readonly=True),
        'budget_paid': fields.boolean('Presupuesto Pagado/Recaudado ?'),
        'budget_accrued': fields.boolean('Presupuesto Devengado ?'),
        'tax_computed': fields.float('Impuestos'),
        'reposition' : fields.related('move_id', 'reposition', type='char',size=32,
                                     string='Reposicion',readonly=True),
        'migrado' : fields.boolean('Es migrado'),
        'migrado2' : fields.boolean('Migra Inicial'),
        'seq':fields.integer('Seq Impreso'),
        'state': fields.selection([('draft','Borrador'), ('valid','Validado')], 'State', readonly=True),
        'ref':fields.char('Referencia',size=15),
        }

    _defaults = dict(
        name = 'REF',
        migrado = False,
        state = 'draft',
        to_pay2 = True,
        company_id = 1,
    )
    
    PRECISION_DP = dp.get_precision('Account')


#    def write(self, cr, uid, ids,vals,context,check=False):
#        for this in self.browse(cr, uid, ids):
#            if this.migrado==True:#
#                raise osv.except_osv(('Error !'), ('No se pueden modificar asientos migrados'))
#        return super(AccountMoveLine, self).write(cr, uid, ids, vals,context,False)

    def onchange_acc(self, cr, uid, ids, account_id,certificate_id):
        account_obj = self.pool.get('account.account')
        certificate_obj = self.pool.get('budget.certificate')
        certificate_line_obj = self.pool.get('budget.certificate.line')
        res = {'value': {}}
        if not account_id:
            return res
        cuenta = account_obj.browse(cr, uid, account_id)
        partidas = []
        lines_code = []
        lines_id = []
        j = 0 
        
        if certificate_id:
            certificate = certificate_obj.browse(cr, uid, certificate_id)
            for line in certificate.line_ids:
                lines_code.append(line.budget_post.code[0:3])
                lines_id.append(line.id)
            if cuenta.budget_id:
                line_ids = certificate_line_obj.search(cr, uid, [('certificate_id','=',certificate_id),
                                                                ('budget_post','=',cuenta.budget_id.id)],limit=1)
                if line_ids:
                    res['value']['budget_id_cert'] = line_ids[0]
                else:
                    #primero si es partida de ingreso busca cp line de ingreso esle return raise que es de gasto y necesita cp line
                    #considerar ctas q no tiene relacion 1 a 1 con partida y si es 53 pasar directo el del CP ejm en impuestos.
                    if cuenta.budget_id.tipo=='i':
                        if cuenta.code[0:5]=='11398':
                            if certifi_124:
                                res['value']['budget_id_cert'] = certifi_124
                            else:
                                raise osv.except_osv('Error de usuario','Para afectar a cuentas por cobrar 11398 debe primero registrar la cuenta de 124')
                        else:
                            #ojo tomar del anio en curso 
                            date_aux = certificate.date_commited
                            certificado_ingreso_ids = certificate_obj.search(cr, uid, [('tipo_aux','=','ingreso'),
                                                                                   ('date_confirmed','>=',date_aux),('date_commited','<=',date_aux)])
                            if not certificado_ingreso_ids:
                                raise osv.except_osv('Error de usuario','No certificado de ingreso 11398')
                            line_ids = certificate_line_obj.search(cr, uid, [('budget_post','=',cuenta.budget_id.id),
                                                                             ('certificate_id','=',certificado_ingreso_ids[0])],limit=1)
                            if line_ids:
                                res['value']['budget_id_cert'] = line_ids[0]
                                if cuenta.code[0:5]=='12498':
                                    global certifi_124 
                                    certifi_124 = line_ids[0]
                            else:
                                raise osv.except_osv('Error de usuario','No certificado linea de ingreso 11398')
                    else:
                        for code_ in lines_code:
                            if cuenta.budget_id.code[0:3] == code_:#es de esas partidas pero no atada especificamente
                                res['value']['budget_id_cert'] = lines_id[j]
                            else:
                                raise osv.except_osv('Error de usuario','La cuenta %s seleccionada es de gasto y debe tener certiticado presupuestraio.'%(cuenta.code))
                            j+=1
        return res

    def _update_journal_check(self, cr, uid, journal_id, period_id, context=None):
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        jour_period_obj = self.pool.get('account.journal.period')
        cr.execute('SELECT state FROM account_journal_period WHERE journal_id = %s AND period_id = %s', (journal_id, period_id))
        result = cr.fetchall()
        for (state,) in result:
            if state == 'done':
                print "si"
#                raise osv.except_osv(_('Error !'), _('You can not add/modify entries in a closed journal.'))
        if not result:
            journal = journal_obj.browse(cr, uid, journal_id, context=context)
            period = period_obj.browse(cr, uid, period_id, context=context)
            jour_period_obj.create(cr, uid, {
                'name': (journal.code or journal.name)+':'+(period.name or ''),
                'journal_id': journal.id,
                'period_id': period.id
            })
        return True

    def _update_check(self, cr, uid, ids, context=None):
        done = {}
        for line in self.browse(cr, uid, ids, context=context):
            err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
            if line.move_id.state <> 'draft' and (not line.journal_id.entry_posted):
                raise osv.except_osv(_('Error !'), _('You can not do this modification on a confirmed entry! You can just change some non legal fields or you must unconfirm the journal entry first! \n%s') % err_msg)
#            if line.reconcile_id:
#                raise osv.except_osv(_('Error !'), _('You can not do this modification on a reconciled entry! You can just change some non legal fields or you must unreconcile first!\n%s') % err_msg)
            t = (line.journal_id.id, line.period_id.id)
            if t not in done:
                self._update_journal_check(cr, uid, line.journal_id.id, line.period_id.id, context)
                done[t] = True
        return True

    def copy_data(self, cr, uid, id, default=None, context=None):
        res = super(AccountMoveLine, self).copy_data(cr, uid, id, default, context)
        res['budget_id'] = False
        res['budget_paid'] = 0
        res['budget_accrued'] = 0
        res['reconcile_id'] = False
        res['reconcile_partial_id'] = False
        res['tax_code_id'] = False
        res['tax_amount'] = 0
        res['account_tax_id'] = False
        res['analytic_lines'] = False
        return res

    def _update_check(self, cr, uid, ids, context=None):
        done = {}
        for line in self.browse(cr, uid, ids, context=context):
            err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
            if line.move_id.state not in ('draft','anulado') and (not line.journal_id.entry_posted):
                raise osv.except_osv(_('Error !'), _('You can not do this modification on a confirmed entry! You can just change some non legal fields or you must unconfirm the journal entry first! \n%s') % err_msg)
#            if line.reconcile_id:
#                raise osv.except_osv(_('Error !'), _('You can not do this modification on a reconciled entry! You can just change some non legal fields or you must unreconcile first!\n%s') % err_msg)
            t = (line.journal_id.id, line.period_id.id)
            if t not in done:
                self._update_journal_check(cr, uid, line.journal_id.id, line.period_id.id, context)
                done[t] = True
        return True

    def create_analytic_lines(self, cr, uid, ids, context=None):
        """
        Redefinicion de creacion de lineas
        """
        val_tmp=0
        acc_ana_line_obj = self.pool.get('account.analytic.line')
        for obj_line in self.browse(cr, uid, ids, context=context):
            if obj_line.analytic_account_id:
                if not obj_line.journal_id.analytic_journal_id:
                    raise osv.except_osv(_('No Analytic Journal !'),_("You have to define an analytic journal on the '%s' journal!") % (obj_line.journal_id.name, ))
                amt = (obj_line.credit or  0.0) - (obj_line.debit or 0.0)
                if amt<0:
                    val_tmp =  obj_line.tax_computed * -1
                amt += val_tmp
                vals_lines = {
                    'name': obj_line.name,
                    'date': obj_line.date,
                    'account_id': obj_line.analytic_account_id.id,
                    'unit_amount': obj_line.quantity,
                    'product_id': obj_line.product_id and obj_line.product_id.id or False,
                    'product_uom_id': obj_line.product_uom_id and obj_line.product_uom_id.id or False,
                    'amount': amt,
                    'general_account_id': obj_line.account_id.id,
                    'journal_id': obj_line.journal_id.analytic_journal_id.id,
                    'ref': obj_line.ref,
                    'move_id': obj_line.id,
                    'user_id': uid
                }
                acc_ana_line_obj.create(cr, uid, vals_lines)
        return True    

    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if obj.move_id.state=='posted':
                print "no"
            else:
                return super(AccountMoveLine, self).unlink(cr, uid, ids, context)


    _constraints = [
        (_check_company_id, 'Company must be the same for its related account and period.', ['company_id']),
    ]
