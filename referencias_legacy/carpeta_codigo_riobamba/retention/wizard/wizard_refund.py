# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

import time

from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
import netsvc

class invRefund(osv.osv_memory):
    _inherit = "account.invoice.refund"

    def compute_refund(self, cr, uid, ids, mode='refund', context=None):
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account invoice refund’s ID or list of IDs

        """
        inv_obj = self.pool.get('account.invoice')
        reconcile_obj = self.pool.get('account.move.reconcile')
        account_m_line_obj = self.pool.get('account.move.line')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        wf_service = netsvc.LocalService('workflow')
        inv_tax_obj = self.pool.get('account.invoice.tax')
        inv_line_obj = self.pool.get('account.invoice.line')
        res_users_obj = self.pool.get('res.users')
        if context is None:
            context = {}

        for form in self.browse(cr, uid, ids, context=context):
            created_inv = []
            date = False
            period = False
            description = False
            company = res_users_obj.browse(cr, uid, uid, context=context).company_id
            journal_id = form.journal_id.id
            for inv in inv_obj.browse(cr, uid, context.get('active_ids'), context=context):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise osv.except_osv(_('Error !'), _('Can not %s draft/proforma/cancel invoice.') % (mode))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise osv.except_osv(_('Error !'), _('Can not %s invoice which is already reconciled, invoice should be unreconciled first. You can only Refund this invoice') % (mode))
                if form.period.id:
                    period = form.period.id
                else:
                    period = inv.period_id and inv.period_id.id or False

                if not journal_id:
                    journal_id = inv.journal_id.id

                if form.date:
                    date = form.date
                    if not form.period.id:
                            cr.execute("select name from ir_model_fields \
                                            where model = 'account.period' \
                                            and name = 'company_id'")
                            result_query = cr.fetchone()
                            if result_query:
                                cr.execute("""select p.id from account_fiscalyear y, account_period p where y.id=p.fiscalyear_id \
                                    and date(%s) between p.date_start AND p.date_stop and y.company_id = %s limit 1""", (date, company.id,))
                            else:
                                cr.execute("""SELECT id
                                        from account_period where date(%s)
                                        between date_start AND  date_stop  \
                                        limit 1 """, (date,))
                            res = cr.fetchone()
                            if res:
                                period = res[0]
                else:
                    date = inv.date_invoice
                if form.description:
                    description = form.description
                else:
                    description = inv.name

                if not period:
                    raise osv.except_osv(_('Data Insufficient !'), \
                                            _('No Period found on Invoice!'))

                refund_id = inv_obj.refund(cr, uid, [inv.id], date, period, description, journal_id)
                refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
                inv_obj.write(cr, uid, [refund.id], {'date_due': date,
                                                     'check_total': inv.check_total,
                                                     'related_invoice_id':inv.id,
                                                     'certificate_id':inv.certificate_id.id,
                                                     })
                inv_obj.button_compute(cr, uid, refund_id)

                created_inv.append(refund_id[0])
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_id
                    to_reconcile_ids = {}
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_ids[line.account_id.id] = [line.id]
                        if type(line.reconcile_id) != osv.orm.browse_null:
                            reconcile_obj.unlink(cr, uid, line.reconcile_id.id)
                    wf_service.trg_validate(uid, 'account.invoice', \
                                        refund.id, 'invoice_open', cr)
                    refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
                    for tmpline in  refund.move_id.line_id:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_ids[tmpline.account_id.id].append(tmpline.id)
                    for account in to_reconcile_ids:
                        account_m_line_obj.reconcile(cr, uid, to_reconcile_ids[account],
                                        writeoff_period_id=period,
                                        writeoff_journal_id = inv.journal_id.id,
                                        writeoff_acc_id=inv.account_id.id
                                        )
                    if mode == 'modify':
                        invoice = inv_obj.read(cr, uid, [inv.id],
                                    ['name', 'type', 'number', 'reference',
                                    'comment', 'date_due', 'partner_id',
                                    'address_contact_id', 'address_invoice_id',
                                    'partner_insite', 'partner_contact',
                                    'partner_ref', 'payment_term', 'account_id',
                                    'currency_id', 'invoice_line', 'tax_line',
                                    'journal_id', 'period_id'], context=context)
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.read(cr, uid, invoice['invoice_line'], context=context)
                        invoice_lines = inv_obj._refund_cleanup_lines(cr, uid, invoice_lines)
                        tax_lines = inv_tax_obj.read(cr, uid, invoice['tax_line'], context=context)
                        tax_lines = inv_obj._refund_cleanup_lines(cr, uid, tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': date,
                            'state': 'draft',
                            'number': False,
                            'invoice_line': invoice_lines,
                            'tax_line': tax_lines,
                            'period_id': period,
                            'name': description,
                        })
                        for field in ('address_contact_id', 'address_invoice_id', 'partner_id',
                                'account_id', 'currency_id', 'payment_term', 'journal_id'):
                                invoice[field] = invoice[field] and invoice[field][0]
                        inv_id = inv_obj.create(cr, uid, invoice, {})
                        if inv.payment_term.id:
                            data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv.payment_term.id, date)
                            if 'value' in data and data['value']:
                                inv_obj.write(cr, uid, [inv_id], data['value'])
                        created_inv.append(inv_id)
            xml_id = (inv.type == 'out_refund') and 'action_invoice_tree1' or \
                     (inv.type == 'in_refund') and 'action_invoice_tree2' or \
                     (inv.type == 'out_invoice') and 'action_invoice_tree3' or \
                     (inv.type == 'in_invoice') and 'action_invoice_tree4'
            result = mod_obj.get_object_reference(cr, uid, 'account', xml_id)
            id = result and result[1] or False
            result = act_obj.read(cr, uid, id, context=context)
            invoice_domain = eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result

invRefund()


class WizardReturnInvoice(osv.Model):
    _name = 'wizard.invoice.return'

    _columns = {
        'move_id': fields.many2one('account.move',
                                   required=True,
                                   string='Asiento de Factura',
                                   readonly=True),
        'payment_ids': fields.many2many('account.move.line',
                                        'line_wiz_rel',
                                        'wiz_id',
                                        'line_id',
                                        string='Pagos', readonly=True),
        'invoice_id': fields.many2one('account.invoice', string='Factura'),
        'date': fields.date('Fecha de Transacción', required=True),
        'period_id': fields.many2one('account.period', string='Periodo', required=True),
        }

    def onchange_date(self, cr, uid, ids, date):
        if not date:
            return {}
        res = self.pool.get('account.period').find(cr, uid, dt=date)
        return {'value': {'period_id': res[0]} }

    def _get_move(self, cr, uid, context=None):
        if not context.get('active_id'):
            raise osv.except_osv('Error', 'Volver a abrir el asistente.')
        data = self.pool.get('account.invoice').read(cr, uid, context.get('active_id'), ['move_id','state'])
        if not data['state'] == 'paid':
            raise osv.except_osv('Error', 'La factura no esta pagada.')
        return data['move_id'][0]

    def _get_payments(self, cr, uid, context=None):
        if not context.get('active_id'):
            raise osv.except_osv('Error', 'Volver a abrir el asistente.')
        data = self.pool.get('account.invoice').read(cr, uid, context.get('active_id'), ['payment_ids','state'])
        if not data['state'] == 'paid':
            raise osv.except_osv('Error', 'La factura no esta pagada.')
        return data['payment_ids']

    def _get_invoice(self, cr, uid, context=None):
        return context.get('active_id')

    def _get_period(self, cr, uid, context=None):
        return self.pool.get('account.period').find(cr, uid)[0]

    _defaults = {
        'move_id': _get_move,
        'payment_ids': _get_payments,
        'invoice_id': _get_invoice,
        'period_id': _get_period
        }

    def action_return_invoice(self, cr, uid, ids, context=None):
        """
        Asistente que crea un asiento copia del asiento de factura
        sin la aplicacion presupuestaria y crea asientos
        reverso de los pagos aplicados a la factura
        CHECK: relacion 1 Pago - 1 Factura ?
        TODO: Agregar periodo en wiz y pasar al move
        """
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        
        wiz = self.browse(cr, uid, ids, context)[0]
        inv_number = wiz.invoice_id.supplier_number
        partner_name = wiz.invoice_id.partner_id.name
        move = wiz.move_id
        payments = wiz.payment_ids
        
        #Asiento de Factura
        move_data = move_obj.copy_data(cr, uid, move.id, default={'period_id':wiz.period_id.id, 'date': wiz.date})
        move_data['name'] = '/'
        move_data['narration'] = 'Asiento de cuentas por cobrar, reverso de transferencia, Factura: %s, Proveedor: %s' % (inv_number, partner_name)
        move_inv_id = move_obj.create(cr, uid, move_data)
        move_obj.post(cr, uid, [move_inv_id])
        
        #Asiento Reverso de Transferencia
        moves = [line.move_id.id for line in wiz.invoice_id.payment_ids if line.journal_id.type in ['bank','cash']]
        moves = list(set(moves))
        move_r_ids = []
        for move in move_obj.browse(cr, uid, moves):
            moved = move_obj.copy_data(cr, uid, move.id, default={'period_id':wiz.period_id.id, 'date': wiz.date})
            moved['name'] = '/'
            moved['narration'] = 'Reverso de transferencia, Factura: %s, Proveedor: %s' % (inv_number, partner_name)
            for l in moved['line_id']:
                tmp = l[2]['debit']
                l[2]['debit'] = l[2]['credit']
                l[2]['credit'] = tmp
            m_id = move_obj.create(cr, uid, moved)
            move_r_ids.append(m_id)
        move_r_ids.append(move_inv_id)
        domain = [('id','in',move_r_ids)]
        return {
              'name': "Asiento de Cuentas por Cobrar y Reverso(s)",
              'view_type': 'form',
              "view_mode": 'tree,form',
              'res_model': 'account.move',
              'type': 'ir.actions.act_window',
              'domain': domain,
              }        


class WizardPaymentSri(osv.TransientModel):
    _name = 'wizard.payment.sri'

    PRECISION_DP = dp.get_precision('Account')    

    _columns = {
        'period_id': fields.many2one('account.period', 'Mes',
                                     required=True, readonly=True),
        'journal_id': fields.many2one('account.journal', string='Banco',
                                      domain=[('type','in',['bank','cash'])],
                                      required=True),
        'date_payment': fields.date('Fecha de Pago', required=True),
#        'name': fields.char('Núm. Formulario SRI',
#                            size=64, required=True,
#                            help='Será referencia en el asiento contable'),
        'total': fields.float(string='Total', digits_compute=PRECISION_DP, readonly=True),
        'total_marcado': fields.float(string='Total A Pagar', digits_compute=PRECISION_DP, readonly=True),
        }

    def _get_period(self, cr, uid, context=None):
        obj_id = context.get('active_id')
        return self.pool.get('account.payment.sri').read(cr, uid, obj_id, ['period_id'])['period_id'][0]

    def _get_total_marcado(self, cr, uid, context=None):
        obj = self.pool.get('account.payment.sri').browse(cr, uid, context.get('active_id'))
        total = 0
        if obj.line_ids:
            for line in obj.line_ids:
                if line.to_pay2:
                    total += line.credit
        return total

    def _get_total(self, cr, uid, context=None):
        obj = self.pool.get('account.payment.sri').browse(cr, uid, context.get('active_id'))
        total = sum([line.credit for line in obj.line_ids])
        return total

    _defaults = {
        'period_id': _get_period,
        'date_payment': time.strftime('%Y-%m-%d'),
        'total': _get_total,
        'total_marcado': _get_total_marcado,
        }

    def action_payment(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        parent_obj = self.pool.get('account.payment.sri')
        move_line_obj = self.pool.get('account.move.line')
        invoice_tax_obj = self.pool.get('account.invoice.tax')
        period_obj = self.pool.get('account.period')
        active_id = context['active_id']
        active = parent_obj.browse(cr, uid, active_id)
        monto_total = 0
        for this in self.browse(cr, uid, ids):
            #aqui igual verificar si hay move
            period_id = period_obj.find(cr, uid, this.date_payment)[0]
            if active.move_id:
                if active.move_id.state=='draft' and active.move_id.name=='/':
                    move_obj.unlink(cr, uid, [active.move_id.id],1)
                    move_id = move_obj.create(cr, uid, {
                        'ref': active.name,
                        'narration':active.name,
                        'journal_id': this.journal_id.id,
                        'date': this.date_payment,
                        'period_id':period_id,
                        'state':'draft',
                        'partner_id':active.partner_id.id,
                        'type':'Impuestos',
                        'afectacion':True,
                        'no_cp':True,
                        'certificate_id':active.certificate_id.id,
                        'validar_cp':True,
                    })
                    parent_obj.write(cr, uid, [active_id], {'move_id':move_id})
                elif active.move_id.state=='draft' and active.move_id.name!='/':
                    cr.execute("delete from account_move_line where move_id=%s"%(active.move_id.id))
                    move_id = active.move_id.id
                elif active.move_id.state=='posted':
                    raise osv.except_osv('Error', 'El asiento %s se encuentra validado, primero debe cancelarlo.'%(active_move_id.name))
            else:
                move_id = move_obj.create(cr, uid, {
                    'ref': active.name,
                    'narration':active.name,
                    'journal_id': this.journal_id.id,
                    'date': this.date_payment,
                    'state':'draft',
                    'period_id':period_id,
                    'partner_id':active.partner_id.id,
                    'type':'Impuestos',
                    'afectacion':True,
                    'no_cp':True,
                    'certificate_id':active.certificate_id.id,
                    'validar_cp':True,
                })
                parent_obj.write(cr, uid, [active_id], {'move_id':move_id})
            monto_total = 0
            date_aux = this.date_payment
            state_aux = 'draft'
            company_aux = 1
            currency_aux = 2
            partner_id = active.partner_id.id
            for account_move_line in active.line_ids:
                #hacer con sql
                if account_move_line.to_pay2:
                    if account_move_line.tax_aux_id:
                        invoice_tax_obj.write(cr, uid, account_move_line.tax_aux_id.id,{'pay':True})
                    monto_total += account_move_line.credit
                    if account_move_line.budget_id_cert:
                        post_id = account_move_line.budget_id_cert.budget_post.id
                        budget_id = account_move_line.budget_id_cert.budget_id.id
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,budget_paid,budget_id_cert,budget_id,budget_post,to_pay,partner_id,move_line_cxp) VALUES (%s,%s,%s,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(move_id,account_move_line.account_id.id,account_move_line.credit,this.journal_id.id,period_id,state_aux,company_aux,currency_aux,date_aux,account_move_line.ref,False,True,account_move_line.budget_id_cert.id,budget_id,post_id,True,partner_id,account_move_line.id))
                    else:
                        cr.execute('''
                        INSERT INTO account_move_line (
                        move_id,account_id,debit,journal_id,period_id,state,company_id,currency_id,date,name,migrado,to_pay,partner_id,move_line_cxp) VALUES (%s,%s,%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)''',(move_id,account_move_line.account_id.id,account_move_line.credit,this.journal_id.id,period_id,state_aux,company_aux,currency_aux,date_aux,account_move_line.ref,False,True,partner_id,account_move_line.id))
            #banco
            line_id = move_line_obj.create(cr, uid, {
                'move_id':move_id,
                'credit':monto_total,
                'journal_id':this.journal_id.id,
                'name':'Pago Banco',
                'partner_id':partner_id,
                'period_id':period_id,
                'account_id':this.journal_id.default_debit_account_id.id,
                'state':'draft',
 #               'period_id':active.period_id.id,
                'date':this.date_payment,
            })
        return {'type': 'ir.actions.act_window_close'}


class AccountPaymentSri(osv.Model):
    _name = 'account.payment.sri'

    STATES_VALUE = {'draft': [('readonly', False)]}    

    _columns = {
        'name': fields.char('Descripcion',size=256,required=True),
        'account_ids': fields.many2many('account.account','p_i_id','p_id','i_id','Ctas. Impuestos Retenidos'),
        'period_id': fields.many2one('account.period',
                                     string='Periodo', required=True,
                                     domain=[('special','=',False)],
                                     readonly=True, states=STATES_VALUE),
        'date_start' : fields.date('Fecha Desde'),
        'date_end' : fields.date('Fecha Hasta'),
        'partner_id': fields.many2one('res.partner',
                                      string='SRI', required=True,
                                      states=STATES_VALUE),
        'line_ids':fields.one2many('account.move.line','p_id','Detalle'),
#        'line_ids': fields.many2many('account.move.line',
#                                     'm_l_id',
#                                     'm_id', 'l_id', 'Detalle de Impuestos'),
        'move_id': fields.many2one('account.move', string="Diario de Pago", readonly=True),
        'state': fields.selection([('draft','Borrador'),
                                   ('paid', 'Pagado')], string='Estado',
                                   required=True, readonly=True),
        'certificate_id':fields.many2one('budget.certificate','Cert'),
        }

    def action_query(self, cr, uid, ids, context=None):
        ml_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        tax_obj = self.pool.get('account.tax')
        invoice_tax_obj = self.pool.get('account.invoice.tax')
        cuentas = []
        certificate_id = 1
        journal_obj = self.pool.get('account.journal')
        for obj in self.browse(cr, uid, ids, context):
            aux_invoice = False#TrueLImon
            if aux_invoice:
                journal_ids = journal_obj.search(cr, uid, [('name','=','EGRESOS')],limit=1)
                if not journal_ids:
                    raise osv.except_osv('Error de configuracion', 'No existe diario de EGRESOS por favor cree uno')
                invoice_tax_ids = invoice_tax_obj.search(cr, uid, [('date','>=',obj.date_start),('date','<=',obj.date_end),('invoice_id.state','!=','cancel'),
                                                                   ('tax_group','in',('ret_vat_b','ret_vat_srv','ret_ir')),('pay','=',False)])
                if invoice_tax_ids:
                    res1 = []
                    for invoice_tax_id in invoice_tax_ids:
                        invoice_tax = invoice_tax_obj.browse(cr, uid, invoice_tax_id)
                        if invoice_tax.budget_id:
                            budget_aux = invoice_tax.budget_id.id
                        else:
                            if not invoice_tax.invoice_id.invoice_line[0].budget_id:
                                raise osv.except_osv('Error de usuario', 'La factura %s del proveedor %s no tiene asociada partida.'%(invoice_tax.num_document,invoice_tax.partner_id.name))
                            budget_aux = invoice_tax.invoice_id.invoice_line[0].budget_id.id
                        if abs(invoice_tax.amount)>0:
                            move_line_id = ml_obj.create(cr, uid, {
                                'tax_aux_id':invoice_tax_id,
                                'p_id':obj.id,
                                'partner_id':invoice_tax.invoice_id.partner_id.id,
                                'account_id':invoice_tax.account_id.id,
                                'budget_id_cert':budget_aux,
                                'credit':abs(invoice_tax.amount),
                                'name':invoice_tax.name,
                                'ref':invoice_tax.invoice_id.new_number,#invoice_tax.num_document,
                                'period_id':obj.period_id.id,
                                'date':obj.date_end,
                                'journal_id':journal_ids[0],
                                'to_pay2':True,
                            })
                            res1.append(move_line_id)
                    res2 = ml_obj.search(cr, uid, [('move_id.state','=','posted'),('date','>=',obj.date_start),('date','<=',obj.date_end),
                                                   ('move_id.type','=','Nomina'),('to_pay2','=',False),
                                                   ('credit','>',0),('state','=','valid'),('migrado','=',False),('name','ilike','renta')])
                    if res2:
                        ml_obj.write(cr, uid, res2,{
                            'p_id':obj.id,
                        })
                #otros comprobantes
                res4 = ml_obj.search(cr, uid, [('move_id.state','=','posted'),('date','>=',obj.date_start),('date','<=',obj.date_end),
                                               ('move_id.type','=',False),('to_pay','=',False),
                                               ('credit','>',0),('state','=','valid'),('migrado','=',False),('name','=','SRI')])
                if res4:
                    ml_obj.write(cr, uid, res4,{
                        'p_id':obj.id,
                    })
                #depositos de intermediacion
                account_ids = account_obj.search(cr, uid, [('code','=','2120101001')])
                res3 = ml_obj.search(cr, uid, [('partner_id','=',obj.partner_id.id),('account_id','=',account_ids[0]),#('to_pay2','=',False),
                                               ('move_id.state','=','posted'),('date','>=',obj.date_start),('date','<=',obj.date_end),
                                           ])
                if res3:
                    ml_obj.write(cr, uid, res3,{
                            'p_id':obj.id,
                        })
#                res = res1+res2+res3
#                values = [(6,0,res)]
#                self.write(cr, uid, obj.id, {'line_ids': values})
            else:
                if obj.account_ids:
                    for account_id in obj.account_ids:
                        cuentas.append(account_id.id)
                    res = ml_obj.search(cr, uid, [('account_id','in',cuentas),('move_id.state','=','posted'),('date','>=',obj.date_start),('date','<=',obj.date_end),
                                                  ('credit','>',0),('state','=','valid'),('migrado','=',False),('to_pay','=',False)])
                    ml_obj.write(cr, uid, res,{
                        'to_pay2':True,
                    })
                else:
                    if obj.partner_id:
                        cuentas = account_obj.search(cr, uid, [('partner_id','=',obj.partner_id.id)])
                        tax_ids = tax_obj.search(cr, uid, [('tax_group','in',('ret_vat_b','ret_vat_srv','ret_ir'))])
                        if tax_ids:
                            aux_code_tax = []
                            for tax_id in tax_ids:
                                tax = tax_obj.browse(cr, uid, tax_id)
                                if tax.base_code_id:
                                    aux_code_tax.append(tax.base_code_id.id)
                                if tax.tax_code_id:
                                    aux_code_tax.append(tax.tax_code_id.id)
                            res1 = ml_obj.search(cr, uid, [('move_id.state','=','posted'),('date','>=',obj.date_start),('date','<=',obj.date_end),
                                                          ('credit','>',0),('state','=','valid'),('migrado','=',False),('tax_code_id','in',aux_code_tax)])
                        res2 = ml_obj.search(cr, uid, [('move_id.state','=','posted'),('date','>=',obj.date_start),('date','<=',obj.date_end),
                                                       ('move_id.type','=','Nomina'),
                                                       ('credit','>',0),('state','=','valid'),('migrado','=',False),('name','ilike','renta')])
                        res = res1+res2
                for line_acc_aux in res:
                    aux_move_line = ml_obj.browse(cr, uid, line_acc_aux)
                    if aux_move_line.move_id.certificate_id.id:
                        certificate_id = aux_move_line.move_id.certificate_id.id
                        break
                values = [(6,0,res)]
                #ojo no deberia escrinir el certificate_id
                if certificate_id:
                    self.write(cr, uid, obj.id, {'line_ids': values,
                                                 'certificate_id':certificate_id})
                else:
                    self.write(cr, uid, obj.id, {'line_ids': values,
                                             })
        return True

    def _get_sri(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if not user.company_id.tax_company_id:
            raise osv.except_osv('Error', 'No esta configurado el SRI en la empresa.')
        return user.company_id.tax_company_id.id

    def _get_start(self, cr, uid, context=None):
        period_obj = self.pool.get('account.period')
        period = self.pool.get('account.period').find(cr, uid)
        periodo = period_obj.browse(cr, uid, period[0])
        return periodo.date_start

    def _get_end(self, cr, uid, context=None):
        period_obj = self.pool.get('account.period')
        period = self.pool.get('account.period').find(cr, uid)
        periodo = period_obj.browse(cr, uid, period[0])
        return periodo.date_stop

    def _get_period(self, cr, uid, context=None):
        period = self.pool.get('account.period').find(cr, uid)
        return period[0]

    _defaults = {
        'period_id': _get_period,
        'date_start':_get_start,
        'date_end':_get_end,
        'partner_id': _get_sri,
        'state': 'draft'
        }
