# -*- coding: utf-8 -*-
##############################################################################
#
# MarioChogllo
# mariofchogllo@gmail.com
#
##############################################################################
from XLSWriter import XLSWriter
from datetime import datetime
from pytz import timezone
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

class spiDatosGenerales(osv.Model):
    _name = 'spi.datos.generales'
    _columns = dict(
        date = fields.date('Fecha Afectacion'),
        period_id = fields.many2one('account.period','Mes'),
        ref = fields.integer('Num.Referencia'),
        localidad = fields.char('Localidad',size=32),
        resp1 = fields.many2one('hr.employee','Responsable1'),
        cargo1 = fields.many2one('hr.job','Cargo1'),
        resp2 = fields.many2one('hr.employee','Responsable2'),
        cargo2 = fields.many2one('hr.job','Cargo2'),
        cuenta = fields.char('Cta. Banco Central',size=32),
        name = fields.char('Nombre Institucion',size=256),
    )

    def _get_name(self, cr, uid,ids, context=None):
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        return user.company_id.name

    _defaults = dict(
        date = time.strftime('%Y-%m-%d'),
        name = _get_name,
    )

spiDatosGenerales()

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
        code = fields.char('Codigo',size=20,required=True),
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

class noAcreditado(osv.TransientModel):
    _name = 'no.acreditado'
    _columns = dict(
        desc = fields.char('Detalle SPI',size=256),
        motivo = fields.char('Motivo',size=128), 
        line_id = fields.many2one('spi.line','SPI Detalle'),
    )

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = {}
        res.update({'line_id':context['active_id']})
        return res

    def no_acreditado(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        line_obj = self.pool.get('spi.line')
        for this in self.browse(cr, uid, ids):
            if this.line_id.move_id:
                move_obj.write(cr, uid, [this.line_id.move_id.id],{'is_pay':False})
                line_obj.write(cr, uid, [this.line_id.id], {'state':'Borrador'})
            else:
                if this.line_id.spi_id.tipo in ('mensual','norol'):
                    line_obj.write(cr, uid, [this.line_id.id], {'no_pagado_rol':True})
#            line_obj.unlink(cr, uid, [this.line_id.id])
        return {'type': 'ir.actions.act_window_close'}
    
noAcreditado()

class spiLine(osv.Model):
    _name = 'spi.line'

    def unlink(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if this.state in ('Generado','Confirmado','Pagado'):
                raise osv.except_osv(('Error !'), 
                                     'No se puede eliminar spi pagados')
        return super(spiLine, self).unlink(cr, uid, ids, context=context)

    def _get_detalle(self, cr, uid, ids, field_name,arg,context=None):
        res = {}
        move_obj = self.pool.get('account.move')
        aux_detalle = ''
        for this in self.browse(cr, uid, ids):
            aux_name = this.name[5:]
            move_ids = move_obj.search(cr, uid, [('name','=',aux_name)])
            if move_ids:
                move = move_obj.browse(cr, uid, move_ids[0])
                aux_detalle = move.narration
            res[this.id] = aux_detalle
        return res

    _columns = dict(
        no_pagado_rol = fields.boolean('No Acreditado'),
        pago_id = fields.related('certificate_id','payment_id',type="many2one",relation="payment.request",store=True,string="Orden de pago"),
        certificate_id = fields.related('move_id','certificate_id',type="many2one",relation="budget.certificate",store=True,string="Compromiso Presupuestario"),
        move_id = fields.many2one('account.move','Comprobante'),
        detalle = fields.function(_get_detalle, string="Detalle", store=True, type="text"), 
        state = fields.related('spi_id','state',type="char",size=12,store=True,string="Estado"),
        date = fields.related('spi_id','date_done',type="date",store=True,string="Fecha"),
        modif_valor = fields.boolean('Modificar monto manual'),
        spi_id = fields.many2one('account.spi.voucher','Spi'),
        partner_id = fields.many2one('res.partner','Beneficiario',required=True),
        amount = fields.float('Valor'),
        name = fields.char('Referencia',size=256),
        ref = fields.char('Referencia BCE',size=6),
        bank_id = fields.many2one('res.partner.bank','Cta. Banco'),
    )
spiLine()

class spiConcepto(osv.Model):
    _name = 'spi.concepto'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = ""
            name = record.code + " - " + record.name
            res.append((record.id, name))
        return res       

    _columns = dict(
        name=fields.char('Nombre',size=128,required=True),
        code=fields.char('Codigo de Ejecucion',size=10,required=True),
        partida_aux = fields.char('Partida',size=10),
    )
spiConcepto()

class spi_voucher(osv.Model):
    _name = 'account.spi.voucher'
    _order = "date desc,ref desc"

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = str(record.ref) + " - " + record.name
            res.append((record.id, name))
        return res   

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        if name:
            ids = self.search(cr, uid, [('ref', '=', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context) 

    def create(self, cr, uid, vals, context=None):
        #validar que no se duplique
        voucher_obj = self.pool.get('account.spi.voucher')
        if int(vals['ref'])>0:
            voucher_ids = voucher_obj.search(cr, uid, [('ref','=',vals['ref'])])
            if len(voucher_ids)>0:
                print "duplicado"
                #raise osv.except_osv('Error', 'No puede crear un SPI con la misma referencia.')
        return super(spi_voucher, self).create(cr, uid, vals, context=None)

    def unlink(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids):
            if this.state in ('Generado','Confirmado','Pagado'):
                raise osv.except_osv(('Error !'), 
                                     'No se puede eliminar spi generados, o pagados')
            sql_1  = """delete from spi_line where spi_id=%s"""%(this.id)
            cr.execute(sql_1)
        return super(spi_voucher, self).unlink(cr, uid, ids, context=None)

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
            'report_name': 'spi_resumen',
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
            'report_name': 'spi_detalle',
            'model': 'account.spi.voucher',
            'datas': datas,
            'nodestroy': True,                        
            }            

    def spi_draft(self, cr, uid, ids, context):
        resume_obj = self.pool.get('spi.resume')
        line_obj = self.pool.get('spi.line')
        for this in self.browse(cr, uid, ids):
            lista_v = []
            for line_spi in this.line_ids:
                line_obj.write(cr, uid, [line_spi.id],{'state':'Borrador'})
                line_obj.unlink(cr, uid, [line_spi.id])
            for line in this.resumen_ids:lista_v.append(line.id)
            resume_obj.unlink(cr, uid, lista_v)
            self.write(cr, uid, this.id, {'state':'Borrador',
                                     'total_qty':0,
                                     'total_amount':0})
        return True

    def spi_import_normal(self,cr, uid, ids, context):
        line_obj = self.pool.get('spi.line')
        partner_obj = self.pool.get('res.partner')
        journal_obj = self.pool.get('account.journal')
        no_obj = self.pool.get('hr.no.cobro')
        move_line_obj = self.pool.get('account.move.line')
        anteriores = []
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                anteriores.append(line.id)
            line_obj.unlink(cr, uid, anteriores)
            if this.tipo=='pgeneral':
                if this.line2_ids:
                    for line in this.line2_ids:
                        if line.partner_id.bank_ids: 
                            ##carga el tipo de pago: 40102 bienes y srv,40101 sueldos,40300 inversion
                            for line_asiento in line.line_id:
                                if int(str(line_asiento.account_id.code[0:1]))>=1 and  int(str(line_asiento.account_id.code[0:1]))<=3:
                                    if line_asiento.debit>0:
                                        aux_ref = 0
                                        aux_code_acc = line_asiento.account_id.code
                                        aux_code_min = aux_code_acc[0:4]
                                        if aux_code_min == '2137': #inversion
                                            aux_ref = 40300
                                            break
                                        elif aux_code_min in ('1121','1120'): #anticipos
                                            aux_ref = 40101
                                            break
                                        elif aux_code_min in ('2135'):
                                            aux_ref = 40102
                                            break
                                        else:
                                            aux_ref = 40102
                                            break
                                else:
                                    aux_ref = 40101
                            bank_id = line.partner_id.bank_ids[0].id
                            aux_name = 'PAGO ' + line.name
                            if line.narration:
                                aux_name = 'PAGO ' + line.name + ' ' + line.narration.replace('\n',' ')
                            aux_name = aux_name[0:254]
                            #validar que solo tome el valor de la cuenta de banco
                            amount_pagar = 0
                            for line_asiento in line.line_id:
                                if line_asiento.credit>0:
                                    aux_account_id = line_asiento.account_id
                                    journal_ids = journal_obj.search(cr, uid, [('type','=','bank'),('default_credit_account_id','=',line_asiento.account_id.id)])
                                    if journal_ids:
                                        if this.journal_id.id not in journal_ids:
                                            raise osv.except_osv(('Error de usuario !'),
                                                                ("La cuenta de banco no corresponde con la del comprobante"))
                                        amount_pagar = line_asiento.credit
                                        move_line_obj.write(cr, uid, line_asiento.id,{'spi_numero':this.ref})
                                        break
                            if amount_pagar <=0:
                                aux_cta_pagar = aux_account_id.code + ' - ' + aux_account_id.name
                                raise osv.except_osv(('Error Configuracion !'),
                                                     ("No existe cuenta de banco en el movimiento contable a pagar '%s' o el monto es menor a 1") % (aux_cta_pagar))
#                            move_line_obj.write(cr, uid, line_asiento.id,{'spi_numero':this.ref})
                            line_obj.create(cr, uid, {
                                'spi_id':this.id,
                                'move_id':line.id,
                                'partner_id':line.partner_id.id,
                                'amount':amount_pagar,#line.amount,
                                'name':aux_name,
                                'bank_id':bank_id,
                                'ref':aux_ref,
                            })
                        else:
                            raise osv.except_osv(('Error Configuracion !'),("No existe cuenta de banco de '%s'") % (line.partner_id.name,))
                else:
                    raise osv.except_osv(('Error de Usuario !'),("No ha seleccionado comprobantes contables para pago"))
            elif this.tipo=='norol':
                line_ids = line_obj.search(cr, uid, [('no_pagado_rol','=',True)])
                if line_ids:
                    for line_id in line_ids:
                        line_obj.write(cr, uid,line_id, {'spi_id':this.id})
            elif this.tipo=='quincena':
                if this.quincena_id:
                    for line_quincena in this.quincena_id.line_ids:
                        for line_line_quincena in line_quincena.line_ids:
                            for line_line_line in line_line_quincena.line_ids:
                                employee = line_line_line.employee_id
                                partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',employee.name)],limit=1)
                                if not partner_ids:
                                    raise osv.except_osv(('Error'), 
                                                         ('El beneficiario %s no esta en la base de proveedores debe estar registrado') % (employee.complete_name))
                                partner = partner_obj.browse(cr, uid, partner_ids[0])
                                if partner.bank_ids:
                                    bank_id = partner.bank_ids[0].id
                                    aux_name = ustr('PAGO QUINCENA' + employee.complete_name)
                                    aux_ref = '40101'
                                    line_obj.create(cr, uid, {
                                        'spi_id':this.id,
                                        'partner_id':partner.id,
                                        'amount':line_line_line.valor,
                                        'name':aux_name,
                                        'ref':aux_ref,
                                        'bank_id':bank_id,
                                    })
                                else:
                                    raise osv.except_osv(('Error'), ('El beneficiario %s no tiene cuenta de banco,registre una') % (employee.complete_name))
            elif this.tipo=='mensual':
                if this.payroll_id:
                    contratos_no = []
                    no_cobra_ids = no_obj.search(cr, uid, [])
                    if no_cobra_ids:
                        for no_cobra_id in no_cobra_ids:
                            no_cobra = no_obj.browse(cr, uid, no_cobra_id)
                            contratos_no.append(no_cobra.contract_id.id)
                    for slip in this.payroll_id.slip_ids:
                        if slip.net>0:
                            employee = slip.employee_id
                            partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',employee.name)],limit=1)
                            if not partner_ids:
                                raise osv.except_osv(('Error'), ('El beneficiario %s no esta en la base de proveedores debe estar registrado') % (employee.complete_name))
                            partner = partner_obj.browse(cr, uid, partner_ids[0])
                            if partner.bank_ids:
                                bank_id = partner.bank_ids[0].id
                                aux_name = ustr('PAGO MENSUAL ' + employee.complete_name)
                                aux_ref = '40101'
                                if slip.net<0:
                                    raise osv.except_osv(('Error'), ('No se puede pagar un rol negativo, verificar rol de %s ') % (partner.name))
                                if slip.contract_id.id in contratos_no:
                                    line_obj.create(cr, uid, {
                                        'no_pagado_rol':True,
                                        'partner_id':partner.id,
                                        'amount':slip.net,
                                        'name':aux_name,
                                        'ref':aux_ref,
                                        'bank_id':bank_id,
                                    })
                                else:
                                    line_obj.create(cr, uid, {
                                        'spi_id':this.id,
                                        'partner_id':partner.id,
                                        'amount':slip.net,
                                        'name':aux_name,
                                        'ref':aux_ref,
                                        'bank_id':bank_id,
                                    })
                            else:
                                if not (slip.contract_id.id in contratos_no):
                                    raise osv.except_osv(('Error'), ('El beneficiario %s no tiene cuenta de banco,registre una') % (employee.complete_name))
            elif this.tipo=='dec3':
                if this.dec3_id:
                    for decimo in this.dec3_id.line_ids:
                        employee = decimo.contract_id.employee_id
                        partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',employee.name)],limit=1)
                        if not partner_ids:
                            raise osv.except_osv(('Error'), ('El beneficiario %s no esta en la base de proveedores debe estar registrado') % (employee.complete_name))
                        partner = partner_obj.browse(cr, uid, partner_ids[0])
                        if partner.bank_ids:
                            bank_id = partner.bank_ids[0].id
                            aux_name = ustr('PAGO DECIMO TERCERO ' + employee.complete_name)
                            aux_ref = '40101'
                            if decimo.recibir<0:
                                raise osv.except_osv(('Error'), ('No se puede pagar decimo negativo, verificar rol de %s ') % (partner.name))
                            line_obj.create(cr, uid, {
                                'spi_id':this.id,
                                'partner_id':partner.id,
                                'amount':decimo.recibir,
                                'name':aux_name,
                                'ref':aux_ref,
                                'bank_id':bank_id,
                            })
                        else:
                            raise osv.except_osv(('Error'), ('El beneficiario %s no tiene cuenta de banco,registre una') % (employee.complete_name))
            elif this.tipo=='dec4':
                if this.dec4_id:
                    for decimo in this.dec4_id.line_ids:
                        if decimo.recibir>0:
                            employee = decimo.contract_id.employee_id
                            partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',employee.name)],limit=1)
                            if not partner_ids:
                                raise osv.except_osv(('Error'), ('El beneficiario %s no esta en la base de proveedores debe estar registrado') % (employee.complete_name))
                            partner = partner_obj.browse(cr, uid, partner_ids[0])
                            if partner.bank_ids:
                                bank_id = partner.bank_ids[0].id
                                aux_name = ustr('PAGO DECIMO CUARTO ' + employee.complete_name)
                                aux_ref = '40101'
                                if decimo.recibir<0:
                                    raise osv.except_osv(('Error'), ('No se puede pagar decimo negativo, verificar rol de %s ') % (partner.name))
                                line_obj.create(cr, uid, {
                                    'spi_id':this.id,
                                    'partner_id':partner.id,
                                    'amount':decimo.recibir,
                                    'name':aux_name,
                                    'ref':aux_ref,
                                    'bank_id':bank_id,
                                })
                            else:
                                raise osv.except_osv(('Error'), ('El beneficiario %s no tiene cuenta de banco,registre una') % (employee.complete_name))
            elif this.tipo=='varios':
                if this.varios_id:
                    for line in this.varios_id.line_ids:
                        partner = line.name
                        if not partner.bank_ids:
                            raise osv.except_osv(('Error'), ('El beneficiario %s no tiene cuenta de banco,registre una') % (partner.name))
                        bank_id = partner.bank_ids[0].id
                        aux_name = ustr('PAGO: ' + this.varios_id.name)
                        aux_ref = '40101'
                        line_obj.create(cr, uid, {
                            'spi_id':this.id,
                            'partner_id':partner.id,
                            'amount':line.valor,
                            'name':aux_name,
                            'ref':aux_ref,
                            'bank_id':bank_id,
                        })
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

    def _spi_generate_xls(self, cr, uid, ids, context):
        move_obj = self.pool.get('account.move')
        writer = XLSWriter()
        writer.append(["CEDULA","REFERENCIA", "NOMBRE","INST.FINANCIERA","CUENTA BENEFICIARIO","TIPO CUENTA","VALOR","CONCEPTO","DETALLE"])
        for this in self.browse(cr, uid, ids):
            j = 0
            for line in this.line_ids:
                j += 1
                cta_aux = line.bank_id
                #tomar en cuenta si es cedula
                cedula = line.partner_id.ced_ruc
                if line.partner_id.pagar_spi:
                    cedula = line.partner_id.ced_ruc[0:10]
                referencia = this.ref
                #nombre maximo 30 caracteres
                nombre_aux = line.partner_id.name
                nombre = nombre_aux[0:28]
                inst = int(cta_aux.bank.bic)
                cuenta = int(cta_aux.acc_number)
                tipo = 1
                if cta_aux.type_cta=='aho':
                    tipo = 2
                valor = line.amount
                concepto = line.ref
                detalle = line.name
                writer.append([cedula,referencia,nombre,inst,cuenta,tipo,valor,concepto,detalle]) 
#            for line in this.line2_ids:
#                move_obj.write(cr, uid, [line.id],{
#                    'state':'payprocess',
#                })
            n_archivo = ("SPI" + ".xls").replace('/','')
            writer.save("SPIPAGO.xls")
            out = open("SPIPAGO.xls","rb").read().encode("base64")
            self.write(cr, uid, ids, {'archivoxls': out, 'file_namexls': n_archivo,'state':'Generado',})
        return True

    def spi_realizado(self, cr, uid, ids, context):
        line_obj = self.pool.get('spi.line')
        contract_obj = self.pool.get('hr.contract')
        run_obj = self.pool.get('hr.payslip.run')
        dec3_obj = self.pool.get('hr.decimo.tercero')
        dec4_obj = self.pool.get('hr.decimo.cuarto')
        payslip_line_obj = self.pool.get('hr.payslip.line')
        rule_obj = self.pool.get('hr.salary.rule')
        move_obj = self.pool.get('account.move')
        mail_message = self.pool.get('mail.message')
        parameter_obj = self.pool.get('ir.config_parameter')
        user_obj = self.pool.get('res.users')
        ####por acabar
        user = user_obj.browse(cr, uid, uid)
        aux_name = ''
        email_from_ids = parameter_obj.search(cr, uid, [('key','=','email_fromtes')],limit=1)
        if email_from_ids:
            email_from = parameter_obj.browse(cr, uid, email_from_ids[0]).value
        #else:
        #    raise osv.except_osv('Error','No ha contratado esta funcionalidad comuniquese con el administrador del sistema.')
        for this in self.browse(cr, uid, ids):
            for line in this.line_ids:
                if not line.move_id:
                    aux_name = line.name[5:]
                    move_ids = move_obj.search(cr, uid, [('name','=',aux_name)])
                    if move_ids:
                        move = move_obj.browse(cr, uid, move_ids[0])
                        if move.certificate_id:
                            if move.certificate_id.payment_id:
                                line_obj.write(cr, uid, line.id,{
                                    'move_id':move_ids[0],
                                    'certificate_id':move.certificate_id.id,
                                    'pago_id':move.certificate_id.payment_id.id,
                                })
                            else:
                                line_obj.write(cr, uid, line.id,{
                                    'move_id':move_ids[0],
                                    'certificate_id':move.certificate_id.id,
                                })
                        else:
                            line_obj.write(cr, uid, line.id,{
                                'move_id':move_ids[0],
                            })
                if this.tipo=='norol':
                    line_obj.write(cr, uid, line.id,{
                        'state':'Pagado',
                        'no_pagado_rol':False,
                    })
                else:
                    line_obj.write(cr, uid, line.id,{
                        'state':'Pagado',
                    })
                    #
                    if line.move_id and email_from_ids:
                        if line.partner_id.email:
                            razonSocial = user.company_id.name
                            aux_name = line.partner_id.name
                            aux_concepto = line.move_id.narration
                            msg = " Estimado  %s, \n\n Su pago por concepto de %s ha sido acreditado en su cuenta\n Saludos Cordiales"  %(aux_name,aux_concepto)
                            vals_msg = {
                                'subject': 'Notificacion de Tesoreria - ' + razonSocial,
                                'body_text': msg,
                                'email_from': email_from,
                                'email_bcc' : line.partner_id.email,
                                'email_to': line.partner_id.email,
                                'state': 'outgoing',
                            }
                            email_msg_id = mail_message.create(cr, uid, vals_msg, context)
                            try:
                                mail_message.send(cr, uid, [email_msg_id])
                            except:
                                pass
            if this.line2_ids:
                for line_move in this.line2_ids:
                    move_obj.write(cr, uid, [line_move.id],{'is_pay':True})
            if this.tipo=='mensual':
                run_obj.pagado_payslip_run(cr, uid, [this.payroll_id.id])
                rule_ids = rule_obj.search(cr, uid, [('code','in',('DEC3','DEC4','dec3','dec4'))])
                if rule_ids:
                    for rol in this.payroll_id.slip_ids:
                        payslip_line_ids = payslip_line_obj.search(cr, uid, [('contract_id','=',rol.contract_id.id),
                                                                             ('salary_rule_id','in',rule_ids),('slip_id','=',rol.id)])
            elif this.tipo=='dec3':
                dec3_obj.pagado_dec3(cr, uid, [this.dec3_id.id])
            elif this.tipo=='dec4':
                dec4_obj.pagado_dec4(cr, uid, [this.dec4_id.id])
        ####
        self.write(cr, uid, ids, {'state':'Pagado'})
        return True

    def spi_generate_proveedor(self, cr, uid, ids, context):
        comp_obj = self.pool.get('res.company')
        partner_obj = self.pool.get('res.partner')
        line_obj = self.pool.get('spi.resume')
        bank_obj = self.pool.get('res.bank')
        voucher_obj = self.pool.get('account.voucher')
        spi_obj = self.pool.get('account.spi.voucher')
        company_id = comp_obj.search(cr, uid, [],limit=1)[0]
        company = comp_obj.browse(cr, uid, company_id)
        for this in self.browse(cr, uid, ids):
            j = 0
            bufp = StringIO.StringIO()
            fechap = time.strftime('%d/%m/%Y')
            if not this.journal_id.cta_number:
                raise osv.except_osv(('No se puede generar el archivo error !'), 
                                     'No existe numero de cuenta en el diario seleccionado')
            totp = 0
            for line in this.line_ids:
               totp+=line.amount 
            num_cta_empresa = "%08d"%(int(this.journal_id.cta_number ))
            aux_uno = '1'
            cabecera_proveedor = fechap + '\t' + str(num_cta_empresa) + '\t' + company.name[0:28] + '\r\n'
            cabecera_proveedor = unicodedata.normalize('NFKD',cabecera_proveedor).encode('ascii','ignore')
            bufp.write(upper(cabecera_proveedor))
            #==========================
            id_partner = {}
            data2 = {}
            data3 = {}
            data4 = {}
            lines = this.line_ids
            tot_amount = l = 0
            if len(this.line_ids)>0:
                for line in lines:
                    j += 1
                    if not data2.get(line.partner_id.id):
                        data2.update({line.partner_id.id:0})
                    data2[line.partner_id.id] += line.amount
                    tot_amount += line.amount
                    #cambiado todo para varias cuentas de banco
                    if not data3.get(line.bank_id.bank.id):
                        data3.update({line.bank_id.bank.id:0})
                        data4.update({line.bank_id.bank.id:0})
                    l += 1
                    data3[line.bank_id.bank.id] += line.amount
                    data4[line.bank_id.bank.id] = l
            else:
                raise osv.except_osv(('No se puede generar el archivo SPI !'), 
                                     'No existen lineas de pago seleccionadas')    
            if len(data2) < 1:
                raise osv.except_osv(('No se puede generar el archivo SPI !'), 
                                     'No existen lineas de pago autorizadas por el Director Financiero')
            for line in lines:
#            for p,v in data2.items():
                partner = line.partner_id#partner_obj.browse(cr, uid, p)
                partner_name = partner.name
                val_1="%.2f"%(line.amount) #v
                val_2=val_1.replace(".",'')
                str_val_aux=str("%09d"%int(val_2))
                str_val = str_val_aux[:-2] + '.' + str_val_aux[-2:]
                if len(partner_name)<40:
                    partner_cut=partner_name.ljust(28,' ')
                else:
                    partner_cut=partner_name[0:28]
                if len(partner.bank_ids)<1:
                    raise osv.except_osv(('No se puede generar el archivo error !'), 
                                         'No existe cuenta definida para el proveedor')
                cuenta = line.bank_id#partner.bank_ids[0]
                numero_cta = int(cuenta.acc_number)
                n_lleno="%018d"%numero_cta
                bank_code = "%08d"%(int(cuenta.bank.bic))
                tipo_cta = '2'
                if cuenta.type_cta == 'aho':
                    tipo_cta = '1'
                aux_cedula = partner.ced_ruc
                if partner.pagar_spi:
                    aux_cedula = aux_cedula[0:10]
                detallep = aux_cedula + '\t' + partner.name[0:28] + '\t' + str(n_lleno) + '\t' + str_val + '\t' + str(bank_code) + '\t' + tipo_cta +'\r\n'
                detallep = unicodedata.normalize('NFKD',detallep).encode('ascii','ignore')
                bufp.write(upper(detallep))
            namep = "%s.TXT" % ("Proveedores-"+str(this.ref_int))
            outp = base64.encodestring(bufp.getvalue())
            self.write(cr, uid, ids, {'archivotxt': outp, 'file_nametxt': namep})
            bufp.close()
            return True        

    def spi_generate(self, cr, uid, ids, context):
        comp_obj = self.pool.get('res.company')
        partner_obj = self.pool.get('res.partner')
        line_obj = self.pool.get('spi.resume')
        bank_obj = self.pool.get('res.bank')
        voucher_obj = self.pool.get('account.voucher')
        spi_obj = self.pool.get('account.spi.voucher')
        company_id = comp_obj.search(cr, uid, [],limit=1)[0]
        company = comp_obj.browse(cr, uid, company_id)
        for this in self.browse(cr, uid, ids):
            spi_obj.spi_generate_proveedor( cr, uid, ids,context)
            obj_sequence = self.pool.get('ir.sequence')
            aux_ref_interna = obj_sequence.get(cr, uid, 'account.spi.voucher')
            if this.ref_int<=0:
                self.write(cr, uid, ids, {
                    'ref_int':aux_ref_interna,
                })
            j = 0
            buf = StringIO.StringIO()
            if this.date_aux:
                fecha_aux = str(this.date_aux)
                fecha = fecha_aux[8:10] + '/' + fecha_aux[5:7] + '/' + fecha_aux[0:4] + ' ' + fecha_aux[11:]
            else:
                fecha = time.strftime('%d/%m/%Y %H:%M:%S')
            if not this.journal_id.cta_number:
                raise osv.except_osv(('No se puede generar el archivo error !'), 
                                     'No existe numero de cuenta en el diario seleccionado')
            tot = 0
            for line in this.line_ids:
               tot+=line.amount 
            num_cta_empresa = this.journal_id.cta_number 
            aux_m  =  this.date_done[5:7] + '/' + this.date_done[0:4]
            aux_uno = '1'
#            cabecera = fecha + ',' +str(this.ref).zfill(10)+','+str(len(this.line_ids))+","+aux_uno+','+("%.2f"%(tot))+","+str(this.ref_int)+","+num_cta_empresa + ','+ num_cta_empresa+','+ company.name +','+company.name+','+aux_m+'\r\n'
            #el tamanio debe ser el len del generado
            total_partners = 0
            partners = []
            for line in this.line_ids:
                if not line.partner_id.id in partners:
                    total_partners += 1
                    partners.append(line.partner_id.id)
#OJO ANTES            cabecera = fecha + ',' +str(this.ref).zfill(10)+','+str(total_partners).zfill(6)+","+aux_uno.zfill(2)+','+("%.2f"%(tot)).zfill(20)+","+str(this.ref_int).zfill(22)+","+num_cta_empresa.zfill(8) + ','+ num_cta_empresa.zfill(8)+','+ company.name[0:28] +','+company.name[0:28]+','+aux_m+'\r\n'
            cabecera = fecha + ',' +str(this.ref).zfill(10)+','+str(len(this.line_ids)).zfill(6)+","+aux_uno.zfill(2)+','+("%.2f"%(tot)).zfill(20)+","+str(this.ref_int).zfill(22)+","+num_cta_empresa.zfill(8) + ','+ num_cta_empresa.zfill(8)+','+ company.name[0:28] +','+company.name[0:28]+','+aux_m+'\r\n'
            cabecera = unicodedata.normalize('NFKD',cabecera).encode('ascii','ignore')
            buf.write(upper(cabecera))
            id_partner = {}
            data2 = {}
            data3 = {}
            data4 = {}
            data5 = {}
            lines = this.line_ids
            tot_amount = l = 0
            if len(this.line_ids)>0:
#                lines.sort(key=lambda x: x.state)
                for line in lines:
                    j += 1
#                    data2.update({line.partner_id.id:line.amount})
                    if not data2.get(line.partner_id.id):
                        data2.update({line.partner_id.id:0})
                        data5.update({line.partner_id.id:line.name})
                    data2[line.partner_id.id] += line.amount
                    tot_amount += line.amount
                    if not data3.get(line.bank_id.bank.id):
                        data3.update({line.bank_id.bank.id:0})
                        data4.update({line.bank_id.bank.id:0})  #0
                    l += 1
                    data3[line.bank_id.bank.id] += line.amount
                    data4[line.bank_id.bank.id] = data4[line.bank_id.bank.id]+1
                    #que no agrupe por proveedor sino por cada linea mande una al archivo de texto
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
            for line in lines:
                partner = line.partner_id
                partner_name = partner.name
                val_1="%.2f"%(line.amount)
                if len(partner_name)<40:
                    partner_cut=partner_name.ljust(28,' ')
                else:
                    partner_cut=partner_name[0:28]
                if len(partner.bank_ids)<1:
                    raise osv.except_osv(('No se puede generar el archivo error !'), 
                                         'No existe cuenta definida para el proveedor')
                cuenta = line.bank_id#partner.bank_ids[0]
                numero_cta = int(cuenta.acc_number)
                n_lleno=str("%018d"%numero_cta)
                val_2=val_1.replace(".",'')
#                str_val_aux=str(int(val_2))#"%09d"%int(val_2)
#                str_val = str_val_aux[:-2] + '.' + str_val_aux[-2:]
                str_val_aux=str("%09d"%int(val_2))
                str_val = str_val_aux[0:7] + '.' + str_val_aux[7:9]
                bank_code = "%08d"%int(cuenta.bank.bic)
                tipo_cta = '1'
                if cuenta.type_cta == 'aho':
                    tipo_cta = '2'
#                detalle = str(this.ref)+','+str_val+','+line.ref+','+str(bank_code)+','+ str(numero_cta) +','+partner.name + ',' + line.name + ',' + partner.ced_ruc +'\r\n'
                aux_cedula = partner.ced_ruc
                if partner.pagar_spi:
                    aux_cedula = aux_cedula[0:10]
                aux_descripcion = line.name#data5[partner.id]
                aux_desc_sin = aux_descripcion.replace(',','')
                aux_desc_sin = aux_desc_sin.replace('.','')
                detalle = str(this.ref).zfill(10)+','+str_val+','+line.ref.zfill(6)+','+ str(bank_code)+','+ n_lleno +','+ tipo_cta.zfill(2) +','+partner.name[0:28] + ',' + aux_desc_sin[0:74] + ',' + aux_cedula +'\r\n'
                detalle = unicodedata.normalize('NFKD',detalle).encode('ascii','ignore')
                buf.write(upper(detalle))                
#            for p,v in data2.items():
#                partner = partner_obj.browse(cr, uid, p)
#                partner_name = partner.name
#                val_1="%.2f"%(v)
#                if len(partner_name)<40:
#                    partner_cut=partner_name.ljust(28,' ')
#                else:
#                    partner_cut=partner_name[0:28]
#                if len(partner.bank_ids)<1:
#                    raise osv.except_osv(('No se puede generar el archivo error !'), 
#                                         'No existe cuenta definida para el proveedor')
#                cuenta = partner.bank_ids[0]
#                numero_cta = int(cuenta.acc_number)
#                n_lleno=str("%018d"%numero_cta)
#                val_2=val_1.replace(".",'')
##                str_val_aux=str(int(val_2))#"%09d"%int(val_2)
##                str_val = str_val_aux[:-2] + '.' + str_val_aux[-2:]
#                str_val_aux=str("%09d"%int(val_2))
#                str_val = str_val_aux[0:7] + '.' + str_val_aux[7:9]
#                bank_code = "%08d"%int(cuenta.bank.bic)
#                tipo_cta = '1'
#                if cuenta.type_cta == 'aho':
#                    tipo_cta = '2'
##                detalle = str(this.ref)+','+str_val+','+line.ref+','+str(bank_code)+','+ str(numero_cta) +','+partner.name + ',' + line.name + ',' + partner.ced_ruc +'\r\n'
#                aux_cedula = partner.ced_ruc
#                if partner.pagar_spi:
#                    aux_cedula = aux_cedula[0:10]
#                aux_descripcion = data5[partner.id]
#                aux_desc_sin = aux_descripcion.replace(',','')
#                aux_desc_sin = aux_desc_sin.replace('.','')
#                detalle = str(this.ref).zfill(10)+','+str_val+','+line.ref.zfill(6)+','+ str(bank_code)+','+ n_lleno +','+ tipo_cta.zfill(2) +','+partner.name[0:28] + ',' + aux_desc_sin[0:74] + ',' + aux_cedula +'\r\n'
#                detalle = unicodedata.normalize('NFKD',detalle).encode('ascii','ignore')
#                buf.write(upper(detalle))
            name1 = "%s.TXT" % ("SPI-SP")
            name = "%s.TXT" % ("SPI-SP_LB")
            out1 = base64.encodestring(buf.getvalue())
            #buf.close()
#            self.write(cr, uid, ids, {'archivotxt': out1, 'file_nametxt': name1})
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
            zf_name = 'spi-sp %s.zip' % time.strftime('%Y-%m-%d')
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
            buf.close()
            self.write(cr, uid, ids, {'dig':digest1,'archivo': out, 'file_name': zf_name,
                                      'total_amount':tot_amount,'state':'Generado',
                                  })
            self._spi_generate_xls(cr, uid, ids,context)
            #pasa directo a pagado
            #self.spi_realizado(cr, uid, ids,context)
            return True


    def ssp_generate_proveedor(self, cr, uid, ids, context):
        comp_obj = self.pool.get('res.company')
        partner_obj = self.pool.get('res.partner')
        line_obj = self.pool.get('spi.resume')
        bank_obj = self.pool.get('res.bank')
        voucher_obj = self.pool.get('account.voucher')
        spi_obj = self.pool.get('account.spi.voucher')
        company_id = comp_obj.search(cr, uid, [],limit=1)[0]
        company = comp_obj.browse(cr, uid, company_id)
        for this in self.browse(cr, uid, ids):
            j = 0
            bufp = StringIO.StringIO()
            fechap = time.strftime('%d/%m/%Y')
            if not this.journal_id.cta_number:
                raise osv.except_osv(('No se puede generar el archivo error !'), 
                                     'No existe numero de cuenta en el diario seleccionado')
            totp = 0
            for line in this.line_ids:
               totp+=line.amount 
            num_cta_empresa = "%08d"%(int(this.journal_id.cta_number ))
            aux_uno = '1'
            cabecera_proveedor = fechap + '\t' + str(num_cta_empresa) + '\t' + company.name[0:28] + '\r\n'
            cabecera_proveedor = unicodedata.normalize('NFKD',cabecera_proveedor).encode('ascii','ignore')
            bufp.write(upper(cabecera_proveedor))
            #==========================
            id_partner = {}
            data2 = {}
            data3 = {}
            data4 = {}
            lines = this.line_ids
            tot_amount = l = 0
            if len(this.line_ids)>0:
                for line in lines:
                    j += 1
                    if not data2.get(line.partner_id.id):
                        data2.update({line.partner_id.id:0})
                    data2[line.partner_id.id] += line.amount
                    tot_amount += line.amount
                    #cambiado todo para varias cuentas de banco
                    if not data3.get(line.bank_id.bank.id):
                        data3.update({line.bank_id.bank.id:0})
                        data4.update({line.bank_id.bank.id:0})
                    l += 1
                    data3[line.bank_id.bank.id] += line.amount
                    data4[line.bank_id.bank.id] = l
            else:
                raise osv.except_osv(('No se puede generar el archivo SPI !'), 
                                     'No existen lineas de pago seleccionadas')    
            if len(data2) < 1:
                raise osv.except_osv(('No se puede generar el archivo SPI !'), 
                                     'No existen lineas de pago autorizadas por el Director Financiero')
            for line in lines:
#            for p,v in data2.items():
                partner = line.partner_id#partner_obj.browse(cr, uid, p)
                partner_name = partner.name
                val_1="%.2f"%(line.amount) #v
                val_2=val_1.replace(".",'')
                str_val_aux=str(int(val_2))#str("%09d"%int(val_2))
                str_val = str_val_aux[:-2] + '.' + str_val_aux[-2:]
                if len(partner_name)<40:
                    partner_cut=partner_name.ljust(28,' ')
                else:
                    partner_cut=partner_name[0:28]
                if len(partner.bank_ids)<1:
                    raise osv.except_osv(('No se puede generar el archivo error !'), 
                                         'No existe cuenta definida para el proveedor')
                cuenta = line.bank_id#partner.bank_ids[0]
                numero_cta = int(cuenta.acc_number)
                n_lleno=numero_cta#"%018d"%numero_cta
                bank_code = (int(cuenta.bank.bic))#"%08d"%(int(cuenta.bank.bic))
                tipo_cta = '2'
                if cuenta.type_cta == 'aho':
                    tipo_cta = '1'
                aux_cedula = partner.ced_ruc
                if partner.pagar_spi:
                    aux_cedula = aux_cedula[0:10]
                detallep = aux_cedula + '\t' + partner.name[0:28] + '\t' + str(n_lleno) + '\t' + str_val + '\t' + str(bank_code) + '\t' + tipo_cta +'\r\n'
                detallep = unicodedata.normalize('NFKD',detallep).encode('ascii','ignore')
                bufp.write(upper(detallep))
            #import pdb
            #pdb.set_trace()
            namep = "%s.txt" % ("proveedores-"+str(this.ref_int))
            outp = base64.encodestring(bufp.getvalue())
            file_spip = open(namep, 'w')
            file_spip.write(bufp.getvalue())
            file_spip.close()
            #zip file
            zf_namep = "%s.zip" % ("proveedores-"+str(this.ref_int))
            zfp = zipfile.ZipFile(zf_namep, mode='w')
            zfp_buf = StringIO.StringIO()
            try:
                zfp.write(namep)
            finally:
                zfp.close()
            zfp_tmp = open(zf_namep, 'rb')
            zfp_buf.write(zfp_tmp.read())
            out_zp = base64.encodestring(zfp_buf.getvalue())
            self.write(cr, uid, ids, {'archivotxt': outp, 'file_nametxt': namep,'archivozp':out_zp,'file_namezp':zf_namep})
            bufp.close()
            zfp_buf.close()
            return True            
        

    def ssp_generate(self, cr, uid, ids, context):
        comp_obj = self.pool.get('res.company')
        partner_obj = self.pool.get('res.partner')
        line_obj = self.pool.get('spi.resume')
        bank_obj = self.pool.get('res.bank')
        voucher_obj = self.pool.get('account.voucher')
        spi_obj = self.pool.get('account.spi.voucher')
        company_id = comp_obj.search(cr, uid, [],limit=1)[0]
        company = comp_obj.browse(cr, uid, company_id)
        for this in self.browse(cr, uid, ids):
            spi_obj.ssp_generate_proveedor( cr, uid, ids,context)
            obj_sequence = self.pool.get('ir.sequence')
            aux_ref_interna = obj_sequence.get(cr, uid, 'account.spi.voucher')
            if this.ref_int<=0:
                self.write(cr, uid, ids, {
                    'ref_int':aux_ref_interna,
                })
            j = 0
            buf = StringIO.StringIO()
            if this.date_aux:
                fecha_aux = str(this.date_aux)
                fecha = fecha_aux[8:10] + '/' + fecha_aux[5:7] + '/' + fecha_aux[0:4] + ' ' + fecha_aux[11:]
            else:
                fecha = time.strftime('%d/%m/%Y %H:%M:%S')
            if not this.journal_id.cta_number:
                raise osv.except_osv(('No se puede generar el archivo error !'), 
                                     'No existe numero de cuenta en el diario seleccionado')
            tot = 0
            for line in this.line_ids:
               tot+=line.amount 
            num_cta_empresa = this.journal_id.cta_number 
            aux_m  =  this.date_done[5:7] + '/' + this.date_done[0:4]
            aux_uno = '1'
#            cabecera = fecha + ',' +str(this.ref).zfill(10)+','+str(len(this.line_ids))+","+aux_uno+','+("%.2f"%(tot))+","+str(this.ref_int)+","+num_cta_empresa + ','+ num_cta_empresa+','+ company.name +','+company.name+','+aux_m+'\r\n'
            #el tamanio debe ser el len del generado
            total_partners = 0
            partners = []
            for line in this.line_ids:
                if not line.partner_id.id in partners:
                    total_partners += 1
                    partners.append(line.partner_id.id)
#OJO ANTES            cabecera = fecha + ',' +str(this.ref).zfill(10)+','+str(total_partners).zfill(6)+","+aux_uno.zfill(2)+','+("%.2f"%(tot)).zfill(20)+","+str(this.ref_int).zfill(22)+","+num_cta_empresa.zfill(8) + ','+ num_cta_empresa.zfill(8)+','+ company.name[0:28] +','+company.name[0:28]+','+aux_m+'\r\n'
            cabecera = fecha + ',' +str(this.ref)+','+str(len(this.line_ids))+","+aux_uno+','+("%.2f"%(tot))+","+str(this.ref_int)+","+num_cta_empresa + ','+ num_cta_empresa+','+ company.name[0:28] +','+company.name[0:28]+','+aux_m+'\r\n'
            cabecera = unicodedata.normalize('NFKD',cabecera).encode('ascii','ignore')
            buf.write(upper(cabecera))
            id_partner = {}
            data2 = {}
            data3 = {}
            data4 = {}
            data5 = {}
            lines = this.line_ids
            tot_amount = l = 0
            if len(this.line_ids)>0:
#                lines.sort(key=lambda x: x.state)
                for line in lines:
                    j += 1
#                    data2.update({line.partner_id.id:line.amount})
                    if not data2.get(line.partner_id.id):
                        data2.update({line.partner_id.id:0})
                        data5.update({line.partner_id.id:line.name})
                    data2[line.partner_id.id] += line.amount
                    tot_amount += line.amount
                    if not data3.get(line.bank_id.bank.id):
                        data3.update({line.bank_id.bank.id:0})
                        data4.update({line.bank_id.bank.id:0})  #0
                    l += 1
                    data3[line.bank_id.bank.id] += line.amount
                    data4[line.bank_id.bank.id] = data4[line.bank_id.bank.id]+1
                    #que no agrupe por proveedor sino por cada linea mande una al archivo de texto
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
            for line in lines:
                partner = line.partner_id
                partner_name = partner.name
                val_1="%.2f"%(line.amount)
                if len(partner_name)<40:
                    partner_cut=partner_name.ljust(28,' ')
                else:
                    partner_cut=partner_name[0:28]
                if len(partner.bank_ids)<1:
                    raise osv.except_osv(('No se puede generar el archivo error !'), 
                                         'No existe cuenta definida para el proveedor')
                cuenta = line.bank_id#partner.bank_ids[0]
                numero_cta = int(cuenta.acc_number)
                n_lleno=str(numero_cta)#str("%018d"%numero_cta)
                val_2=val_1.replace(".",'')
#                str_val_aux=str(int(val_2))#"%09d"%int(val_2)
#                str_val = str_val_aux[:-2] + '.' + str_val_aux[-2:]
                str_val_aux=str(int(val_2))#str("%09d"%int(val_2))
                #import pdb
                #pdb.set_trace()
                str_val = str(val_1)#str_val_aux[0:7] + '.' + str_val_aux[7:9]
                bank_code = int(cuenta.bank.bic)#"%08d"%int(cuenta.bank.bic)
                tipo_cta = '1'
                if cuenta.type_cta == 'aho':
                    tipo_cta = '2'
#                detalle = str(this.ref)+','+str_val+','+line.ref+','+str(bank_code)+','+ str(numero_cta) +','+partner.name + ',' + line.name + ',' + partner.ced_ruc +'\r\n'
                aux_cedula = partner.ced_ruc
                if partner.pagar_spi:
                    aux_cedula = aux_cedula[0:10]
                aux_descripcion = line.name#data5[partner.id]
                aux_desc_sin = aux_descripcion.replace(',','')
                aux_desc_sin = aux_desc_sin.replace('.','')
                detalle = str(this.ref)+','+str_val+','+line.ref+','+ str(bank_code)+','+ n_lleno +','+ tipo_cta +','+partner.name[0:28] + ',' + aux_desc_sin[0:74] + ',' + aux_cedula +'\r\n'
                detalle = unicodedata.normalize('NFKD',detalle).encode('ascii','ignore')
                buf.write(upper(detalle))                
            name1 = "%s.TXT" % ("SSP-SP")
            name = "%s.TXT" % ("SSP-SP_LB")
            out1 = base64.encodestring(buf.getvalue())
            #buf.close()
#            self.write(cr, uid, ids, {'archivotxt': out1, 'file_nametxt': name1})
            digest_name = 'SSP-SP-LB.md5'
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
            zf_name = 'ssp-sp %s.zip' % time.strftime('%Y-%m-%d')
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
            buf.close()
            self.write(cr, uid, ids, {'dig':digest1,'archivo': out, 'file_name': zf_name,
                                      'total_amount':tot_amount,'state':'Generado',
                                  })
            self._spi_generate_xls(cr, uid, ids,context)
            #pasa directo a pagado
            #self.spi_realizado(cr, uid, ids,context)
            return True

    def _compute_total(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            aux_total = 0
            for line in obj.line_ids:
                aux_total += line.amount
        result[obj.id] = aux_total
        return result
        

    _columns = dict(
        total = fields.function(_compute_total, method=True, store=True, string='TOTAL'),
        date_aux = fields.datetime('Otra Fecha Pago'),
        dec3_id = fields.many2one('hr.decimo.tercero','Decimo Tercero'),
        dec4_id = fields.many2one('hr.decimo.cuarto','Decimo Cuarto'),
        dig = fields.char('dig',size=256),
        total_qty = fields.integer('Total pagos'),
        total_amount = fields.float('Total monto'),
        resumen_ids = fields.one2many('spi.resume','spi_id','Resumen'),
        ref_int = fields.integer('Referencia Interna'),
        ref = fields.integer('Referencia SPI'),
        name = fields.char('Descripcion',size=256),
        date = fields.date('Fecha Creacion'),
        date_done = fields.date('Fecha Pago'),
        journal_id = fields.many2one('account.journal','Banco'),
        line2_ids = fields.many2many('account.move','spi_move_rel','spi_id','move_id','Agregar Pagos'),
        line_ids = fields.one2many('spi.line','spi_id','SPI'),
        tipo = fields.selection([('pgeneral','Pagos Generales'),('quincena','Nomina Quincena'),('mensual','Nomina Mensual/Semanal'),
                                 ('varios','Varios TTHH'),('dec3','Decimo Tercero'),('dec4','Decimo Cuarto'),('norol','No Acreditado Roles')],'Tipo',required=True),
#        line_ids = fields.many2many('account.move','spi_voucher_rel','spi_id','account_id','Detalle Pagos'),
#        line_ids = fields.many2many('account.voucher','spi_voucher_rel','spi_id','voucher_id','Detalle Pagos'),
        varios_id = fields.many2one('hr.varios','Varios'),
        quincena_id = fields.many2one('hr.quincena','Rol Quincena'),
        payroll_id = fields.many2one('hr.payslip.run','Rol Mensual'),
        state = fields.selection([('Borrador','Borrador'),('Confirmado','Confirmado'),('Generado','Generado'),('Pagado','Pagado')],'Estado'),
        archivo = fields.binary('Archivo SPI/SSP ZIP',readonly=True),
        file_name = fields.char('N. archivo', size=32),
        archivoxls = fields.binary('Archivo SPI xls',readonly=True),
        file_namexls = fields.char('N. archivo xls', size=32),
        archivotxt = fields.binary('Archivo Txt Proveedores',readonly=True),
        file_nametxt = fields.char('N. archivo txt', size=32),
        archivozp = fields.binary('Archivo Zip Proveedores',readonly=True),
        file_namezp = fields.char('N. archivo Zip', size=32),
        )
    
    def _get_date(self, cr, uid, ids, context=None):
        fmt = "%Y-%m-%d"
        now_ec = datetime.now(timezone('America/Lima'))
        fecha = now_ec.strftime(fmt)
        return fecha    

    _defaults = dict(
        tipo = 'pgeneral',
        state = 'Borrador',
        date_done = _get_date,
        date = time.strftime('%Y-%m-%d'),
        name = "PAGOS VARIOS ",
        )

spi_voucher()
