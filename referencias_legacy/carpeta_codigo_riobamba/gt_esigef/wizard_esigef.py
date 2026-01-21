# -*- coding: utf-8 -*-
##############################################################################

import time
import csv
import base64
import StringIO

from osv import osv, fields

class WizardEsigefTemplate(osv.TransientModel):
    _inherit = 'account.common.report'
    _name = 'esigef.template'

    def onchange_period_from(self, cr, uid, ids, period):
        return {'value': {'period_to': period} }    

    def build_datas(self, cr, uid, ids, context=None):
        datas = {}
        wiz = self.browse(cr, uid, ids[0])
        datas['form'] = self.read(cr, uid, ids,
                                 ['date_from',  'date_to',  'fiscalyear_id',
                                  'journal_ids', 'period_from', 'period_to',
                                 'filter',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return datas

        
    _columns = {
        'level': fields.selection([('5','5')], string='Nivel',
                                  required=True,
                                  help="Nivel requerido por el Ministerio de Finanzas"),
        'data': fields.binary('Archivo de Texto', filters="*.txt"),
        'separator': fields.char('Separador', size=1, required=True,
                                 help="El valor por defecto es '|'."),
        'state': fields.selection([('init', 'init'),
                                   ('done', 'done')], string='Estado'),
        'filename': fields.char('Nombre de archivo', size=64, required=True, readonly=True),
        }

    _defaults = {
        'state': 'init',
        'level': '5',
        'separator': '|',
        'filename': '/',
        }


class WizardAccountInitial(osv.TransientModel):
    """
    el tipo de archivo es .TXT
    el separador de texto en el archivo es '|'
    el archivo no tiene fila de titulos ni totales al final
    el archivo tiene 6 columnas
    4 columnas son texto, 2 columnas son numericas separador decimal '.'
    Defincion de columnas:
      * col 1: PERIODO, rango [1,2,3,4,5,6,7,8,9,10,11,12]
      * col 2: Codigo del mayor de la cuenta contable
      * col 3: Codigo de la cuenta nivel 1
      * col 4: codigo de la cuenta nivel 2
      * col 5: saldo inicial deudor
      * col 6: saldo inicial acreedor
    Segun especificacion, son las cuentas de nivel 5
    CHECK: nivel de cuentas a leer
    """
    _inherit = 'esigef.template'
    _name = 'esigef.account.initial'

    def action_export_file(self, cr, uid, ids, context=None):
        datas = {}
        account_obj = self.pool.get('account.account')
        wiz = self.browse(cr, uid, ids[0])
        datas['form'] = self.read(cr, uid, ids,
                                 ['date_from',  'date_to',  'fiscalyear_id',
                                  'journal_ids', 'period_from', 'period_to',
                                 'filter',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, datas, context=context)
        used_context['period_from'] = datas['form']['period_from']
        used_context['period_to'] = datas['form']['period_to']
        used_context['fiscalyear_id'] =datas['form']['fiscalyear_id']
        account_ids = account_obj.search(cr, uid, [('level','=', wiz.level)])
        data = []
        for account in account_obj.read(cr, uid, account_ids, ['code', 'name', 'debit', 'credit'], context=used_context):
            if account['debit'] == 0 and account['credit'] == 0:
                continue
            code = account['code'].split('.')
            data.append(['1', ''.join(code[:3]), str(int(code[3])), str(int(code[4])), '%.2f'%account['debit'], '%.2f'%account['credit']])
        open_initial = StringIO.StringIO() 
        writer = csv.writer(open_initial, delimiter='|')
        writer.writerows(data)
        out = base64.encodestring(open_initial.getvalue())
        open_initial.close()
        name = 'APERTURA INICIAL %s %s.txt' % (wiz.company_id.name, wiz.fiscalyear_id.name)
        self.write(cr, uid, ids, {'state': 'done', 'data': out, 'filename': name})
        return True


class WizardAccountBalance(osv.TransientModel):
    """
    el tipo de archivo es .TXT
    el separador de texto en el archivo es '|'
    el archivo no tiene fila de titulos ni totales al final
    el archivo tiene 12 columnas
    4 columnas son texto, 8 columnas son numericas separador decimal '.'
    Definicion de columnas:
        * col 1: perido, rango [1,2,3,4,5,6,7,8,9,10,11,12]
        * col 2: codigo del mayor de la cuenta contable
        * col 3: codigo de la cuenta nivel 1
        * col 4: codigo de la cuenta nivel 2
        * col 5: saldo inicial deudor
        * col 6: saldo inicial acreedor
        * col 7: flujo deudor
        * col 8: flujo acreedor
        * col 9: sumas debe
        * col 10: sumas haber
        * col 11: saldo deudor
        * col 12: saldo acreedor        
    """
    _inherit = 'esigef.template'
    _name = 'esigef.account.balance'

    _defaults = {
        'filter': 'filter_period'
        }

    def action_export_file(self, cr, uid, ids, context=None):
        data = []
        datas = {}
        account_obj = self.pool.get('account.account')
        wiz = self.browse(cr, uid, ids[0])
        datas = self.build_datas(cr, uid, ids, context)
        #contexto para flujo
        used_context = self._build_contexts(cr, uid, ids, datas, context=context)
        #contexto para saldo inicial
        init_context = {}
        init_period_id = self.pool.get('account.period').search(cr, uid,
                                                [('fiscalyear_id','=', wiz.fiscalyear_id.id),
                                                ('special','=',True)], limit=1)[0]
        init_context['period_from'] = init_period_id
        init_context['period_to'] = init_period_id
        account_ids = account_obj.search(cr, uid, [('level','=', wiz.level)])
        for account in account_obj.read(cr, uid, account_ids, ['code', 'debit', 'credit', 'balance'], context=used_context):
            initial = account_obj.read(cr, uid, account['id'], ['debit', 'credit'], context=init_context)            
            code = account['code'].split('.')
            #sumas
            sum_debit = initial['debit'] + account['debit']
            sum_credit = initial['credit'] + account['credit']
            #saldos
            bl_debit = sum_debit>sum_credit and sum_debit or 0.00
            bl_credit = sum_credit>sum_debit and sum_credit or 0.00
            list_tmp = [wiz.period_from.name[:2],
                        ''.join(code[:3]), code[3], code[4],
                        initial['debit'], initial['credit'],
                        account['debit'], account['credit'],
                        sum_debit,
                        sum_credit,
                        bl_debit,
                        bl_credit]
            data.append(list_tmp)
        acc_balance = StringIO.StringIO() 
        writer = csv.writer(acc_balance, delimiter='|')
        writer.writerows(data)
        out = base64.encodestring(acc_balance.getvalue())
        acc_balance.close()
        name = 'BALANCE DE COMPROBACION %s - %s.txt' % (wiz.company_id.name, wiz.period_from.name)
        self.write(cr, uid, ids, {'state': 'done', 'data': out, 'filename': name})
        return True            
        

class WizardAccountTransfer(osv.TransientModel):
    """
    ** Transferencias recibidas **
    Ref: Pag 25
    el tipo de archivo es .TXT
    el separador de texto en el archivo es '|'
    el archivo no tiene fila de titulos ni totales al final
    el archivo tiene 9 columnas
    1-6,9 columnas son texto, cols 7,8 son numericas separador decimal '.'
    Definicion de columnas:
      * col 1: periodo rango [1,2,3,4,5,6,7,8,9,10,11,12]
      * col 2: Codigo del mayor de la cuenta contable
      * col 3: Codigo de la cuenta nivel 1
      * col 4: Codigo de la cuenta nivel 1
      * col 5: RUC receptor
      * col 6: RUC otorgante
      * col 7: flujo deudor
      * col 8: flujo acreedor
      * col 9: Cuenta monetaria, siempre 0

    Info en ERP:
    account.voucher, type: receipt|payment, extra_type: advances_custom|advances
    """
    _inherit = 'esigef.template'
    _name = 'esigef.account.transfer'

    _columns = {
        'partner_id': fields.many2one('res.partner',
                                      string='Tesorería de la Nación',
                                      required=True, readonly=True),
        }

    def _get_partner(self, cr, uid, context=None):
        return self.pool.get('res.partner').search(cr, uid, [('ced_ruc','=','9999999999996')], limit=1)[0]

    def _get_all_journal(self, cr, uid, context=None):
        return self.pool.get('account.journal').search(cr, uid ,[('type','=','bank')])

    _defaults = {
        'partner_id': _get_partner,
        'journal_ids': _get_all_journal
        }

    def action_export_file(self, cr, uid, ids, context=None):
        """
        Metodo de generacion de archivo plano segun especificacion
        tecnica.
        Info que representa transferencias en el ERP:
        account.voucher, type: receipt|payment,
                        extra_type: advances_custom|advances
        """
        partner_obj = self.pool.get('res.partner')
        voucher_obj = self.pool.get('account.voucher')
        wiz = self.browse(cr, uid, ids, context)[0]
        journal_ids = [j.id for j in wiz.journal_ids]
        #TODO: create data
        acc_transfer = StringIO.StringIO() 
        writer = csv.writer(acc_transfer, delimiter='|')
        writer.writerows(data)
        out = base64.encodestring(acc_transfer.getvalue())
        acc_transfer.close()
        name = 'TRANSFERENCIAS %s - %s.txt' % (wiz.company_id.name, wiz.period_from.name)
        self.write(cr, uid, ids, {'state': 'done', 'data': out, 'filename': name})
        return True        


class WizardBudgetInitial(osv.TransientModel):
    """
    ** Presupuesto Inicial **
    el tipo de archivo es .TXT
    el separador de texto en el archivo es '|'
    el archivo no tiene fila de titulos ni totales al final
    el archivo tiene 6 columnas
    1-5 columnas son texto, col 6 son numericas separador decimal '.'
    Definicion de columnas:
      * col 1: periodo en rango [1,2,3,4,5,6,7,8,9,10,11,12]
      * col 2: Tipo de presupuesto I=Ingreso, G=Gasto
      * col 3: Grupo
      * col 4: Subgrupo
      * col 5: item
      * col 6: valor
    Partida: 510101:
      * digito 1,2: grupo
      * digito 3,4: subgrupo
      * digito 5,6: item
    Ingresos:
     * 1 Corriente
     * 2 Capital
     * 3 Financiamiento
    Gastos:
     * 5 Corriente
     * 6 Producción
     * 7 Inversión
     * 8 Capital
     * 9 Aplicacion del financiamiento
    """
    _inherit = 'esigef.template'
    _name = 'esigef.budget.initial'
    _columns = {
        'budget_id': fields.many2one('budget.poa',
                                     string='Presupuesto a Consultar',
                                     required=True),
        }

    def action_export_file(self, cr, uid, ids, context=None):
        data = []
        budget_obj = self.pool.get('crossovered.budget')
        wiz = self.browse(cr, uid, ids[0])
        period = '1'#wiz.period_from.name[:2] CHECK
        datas = {}
        for line in wiz.budget_id.crossovered_budget_line:
            type_budget = line.type_budget=='gasto' and 'G' or 'I'
            code_tmp = line.code
            c, t, code = code_tmp.split('.')
            if not datas.get(code):
                datas.update({code: [0, type_budget]})
            datas[code][0] += line.planned_amount
        for code in sorted(datas):
            grupo = code[:2]
            subgrupo = code[2:4]
            item = code[4:6]
            data.append([period, datas[code][1], str(int(grupo)), str(int(subgrupo)), str(int(item)), '%.2f'%datas[code][0]])
        budget_buf = StringIO.StringIO() 
        writer = csv.writer(budget_buf, delimiter='|')
        writer.writerows(data)
        out = base64.encodestring(budget_buf.getvalue())
        budget_buf.close()
        fname = 'PRESUPUESTO INICIAL %s - %s.txt' % (wiz.company_id.name, wiz.fiscalyear_id.name)        
        self.write(cr, uid, ids, {'state': 'done', 'data': out, 'filename': fname})
        return True


class WizardBudgetBalance(osv.TransientModel):
    """
    TODO:
    """
    _inherit = 'esigef.template'
    _name = 'esigef.budget.balance'
