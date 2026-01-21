# -*- coding: utf-8 -*-
##############################################################################
#
# Mario Chogllo
# mariofchogllo@gmail.com
#
##############################################################################

__author__ = 'Mario Chogllo & Diego Abad'

import time
from datetime import datetime

from osv import osv, fields
from tools import ustr

from dateutil.relativedelta import relativedelta
from operator import itemgetter

import netsvc
import pooler
import decimal_precision as dp
from tools.translate import _

import pdb

class accPeriod(osv.Model):
    _inherit = 'account.period'
    _columns = dict(
        total_cierre = fields.integer('Total Cierres'),
        data_balance = fields.binary('Archivo de Balance', filters="*.txt"),
        data_cedulas = fields.binary('Archivo de Cedulas', filters="*.txt"),
        data_transferencias = fields.binary('Archivo de Transferencias', filters="*.txt"),
    )
accPeriod()

class account_retention_cache(osv.osv):

    _name = 'account.retention.cache'

    def get_number(self, cr, uid, id):
        obj = self.browse(cr, uid, int(id))
        number = obj.name
        self.write(cr, uid, int(id), {'active': False})
        return number

    _columns = {
        'name': fields.char('Numero a Reservar', size=32, readonly=True),
        'active': fields.boolean('Activo', readonly=True),
        }

    _defaults = {
        'active': True,
        }


#class AccountFiscalPosition(osv.Model):
#    _inherit = 'account.fiscal.position'
#
#    def map_tax(self, cr, uid, fposition_id, taxes, context=None):
#        if context is None:
#            context = {}
#        if not taxes:
#            return []
#        if not fposition_id:
#            return map(lambda x: x.id, taxes)
#        result = []
#        budget = context.get('budget_type', False)
#        for t in taxes:
#            ok = False
#            if budget and not t.tax_group=='vat' and not t.budget == budget:
#                continue
#            for tax in fposition_id.tax_ids:
#                if tax.tax_src_id.id == t.id:
#                    if tax.tax_dest_id:
#                        result.append(tax.tax_dest_id.id)
#                    ok=True
#            if not ok:
#                result.append(t.id)
#        return result


class AccountAccount(osv.osv):

    _inherit = 'account.account'

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        try:
            if name and str(name).startswith('partner:'):
                part_id = int(name.split(':')[1])
                part = self.pool.get('res.partner').browse(cr, user, part_id, context=context)
                args += [('id', 'in', (part.property_account_payable.id, part.property_account_receivable.id))]
                name = False
            if name and str(name).startswith('type:'):
                type = name.split(':')[1]
                args += [('type', '=', type)]
                name = False
        except:
            pass
        if name:
            ids = self.search(cr, user, [('code', '=like', name+"%")]+args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('code_aux', '=like', name+"%")]+args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('shortcut', '=', name)]+ args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit)
            if not ids and len(name.split()) >= 2:
                #Separating code and name of account for searching
                operand1,operand2 = name.split(' ',1) #name can contain spaces e.g. OpenERP S.A.
                ids = self.search(cr, user, [('code', operator, operand1), ('name', operator, operand2)]+ args, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)

    def _check_allow_type_change(self, cr, uid, ids, new_type, context=None):
        group1 = ['payable', 'receivable', 'other']
        group2 = ['consolidation','view']
        line_obj = self.pool.get('account.move.line')
        for account in self.browse(cr, uid, ids, context=context):
            old_type = account.type
            account_ids = self.search(cr, uid, [('id', 'child_of', [account.id])])
            if line_obj.search(cr, uid, [('account_id', 'in', account_ids)]):
                #Check for 'Closed' type
                if old_type == 'closed' and new_type !='closed':
                    raise osv.except_osv(_('Warning !'), _("You cannot change the type of account from 'Closed' to any other type which contains journal items!"))
                #Check for change From group1 to group2 and vice versa
#                if (old_type in group1 and new_type in group2) or (old_type in group2 and new_type in group1):
#                    raise osv.except_osv(_('Warning !'), _("You cannot change the type of account from '%s' to '%s' type as it contains journal items!") % (old_type,new_type,))
        return True

    def onchange_parent(self, cr, uid, ids, parent_id,code_aux):
        if not code_aux:
            res = {'value': {}}
            account_obj = self.pool.get('account.account')
            parent = account_obj.browse(cr, uid, parent_id)
            hijas_ids = account_obj.search(cr,uid, [('parent_id','=',parent_id)],order='code desc')
            if hijas_ids:
                hija_last = account_obj.browse(cr, uid, hijas_ids[0])
                code_aux = int(hija_last.code)+1
                res['value']['code_aux'] = code_aux
            return res    

    def _check_type(self, cr, uid, ids, context=None):
        return True
    
    def _check_account_type(self, cr, uid, ids, context=None):
        return True

    def _get_code(self, cr, uid, ids, name, args, context=None):
        result = {}
        for account in self.browse(cr, uid, ids,context):
            aux1 = account.code_aux.replace(".","")
            result[account.id] = aux1.replace(" ","")
        return result

    def _get_codeint(self, cr, uid, ids, name, args, context=None):
        result = {}
        for account in self.browse(cr, uid, ids,context):
            aux1 = account.code_aux.replace(".","")
            result[account.id] = int(aux1.replace(" ",""))
        return result

    def _checkPay(self, cr, uid, ids, context=None):
        result = True
        for this in self.browse(cr, uid, ids):
            if this.id == this.account_rec_id.id:
                result = False
            elif this.id == this.account_pay_id.id:
                result = False
        return result
        

    def _checkCode(self, cr, uid, ids, context=None):
        result = False
        #max diferencia de tamanios 4
        for this in self.browse(cr, uid, ids):
            print "CODIGOOOO", this.code_aux
            code_sin_punto = this.code_aux.replace('.','')
#            code_sin_punto = code_sin_punto_aux.replace(' ','')
            if not code_sin_punto.isnumeric():
                raise osv.except_osv('Error de usuario','EL codigo debe contener solo numeros y no debe tener espacios en blanco')
            if this.parent_id:
                aux_parent = this.parent_id.code.strip()
                aux_to = len(aux_parent)
                aux_hija = this.code_aux.replace('.','')[0:aux_to].strip()
                diferencia = len(this.code_aux.replace('.','')) - len(this.parent_id.code_aux.replace('.',''))
                if (aux_parent==aux_hija) and (diferencia<=4):
                    result=True
            else:
                raise osv.except_osv('Error de usuario','La cuenta debe pertenecer a una cuenta de mayor o padre.')
        return result

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        if ids[0]:
            reads = self.read(cr, uid, ids, ['name', 'code_aux'], context=context)
            res = []
            for record in reads:
                name = record['name']
                if record['code_aux']:
                    name = record['code_aux'] + ' ' + name
                res.append((record['id'], name))
        return res

    _columns = {
#        'parent_id': fields.many2one('account.account', 'Parent', ondelete='cascade'),
        'tercero_id':fields.many2one('account.account','Cuenta Fondo Tercero'),
        'anterior_id':fields.many2one('account.account','Anio Anterior(212..)'),
        'partner_id':fields.many2one('res.partner','Institucion a Pagar'),
        'code_aux': fields.char('Codigo', size=64, required=True, select=1),
        'code': fields.function(_get_code, 'Codigo interno', method=True, store=True, type='char'),
        #'codeint': fields.function(_get_codeint, 'Codigo int', method=True, store=True, type='integer'),
        #Revisar que cuando se haga un movimiento contable se agrege la cuenta complementaria
        'in_stock': fields.boolean('Afecta en Stock'),
        'account_comp_id': fields.many2one('account.account', 'Cuenta Complementaria',help="Utilizada para complementar movimientos contables para gobierno."),
        'account_p_ids': fields.many2many('account.account', 'account_pay_rel', 'acc_id', 'pay_id', 'Cuentas por Pagar'),
        'account_c_ids': fields.many2many('account.account', 'account_cob_rel', 'acc_id', 'rec_id', 'Cuentas por Cobrar'),
        }
    _constraints = [
        (_checkPay, 'Error de configuracion! \nNo puede ser la misma cuenta por pagar o cobrar que la cuenta actual! ', ['code']),
        (_checkCode, 'Error de configuracion! \nVerifique la cuenta padre o de mayor! ', ['code']),
         (_check_type, 'Configuration Error! \nYou can not define children to an account with internal type different of "View"! ', ['type']),
        (_check_account_type, 'Configuration Error! \nYou can not select an account type with a deferral method different of "Unreconciled" for accounts with internal type "Payable/Receivable"! ', ['user_type','type']),
    ]

class AccountAuthorisation(osv.osv):

    _name = 'account.authorisation'
    _description = 'Authorisation for Accounting Documents'
    _order = 'expiration_date desc'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = '%s (%s-%s)' % (record.name, record.num_start, record.num_end)
            res.append((record.id, name))
        return res        
    
    def _check_active(self, cr, uid, ids, name, args, context):
        """
        Check the due_date to give the value active field
        """
        res = {}
        objs = self.browse(cr, uid, ids)
        now = datetime.strptime(time.strftime("%Y-%m-%d"),'%Y-%m-%d')
        for item in objs:
            if item.is_electronic == False:
                due_date = datetime.strptime(item.expiration_date, '%Y-%m-%d')
                res[item.id] = now<due_date
            else:
                res[item.id] = True
        return res
  
    def _get_type(self, cursor, uid, context):
        return context.get('type', 'in_invoice')
    
    def _get_in_type(self, cursor, uid, context):
        return context.get('in_type', 'externo')

    def _get_partner(self, cursor, uid, context):
        if context.get('partner_id', False):
            return context.get('partner_id')
        else:
            user = self.pool.get('res.users').browse(cursor, uid, uid)
            return user.company_id.partner_id.id

    def create(self, cr, uid, values, context=None):
        partner_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.id
        if values.has_key('partner_id') and partner_id == values['partner_id']:
            ats_obj = self.pool.get('account.ats.doc')
            name_type = ats_obj.read(cr, uid, values['type_id'], ['name'])['name']
            code_obj = self.pool.get('ir.sequence.type')
            seq_obj = self.pool.get('ir.sequence')
            code_data = {
                'code': '%s.%s.%s' % (values['name'],values['serie_entidad'],values['serie_emision']),
                'name': name_type,
                }
            code_id = code_obj.create(cr, uid, code_data)
            seq_data = {'name': name_type,
                        'padding': 9,
                        'number_next': values['num_start']}
            seq_id = seq_obj.create(cr, uid, seq_data)
            values.update({'sequence_id': seq_id})
        return super(AccountAuthorisation, self).create(cr, uid, values, context)


    def unlink(self, cr, uid, ids, context=None):
        type_obj = self.pool.get('ir.sequence.type')
        for obj in self.browse(cr, uid, ids, context):
            aux = obj.sequence_id.code
            self.pool.get('ir.sequence').unlink(cr, uid, obj.sequence_id.id)
        return super(AccountAuthorisation, self).unlink(cr, uid, ids, context)

    _columns = {
        'name' : fields.char('Num. de Autorizacion', size=128, required=True),
        'serie_entidad' : fields.char('Establecimiento', size=3),
        'serie_emision' : fields.char('Punto Emision', size=3),
        'num_start' : fields.integer('Desde'),
        'num_end' : fields.integer('Hasta'),
        'is_electronic': fields.boolean('Electrónica?'),
        'emision_date': fields.date('Fecha Emision'),
        'expiration_date' : fields.date('Fecha Vencimiento'),
        'active' : fields.function(_check_active, string='Activo',
                                   method=True, type='boolean'),
        'in_type': fields.selection([('interno', 'Internas'),
                                     ('externo', 'Externas')],
                                    string='Tipo Interno',
                                    readonly=True,
                                    change_default=True),
        'type_id': fields.many2one('account.ats.doc', 'Tipo de Comprobante', required=True),
        'partner_id' : fields.many2one('res.partner', 'Empresa', required=True),
        'sequence_id' : fields.many2one('ir.sequence', 'Secuencia',
                                        help='Secuencia Alfanumerica para el documento, se debe registrar cuando pertenece a la compañia'),
        }


    def _checkNumeroAut(self, cr, uid, ids):
        auth_obj = self.pool.get('account.authorisation')
        for this in self.browse(cr, uid, ids):
            auth_ids = auth_obj.search(cr, uid,[('name','=',this.name),('partner_id','=',this.partner_id.id),('id','!=',ids[0])])
            if not this.name.isdigit():
                raise osv.except_osv('Error de usuario','El numero de autorizacion no deben contener caracteres.')
            else:
                if not int(this.name)>0:
                    raise osv.except_osv('Error de usuario','El numero de autorizacion debe ser mayor a cero.')
#            if len(auth_ids)>0:
#                raise osv.except_osv('Error de usuario','El numero de autorizacion debe ser unico por proveedor.')
            if not this.serie_entidad.isdigit():
                raise osv.except_osv('Error de usuario','El numero de establecimiento no deben contener caracteres.')
            else:
                if not int(this.serie_entidad)>0:
                    raise osv.except_osv('Error de usuario','El numero de establecimiento debe ser mayor a cero.')
            if not this.serie_emision.isdigit():
                raise osv.except_osv('Error de usuario','Los puntos de emision no deben contener caracteres.')
            else:
                if not int(this.serie_emision)>0:
                    raise osv.except_osv('Error de usuario','El punto de emision debe ser mayor a cero.')
        return True

    _constraints = [
        (_checkNumeroAut,
         ustr('Verifique los numeros de la autorizacion.'),[ustr('Numero'), 'Numero']),
    ]

    def set_authorisation(cr, uid, ids, context):
        return True

    _defaults = {
        'active': False,
        'in_type': _get_in_type,
        'partner_id': _get_partner,
        }

    _sql_constraints = [
        ('number_unique',
         'unique(name,partner_id)',
         u'La autorizacion debe ser única.'),
        ]

    def is_valid_number(self, cr, uid, id, number):
        """
        Metodo que verifica si @number esta en el rango
        de [@num_start,@num_end]
        """
        obj = self.browse(cr, uid, id)
        if obj.num_start <= number <= obj.num_end:
            return True
        return False

AccountAuthorisation()


class account_journal(osv.osv):

    _name = 'account.journal'
    _inherit = 'account.journal'

    _columns = {
        'auth_id': fields.many2one('account.authorisation', help='Autorización utilizada para Facturas de Venta y Liquidaciones de Compra',
                                   string='Autorización', domain="[('in_type','=','interno')]"),
        'auth_ret_id': fields.many2one('account.authorisation', domain="[('in_type','=','interno')]",
                                       string='Autorización de Ret.',
                                       help='Autorizacion utilizada para documentos de retención en Facturas de Proveedor y Liquidaciones de Compra')
        }

account_journal()

class presp_ref_aplication(osv.Model):
    _name = 'presp.ref.aplication'
    _columns = dict(
        name = fields.char('Aplicación',size=32),
        )
presp_ref_aplication()

class account_tax_map(osv.Model):
    _name = 'account.tax.map'
    _columns = dict(
        tax_id = fields.many2one('account.tax','Impuesto'),
        budget = fields.char('Partida', size=2),
        account_id = fields.many2one('account.account','Cta. x Pagar',required=True),
        account_id2 = fields.many2one('account.account','Cta. Fondo Teceros'),
        )
account_tax_map()

class account_tax(osv.osv):
    
    _name = 'account.tax'
    _inherit = 'account.tax'
    _order = 'tax_group desc'

    def _compute(self, cr, uid, taxes, price_unit, quantity, address_id=None, product=None, partner=None):
        """
        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.

        RETURN:
            [ tax ]
            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
            one tax for each tax id in IDS and their children
        """
        res = self._unit_compute(cr, uid, taxes, price_unit, address_id, product, partner, quantity)
        total = 0.0
        precision_pool = self.pool.get('decimal.precision')
        for r in res:
            if r.get('balance',False):
                r['amount'] = (r.get('balance', 0.0) * quantity) - total
            else:
                #aqui hace el round
                r['amount'] = r.get('amount', 0.0) * quantity
                #r['amount'] = round(r.get('amount', 0.0) * quantity, precision_pool.precision_get(cr, uid, 'Account'))
                total += r['amount']
        return res

    def copy_data(self, cr, uid, id, default=None, context=None):
        """
        Redefinicion para permitir duplicar los impuestos
        """        
        data = super(account_tax, self).copy_data(cr, uid, id, default, context)
        data['name'] = data['name'] + '(copia)'
        return data

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for record in self.read(cr, uid, ids, ['description','name','budget','porcentaje'], context=context):
            texto = record['name']
            perc = record['porcentaje'] and record['porcentaje'] or '0'
            name = ' '.join([texto,'(',perc,"% ",')']) 
            res.append((record['id'],name ))
        return res    

    def _unit_compute(self, cr, uid, taxes, price_unit, address_id=None, product=None, partner=None, quantity=0):
        taxes = self._applicable(cr, uid, taxes, price_unit, address_id, product, partner)
        res = []
        cur_price_unit=price_unit
        obj_partener_address = self.pool.get('res.partner.address')
        for tax in taxes:
            # we compute the amount for the current tax object and append it to the result
            data = {'id':tax.id,
                    'name':tax.description and tax.description + " - " + tax.name or tax.name,
                    'account_collected_id':tax.account_collected_id.id,
                    'account_paid_id':tax.account_paid_id.id,
                    'base_code_id': tax.base_code_id.id,
                    'ref_base_code_id': tax.ref_base_code_id.id,
                    'sequence': tax.sequence,
                    'base_sign': tax.base_sign,
                    'tax_sign': tax.tax_sign,
                    'ref_base_sign': tax.ref_base_sign,
                    'ref_tax_sign': tax.ref_tax_sign,
                    'price_unit': cur_price_unit,
                    'tax_code_id': tax.tax_code_id.id,
                    'ref_tax_code_id': tax.ref_tax_code_id.id,
                    'tax_group': tax.tax_group,
            }
            res.append(data)
            if tax.type=='percent':
                amount = cur_price_unit * tax.amount
                data['amount'] = amount

            elif tax.type=='fixed':
                data['amount'] = tax.amount
                data['tax_amount']=quantity
               # data['amount'] = quantity
            elif tax.type=='code':
                address = address_id and obj_partener_address.browse(cr, uid, address_id) or None
                localdict = {'price_unit':cur_price_unit, 'address':address, 'product':product, 'partner':partner}
                exec tax.python_compute in localdict
                amount = localdict['result']
                data['amount'] = amount
            elif tax.type=='balance':
                data['amount'] = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)
                data['balance'] = cur_price_unit

            amount2 = data.get('amount', 0.0)
            if tax.child_ids:
                if tax.child_depend:
                    latest = res.pop()
                amount = amount2
                child_tax = self._unit_compute(cr, uid, tax.child_ids, amount, address_id, product, partner, quantity)
                res.extend(child_tax)
                if tax.child_depend:
                    for r in res:
                        for name in ('base','ref_base'):
                            if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
                                r[name+'_code_id'] = latest[name+'_code_id']
                                r[name+'_sign'] = latest[name+'_sign']
                                r['price_unit'] = latest['price_unit']
                                latest[name+'_code_id'] = False
                        for name in ('tax','ref_tax'):
                            if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
                                r[name+'_code_id'] = latest[name+'_code_id']
                                r[name+'_sign'] = latest[name+'_sign']
                                r['amount'] = data['amount']
                                latest[name+'_code_id'] = False
            if tax.include_base_amount:
                cur_price_unit+=amount2
        return res    

    def _unit_compute_inv(self, cr, uid, taxes, price_unit, address_id=None, product=None, partner=None):
        taxes = self._applicable(cr, uid, taxes, price_unit, address_id, product, partner)
        obj_partener_address = self.pool.get('res.partner.address')
        res = []
        taxes.reverse()
        cur_price_unit = price_unit

        tax_parent_tot = 0.0
        for tax in taxes:
            if (tax.type=='percent') and not tax.include_base_amount:
                tax_parent_tot += tax.amount

        for tax in taxes:
            if (tax.type=='fixed') and not tax.include_base_amount:
                cur_price_unit -= tax.amount

        for tax in taxes:
            if tax.type=='percent':
                if tax.include_base_amount:
                    amount = cur_price_unit - (cur_price_unit / (1 + tax.amount))
                else:
                    amount = (cur_price_unit / (1 + tax_parent_tot)) * tax.amount

            elif tax.type=='fixed':
                amount = tax.amount

            elif tax.type=='code':
                address = address_id and obj_partener_address.browse(cr, uid, address_id) or None
                localdict = {'price_unit':cur_price_unit, 'address':address, 'product':product, 'partner':partner}
                exec tax.python_compute_inv in localdict
                amount = localdict['result']
            elif tax.type=='balance':
                amount = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)

            if tax.include_base_amount:
                cur_price_unit -= amount
                todo = 0
            else:
                todo = 1
            res.append({
                'id': tax.id,
                'todo': todo,
                'name': tax.name,
                'amount': amount,
                'account_collected_id': tax.account_collected_id.id,
                'account_paid_id': tax.account_paid_id.id,
                'base_code_id': tax.base_code_id.id,
                'ref_base_code_id': tax.ref_base_code_id.id,
                'sequence': tax.sequence,
                'base_sign': tax.base_sign,
                'tax_sign': tax.tax_sign,
                'ref_base_sign': tax.ref_base_sign,
                'ref_tax_sign': tax.ref_tax_sign,
                'price_unit': cur_price_unit,
                'tax_code_id': tax.tax_code_id.id,
                'ref_tax_code_id': tax.ref_tax_code_id.id,
                'tax_group': tax.tax_group,
            })
            if tax.child_ids:
                if tax.child_depend:
                    del res[-1]
                    amount = price_unit

            parent_tax = self._unit_compute_inv(cr, uid, tax.child_ids, amount, address_id, product, partner)
            res.extend(parent_tax)

        total = 0.0
        for r in res:
            if r['todo']:
                total += r['amount']
        for r in res:
            r['price_unit'] -= total
            r['todo'] = 0
        return res

    _columns = {
        'account_id':fields.many2one('account.account','Cta. por Pagar Fondo Tercero'),
        'tax_company_id': fields.many2one('res.partner', 'SRI Partner',
                                          help="Este partner se aplicará en asiento contables de facturas"),
        'tax_map_ids' : fields.one2many('account.tax.map','tax_id','Cuentas Contables'),
        'porcentaje': fields.char('Porcentaje', size=128),
        'budget': fields.selection([('corriente','CORRIENTE'),
                                    ('inversion','INVERSION'),
                                    ('general','GENERAL'),
                                    ('ogastos','OTROS GASTOS (CORRIENTE)'),
                                    ('opublica','OBRAS PUBLICAS (INVERSION)'),
                                    ('ginversion', 'GASTOS DE INVERSION'),
                                    ('tranf','TRANSF. DE INVERSION'),
                                    ('bienesld','BIENES DE LARGA DURACION (INVERSION)')],
                                   string='Aplicacion Presupuestaria.'),
        'apply_budget': fields.boolean('Afectar Presupuesto?'),
        'tax_group' : fields.selection([('vat','IVA Diferente de 0%'),
                                        ('vat0','IVA 0%'),
                                        ('novat','No objeto de IVA'),
                                        ('ret_vat_b', 'Retención de IVA (Bienes)'),
                                        ('ret_vat_srv', 'Retención de IVA (Servicios)'),
                                        ('ret_ir', 'Ret. Imp. Renta'),
                                        ('no_ret_ir', 'No sujetos a Ret. de Imp. Renta'), 
                                        ('imp_ad', 'Imps. Aduanas'),
                                        ('ice', 'ICE'),
                                        ('other','Otro/Complemento')], 'Grupo', required=True),
        }

    _defaults = {
        'tax_group': 'vat',
        'budget': 'corriente',
        }

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        """
        hijacking: read, browse
        TODO: test test test
        Si lee los campos de cuentas devuelva los IDs segun el campo de contexto
        o los que son por defecto.
        browse, llama a read para fields_values
        CHECK: run SQL to avoid recurssion
        """
        if fields is None:
            fields=[]
        select = ids
        if isinstance(ids, (int, long)):
            select = [ids]
        res = super(account_tax, self).read(cr, uid, select, fields=fields, context=context, load=load)
        if context is None:
            context = {}
        if context.get('budget', False) and 'account_collected_id' in fields or 'account_paid_id' in fields:
            for record in res:
                cr.execute("SELECT account_id FROM account_tax_map WHERE tax_id=%s AND budget='%s'" % (record['id'], context.get('budget_type')))
                result = cr.fetchall()
                if result:
                    record['account_collected_id'] = result[0]
        if isinstance(ids, (int, long)):
            if res:
                return res[0]
            else:
                return False
        return res

account_tax()


class account_tax_template(osv.Model):
    
    _name = 'account.tax.template'
    _inherit = 'account.tax.template'
    
    _columns = {
        'tax_group' : fields.selection([('iva0','IVA 0% x'),('noiva','No objeto de IVA x'),('ret', 'Retención x'),
                                        ('vat','IVA Diferente de 0%'),
                                        ('vat0','IVA 0%'),
                                        ('novat','No objeto de IVA'),
                                        ('ret_vat', 'Retención de IVA'),
                                        ('ret_ir', 'Ret. Imp. Renta'), 
                                        ('no_ret_ir', 'No sujetos a Ret. de Imp. Renta'), 
                                        ('imp_ad', 'Imps. Aduanas'), 
                                        ('other','Other')], 'Grupo', required=True),
        }

    _defaults = {
        'tax_group': 'vat',
        }

account_tax()


class account_tax_template(osv.Model):
    
    _name = 'account.tax.template'
    _inherit = 'account.tax.template'
    
    _columns = {
        'tax_group' : fields.selection([('iva0','IVA 0% x'),('noiva','No objeto de IVA x'),('ret', 'Retención x'),
                                        ('vat','IVA Diferente de 0%'),
                                        ('vat0','IVA 0%'),
                                        ('novat','No objeto de IVA'),
                                        ('ret_vat', 'Retenciónde IVA'),
                                        ('ret_ir', 'Ret. Imp. Renta'), 
                                        ('no_ret_ir', 'No sujetos a Ret. de Imp. Renta'), 
                                        ('imp_ad', 'Imps. Aduanas'), 
                                        ('other','Other')], 'Grupo'),
        }

account_tax_template()

class partnerAccount(osv.Model):
    _name = 'partner.account'
    _columns = dict(
        p_id = fields.many2one('res.partner','Proveedor'),
        name = fields.char('Partida',size=2,required=True),
        account_id = fields.many2one('account.account','Cuenta',required=True),
    )
partnerAccount()

class Partner(osv.Model):
    
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Formulario de Partner para Ecuador'

    def unlink(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        for obj in self.browse(cr, uid, ids, context):
            move_ids = move_obj.search(cr, uid, [('partner_id','=',obj.id)])
            if move_ids:
                raise osv.except_osv('Aviso','No se permite borrar proveedores que estan en asientos contables.')
        res = super(Partner, self).unlink(cr, uid, ids, context)
        return res
    

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            if record.ced_ruc:
                name = record.ced_ruc + " - " + record.name
            else:
                name = record.name
            res.append((record.id, name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        if name:
            ids = self.search(cr, uid, [('ced_ruc', operator, name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def _check_mail(self, cr, uid, ids):
        result = False
        import re
        for partner in self.browse(cr, uid, ids):
            if partner.email:
                correo = partner.email
                if re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$',correo.lower()):
                    result = True
            else:
                result = True
        return result

    def _check_cedula(self, identificador):
        if len(identificador) == 13 and not identificador[10:13] == '001':
            return False
        else:
            if len(identificador) < 10:
                return False
        coef = [2,1,2,1,2,1,2,1,2]
        cedula = identificador[:9]
        suma = 0
        for c in cedula:
            val = int(c) * coef.pop()
            suma += val > 9 and val-9 or val
        result = 10 - ((suma % 10)!=0 and suma%10 or 10)
        if result == int(identificador[9:10]):
            return True
        else:
            return False

    def _check_ruc(self, partner):
        ruc = partner.ced_ruc
        if not len(ruc) == 13:
            return False
        if ruc[2:3] == '9':
            coef = [4,3,2,7,6,5,4,3,2,0]
            coef.reverse()
            verificador = int(ruc[9:10])
        elif ruc[2:3] == '6':
            coef = [3,2,7,6,5,4,3,2,0,0]
            coef.reverse()
            verificador = int(ruc[8:9])
        else:
            raise osv.except_osv('Error', 'Cambie el tipo de persona')
        suma = 0
        for c in ruc[:10]:
            suma += int(c) * coef.pop()
        result = 11 - (suma>0 and suma % 11 or 11)
        if result == verificador:
            return True
        else:
            return False

    def _check_unique(self, cr, uid, ids):
        partner_obj = self.pool.get('res.partner')
        for partner in self.browse(cr, uid, ids):
            partner_ids = partner_obj.search(cr, uid, [('ced_ruc','=',partner.ced_ruc)])
            if len(partner_ids)>1:
                raise osv.except_osv(('Aviso !'), 'Identificador es unico')
            else:
                return True

    def _check_ced_ruc(self, cr, uid, ids):
        return True
        for partner in self.browse(cr, uid, ids):
            if partner.type_ced_ruc == 'otro':
                return True
            if not partner.ced_ruc:
                return True
            if partner.type_ced_ruc == 'pasaporte':
                return True
            if partner.tipo_persona == '9':
                try:
                    ident=int(partner.ced_ruc)
                except ValueError:
                    raise osv.except_osv(('Aviso !'), 'RUC no puede contener caracteres')
                return self._check_ruc(partner)
            else:
                try:
                    ident=int(partner.ced_ruc)
                except ValueError:
                    raise osv.except_osv(('Aviso !'), 'Cedula no puede contener caracteres')
                return self._check_cedula(partner.ced_ruc)

    def _emp_name(self, cr, uid, ids, field_name, arg, context):
        employee_obj = self.pool.get('hr.employee')
        res = {}
        for partner in self.browse(cr, uid, ids):
            aux_name = ""
            employee_ids = employee_obj.search(cr, uid, [('name','=',partner.ced_ruc)],limit=1)
            if employee_ids:
                employee = employee_obj.browse(cr, uid, employee_ids[0])
                aux_name = employee.complete_name
            res[partner.id] = aux_name
        return res

    _columns = {
        'is_abonado_agua':fields.boolean('Abonado Agua'),
        'name_empleado':fields.function(_emp_name, method=True, string="Empleado Nombre", store=True, type="char",size=256), 
        'cxp_ids':fields.one2many('partner.account','p_id','Cuentas por pagar'),
        'ced_ruc': fields.char('Cedula/ RUC', size=13, required=True, help='Idenficacion o Registro Unico de Contribuyentes'),
        'type_ced_ruc': fields.selection([('cedula','Cedula'),
                                          ('ruc','RUC'),
                                          ('pasaporte','Pasaporte'),
                                          ('otro', 'OTRO')], 'Tipo ID', required=True),
        'tipo_persona': fields.selection([('6','Persona Natural'),('9','Persona Juridica')], 'Persona', required=True),
        'authorisation_ids': fields.one2many('account.authorisation', 'partner_id', 'Autorizaciones'),
        'legal_rep' : fields.char('Rep. Legal',size=256),
        'partner_incop_type' : fields.selection([('economia_popular','Economia popular y solidaria'),
                                                 ('micro','Micro'),
                                                 ('pequena','Pequena'),
                                                 ('mediana', 'Mediana'),
                                                 ('grande','Grande')], 'Tipo Empresa INCOP'),
        'ref' : fields.char('RUP',size=13),
        }

    _defaults = {
        'tipo_persona': '9',
        'partner_incop_type':'micro',
        'supplier':True,
        }

    _constraints = [
        (_check_ced_ruc, 'Error en su Cedula/RUC/Pasaporte', ['cedu_ruc']),
        (_check_mail, 'Error el mail no es valido', ['email']),
        (_check_unique, 'No puede registrar dos veces el mismo identidicador, este es unico', ['email']),
        ]

    _sql_constraints = [
        ('partner_unique', 'unique(ced_ruc)',  ustr('El identificador es único.')),
        ]

Partner()


class ResCompany(osv.Model):
    _inherit = 'res.company'

    _columns = {
        'ruc_company': fields.char('Ruc de la institucion', size=13),
        'cont_especial': fields.char('Nro. contribuyente especial', size=13),
        'ruc_contador': fields.char('Ruc del Contador', size=13),
        'cedula_rl': fields.char('Cédula Representante Legal', size=10),
        'tax_company_id': fields.many2one('res.partner', 'SRI',required=True),
        'iess_id':fields.many2one('res.partner', 'IESS',required=True),
        }

    _defaults = {
        'cont_especial': "",
    }

class AccountVoucher(osv.Model):

    _inherit = 'account.voucher'

    def create_expedient_task(self, cr, uid, ids, context=None):
        return True

    def _check_accounts(self, cr, uid, ids):
        acc_obj = self.pool.get('account.account')
        for obj in self.browse(cr, uid, ids):
            if obj.type not in ['sale', 'purchase']:
                return True
            account_id = obj.account_id.id
            acc_cr_ids = [line.account_id.id for line in obj.line_cr_ids]
            acc_dr_ids = [line.account_id.id for line in obj.line_dr_ids]
            resc = acc_obj.search(cr, uid, [('id','in',acc_cr_ids),('account_c_ids','in',[account_id])])
            resp = acc_obj.search(cr, uid, [('id','in',acc_dr_ids),('account_p_ids','in',[account_id])])
            if not resc and not resp:
                return False
        return True

    _constraints = [
        (_check_accounts, 'Su detalle no tiene relacion con la cuenta por cobrar / pagar seleccionada.', ['Cuenta'])
        ]

#    def onchange_account_id(self, cr, uid, ids, account_id,certificate_id):
#        id=[]   
#        if not account_id:
#            return {}
#        budget_obj = self.pool.get('crossovered.budget.certificate.line')
#        certificate_obj = self.pool.get('crossovered.budget.certificate')
#        post_obj = self.pool.get('account.budget.post')
#        account_obj = self.pool.get('account.account')
#        account = account_obj.browse(cr, uid, account_id)
#        res = post_obj.search(cr, uid, [('account_ids','in',[account_id])])
#        #'budget_line_id.general_budget_id.account_ids','in',[account_id])
#        if not res:
#            return {}        
#        # leer detalle de certificate_id y ver cual tiene el post de la cta
#        certificate = certificate_obj.browse(cr, uid, certificate_id)
#        for lines_cert in certificate.line_ids:
#            for accounts in lines_cert.budget_line_id.general_budget_id.account_ids:
#                if accounts.id==account_id:
#                    id=[lines_cert.id]
#                    break                
#        #line_ids = [line.id for line in certificate.line_ids]
#        partida = budget_obj.search(cr, uid, [('certificate_id','=',certificate.id),('id','in',id)])
#        if partida:
#            budget_id_id=budget_obj.browse(cr,uid,partida[0]).id
#        else:
#            budget_id_id=[]  
#        return {'value':{'budget_id': budget_id_id}}

    def print_ingreso_caja(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de ingreso en caja
        TODO: Revisar el pagado en el reporte
        '''                
        if not context:
            context = {}
        voucher = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [voucher.id],
                 'model': 'account.voucher',
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'customer.pay.pdf',
            'model': 'account.voucher',
            'datas': datas,
            'nodestroy': True,
            }        

    def print_account_move(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de diario
        TODO: Revisar el pagado en el reporte
        '''                
        if not context:
            context = {}
        voucher = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [voucher.move_id.id],
                 'model': 'account.move',
                 'pagado': True}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.move',
            'model': 'account.move',
            'datas': datas,
            'nodestroy': True,
            }        





