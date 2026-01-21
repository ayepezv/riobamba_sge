# -*- coding: utf-8 -*-
import logging
from osv import osv, fields
import time


class AccountVoucherLine(osv.Model):
    _inherit = 'account.voucher.line'
    __logger = logging.getLogger(_inherit)    

    def default_get(self, cr, user, fields_list, context=None):
        """
        Returns default values for fields
        @param fields_list: list of fields, for which default values are required to be read
        @param context: context arguments, like lang, time zone

        @return: Returns a dict that contains default values for fields
        """
        if context is None:
            context = {}
        journal_id = context.get('journal_id', False)
        partner_id = context.get('partner_id', False)
        journal_pool = self.pool.get('account.journal')
        partner_pool = self.pool.get('res.partner')
        values = super(AccountVoucherLine, self).default_get(cr, user, fields_list, context=context)
        if (not journal_id) or ('account_id' not in fields_list):
            return values
        journal = journal_pool.browse(cr, user, journal_id, context=context)
        account_id = False
        ttype = 'cr'
        if journal.type in ('sale', 'sale_refund'):
            account_id = journal.default_credit_account_id and journal.default_credit_account_id.id or False
            ttype = 'cr'
        elif journal.type in ('purchase', 'expense', 'purchase_refund'):
            account_id = journal.default_debit_account_id and journal.default_debit_account_id.id or False
            ttype = 'dr'
        elif partner_id:
            partner = partner_pool.browse(cr, user, partner_id, context=context)
            if context.get('type') == 'payment':
                ttype = 'dr'
                if partner.anticipo_id:
                    account_id = partner.anticipo_id.id
            elif context.get('type') == 'receipt':
                if partner.anticipo_id:
                    account_id = partner.anticipo_id.id
            else:
                ttype='dr'
                if partner.anticipo_id:
                    account_id = partner.anticipo_id.id
                else:
                    raise osv.except_osv('Error de configuracion', 'Asigne la cuenta de anticipo en el proveedor.')
        values.update({
            'account_id':account_id,
            'type':ttype
        })
        return values

    def onchange_account_id(self, cr, uid, ids, account_id, certificate_id, context):
        """
        Redefinicion para carga de cuenta contable
        Recibe la cuenta por pagar, debe leer la cuenta que tenga a account_id
        como por pagar y buscar el account.budget.post que tenga configurada esa cta
        luego leer el codigo y verificar que este en el detalle del presupuesto
        referencial y cargar la correcta.
        """
        id = []
        res = {'value': {'budget_id': False}}
        if not account_id or not certificate_id:
            return res
        budget_obj = self.pool.get('budget.certificate.line')
        certificate_obj = self.pool.get('budget.certificate')
        ml_obj = self.pool.get('account.move.line')
        post_obj = self.pool.get('budget.post')
        account_obj = self.pool.get('account.account')
        account = account_obj.browse(cr, uid, account_id)
        if context.get('type') in ['sale', 'purchase']:
            certificate = certificate_obj.browse(cr, uid, certificate_id)
            for line in certificate.line_ids:
                acc_ids = [acc.id for acc in line.budget_line_id.general_budget_id.account_ids]
                if account_id in acc_ids:
                    res= {'value': {'budget_id': line.id}}
        else:
            ml_id = context.get('move_line_ids')[0]
            move_line = ml_obj.browse(cr, uid, ml_id)
            move = move_line.move_id
            budgets = [line.budget_id.id for line in move.line_id if line.budget_id] #son partidas
            certificate = certificate_obj.browse(cr, uid, certificate_id)
            for line in certificate.line_ids:
                if line.budget_id.id in budgets:
                    res = {'value': {'budget_id': line.id}}
        return res
    
    def recompute_voucher_lines_account(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):

        if context is None:
            context = {}
        context_multi_currency = context.copy()
        if date:
            context_multi_currency.update({'date': date})

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')

        #set default values
        default = {
            'value': {'line_ids': [] ,'line_dr_ids': [] ,'line_cr_ids': [] ,'pre_line': False,},
        }

        #drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id
        account_id = False
        if journal.type in ('sale','sale_refund'):
            account_id = partner.property_account_receivable.id
        elif journal.type in ('purchase', 'purchase_refund','expense'):
            account_id = partner.property_account_payable.id
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id

        default['value']['account_id'] = account_id

        if journal.type not in ('cash', 'bank'):
            return default

        total_credit = 0.0
        total_debit = 0.0
        account_type = 'receivable'
        if ttype == 'payment':
            account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            account_type = 'receivable'

        if not context.get('move_line_ids', False):
            #Cambio para considerar solo las lineas de la factura.
            #domain = [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)]
            domain = [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)]
            if context.get('invoice_id'):
                domain.append(('invoice','=',context.get('invoice_id')))
            ids = move_line_pool.search(cr, uid, domain, context=context)
        else:
            ids = context['move_line_ids']
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_line_found = False

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

        for line in account_move_lines:
            if line.reconcile_partial_id and line.amount_residual_currency < 0:
                # skip line that are totally used within partial reconcile
                continue
            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_line_found = line.id
                    break
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_line_found = line.id
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit or 0.0
                total_debit += line.debit or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_line_found = line.id
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0        
        #voucher line creation
        for line in account_move_lines:  
            ids=[]
            #Partida
            for line_moves in line.move_id.line_id:
                if line_moves.budget_id.id:                    
                    ids.append(line_moves.budget_id.id)                                
            bud_id=list(set(ids))[0]
            
            if line.reconcile_partial_id and line.amount_residual_currency < 0:
                # skip line that are totally used within partial reconcile
                continue
            if line.currency_id and currency_id==line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual))
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': (move_line_found == line.id) and min(price, amount_unreconciled) or 0.0,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
                'budget_id':bud_id,
            }
            #split voucher amount by most old first, but only for lines in the same currency
            if not move_line_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if ttype == 'payment' and len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif ttype == 'receipt' and len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price)
            default['value']['amount'] = self.pool.get('account.voucher')._compute_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price)
        return default
    
    _columns = {
#        'budget_id': fields.many2one('budget.post', 'Partida Presupuestaria'),
        'budget_id': fields.many2one('budget.certificate.line', 'Partida Presupuestaria'),
        'type_move' : fields.char('Tipo Movimiento', size=128),
        }


class AccountVoucher(osv.Model):

    _inherit = 'account.voucher'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name  = str(record.amount) + ' - ' + record.narration
#            if record.date:
#                if record.narration:
#                    name = record.date + ' - ' + record.reference + ' - '  + record.narration
#                else:
#                    name = record.date + ' - ' + record.reference 
#            else:
#                if record.narration:
#                    name = record.reference + ' - '  + record.narration
#                else:
#                    name = record.reference
            res.append((record.id, name))
        return res            

    def _make_journal_search(self, cr, uid, ttype, context=None):
        parameter_obj = self.pool.get('ir.config_parameter')
        anticipo_ids = parameter_obj.search(cr, uid, [('key','=','anticipo')],limit=1)
        journal_pool = self.pool.get('account.journal')
        if anticipo_ids:
            ant_name = parameter_obj.browse(cr, uid, anticipo_ids[0]).value
            j_ids = journal_pool.search(cr, uid, [('name','=',ant_name)],limit=1)
        else:
            j_ids = journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
        return j_ids

    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        if context is None:
            context = {}
        context_multi_currency = context.copy()
        if date:
            context_multi_currency.update({'date': date})

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')

        #set default values
        default = {
            'value': {'line_ids': [] ,'line_dr_ids': [] ,'line_cr_ids': [] ,'pre_line': False,},
        }

        #drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id
        account_id = False
        if journal.type in ('sale','sale_refund'):
            account_id = partner.property_account_receivable.id
        elif journal.type in ('purchase', 'purchase_refund','expense'):
            account_id = partner.property_account_payable.id
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id

        default['value']['account_id'] = account_id

        if journal.type not in ('cash', 'bank'):
            return default

        total_credit = 0.0
        total_debit = 0.0
        account_type = 'receivable'
        if ttype == 'payment':
            account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            account_type = 'receivable'

        if not context.get('move_line_ids', False):
            #modificado para cargar solo de factura
            domain = [('state','=','valid'),
                      ('account_id.type', '=', account_type),
                      ('reconcile_id', '=', False),('partner_id', '=', partner_id)]
            if context.get('invoice_id',False):
                domain.append(('invoice','=',context.get('invoice_id')))
            ids = move_line_pool.search(cr, uid, domain, context=context)                
            ids = move_line_pool.search(cr, uid, domain, context=context)
        else:
            ids = context['move_line_ids']
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_line_found = False

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

        for line in account_move_lines:
            if line.reconcile_partial_id and line.amount_residual_currency < 0:
                # skip line that are totally used within partial reconcile
                continue
            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_line_found = line.id
                    break
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_line_found = line.id
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit or 0.0
                total_debit += line.debit or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_line_found = line.id
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0

        #voucher line creation
        for line in account_move_lines:
            if line.reconcile_partial_id and line.amount_residual_currency < 0:
                # skip line that are totally used within partial reconcile
                continue
            if line.currency_id and currency_id==line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual))
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': (move_line_found == line.id) and min(price, amount_unreconciled) or 0.0,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
            }

            #split voucher amount by most old first, but only for lines in the same currency
            if not move_line_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if ttype == 'payment' and len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif ttype == 'receipt' and len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price)
        return default    

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
        line_field = {'payment': 'line_dr_ids',
                       'receipt': 'line_cr_ids'}
        line_obj = self.pool.get('account.voucher.line')        
        if context is None:
            context = {}
        res = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=context)
        ctx = context.copy()
        ctx.update({'date': date})
        vals = res
        if ttype in ['payment', 'receipt']:
            if vals.get('value') and vals['value'].get(line_field[ttype], False):
                for li in vals['value'][line_field[ttype]]:
                    if not context.get('move_line_ids'):
                        context.update({'move_line_ids': [li['move_line_id']] })
                    line = self.pool.get('account.move.line').browse(cr, uid, li['move_line_id'])                    
                    if line.invoice.type == 'out_invoice' and line.tax_amount:
                        continue
                    aux = line_obj.onchange_account_id(cr, uid, [], li['account_id'], context.get('default_certificate_id'), context)['value']['budget_id']
                    li['budget_id'] = line_obj.onchange_account_id(cr, uid, [], li['account_id'], context.get('default_certificate_id'), context)['value']['budget_id']
        for key in vals.keys():
            res[key].update(vals[key])        
#        vals = self.onchange_rate(cr, uid, ids, rate, amount, currency_id, payment_rate_currency_id, company_id, context=ctx)
#        for key in vals.keys():
#            res[key].update(vals[key])
        return res    

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        """
        Redefinicion para cargar la partida en el detalle
        """
        line_field = {'payment': 'line_dr_ids',
                       'receipt': 'line_cr_ids'}
        line_obj = self.pool.get('account.voucher.line')
        if not journal_id:
            return {}
        res = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=context)
        vals = self.recompute_payment_rate(cr, uid, ids, res, currency_id, date, ttype, journal_id, amount, context=context)
        if ttype in ['payment', 'receipt']:
            if vals.get('value') and vals['value'].get(line_field[ttype], False):
                for li in vals['value'][line_field[ttype]]:
                    if not context.get('move_line_ids'):
                        print "NO CTX"
                        context.update({'move_line_ids': [li['move_line_id']] })
                    line = self.pool.get('account.move.line').browse(cr, uid, li['move_line_id'])
                    if line.invoice.type == 'out_invoice' and line.tax_amount:
                        print "CONTINUE"
                        continue
#                    aux = line_obj.onchange_account_id(cr, uid, [], li['account_id'], context.get('default_certificate_id'), context)['value']['budget_id']
#                    li['budget_id'] = line_obj.onchange_account_id(cr, uid, [], li['account_id'], context.get('default_certificate_id'), context)['value']['budget_id']
        for key in vals.keys():
            res[key].update(vals[key])
        return res    

    def print_move_payment(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir la solicitud de compra
        '''        
        if not context:
            context = {}
        payment = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [payment.move_id.id], 'model': 'account.move'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.move',
            'model': 'account.move',
            'datas': datas,
            'nodestroy': True,
            }        
        return True

    def account_move_get(self, cr, uid, voucher_id, context=None):
        '''
        This method prepare the creation of the account move related to the given voucher.

        :param voucher_id: Id of voucher for which we are creating account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        seq_obj = self.pool.get('ir.sequence')
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher_brw.number:
            name = voucher_brw.number
        elif voucher_brw.journal_id.sequence_id:
            name = seq_obj.next_by_id(cr, uid, voucher_brw.journal_id.sequence_id.id, context=context)
        else:
            raise osv.except_osv(_('Error !'),
                        _('Please define a sequence on the journal !'))
        if not voucher_brw.reference:
            ref = name.replace('/','')
        else:
            ref = voucher_brw.reference
        #aqui si es de anticipo va false en afectacion
        if voucher_brw.internal_type in ('AP','AS'):
            move = {
                'name': name,
                'journal_id': voucher_brw.journal_id.id,
                'narration': voucher_brw.narration,
                'date': voucher_brw.date,
                'ref': ref,
                'partner_id':voucher_brw.partner_id.id,
                'period_id': voucher_brw.period_id and voucher_brw.period_id.id or False
            }
        else:
            move = {
                'name': name,
                'journal_id': voucher_brw.journal_id.id,
                'narration': voucher_brw.narration,
                'date': voucher_brw.date,
                'certificate_id':voucher_brw.certificate_id.id,
                'afectacion':True,
                'ref': ref,
                'partner_id':voucher_brw.partner_id.id,
                'period_id': voucher_brw.period_id and voucher_brw.period_id.id or False
            }
        return move

    def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        '''
        Return a dict to be use to create the first account move line of given voucher.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param move_id: Id of account move where this line will be added.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: mapping between fieldname and value of account move line to create
        :rtype: dict
        '''
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        debit = credit = 0.0
        # TODO: is there any other alternative then the voucher type ??
        # ANSWER: We can have payment and receipt "In Advance".
        # TODO: Make this logic available.
        # -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt
        if voucher_brw.type in ('purchase', 'payment'):
            credit = voucher_brw.paid_amount_in_company_currency
        elif voucher_brw.type in ('sale', 'receipt'):
            debit = voucher_brw.paid_amount_in_company_currency
        if debit < 0: credit = -debit; debit = 0.0
        if credit < 0: debit = -credit; credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        #set the first line of the voucher
        move_line = {
                'name': voucher_brw.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': voucher_brw.account_id.id,
                'move_id': move_id,
                'journal_id': voucher_brw.journal_id.id,
                'period_id': voucher_brw.period_id.id,
                'partner_id': voucher_brw.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * voucher_brw.amount or 0.0,
                'date': voucher_brw.date,
                'date_maturity': voucher_brw.date_due
            }
        return move_line

    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Boton validar del anticipo
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        voucher_obj = self.pool.get('account.voucher')
        move_line_pool = self.pool.get('account.move.line')
        ie_line_obj = self.pool.get('hr.ie.line')
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        period_obj = self.pool.get('hr.work.period.line')
        categ_obj = self.pool.get('hr.salary.rule')
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.move_id:
                continue
            if voucher.extra_type != 'ninguno' and not voucher.amount:
                raise osv.except_osv('Error', 'No hay ingresado el valor total del documento.')
            if voucher.extra_type != 'ninguno':
                val_temporal = sum([l.amount for l in voucher.line_dr_ids])
                val_temporal += sum([l.amount for l in voucher.line_cr_ids])
                if round(val_temporal, 2) != round(voucher.amount, 2):
                    raise osv.except_osv('Error', 'El monto total es diferente de la suma del detalle.')
            if voucher.type in ['sale', 'purchase', 'payment']:
                val_temporal = sum([l.amount for l in voucher.line_dr_ids])
                val_temporal += sum([l.amount for l in voucher.line_cr_ids])
                self.write(cr, uid, [voucher.id], {'amount': val_temporal,
                                                   'paid_amount_in_company_currency': val_temporal,
                                                   'writeoff_amount': 0})
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, context), context)
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)

            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, context)
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
            #creamos el descuento del anticipo automatico
            if voucher.internal_type=='AS':
                employee_ids = employee_obj.search(cr, uid, [('name','=',voucher.partner_id.ced_ruc)])
                if employee_ids:
                    contract_ids = contract_obj.search(cr, uid, [('employee_id','=',employee_ids[0]),('activo','=',True)])
                    if contract_ids:
                        period_ids = period_obj.search(cr, uid, [('date_start','<=',voucher.date),('date_stop','>=',voucher.date)])
                        if not period_ids:
                            raise osv.except_osv('Error configuracion','No existe periodo para la fecha del anticipo.')
                        rule_ids = categ_obj.search(cr, uid, [('code','=','ANTICIPOA')])
                        if not rule_ids:
                            raise osv.except_osv('Error configuracion','No existe regla salarial con Codigo ANTICIPOA.')
                            #si no usan los tipo c: ejm milagro
                            #parameter_obj = self.pool.get('ir.config_parameter')
                            #noc_ids = parameter_obj.search(cr, uid, [('key','=','noc')],limit=1)
                            #noc = 'No'
                            #if noc_ids:
                            #    noc = parameter_obj.browse(cr, uid, noc_ids[0]).value
                            #    if noc=='Si':
                            #        rule_ids = categ_obj.search(cr, uid, [('code','=','ANTICIPOS')])
                            #else:
                            #    raise osv.except_osv('Error configuracion','No existe regla salarial con Codigo ANTICIPOA.')
                        contrato = contract_obj.browse(cr, uid, contract_ids[0])
                        ie_line_id = ie_line_obj.create(cr, uid, {
                            'name': contrato.employee_id.complete_name,
                            'employee_id': contrato.employee_id.id,
                            'date': voucher.date,
                            'valor': float("%.2f" % voucher.amount),
                            'categ_id': rule_ids[0],
                            'period_id': period_ids[0],
                            'state': 'pendiente',
                            'referencia':voucher.reference,
                        })
                        self.write(cr, uid, [voucher.id], {
                            'rule_id': rule_ids[0],
                        })          
        return True    

    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []

        voucher_brw = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context)
        ctx = context.copy()
        ctx.update({'date': voucher_brw.date})
        k = s =  0
        if voucher_brw.certificate_id:
            if not voucher_brw.partner_id.id==voucher_brw.partner_id.id:
                raise osv.except_osv('Error', 'El compromiso presupuestario seleccionado no corresponde al proveedor')
            for line in voucher_brw.line_ids:
                if line.amount>0:
                    if not line.budget_id:
                        raise osv.except_osv('Error', 'En el valor seleccionado a pagar debe elegir la partida presupuestaria a pagar')
                    s += 1
            if s<=0:
                raise osv.except_osv('Error', 'Debe seleccionar por lo menos un valor a pagar')
        for line in voucher_brw.line_ids:
            #create one move line per voucher line where amount is not 0.0
            if not line.amount:
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher_brw.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                currency_rate_difference = line.amount_original - amount
            else:
                currency_rate_difference = 0.0
            move_line = {
                'journal_id': voucher_brw.journal_id.id,
                'period_id': voucher_brw.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': voucher_brw.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher_brw.date,
            }

            #Consideracion de partidas
            if line.budget_id and line.voucher_id.type in ['sale','purchase']:
                if line.account_id.type=='other':                
                    move_line.update({'budget_id_cert': line.budget_id.id, 'budget_accrued': True})
                if line.account_id.type in ['receivable','payable']:
                    move_line.update({'budget_id_cert': line.budget_id.id, 'budget_paid': True})                
            else:
                move_line.update({'budget_id_cert': line.budget_id.id, 'budget_paid': True})

            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type=='dr'):
                tot_line += amount
                move_line['debit'] = amount
            else:
                tot_line -= amount
                move_line['credit'] = amount

            if voucher_brw.tax_id and voucher_brw.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher_brw.tax_id.id,
                })

            if move_line.get('account_tax_id', False):
                tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                if not (tax_data.base_code_id and tax_data.tax_code_id):
                    raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                voucher_currency = voucher_brw.currency_id and voucher_brw.currency_id.id or voucher_brw.journal_id.company_id.currency_id.id
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency. 
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    elif line.move_line_id.currency_id.id == voucher_brw.payment_rate_currency_id.id:
                        # if the rate is specified on the voucher, we must use it
                        voucher_rate = currency_obj.browse(cr, uid, voucher_currency, context=ctx).rate
                        amount_currency = (move_line['debit'] - move_line['credit']) * voucher_brw.payment_rate * voucher_rate
                    else:
                        # otherwise we use the rates of the system (giving the voucher date in the context)
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled and line.move_line_id.currency_id.id == voucher_currency:
                    sign = voucher_brw.type in ('payment', 'purchase') and -1 or 1
                    foreign_currency_diff = sign * line.move_line_id.amount_residual_currency + amount_currency

            move_line['amount_currency'] = amount_currency
            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]

            if not currency_obj.is_zero(cr, uid, voucher_brw.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0],context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change')+': '+(line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.voucher_id.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': -1 * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                }
                new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)

            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
        return (tot_line, rec_lst_ids)    

    def action_budget_payment(self, cr, uid, ids, context=None):
        """
        Metodo que implementa la aplicacion de pago
        presupuestario.
        REVISAR: la aplicacion presupuestaria. -- PAGADO
        """
#        budget_item_obj = self.pool.get('budget.item')
#        log_obj = self.pool.get('budget.item.log')
#        for this in self.browse(cr, uid, ids):
#            for line in this.line_dr_ids:
#                pagado = 0
                #si hay certificacion
#                if line.budget_id:
#                    budget_item = budget_item_obj.browse(cr, uid, line.budget_id.id)
#                    pagado = budget_item.paid_amount + line.amount
#                    budget_item_obj.write(cr, uid, budget_item.id,{
#                        'paid_amount':pagado,
#                    })
#                    log_obj.create(cr, uid, {
#                        'budget_log_id':budget_item.id,
#                        'aplicacion':'Pagado',
#                        'date':time.strftime('%Y-%m-%d'),
#                        'monto':pagado,
#                    })
        return True

    

    def cancel_voucher(self, cr, uid, ids, context=None):
        reconcile_pool = self.pool.get('account.move.reconcile')
        move_pool = self.pool.get('account.move')

        for voucher in self.browse(cr, uid, ids, context=context):
            recs = []
            for line in voucher.move_ids:
                if line.reconcile_id:
                    recs += [line.reconcile_id.id]
                if line.reconcile_partial_id:
                    recs += [line.reconcile_partial_id.id]

            reconcile_pool.unlink(cr, uid, recs)

            if voucher.move_id:
                move_pool.button_cancel(cr, uid, [voucher.move_id.id])
                move_pool.unlink(cr, uid, [voucher.move_id.id],1)
        res = {
            'state':'cancel',
            'move_id':False,
            'pay_states':False,
        }
        self.write(cr, uid, ids, res)
        return True    

    
    def change_pay_state(self, cr, uid, voucher):       
        if voucher:        
            for lines in voucher.line_ids:
                if lines.move_line_id.move_id:
                    ids=self.pool.get('account.voucher').search(cr,uid,[('move_id','=',lines.move_line_id.move_id.id),('type','=','sale')])
                    pay_state = (lines.amount == lines.amount_unreconciled)
                    if pay_state==True:
                        self.write(cr, uid, ids, {'pay_states': pay_state})  
                    if pay_state==False:
                        if lines.amount > lines.amount_unreconciled:
                            raise osv.except_osv('Error', u'Valor total mayor al saldo pendiente')
#                        else:
#                            if lines.amount==0:
#                                raise osv.except_osv('Error', u'Valor total debe ser mayor a cero 0')
#                            else:
#                                self.write(cr, uid, ids, {'pay_states': pay_state})
        return True
    
    
    def _get_type_budget(self, cr, uid, context=None):
        if context is None:
            context = {}        
        if  context.get('type', False) in ('purchase', 'payment'):            
            return []
        if  context.get('type', False) in ('sale','receipt'):
            budget_certificate=self.pool.get('budget.certificate').search(cr, uid, [('accured','=',False),('state','=','compromised'),('project_id.type_budget','=','ingreso')])           
            return budget_certificate[0]
    
    def date_ind(self, cr, uid, voucher):
        date_voucher=voucher.date
        if voucher.line_ids[0]:
            date_invoice=voucher.line_ids[0].date_original     
        if date_voucher==date_invoice:
            self.write(cr, uid, [voucher.id], {
                'date_ind': False,                
            })   
        else:              
            self.write(cr, uid, [voucher.id], {
                'date_ind': True,            
            })
                        
    def _check_lines(self, cr, uid, context=None):
        if context is None:
            context = {}        
        if  context.get('type', False) in ('receipt', 'payment'):            
            return False
        if  context.get('type', False) in ('sale','purchase'):                       
            return True
        
    _columns = {
        'rule_id':fields.many2one('hr.salary.rule','Regla Salarial'),
        'internal_type' : fields.selection([('AS','Anticipo Sueldo'),('AP','Anticipo Proveedor')],
                                           'Tipo Interno'),
        'doc_reference' : fields.char('Doc. Referencia',size=64),
        'certificate_id': fields.many2one('budget.certificate',
                                          string='Compromiso presupuestario',
                                          domain=[('state','=','compromised')],
                                          required=False,
                                          readonly=True, states={'draft': [('readonly',False)]}),
         'date_ind': fields.boolean('Fecha Generacion'),
         'pay_states': fields.boolean('Pagado'),
         'ind_pay_doc': fields.boolean('Tipo doc'),
        }
    
    def _check_lines_unique(self, cr, uid, ids):  
        return True
        ## for obj in self.browse(cr, uid, ids):
        ##     if obj.ind_pay_doc==True:
        ##         if len(obj.line_ids)==1:
        ##             result = True
        ##         else:
        ##             result = False
        ##     else:
        ##         result = True                
        ## return result
    
    _defaults = {
        'doc_reference':'Proveedor',
        'date_ind': False,
        'pay_states': False,
        'ind_pay_doc':_check_lines,
        'type':'payment',
    }
    
    _constraints = [
        (_check_lines_unique,'Verifique que el documento tenga una sola línea en el Detalle de Ventas',['Detalle de Ventas']),
        ]
