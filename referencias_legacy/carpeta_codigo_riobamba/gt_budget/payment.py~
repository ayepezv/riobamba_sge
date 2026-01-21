# -*- coding: utf-8 -*-
##############################################################################
#
# mario chogllo
#
##############################################################################

from osv import osv, fields
import time
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
from tools import ustr

class paymentRequest(osv.Model):
    _name = "payment.request"
    _description="Solicitud de Pago"
    _order = 'date_request desc,name desc'

    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            raise osv.except_osv('Aviso','No se permite eliminar ordenes de pago.')
        res = super(paymentRequest, self).unlink(cr, uid, ids, context)
        return res
        
    def create(self, cr, uid, vals, context):      
        name=''
        if context is None:            
            context = {}    
        seq_obj = self.pool.get('ir.sequence')
        seq_num = seq_obj.get(cr, uid, 'payment.request')
        if not seq_num:
            raise osv.except_osv('Error', 'No ha configurado la secuencia para este documento.')
        vals['name'] = seq_num  
        return super(paymentRequest, self).create(cr, uid, vals, context)

    def emitir_payment(self, cr, uid, ids, context=None):  
        return self.write(cr, uid, ids, {'state': 'emitido'}, context=context)

    def recibido_payment(self, cr, uid, ids, context=None):  
        return self.write(cr, uid, ids, {'state': 'Recibido Financiero'}, context=context)

    def financiero_draft(self, cr, uid, ids, context=None):  
        return self.write(cr, uid, ids, {'state': 'emitido'}, context=context)

    def return_payment(self, cr, uid, ids, context=None):           
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def cancel_payment(self, cr, uid, ids, context=None):  
        return self.write(cr, uid, ids, {'state': 'Cancelado'}, context=context)

    def pay_payment(self, cr, uid, ids, context=None):           
        return self.write(cr, uid, ids, {'state': 'Pagado'}, context=context)

    def print_payment(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        order = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [order.id], 'model': 'payment.request'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'payment_request',
            'model': 'payment.request',
            'datas': datas,
            'nodestroy': True,                        
            }
        
    def _validar_monto(self, cr, uid, ids):
        result = False       
        for obj in self.browse(cr, uid, ids):
            if 'amount_invoice' in obj:
                if float(obj.amount_invoice)<=0:
                    raise osv.except_osv('Error!', 'Monto de pago inválido')
                else:                
                    result = True
        return result 

    _state = [('Cancelado','Cancelado'),('draft','Borrador'),('emitido','Emitido'),('Recibido Financiero','Recibido Financiero'),
              ('Contabilizado','Contabilizado'),('Pagado','Pagado')]
     
    _columns = dict(
        emp_solicitante = fields.many2one('hr.employee','Solicitante'),
        type_doc = fields.selection([('Infima','Infima Cuantia Bienes'),('Infima Servicio','Infima Cuantia Servicos'),
                                     ('Contrato','Contrato'),('Convenio','Convenio'),
                                     ('Otro','Otro')],'Proceso',required=True),
        name = fields.char('Solicitud de Pago No.', size=32,
                           readonly=True),    
        date_request = fields.datetime('Fecha Solicitud',required=True),
        user_id = fields.many2one('res.users' ,'Elaborado por',required=True,readonly=True),
        partner_id = fields.many2one('res.partner' ,'Proveedor',required=True),
        amount_invoice=fields.float('Monto (inc. IVA)',required=True),
        concepto = fields.text('Concepto',required=True),
        observaciones = fields.text('Observaciones'),
        state = fields.selection(_state,'Estado'),
        type_num = fields.char('Convenio/Contrato No.',size=128),
        otra_fecha = fields.boolean('Otra fecha'),
        )
    
    _defaults = dict(
        state = 'draft',
        name = '/',
        date_request = lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        user_id = lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
        )

    _constraints = [
        (_validar_monto,'Monto de Factura inválido',['amount_invoice']),
        ]
               
paymentRequest()
